import random
import string
import logging
from utills.logging import log_result
from utils import bring_page_to_front

@bring_page_to_front
def sign_up_info(page, email_text, password, name, company_name, phone_number):

    logging.info(f"와탭 페이지로 이동 중...")

    page.goto("https://whatap.io/")

    page.get_by_role("link", name="회원가입").click()

    logging.info(f" 회원가입 정보 입력 중...")
    page.get_by_placeholder("이름을 입력하세요").fill(name) 
    page.get_by_placeholder("회사명을 입력하세요").fill(company_name) 
    page.get_by_placeholder("메일을 입력하세요").fill(email_text)
    page.locator("#password").fill(password)
    page.locator("#password_again").fill(password) 
    page.get_by_placeholder("숫자만 입력하세요").fill(phone_number)

    page.locator("label").filter(has_text="전체 동의").locator("span").click()
    page.locator('#createAccount').click()

    logging.info(f"회원가입 완료")


@bring_page_to_front
def login(page, email, password, test_results):

    try:
        logging.info(f"로그인 페이지로 이동 중...")
        page.goto("https://www.whatap.io/")
        page.get_by_role("link", name="로그인").click()
        page.get_by_placeholder("Company Email").fill(email)
        #logging.info(f"Password being inputted: {password}")
        page.get_by_placeholder("Password").type(password)

        page.wait_for_load_state('networkidle')

        page.get_by_role("button", name="로그인").click()

        # 페이지 로드 완료 후 URL 확인
        after_url = page.url
        logging.info(f"현재 URL: {after_url}")
        expected_value = "account/project"

         # 첫번째 조건: URL에 expected_value가 포함되면 성공
        assert expected_value in after_url, f"로그인 실패"
        
        log_result(True, f" 로그인 성공")
        test_results.append(f" 로그인 성공")

    except AssertionError as e:
        # Assertion 실패 시 로그 및 결과 기록
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        # 기타 예외 처리 로그 및 결과 기록
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


@bring_page_to_front
def logout(page):
    try:
        logging.info(f"로그아웃 시도 중...")
        page.locator('//*[@id="whatap-header-right"]/button[3]').click()
        page.get_by_text("로그아웃").click()
        logging.info(f"로그아웃 성공")
    except Exception as e:
        logging.error(f"로그아웃 중 오류 발생: {str(e)}")


'''필요없는 기능이라 일단 제외
@bring_page_to_front
def reset_password_to_original(page, current_password, new_password):
    try:
        # 계정 관리 메뉴 클릭
        page.locator('//*[@id="whatap-header-right"]/button[3]').click()
        page.click('text="계정 관리"')
        
        # 기존 비밀번호와 새 비밀번호 입력
        page.locator("#currentPassword").fill(current_password)
        page.locator("#newPassword").fill(new_password)
        page.locator("#confirmNewPassword").fill(new_password)
        
        # 비밀번호 변경 버튼 클릭
        page.get_by_role("button", name="비밀번호 변경").click()
        logging.info(f"비밀번호가 {new_password}로 성공적으로 변경되었습니다.")

    except Exception as e:
        logging.error(f"비밀번호 변경 중 오류 발생: {str(e)}")'''


#12 글자 비밀번호 랜덤 생성
def generate_random_password(length=12):
    # 비밀번호는 숫자, 소문자, 대문자, 특수문자 모두 포함해야 함 
    # !@#$%^&*()_+ 이 특수문자만 사용해서 생성
    all_characters = string.ascii_letters + string.digits + "!@#$%^&*()_+"
    
    # 무작위로 한 개의 소문자, 대문자, 숫자, 특수문자를 먼저 포함시킴 (최소 하나씩 포함 보장)
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*()_+")
    ]
    
    # 나머지 길이만큼 무작위로 추가
    password += random.choices(all_characters, k=length - 4)
    random.shuffle(password)
    
    return ''.join(password)
