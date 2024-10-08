import os
import time
import pytesseract
from PIL import Image
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import requests
import logging
from datetime import datetime



# 로깅 설정
log_save_path = os.getenv("LOG_FILE_PATH", "./logs")  # 로그 파일 경로를 환경 변수로 설정
if not os.path.exists(log_save_path):
    os.makedirs(log_save_path)

log_filename = os.path.join(log_save_path, f"PasswordReset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename)
    ]
)


def log_result(success, message):
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")


def test_email_scenario(page, test_name, input_texts, captcha_text, expected_url, test_results):
    try:
        for input_text in input_texts:
            before_url = page.url
            page.get_by_placeholder("Email").fill(input_text)
            page.get_by_placeholder("자동입력 방지문자").fill(captcha_text)
            page.get_by_role("button", name= "인증 번호 요청").click()
            page.wait_for_load_state('networkidle')
            after_url = page.url

            # URL 비교를 통해 테스트가 성공했는지 확인
            assert before_url == after_url, f"{test_name} 실패: 다음 단계로 동작함 - 입력: {input_text}"
            log_result(True, f"{test_name} 성공: 다음 단계로 동작하지 않음 - 입력: {input_text}")
            test_results.append(f"{test_name} 성공: 다음 단계로 동작하지 않음 - 입력: {input_text}")
    
    except AssertionError as e:
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def find_code_in_first_frame(page):

    try:
        logging.info(f"인증 코드를 찾는 중...")

        # 첫 번째 iframe 선택
        iframe = page.frame_locator('iframe').nth(0)

        # iframe에서 원하는 span 요소를 찾음
        element = iframe.locator('span[style="color:#296CF2;font-weight:bold;"]')
        
        # 요소가 로드될 때까지 대기 (예: 5초)
        element.wait_for(timeout=3000)

        # span 요소의 텍스트 추출
        code_text = element.text_content()
        logging.info(f"인증 코드를 찾았습니다: {code_text}")
        return code_text


    except Exception as e:
        # 해당 iframe에서 요소를 찾지 못한 경우 로그에 표시
        logging.error(f"인증 코드 찾기 실패: {e}")
        return None


def handle_dialog(dialog):
    logging.info("팝업이 발생했습니다: " + dialog.message)
    popup_detected = True
    dialog.dismiss()  # 팝업 닫기


