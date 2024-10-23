import os
import time
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests
import random
import string

# 로깅 설정 파일 위치 따로 설정하기
log_save_path = os.getenv("LOG_FILE_PATH", "./reports/logs/password")  # 로그 파일 경로를 환경 변수로 설정
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


def bring_page_to_front(func):
    def wrapper(*args, **kwargs):
        page = kwargs.get('page', None)
        if page:
            page.bring_to_front()  # 항상 페이지를 앞으로 가져오기
        return func(*args, **kwargs)
    return wrapper


def log_result(success, message):
    if success:
        logging.info(f"✅ {message}")
    else:
        logging.error(f"❌ {message}")


def handle_dialog(dialog):
    global popup_detected
    logging.info(f"팝업 감지됨: {dialog.message}")
    popup_detected = True
    dialog.accept()  # 팝업을 수락


def generate_random_password(length=12):
    # 비밀번호는 숫자, 소문자, 대문자, 특수문자 모두 포함해야 함
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

    # 패스워드 순서를 섞음
    random.shuffle(password)

    # 리스트를 문자열로 변환하여 반환
    return ''.join(password)


@bring_page_to_front
def test_scenario(page, test_name, inputs, button_name, expected_conditions, test_results, text_name=None, popup_expected=False):
    global popup_detected
    
    try:
        if popup_expected:
            page.once("dialog", handle_dialog)  # 팝업 처리 대기

        # 사전을 통해 필드에 대한 입력 방식을 매핑 (패스워드는 특수문자라 type으로 입력이 필요함)
        input_methods = {
            "Password": lambda field, value: field.type(value),
            "default": lambda field, value: field.fill(value),
        }

        # 입력 필드에 값 입력
        for placeholder, value in inputs.items():
            if value is not None:  # None 값은 입력하지 않음
                field = page.get_by_placeholder(placeholder, exact=True)
                # 'Password' 키워드를 포함하면 type(), 그렇지 않으면 fill() 사용
                method = input_methods.get("Password" if "Password" in placeholder else "default")
                method(field, value)

        # 버튼 클릭 또는 텍스트 클릭
        actions = {
            'button': lambda: page.get_by_role("button", name=button_name).click(),
            'text': lambda: page.get_by_text(text_name).click() if text_name is not None else None
        }
        actions['button']() if button_name else actions['text']()

        # 페이지 로드 상태 대기
        page.wait_for_load_state('networkidle')

        # 조건 검증
        condition_map = {
            "url_contains": lambda val: val in page.url,
            "text_present": lambda val: page.query_selector(f"text={val}") is not None,
            "element_present": lambda val: page.query_selector(val) is not None,
            "element_readonly": lambda val: page.query_selector(val).get_attribute("readonly") is not None,
            "popup_detected": lambda val: popup_detected
        }

        for condition_type, condition_value in expected_conditions.items():
            assert condition_map[condition_type](condition_value), f"{test_name} 실패: 조건 '{condition_type}' 검증 실패 - {condition_value}"

        # 성공 로그 기록
        log_result(True, f"{test_name} 성공: 입력값 - {inputs}")
        test_results.append(f"{test_name} 성공: 입력값 - {inputs}")
    
    except AssertionError as e:
        # Assertion 실패 로그 기록
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        # 기타 예외 처리 로그 기록
        log_result(False, f"예외 발생: {str(e)} - 입력값: {inputs}")
        test_results.append(f"예외 발생: {str(e)} - 입력값: {inputs}")


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

        page.wait_for_load_state('networkidle')
        time.sleep(5)
        page.reload()
        
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


@bring_page_to_front
def get_verification_code_from_email(page):
    try:

        page.goto("https://moakt.com/ko/inbox")
        page.wait_for_load_state('networkidle')
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


