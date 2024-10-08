from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import requests
from PIL import ImageGrab
import time
import os
import cv2
import glob

def capture_screenshot(page, filename, save_path):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_name = f"{filename}_{timestamp}.png"
    filepath = os.path.join(save_path, screenshot_name)
    page.screenshot(path=filepath)
    print(f"스크린샷이 저장되었습니다: {os.path.abspath(filepath)}")
    return filepath

def check_for_whiteout(page, button_text, save_path):
    whiteout_texts = ["죄송합니다", "페이지를 찾을 수 없습니다.", "Bad Gate", "OOOPS"]
    
    try:
        page_content = page.content()
        found_text = None
        for text in whiteout_texts:
            if text in page_content:
                found_text = text
                break
        
        if found_text:
            print(f"화이트아웃 화면 감지: '{found_text}' 특정 텍스트 발견")
            screenshot_path = capture_screenshot(page, f"whiteout_screen_{found_text}", save_path)
            print(f"화이트아웃 스크린샷 저장됨: {screenshot_path}")
            
            # 화이트 아웃 발생 원인 버튼의 텍스트를 출력
            button_element = page.query_selector(f"//*[text()='{button_text}']")
            if button_element:
                button_text = page.evaluate('(element) => element.textContent', button_element)
                element_html = page.evaluate('(element) => element.outerHTML', button_element)
                print(f"화이트아웃을 발생시킨 버튼 텍스트: {button_text}")
                print(f"화이트아웃을 발생시킨 버튼 HTML:\n{element_html}")
            else:
                print(f"화이트아웃을 발생시킨 버튼 '{button_text}'을(를) 찾을 수 없습니다.")
            
            # 뒤로가기 동작 후의 스크린샷 저장
            page.go_back()
            time.sleep(2)  # 페이지 로딩 대기
            back_screenshot_path = capture_screenshot(page, f"back_screen_{found_text}", save_path)
            print(f"뒤로가기 후 스크린샷 저장됨: {back_screenshot_path}")
            
            raise Exception("화이트아웃 화면 감지됨")
        else:
            print("정상 페이지로 보입니다.")
    except PlaywrightTimeoutError:
        screenshot_path = capture_screenshot(page, "timeout_screen", save_path)
        print(f"페이지를 로드하는 동안 타임아웃이 발생했습니다: {screenshot_path}")