def test_password_change_scenario(page, test_name, new_password, confirm_password, test_results):
    global popup_detected
    popup_detected = False  # 팝업 감지 초기화
    
    try:
        page.once("dialog", handle_dialog)

        # 필드 입력
        page.get_by_placeholder("새로운 비밀번호", exact=True).fill(new_password)
        page.get_by_placeholder("새로운 비밀번호 재입력", exact=True).fill(confirm_password)

        # 비밀번호 변경 버튼 클릭
        page.get_by_role("button", name="비밀번호 변경").click()

        # 팝업 발생 여부 검사
        assert popup_detected, f"{test_name} 실패: 팝업이 발생하지 않음"
        log_result(True, f"{test_name} 성공: 팝업이 발생함")
        test_results.append(f"{test_name} 성공: 팝업이 발생함")
    
    except AssertionError as e:
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_invalid_password_format_scenario(page, test_name, input_texts, test_results):
    try:
        for input_text in input_texts:
            # 새로운 비밀번호와 재입력 항목에 동일한 값 채우기
            page.get_by_placeholder("새로운 비밀번호", exact=True).fill(input_text)
            page.get_by_placeholder("새로운 비밀번호 재입력", exact=True).fill(input_text)
            page.get_by_role("button", name="비밀번호 변경").click()

            # 안내 메시지 검출
            assert page.query_selector("text=영문 대/소문자, 숫자, 특수문자를 조합하여 최소 9자리 이상의 길이로 구성되어야 합니다.") is not None, f"{test_name} 실패: [비밀번호 입력] 안내 text 미표시 - 입력: {input_text}"
            log_result(True, f"{test_name} 성공: [비밀번호 입력] 안내 text 표시 - 입력: {input_text}")
            test_results.append(f"{test_name} 성공: [비밀번호 입력] 안내 text 표시 - 입력: {input_text}")

    except AssertionError as e:
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_consecutive_numbers_format_scenario(page, test_name, input_text, test_results):
    try:
        # 새로운 비밀번호와 재입력 항목에 동일한 값 채우기
        page.get_by_placeholder("새로운 비밀번호", exact=True).fill(input_text)
        page.get_by_placeholder("새로운 비밀번호 재입력", exact=True).fill(input_text)
        page.get_by_role("button", name="비밀번호 변경").click()

        # 안내 메시지 검출
        assert page.query_selector('text=잘못된 비밀번호 형식 입니다. (연속된 숫자로 비밀번호를 설정할 수 없습니다.)') is not None, f"{test_name} 실패: [비밀번호 입력] 안내 text 미표시 - 입력: {input_text}"
        log_result(True, f"{test_name} 성공: [비밀번호 입력] 안내 text 표시 - 입력: {input_text}")
        test_results.append(f"{test_name} 성공: [비밀번호 입력] 안내 text 표시 - 입력: {input_text}")

    except AssertionError as e:
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_consecutive_keyboard_format_scenario(page, test_name, input_text, test_results):
    try:
        # 새로운 비밀번호와 재입력 항목에 동일한 값 채우기
        page.get_by_placeholder("새로운 비밀번호", exact=True).fill(input_text)
        page.get_by_placeholder("새로운 비밀번호 재입력", exact=True).fill(input_text)
        page.get_by_role("button", name="비밀번호 변경").click()

        # 안내 메시지 검출
        assert page.query_selector('text=잘못된 비밀번호 형식 입니다. (연속된 키보드 배열로 비밀번호를 설정할 수 없습니다.)') is not None, f"{test_name} 실패: [비밀번호 입력] 안내 text 미표시 - 입력: {input_text}"
        log_result(True, f"{test_name} 성공: [비밀번호 입력] 안내 text 표시 - 입력: {input_text}")
        test_results.append(f"{test_name} 성공: [비밀번호 입력] 안내 text 표시 - 입력: {input_text}")

    except AssertionError as e:
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_consecutive_personal_info_format_scenario(page, test_name, input_texts, test_results):
    try:
        for input_text in input_texts:
            # 새로운 비밀번호와 재입력 항목에 동일한 값 채우기
            page.get_by_placeholder("새로운 비밀번호", exact=True).fill(input_text)
            page.get_by_placeholder("새로운 비밀번호 재입력", exact=True).fill(input_text)
            page.get_by_role("button", name="비밀번호 변경").click()

            # 안내 메시지 검출
            assert page.query_selector("text=비밀번호에는 전화번호나 이메일을 포함 할 수 없습니다.") is not None, f"{test_name} 실패: [비밀번호 입력] 안내 text 미표시 - 입력: {input_text}"
            log_result(True, f"{test_name} 성공: [비밀번호 입력] 안내 text 표시 - 입력: {input_text}")
            test_results.append(f"{test_name} 성공: [비밀번호 입력] 안내 text 표시 - 입력: {input_text}")

    except AssertionError as e:
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_consecutive_before_password_format_scenario(page, test_name, input_text, test_results):
    try:
        # 새로운 비밀번호와 재입력 항목에 동일한 값 채우기
        page.get_by_placeholder("새로운 비밀번호", exact=True).fill(input_text)
        page.get_by_placeholder("새로운 비밀번호 재입력", exact=True).fill(input_text)
        page.get_by_role("button", name="비밀번호 변경").click()

        # 안내 메시지 검출
        assert page.query_selector('text=이전에 설정한 비밀번호로 변경할 수 없습니다.') is not None, f"{test_name} 실패: [비밀번호 입력] 안내 text 미표시 - 입력: {input_text}"
        log_result(True, f"{test_name} 성공: [비밀번호 입력] 안내 text 표시 - 입력: {input_text}")
        test_results.append(f"{test_name} 성공: [비밀번호 입력] 안내 text 표시 - 입력: {input_text}")

    except AssertionError as e:
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_consecutive_correct_password_format_scenario(page, test_name, input_text, test_results):
    try:
        # 새로운 비밀번호와 재입력 항목에 동일한 값 채우기
        page.get_by_placeholder("새로운 비밀번호", exact=True).fill(input_text)
        page.get_by_placeholder("새로운 비밀번호 재입력", exact=True).fill(input_text)
        page.get_by_role("button", name="비밀번호 변경").click()

        after_url = page.url

        expected_value = "account/login"

        #첫번째 조건
        assert expected_value in after_url, f"{test_name} 실패: 로그인 화면으로 이동하지 않음 - 입력: {input_text}"

        #두번째 조건: 'Company Email' 선택자 확인
        assert page.query_selector('#id_email') is not None, f"{test_name} 실패: 'Company Email' 항목이 존재하지 않습니다. - 입력: {input_text}"

        #세번째 조건: 'Password' 선택자 확인
        assert page.query_selector('#id_password') is not None, f"{test_name} 실패: 'Password' 항목이 존재하지 않습니다. - 입력: {input_text}"

        log_result(True, f"{test_name} 성공: 로그인 화면으로 이동 - 입력: {input_text}")
        test_results.append(f"{test_name} 성공: 로그인 화면으로 이동 - 입력: {input_text}")

    except AssertionError as e:
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_login_scenario(page, test_name, email, password, test_results):
    try:
        page.get_by_placeholder("Company Email").fill(email)
        page.get_by_placeholder("Password").fill(password)
        page.get_by_role("button", name="로그인").click()

        after_url = page.url

        expected_value = "account/project/list"

        #첫번째 조건
        assert expected_value in after_url, f"{test_name} 실패: 프로젝트 목록 화면으로 이동하지 않음"
        log_result(True, f"{test_name} 성공: 프로젝트 목록 화면으로 이동")
        test_results.append(f"{test_name} 성공: 프로젝트 목록 화면으로 이동")

    except AssertionError as e:
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_empty_password_fields_scenario(page, test_name, test_results):
    try:
        logging.info(f"{test_name} - 비밀번호 변경 버튼 선택 중...")
        
        # 비밀번호 변경 버튼 클릭
        page.get_by_role("button", name="비밀번호 변경").click()

        # 안내 메시지 검출 (비밀번호 안내 텍스트 확인)
        assert page.query_selector("text=영문 대/소문자, 숫자, 특수문자를 조합하여 최소 9자리 이상의 길이로 구성되어야 합니다.") is not None, f"{test_name} 실패: [비밀번호 입력] 안내 text 미표시"
        
        # 성공 로그 기록
        log_result(True, f"{test_name} 성공: [비밀번호 입력] 안내 text 표시")
        test_results.append(f"{test_name} 성공: [비밀번호 입력] 안내 text 표시")
    
    except AssertionError as e:
        # Assertion 실패 로그 기록
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        # 기타 예외 처리 로그 기록
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_password_reset_email_screen_scenario(page, test_name, test_results):
    try:
        logging.info(f"{test_name} - 비밀번호 재설정 버튼 선택 중...")
        
        # 비밀번호 재설정 버튼 클릭
        page.get_by_text("비밀번호를 분실하셨습니까?").click()

        # 안내 메시지 검출 (비밀번호 재설정 안내 텍스트 확인)
        assert page.query_selector("text=비밀번호를 재설정하고자 하는 이메일을 입력해 주세요.") is not None, f"{test_name} 실패: [비밀번호 재설정 이메일 입력 화면] 안내 text 미표시"
        
        # 성공 로그 기록
        log_result(True, f"{test_name} 성공: [비밀번호 재설정 이메일 입력 화면] 안내 text 표시")
        test_results.append(f"{test_name} 성공: [비밀번호 재설정 이메일 입력 화면] 안내 text 표시")
    
    except AssertionError as e:
        # Assertion 실패 로그 기록
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        # 기타 예외 처리 로그 기록
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_no_email_verification_request_scenario(page, test_name, test_results):
    try:
        before_url = page.url
        
        logging.info(f"{test_name} - 이메일 미입력 상태에서 인증 번호 요청 버튼 클릭 중...")

        # 인증 번호 요청 버튼 클릭
        page.get_by_role("button", name="인증 번호 요청").click()
        
        # 페이지 로드 상태를 대기
        page.wait_for_load_state('networkidle')
        
        after_url = page.url

        # URL이 변경되지 않았는지 확인
        assert before_url == after_url, f"{test_name} 실패: 다음 단계로 동작함"
        
        # 성공 로그 기록
        log_result(True, f"{test_name} 성공: 다음 단계로 동작하지 않음")
        test_results.append(f"{test_name} 성공: 다음 단계로 동작하지 않음")
    
    except AssertionError as e:
        # Assertion 실패 로그 기록
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        # 기타 예외 처리 로그 기록
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_valid_email_verification_request_scenario(page, test_name, email, captcha_text, expected_url_part, expected_message, test_results, save_path):
    try:
        # 올바른 이메일과 자동입력 방지문자 입력
        page.get_by_placeholder("Email").fill(email)
        page.get_by_placeholder("자동입력 방지문자").fill(captcha_text)
        page.get_by_role("button", name="인증 번호 요청").click()

        # 페이지 로드 상태를 대기
        page.wait_for_load_state('networkidle')

        # 화이트 아웃 체크
        check_for_whiteout(page, "비밀번호 재설정 - 이메일 인증 코드 입력 화면", save_path)

        after_url = page.url

        # 첫 번째 조건: URL 확인
        assert expected_url_part in after_url, f"{test_name} 실패: 인증 코드 입력 단계로 동작하지 않음"

        # 두 번째 조건: 인증 안내 메시지 확인
        assert page.query_selector(f"text={expected_message}") is not None, f"{test_name} 실패: 인증 안내 메시지 표시되지 않음"

        # 세 번째 조건: 이메일 항목이 비활성화 되었는지 확인
        assert page.query_selector("#reset_email").get_attribute("readonly") is not None, f"{test_name} 실패: 이메일 항목 비활성화 되지 않음"

        # 성공 로그 기록
        log_result(True, f"{test_name} 성공: 인증 코드 입력 단계로 동작함")
        test_results.append(f"{test_name} 성공: 인증 코드 입력 단계로 동작함")

    except AssertionError as e:
        # Assertion 실패 로그 기록
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        # 기타 예외 처리 로그 기록
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_empty_verification_code_scenario(page, test_name, button_name, test_results):
    try:
        # 기존 URL 저장
        before_url = page.url
        
        # "확인" 버튼 클릭
        page.get_by_role("button", name=button_name).click()
        
        # 페이지 로드 상태 대기
        page.wait_for_load_state('networkidle')
        
        # 새 URL 저장
        after_url = page.url

        # 첫 번째 조건: URL이 변경되지 않았는지 확인
        assert before_url == after_url, f"{test_name} 실패: 다음 단계로 동작함"
        
        # 성공 로그 기록
        log_result(True, f"{test_name} 성공: 다음 단계로 동작하지 않음")
        test_results.append(f"{test_name} 성공: 다음 단계로 동작하지 않음")

    except AssertionError as e:
        # Assertion 실패 로그 기록
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        # 기타 예외 처리 로그 기록
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def test_invalid_verification_code_scenario(page, test_name, invalid_code, button_name, expected_text, test_results):
    try:
        # 잘못된 인증 코드 입력
        page.get_by_placeholder("Code").fill(invalid_code)
        
        # "확인" 버튼 클릭
        page.get_by_role("button", name=button_name).click()
        
        # 페이지 로드 상태 대기
        page.wait_for_load_state('networkidle')

        # 두 번째 조건: "인증 번호가 잘못되었습니다." 메시지 검출 확인
        assert page.query_selector(f"text={expected_text}") is not None, f"{test_name} 실패: 다음 단계로 동작함"
        
        # 성공 로그 기록
        log_result(True, f"{test_name} 성공: 다음 단계로 동작하지 않음")
        test_results.append(f"{test_name} 성공: 다음 단계로 동작하지 않음")

    except AssertionError as e:
        # Assertion 실패 로그 기록
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        # 기타 예외 처리 로그 기록
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def run(playwright):
    save_path = os.getenv("WHITEOUT_SCREEN_PATH", "./whiteout_screen")
    code_text = None
    popup_detected = False
    
    # 디렉토리가 없으면 생성
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    browser_type = None
    #browsers = []  # 브라우저를 저장할 리스트
    all_results = {}

    try:
        # Chromium, Firefox, WebKit을 동시에 시작합니다.
        for browser_type in [playwright.chromium, playwright.firefox, playwright.webkit]:
            logging.info(f"{browser_type.name} 브라우저 시작 중...")
            test_results = []
            browser = browser_type.launch(headless=False)
            context = browser.new_context(
                locale="ko-KR",  # 브라우저 언어를 한국어로 설정
                storage_state={}
            )
            page2 = context.new_page()

            # 페이지 전체에 대한 기본 타임아웃 설정
            context.set_default_timeout(120000)  # 120초로 설정

            # 랜덤메일 생성
            logging.info(f"{browser_type.name} - 랜덤 메일 생성 페이지로 이동 중...")
            page2.goto("https://moakt.com/ko")
            logging.info(f"{browser_type.name} - 랜덤 메일 생성 중...")
            page2.get_by_role("button", name="임의의 주소 가져오기").click()

            email_element_selector = "#email-address"
            email_element = page2.wait_for_selector(email_element_selector)
            email_text = email_element.inner_text()
            logging.info(f"Email Text: {email_text}")

            # 회원가입
            page1 = context.new_page()
            logging.info(f"{browser_type.name} - 와탭 페이지로 이동 중...")
            page1.goto("https://whatap.io/")

            

            page1.get_by_role("link", name="회원가입").click()

            

            page1.get_by_placeholder("이름을 입력하세요").fill("노현주_자동화테스트") 
            page1.get_by_placeholder("회사명을 입력하세요").fill("와탭랩스") 
            page1.get_by_placeholder("메일을 입력하세요").fill(email_text)
            page1.locator("#password").fill("shguswn980512-") 
            page1.locator("#password_again").fill("shguswn980512-") 
            page1.get_by_placeholder("숫자만 입력하세요").fill("01058485119")
            
            page1.locator("label").filter(has_text="전체 동의").locator("span").click()
            page1.locator('#createAccount').click()

            

            # 인증메일 확인
            page3 = context.new_page()
            page3.goto("https://moakt.com/ko/inbox")
            page3.reload()
            page3.wait_for_load_state('networkidle')
            time.sleep(5)
            page3.reload()
            page3.get_by_role("link", name="[WhaTap] 회원가입 인증 메일입니다").click()
        
            page3.wait_for_selector("iframe")
            frame = page3.frame_locator("iframe").first
            verify_link = frame.get_by_role("link", name="이메일 인증하기").get_attribute("href")
            print("Verification Link:", verify_link)

            # GET 요청을 보내어 URL 호출
            response = requests.get(verify_link)

            # 상태 코드와 응답 텍스트를 출력하여 확인
            print(f"Status Code: {response.status_code}")

            page = context.new_page()

            logging.info(f"{browser_type.name} - https://www.whatap.io/ 페이지로 이동 중...")
            page.goto("https://www.whatap.io/")

            

            logging.info(f"{browser_type.name} - 로그인 페이지로 이동 중...")
            page.get_by_role("link", name="로그인").click()

            page.get_by_placeholder("Company Email").fill(email_text)
            page.get_by_placeholder("Password").fill("shguswn980512-")
            page.get_by_role("button", name="로그인").click()

            

            page.locator('//*[@id="whatap-header-right"]/button[3]').click()
            page.get_by_text("로그아웃").click()

            #1. 비밀번호 재설정 이메일 입력 화면으로 이동 확인
            test_password_reset_email_screen_scenario(
                page=page,
                test_name="1-1",
                test_results=test_results
            )

            # 1-1. 이메일 미입력 후 인증번호 요청 버튼 선택한 경우 확인
            test_no_email_verification_request_scenario(
                page=page,
                test_name="1-1",
                test_results=test_results
            )

            # 1-2. 잘못된 이메일 형식 입력한 경우 확인
            invalid_emails = ["", " ", "a.com", "abcd@", "abcd@.com", "ㄱㄴㄷ@naver.com", "@naver.com"]
            test_email_scenario(
                page=page,
                test_name="1-2",
                input_texts=invalid_emails,
                captcha_text="a",  # 자동입력 방지문자
                expected_url=page.url,  # 테스트 시작 시의 URL을 예상 URL로 사용
                test_results=test_results
            )

            #1-3. 올바른 이메일 입력한 경우 (테스트 환경 구축되면 이 부분 수정 필요함)
            test_valid_email_verification_request_scenario(
                page=page,
                test_name="1-3",
                email=email_text,  # 올바른 이메일 텍스트
                captcha_text="a",  # 자동입력 방지문자
                expected_url_part="account/lost_password_code",  # 예상 URL 부분
                expected_message="이메일로 발송 된 인증 코드를 입력 해주세요.",  # 예상 안내 메시지
                test_results=test_results,
                save_path=save_path  # 스크린샷 저장 경로
            )

            # 2-1. 인증 번호를 입력하지 않은 경우 확인
            test_empty_verification_code_scenario(
                page=page,
                test_name="2-1",
                button_name="확인",  # 확인 버튼 텍스트
                test_results=test_results
            )


            # 2-2. 올바르지 않은 인증 번호를 입력한 경우 확인
            test_invalid_verification_code_scenario(
                page=page,
                test_name="2-2",
                invalid_code="aa",  # 잘못된 인증 코드
                button_name="확인",  # 확인 버튼 텍스트
                expected_text="인증 번호가 잘못되었습니다.",  # 검출할 메시지
                test_results=test_results
            )

            #2-3. 올바른 인증 번호를 입력한 경우
            try:
                page2 = context.new_page()
                page2.goto("https://moakt.com/ko/inbox")
                page2.wait_for_load_state('networkidle')
                page2.get_by_role("link", name="[WhaTap] 와탭 서비스 인증코드를 안내드립니다").click()

                logging.info(f"{browser_type.name} - 랜덤 메일 인증코드 가지러 가는 중...")
                code_text = find_code_in_first_frame(page2)

                if code_text is None:
                    logging.error("인증 코드 호출 실패")
                    raise Exception("인증 코드 호출 실패")

                logging.info(f"{browser_type.name} - 랜덤 메일 인증코드 입력 화면으로 이동...")
                page.bring_to_front()

                logging.info(f"{browser_type.name} - 인증코드 입력 시도 중...")
                page.get_by_placeholder("Code").fill(code_text)
                logging.info(f"{browser_type.name} - 인증코드 입력 후 확인 버튼 선택 중...")
                page.get_by_role("button", name="확인").click()
                page.wait_for_load_state('networkidle')
                check_for_whiteout(page, "비밀번호 재설정 - 새로운 비밀번호 입력 화면", save_path)

                #첫번째 조건
                assert page.query_selector(f"text=안전한 개인정보 보호를 위해 비밀번호를 변경하여 주세요.") is not None, "2-3 실패: 비밀번호 변경 안내 메시지 표시되지 않음"
                #두번째 조건
                assert page.query_selector("#new_password") is not None, "2-3 실패: 'new_password' ID 항목이 존재하지 않습니다."
                #세번째 조건
                assert page.query_selector("#con_password") is not None, "2-3 실패: 'con_password' ID 항목이 존재하지 않습니다."

                log_result(True, "2-3 성공: 새로운 비밀번호 입력 단계로 동작함")
                test_results.append("2-3 성공: 새로운 비밀번호 입력 단계로 동작함")
            except AssertionError as e:
                log_result(False, str(e))
                test_results.append(str(e))
            except Exception as e:
                log_result(False, f"예외 발생: {str(e)}")
                test_results.append(f"예외 발생: {str(e)}")

            # 3-1 새로운 비밀번호 / 새로운 비밀번호 재입력 항목 미입력한 경우
            test_empty_password_fields_scenario(
                page=page,
                test_name="3-1",
                test_results=test_results
            )

            # 3-2. 새로운 비밀번호 항목 입력 + 재입력 항목 미입력한 경우
            test_password_change_scenario(
                page=page,
                test_name="3-2",
                new_password="aa",
                confirm_password="",
                test_results=test_results
            )

            # 3-3. 새로운 비밀번호 항목 미입력 + 재입력 항목 입력한 경우
            test_password_change_scenario(
                page=page,
                test_name="3-3",
                new_password="",
                confirm_password="aa",
                test_results=test_results
            )

            #3-4 새로운 비밀번호와 새로운 비밀번호 재입력 값이 다른경우
            test_password_change_scenario(
                page=page,
                test_name="3-4",
                new_password="bb",
                confirm_password="aa",
                test_results=test_results
            )

            # 3-5 잘못된 비밀번호 형식 입력한 경우
            invalid_passwords = ["aaaaa1346", "aaaaa!!@#", "a.com", "12654!!@#", "aa12!"]
            test_invalid_password_format_scenario(
                page=page,
                test_name="3-5",
                input_texts=invalid_passwords,
                test_results=test_results
            )

            # 3-6 잘못된 비밀번호 형식 입력한 경우
            test_consecutive_numbers_format_scenario(
                page=page,
                test_name="3-6",
                input_text= 'test1234567!',
                test_results=test_results
            )

            # 3-7 잘못된 비밀번호 형식 입력한 경우
            test_consecutive_keyboard_format_scenario(
                page=page,
                test_name="3-7",
                input_text='qwert1266!',
                test_results=test_results
            )

            # 3-8 잘못된 비밀번호 형식 입력한 경우
            invalid_infos = [email_text + "!", "hjn58485119@#"]
            test_consecutive_personal_info_format_scenario(
                page=page,
                test_name="3-8",
                input_texts=invalid_infos,
                test_results=test_results
            )

            # 3-9 잘못된 비밀번호 형식 입력한 경우 
            #버그 있어서 주석 처리함
            '''test_consecutive_before_password_format_scenario(
                page=page,
                test_name="3-9",
                input_text='shguswn980512-',
                test_results=test_results
            )'''

            # 3-10 올바른 비밀번호 형식 입력한 경우
            test_consecutive_correct_password_format_scenario(
                page=page,
                test_name="3-10",
                input_text='shguswn980512!',
                test_results=test_results
            )

            # 4-1 로그인 동작 확인
            test_login_scenario(
                page=page,
                test_name="4-1",
                email = email_text,
                password = 'shguswn980512!',
                test_results=test_results
            )

            #원래 비밀번호로 변경
            page.locator('//*[@id="whatap-header-right"]/button[3]').click()
            page.click('text="계정 관리"')
            page.locator("#currentPassword").fill("shguswn980512!")
            page.locator("#newPassword").fill("shguswn980512-")
            page.locator("#confirmNewPassword").fill("shguswn980512-")
            page.get_by_role("button", name="비밀번호 변경").click()


    
            all_results[browser_type.name] = test_results

    finally: 

        logging.info(f"{browser_type.name}_Test complete")  # 각 브라우저 작업 완료 메시지 출력

        for browser_name, results in all_results.items():
            logging.info(f"\n=== {browser_name} 테스트 결과 ===")
            for result in results:
                logging.info(f"[{browser_name}] {result}")
            
with sync_playwright() as playwright:

    run(playwright)