@bring_page_to_front
def sign_up_info(page, email_text, password, name, company_name, phone_number):

    logging.info(f"{browser_type.name} - 와탭 페이지로 이동 중...")

    page.goto("https://whatap.io/")

    page.get_by_role("link", name="회원가입").click()

    logging.info(f"{browser_type.name} - 회원가입 정보 입력 중...")
    page.get_by_placeholder("이름을 입력하세요").fill(name) 
    page.get_by_placeholder("회사명을 입력하세요").fill(company_name) 
    page.get_by_placeholder("메일을 입력하세요").fill(email_text)
    page.locator("#password").fill(password)
    page.locator("#password_again").fill(password) 
    page.get_by_placeholder("숫자만 입력하세요").fill(phone_number)

    page.locator("label").filter(has_text="전체 동의").locator("span").click()
    page.locator('#createAccount').click()

    logging.info(f"{browser_type.name} - 회원가입 완료")


@bring_page_to_front
def login(page, email, password, test_results):
    try:
        logging.info(f"{browser_type.name} - 로그인 페이지로 이동 중...")
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
        logging.info(f"{browser_type.name} - 로그아웃 시도 중...")
        page.locator('//*[@id="whatap-header-right"]/button[3]').click()
        page.get_by_text("로그아웃").click()
        logging.info(f"로그아웃 성공")
    except Exception as e:
        logging.error(f"로그아웃 중 오류 발생: {str(e)}")


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
        logging.error(f"비밀번호 변경 중 오류 발생: {str(e)}")


