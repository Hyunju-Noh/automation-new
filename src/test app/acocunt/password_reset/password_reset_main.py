from playwright.sync_api import sync_playwright
from utils import bring_page_to_front, handle_dialog
from utils.logging import setup_logging, log_result
from useraccount_actions import sign_up_info, login, logout, generate_random_password
from verification import verify_email_and_get_link, get_verification_code_from_email, generate_random_email, find_code_in_first_frame
from password_reset import password_reset
from globals import popup_detected, code_text, browser_type

import logging

def run(playwright):

    setup_logging()

    #화이트아웃 검증을 해당 스크립트에도 각 화면마다 추가해야할지 고민중
    #save_path = os.getenv("WHITEOUT_SCREEN_PATH", "./whiteout_screen")

    # 디렉토리가 없으면 생성
    #if not os.path.exists(save_path):
    #    os.makedirs(save_path)

    global browser_type
    global popup_detected
    global code_text

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

            password_reset(
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

            password_reset(
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

                password_reset(
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

            password_reset(
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

            password_reset(
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

            password_reset(
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

                    password_reset(
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

            password_reset(
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

            password_reset(
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

            password_reset(
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

            password_reset(
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
                
                password_reset(
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

            password_reset(
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

            password_reset(
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

            password_reset(
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

            password_reset(
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

            password_reset(
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
            password_reset(
                page=page,
                test_name=test_name,
                inputs=inputs,
                button_name="로그인",
                text_name=None,
                expected_conditions=expected_conditions,
                test_results=test_results
            )

            #reset_password_to_original(page, random_password2, random_password3)

            all_results[browser_type.name] = test_results

    finally: 

        logging.info(f"{browser_type.name}_Test complete")  # 각 브라우저 작업 완료 메시지 출력

        for browser_name, results in all_results.items():
            logging.info(f"\n=== {browser_name} 테스트 결과 ===")
            for result in results:
                logging.info(f"[{browser_name}] {result}")
            
if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)