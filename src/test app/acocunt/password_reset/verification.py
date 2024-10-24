import time
import requests
import logging
from utils import bring_page_to_front
from logging_utils import log_result
from globals import code_text

#디버그 로깅
logging.basicConfig(level=logging.DEBUG)

@bring_page_to_front
def generate_random_email(page):

    logging.info("랜덤 메일 생성 페이지로 이동 중...")
    page.goto("https://moakt.com/ko")
    
    logging.info("랜덤 메일 생성 중...")
    page.get_by_role("button", name="임의의 주소 가져오기").click()

    # 이메일 주소 선택자에서 텍스트 추출
    email_element = page.wait_for_selector("#email-address")
    email_text = email_element.inner_text()
    
    logging.info(f"생성된 랜덤 이메일: {email_text}")
    return email_text


@bring_page_to_front
def verify_email_and_get_link(page):
    try:
        # 받은 편지함으로 이동
        logging.info("인증 메일 확인을 위해 받은 편지함으로 이동 중...")
        page.goto("https://moakt.com/ko/inbox")

        logging.debug("DEBUG: This is a debug message.")
        page.wait_for_load_state('networkidle')
        logging.debug("DEBUG: This is a debug message.")
        time.sleep(5)
        #page.reload()
        logging.debug("DEBUG: This is a debug message.")
        page.goto(page.url)
        
        logging.info("인증 메일 클릭 중...")
        page.get_by_role("link", name="[WhaTap] 회원가입 인증 메일입니다").click()

        page.wait_for_selector("iframe")
        frame = page.frame_locator("iframe").first
        verify_link = frame.get_by_role("link", name="이메일 인증하기").get_attribute("href")

        response = requests.get(verify_link)

        if response.status_code == 200:
            logging.info("인증 메일 확인 및 인증 링크 호출 성공")
        else:
            logging.error(f"인증 링크 호출 실패: 상태 코드 {response.status_code}")

    except Exception as e:
        logging.error(f"인증 메일 확인 중 오류 발생: {str(e)}")


@bring_page_to_front
def get_verification_code_from_email(page):
    try:

        page.goto("https://moakt.com/ko/inbox")
        logging.debug("DEBUG: This is a debug message.")
        page.wait_for_load_state('networkidle')
        logging.debug("DEBUG: This is a debug message.")
        page.goto(page.url)
        page.get_by_role("link", name="[WhaTap] 와탭 서비스 인증코드를 안내드립니다").click()
        logging.info("랜덤 메일 인증코드 찾는 중...")

        code_text = find_code_in_first_frame(page)

        if code_text is None:
            logging.error("인증 코드 호출 실패")
            raise Exception("인증 코드 호출 실패")

        return code_text

    except Exception as e:
        logging.error(f"인증 코드 추출 중 오류 발생: {str(e)}")
        return None


def find_code_in_first_frame(page):

    try:
        logging.info(f"인증 코드를 찾는 중...")

        iframe = page.frame_locator('iframe').nth(0)

        element = iframe.locator('span[style="color:#296CF2;font-weight:bold;"]')

        element.wait_for(timeout=3000)

        code_text = element.text_content()
        logging.info(f"인증 코드를 찾았습니다: {code_text}")
        return code_text


    except Exception as e:

        logging.error(f"인증 코드 찾기 실패: {e}")
        return None
    