def run(playwright):
    save_path = "/Users/nohhyunju/Documents/whiteout_screen"  # 지정한 저장 경로

    try:
        # Chromium, Firefox, WebKit을 동시에 시작합니다.
        for browser_type in [playwright.chromium, playwright.firefox, playwright.webkit]:
            browser = browser_type.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # 페이지 전체에 대한 기본 타임아웃 설정
            context.set_default_timeout(120000)  # 120초로 설정

            # 랜덤메일 생성
            page.goto("https://moakt.com/ko")
            page.get_by_role("button", name="임의의 주소 가져오기").click()

            email_element_selector = "#email-address"
            email_element = page.wait_for_selector(email_element_selector)
            email_text = email_element.inner_text()
            print("Email Text:", email_text)

            # 회원가입
            page1 = context.new_page()
            page1.goto("https://whatap.io/")

            # 화이트 아웃 확인
            page1.wait_for_timeout(5000)
            check_for_whiteout(page1, "https://whatap.io/", save_path)

            page1.get_by_role("link", name="회원가입").click()

            # 화이트 아웃 확인
            page1.wait_for_timeout(5000)
            check_for_whiteout(page1, "회원가입", save_path)

            page1.get_by_placeholder("이름을 입력하세요").click()
            page1.get_by_placeholder("이름을 입력하세요").fill("노현주_자동화테스트") 
            
            page1.get_by_placeholder("회사명을 입력하세요").click()
            page1.get_by_placeholder("회사명을 입력하세요").fill("와탭랩스") 
            
            page1.get_by_placeholder("메일을 입력하세요").click()
            page1.get_by_placeholder("메일을 입력하세요").fill(email_text)
            
            page1.locator("#password").click()
            page1.locator("#password").fill("Jyoung1637-") 
            
            page1.locator("#password_again").click()
            page1.locator("#password_again").fill("Jyoung1637-") 
            
            page1.locator("label").filter(has_text="전체 동의").locator("span").click()
            #page1.wait_for_timeout(10000)
            #page1.get_by_role("button", name="가입하기").click()
            page1.locator('#createAccount').click()

            # 화이트 아웃 확인
            page1.wait_for_timeout(5000)
            check_for_whiteout(page1, "가입하기", save_path)

            # 인증메일 확인
            page3 = context.new_page()
            page3.goto("https://moakt.com/ko/inbox")
            page3.reload()
            page3.wait_for_timeout(5000)
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

            # 로그인
            page2 = context.new_page()
            page2.goto("https://whatap.io/")

            # 화이트 아웃 확인
            page2.wait_for_timeout(5000)
            check_for_whiteout(page2, "www.whatap.io", save_path)

            page2.wait_for_load_state("domcontentloaded")
            page2.get_by_role("link", name="로그인").click()

            # 화이트 아웃 확인
            page2.wait_for_timeout(5000)
            check_for_whiteout(page2, "로그인", save_path)

            page2.get_by_placeholder("Company Email").click()
            page2.get_by_placeholder("Company Email").fill(email_text)
            page2.get_by_placeholder("Password").click()
            page2.get_by_placeholder("Password").fill("Jyoung1637-")
            page2.get_by_role("button", name="로그인").click()

            #page.goto("https://service.whatap.io/v2/project/ap")

            # 화이트 아웃 확인
            #page2.wait_for_timeout(5000)
            #check_for_whiteout(page2, "https://service.whatap.io/v2/project/ap", save_path)

            # 탈퇴
            page2.locator('//*[@id="whatap-header-right"]/button[3]').click()

            page2.click('text="계정 관리"')

            # 화이트 아웃 확인
            page2.wait_for_timeout(5000)
            check_for_whiteout(page2, "계정 관리", save_path)

            page2.get_by_label("기타").check()
            page2.get_by_placeholder("개선사항이나 남기고 싶으신 의견이 있으시면 기재해주세요").click()
            page2.get_by_placeholder("개선사항이나 남기고 싶으신 의견이 있으시면 기재해주세요").fill("test용")
            page2.get_by_label("(필수) 개인정보 삭제에 동의합니다. (회원님의 계정정보가 와탭에서 삭제됩니다.)").check()
            page2.get_by_role("button", name="회원 탈퇴").click()

            # 화이트 아웃 확인
            page2.wait_for_timeout(5000)
            check_for_whiteout(page2, "회원탈퇴", save_path)

            page2.get_by_placeholder("회원 탈퇴").click()
            page2.get_by_placeholder("회원 탈퇴").fill("회원 탈퇴")
            page2.get_by_role("button", name="확인").click()

            # 화이트 아웃 확인
            page2.wait_for_timeout(5000)
            check_for_whiteout(page2, "확인", save_path)
        
            # 회원탈퇴 후 추가 확인 과정
            page2.get_by_placeholder("Company Email").click()
            page2.get_by_placeholder("Company Email").fill(email_text)
            page2.get_by_placeholder("Password").click()
            page2.get_by_placeholder("Password").fill("Jyoung1637-")
            #page2.get_by_role("button", name="로그인").click()
            page2.locator('#btn_login').click()

             # 화이트 아웃 확인
            page2.wait_for_timeout(5000)
            check_for_whiteout(page2, "로그인", save_path)

            print(f"{browser_type.name} Test complete")

    finally: 
        # Enter를 누르면 실행창 종료
        input("Press Enter to close the browser...")

with sync_playwright() as playwright:
    run(playwright)