def run(playwright):
    #화이트아웃 검증을 해당 스크립트에도 각 화면마다 추가해야할지 고민중
    save_path = os.getenv("WHITEOUT_SCREEN_PATH", "./whiteout_screen")
    code_text = None
    popup_detected = False
    
    # 디렉토리가 없으면 생성
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    global browser_type
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

            # 페이지 전체에 대한 기본 타임아웃 설정
            context.set_default_timeout(120000)  # 120초로 설정
            page = context.new_page()
            page1 = context.new_page()

            #랜덤 메일 생성
            email_text = generate_random_email(page1)

            #랜덤 비밀번호 생성
            random_password = generate_random_password()
            logging.info(f"Generated password : {random_password}")


            #회원가입 정보 입력
            sign_up_info(
                page=page,
                email_text=email_text,
                password=random_password,
                name="노현주_자동화테스트",
                company_name="와탭랩스",
                phone_number="01058485119"
            )

            # 인증 메일 확인 및 인증 처리
            verification_link = verify_email_and_get_link(page1)

            #logging.info(f"Password for login: {random_password}")

            login (
                page=page,
                email=email_text,
                password=random_password,
                test_results=test_results
            )

            logout(page)

            # 1. 비밀번호 재설정 이메일 입력 화면으로 이동 확인
            test_name = "1. 비밀번호 재설정 화면으로 이동 확인"

            inputs = {}

            expected_conditions = {
                "text_present": "비밀번호를 재설정하고자 하는 이메일을 입력해 주세요."
            }

            test_scenario(
                page=page,  
                test_name=test_name,  
                inputs=inputs,
                button_name=None,  
                text_name="비밀번호를 분실하셨습니까?",
                expected_conditions=expected_conditions,  # 기대되는 조건들
                test_results=test_results,  # 테스트 결과 리스트
            )

            #1-1. 이메일 미입력 후 인증번호 요청 버튼 선택한 경우 확인
            test_name = "1-1. 이메일 미입력 후 인증번호 요청 버튼 선택한 경우 확인"

            inputs = {
                 "Email": ""
            }

            expected_conditions = {
                "url_contains": page.url
            }

            test_scenario(
                page=page,  
                test_name=test_name,  
                inputs=inputs,
                button_name="인증 번호 요청",  
                text_name=None,
                expected_conditions=expected_conditions,  # 기대되는 조건들
                test_results=test_results,  # 테스트 결과 리스트
            )

            # 1-2. 잘못된 이메일 형식 입력한 경우 확인
            invalid_emails = ["", " ", "a.com", "abcd@", "abcd@.com", "ㄱㄴㄷ@naver.com", "@naver.com"]

            for email in invalid_emails:
                test_name = "1-2. 잘못된 이메일 형식 입력한 경우 확인"
                
                inputs = {
                    "Email": email,
                }

                expected_conditions = {
                    "url_contains": page.url  # URL이 동일해야 하므로 URL이 변경되지 않음을 확인
                }

                test_scenario(
                    page=page,
                    test_name=test_name,
                    inputs=inputs,
                    button_name="인증 번호 요청",  # 인증 번호 요청 버튼 클릭
                    text_name=None,
                    expected_conditions=expected_conditions,
                    test_results=test_results
                )

            # 1-3. 올바른 이메일 입력한 경우 (테스트 환경 구축되면 이 부분 수정 필요함)
            test_name = "1-3. 올바른 이메일 입력한 경우 확인"

            inputs = {
                "Email": email_text,  # 랜덤으로 생성된 이메일 텍스트
            }

            expected_conditions = {
                "url_contains": "account/lost_password_code",  # 예상되는 URL 부분
                "text_present": "이메일로 발송 된 인증 코드를 입력 해주세요.",  # 예상되는 안내 메시지
                "element_readonly": "#reset_email"  # 이메일 항목이 비활성화되어야 함
            }

            test_scenario(
                page=page,
                test_name=test_name,
                inputs=inputs,
                button_name="인증 번호 요청",  # '인증 번호 요청' 버튼 클릭
                text_name=None,
                expected_conditions=expected_conditions,  # 기대 조건을 설정
                test_results=test_results,  # 테스트 결과를 저장할 리스트
            )

            # 2-1. 인증 번호를 입력하지 않은 경우 확인
            test_name = "2-1. 인증 번호를 입력하지 않은 경우 확인"

            inputs = {}

            expected_conditions = {
                "url_contains": page.url  # URL이 변경되지 않아야 함
            }

            test_scenario(
                page=page,
                test_name=test_name,
                inputs=inputs,  # 빈 입력값
                button_name="확인",  # '확인' 버튼 클릭
                text_name=None,
                expected_conditions=expected_conditions,  # URL이 변경되지 않음
                test_results=test_results  # 결과 저장
            )

            # 2-2. 올바르지 않은 인증 번호를 입력한 경우 확인
            test_name = "2-2. 올바르지 않은 인증 번호를 입력한 경우 확인"

            inputs = {
                "Code": "aa"  
            }

            expected_conditions = {
                "text_present": "인증 번호가 잘못되었습니다." 
            }

            test_scenario(
                page=page,  
                test_name=test_name,  
                inputs=inputs,
                button_name="확인",  
                text_name=None,
                expected_conditions=expected_conditions,  
                test_results=test_results  
            )

            # 2-3. 올바른 인증 번호를 입력한 경우 확인
            try:
                code_text = get_verification_code_from_email(page1)

                if code_text:
                    test_name = "2-3. 올바른 인증 번호를 입력한 경우 확인"
                    inputs = {
                        "Code": code_text  # 추출한 인증 코드를 입력
                    }

                    expected_conditions = {
                        "text_present": "안전한 개인정보 보호를 위해 비밀번호를 변경하여 주세요.",  # 안내 메시지 확인
                        "element_present": "#new_password",  # 새로운 비밀번호 필드가 존재하는지 확인
                        "element_present": "#con_password"  # 새로운 비밀번호 재입력 필드가 존재하는지 확인
                    }

                    test_scenario(
                        page=page,
                        test_name=test_name,
                        inputs=inputs,
                        button_name="확인",  # 확인 버튼 클릭
                        text_name=None,
                        expected_conditions=expected_conditions,
                        test_results=test_results,
                    )
                else:
                    raise Exception("인증 코드가 없어서 테스트를 진행할 수 없습니다.")

            except AssertionError as e:
                log_result(False, str(e))
                test_results.append(str(e))
            except Exception as e:
                log_result(False, f"예외 발생: {str(e)}")
                test_results.append(f"예외 발생: {str(e)}")

            # 3-1 새로운 비밀번호 / 새로운 비밀번호 재입력 항목 미입력한 경우
            test_name = "3-1. 새로운 비밀번호 / 새로운 비밀번호 재입력 항목 미입력한 경우 확인"

            inputs = {
                "새로운 비밀번호": None,  # 비워두기
                "새로운 비밀번호 재입력": None  # 비워두기
            }

            expected_conditions = {
                "text_present": "영문 대/소문자, 숫자, 특수문자를 조합하여 최소 9자리 이상의 길이로 구성되어야 합니다."  # 경고 메시지 확인
            }

            test_scenario(
                page=page,  
                test_name=test_name,  
                inputs=inputs,  
                button_name="비밀번호 변경",  # 버튼명
                text_name=None,
                expected_conditions=expected_conditions,  # 예상 조건
                test_results=test_results  # 결과 저장
            )

            # 3-2. 새로운 비밀번호 항목 입력 + 재입력 항목 미입력한 경우
            test_name = "3-2. 새로운 비밀번호 항목 입력 + 재입력 항목 미입력한 경우 확인"

            inputs = {
                "새로운 비밀번호": "aa",  # 새로운 비밀번호 입력
                "새로운 비밀번호 재입력": None  # 재입력은 비워둠
            }

            expected_conditions = {
                "popup_detected": True  # 팝업이 발생할 것으로 예상
            }

            test_scenario(
                page=page,
                test_name=test_name,
                inputs=inputs,
                button_name="비밀번호 변경",  # 버튼명
                text_name=None,
                expected_conditions=expected_conditions,  # 기대되는 조건들
                test_results=test_results,  # 테스트 결과 리스트
                popup_expected=True  # 팝업이 발생해야 함
            )

            # 3-3. 새로운 비밀번호 항목 미입력 + 재입력 항목 입력한 경우
            test_name = "3-3. 새로운 비밀번호 항목 미입력 + 재입력 항목 입력한 경우 확인"

            inputs = {
                "새로운 비밀번호": None,  # 새로운 비밀번호 입력
                "새로운 비밀번호 재입력": "aa"  # 재입력은 비워둠
            }

            expected_conditions = {
                "popup_detected": True  # 팝업이 발생할 것으로 예상
            }

            test_scenario(
                page=page,
                test_name=test_name,
                inputs=inputs,
                button_name="비밀번호 변경",  # 버튼명
                expected_conditions=expected_conditions,  # 기대되는 조건들
                test_results=test_results,  # 테스트 결과 리스트
                popup_expected=True  # 팝업이 발생해야 함
            )

            # 3-4 새로운 비밀번호와 새로운 비밀번호 재입력 값이 다른경우
            test_name = "3-4. 새로운 비밀번호와 새로운 비밀번호 재입력 값이 다른 경우 확인"

            inputs = {
                "새로운 비밀번호": "bb",  # 새로운 비밀번호 입력
                "새로운 비밀번호 재입력": "aa"  # 재입력은 비워둠
            }

            expected_conditions = {
                "popup_detected": True  # 팝업이 발생할 것으로 예상
            }

            test_scenario(
                page=page,
                test_name=test_name,
                inputs=inputs,
                button_name="비밀번호 변경",  # 버튼명
                text_name=None,
                expected_conditions=expected_conditions,  # 기대되는 조건들
                test_results=test_results,  # 테스트 결과 리스트
                popup_expected=True  # 팝업이 발생해야 함
            )

            # 3-5 잘못된 비밀번호 형식 입력한 경우
            invalid_passwords = ["aaaaa1346", "aaaaa!!@#", "a.com", "12654!!@#", "aa12!"]

            for password in invalid_passwords:
                test_name = "3-5. 잘못된 비밀번호 형식 입력한 경우 확인"
                
                inputs = {
                    "새로운 비밀번호": password,
                    "새로운 비밀번호 재입력": password
                }
                
                expected_conditions = {
                    "text_present": "영문 대/소문자, 숫자, 특수문자를 조합하여 최소 9자리 이상의 길이로 구성되어야 합니다."
                }
                
                test_scenario(
                    page=page,
                    test_name=test_name,
                    inputs=inputs,
                    button_name="비밀번호 변경",
                    text_name=None,
                    expected_conditions=expected_conditions,
                    test_results=test_results
                )

            # 3-6. 연속된 숫자로 비밀번호를 설정한 경우 확인
            test_name = "3-6. 연속된 숫자로 비밀번호를 설정한 경우 확인"

            inputs = {
                "새로운 비밀번호": "test1234567!",
                "새로운 비밀번호 재입력": "test1234567!"
            }

            expected_conditions = {
                "text_present": "잘못된 비밀번호 형식 입니다. (연속된 숫자로 비밀번호를 설정할 수 없습니다.)"
            }

            test_scenario(
                page=page,
                test_name=test_name,
                inputs=inputs,
                button_name="비밀번호 변경",
                text_name=None,
                expected_conditions=expected_conditions,
                test_results=test_results
            )

            # 3-7 잘못된 비밀번호 형식 입력한 경우
            test_name = "3-7. 잘못된 비밀번호 형식 입력한 경우 확인"

            inputs = {
                "새로운 비밀번호": "qwert1266!",
                "새로운 비밀번호 재입력": "qwert1266!"
            }

            expected_conditions = {
                "text_present": "잘못된 비밀번호 형식 입니다. (연속된 키보드 배열로 비밀번호를 설정할 수 없습니다.)"
            }

            test_scenario(
                page=page,
                test_name=test_name,
                inputs=inputs,
                button_name="비밀번호 변경",
                text_name=None,
                expected_conditions=expected_conditions,
                test_results=test_results
            )

            # 3-8. 잘못된 비밀번호 형식(개인 정보 포함) 입력한 경우 확인
            invalid_info = email_text + "!"

            test_name = "3-8. 잘못된 비밀번호 형식(개인 정보 포함) 입력한 경우 확인"
                
            inputs = {
                "새로운 비밀번호": invalid_info,
                "새로운 비밀번호 재입력": invalid_info
            }
                
            expected_conditions = {
                "text_present": "비밀번호에는 전화번호나 이메일을 포함 할 수 없습니다."
            }

            test_scenario(
                page=page,
                test_name=test_name,
                inputs=inputs,
                button_name="비밀번호 변경",
                text_name=None,
                expected_conditions=expected_conditions,
                test_results=test_results
            )

            # 3-9 잘못된 비밀번호 형식 입력한 경우 (지금 버그 있어서 잠깐 비활시킴)
            '''test_name = "3-9. 잘못된 비밀번호 형식 입력한 경우 확인"

            inputs = {
                "새로운 비밀번호": random_password,
                "새로운 비밀번호 재입력": random_password
            }

            expected_conditions = {
                "text_present": "이전에 설정한 비밀번호로 변경할 수 없습니다."
            }

            test_scenario(
                page=page,
                test_name=test_name,
                inputs=inputs,
                button_name="비밀번호 변경",
                text_name=None,
                expected_conditions=expected_conditions,
                test_results=test_results
            )'''

            # 3-10. 올바른 비밀번호 형식 입력한 경우 확인
            random_password2 = generate_random_password()

            test_name = "3-10. 올바른 비밀번호 형식 입력한 경우 확인"

            inputs = {
                "새로운 비밀번호": random_password2,
                "새로운 비밀번호 재입력": random_password2
            }

            expected_conditions = {
                "url_contains": "account/login",  # URL에 "account/login"이 포함되는지 확인
                "element_present": "#id_email",  # 'Company Email' 필드가 존재하는지 확인
                "element_present": "#id_password"  # 'Password' 필드가 존재하는지 확인
            }

            test_scenario(
                page=page,
                test_name=test_name,
                inputs=inputs,
                button_name="비밀번호 변경",
                text_name=None,
                expected_conditions=expected_conditions,
                test_results=test_results
            )

            # 4-1 비밀번호 변경 후 로그인 동작 확인

            #먼저 다른 비밀번호 새로 생성
            random_password3 = generate_random_password()

            test_name = "4-1. 비밀번호 변경 후 로그인 동작 확인"

            inputs = {
                "Company Email": email_text,  # 입력할 이메일
                "Password": random_password2  # 입력할 비밀번호
            }

            expected_conditions = {
                "url_contains": "account/project"  # 로그인 후 이동할 예상 URL
            }

            # 테스트 실행
            test_scenario(
                page=page,
                test_name=test_name,
                inputs=inputs,
                button_name="로그인",
                text_name=None,
                expected_conditions=expected_conditions,
                test_results=test_results
            )

            reset_password_to_original(page, random_password2, random_password3)

            all_results[browser_type.name] = test_results

    finally: 

        logging.info(f"{browser_type.name}_Test complete")  # 각 브라우저 작업 완료 메시지 출력

        for browser_name, results in all_results.items():
            logging.info(f"\n=== {browser_name} 테스트 결과 ===")
            for result in results:
                logging.info(f"[{browser_name}] {result}")
            
with sync_playwright() as playwright:

    run(playwright)

