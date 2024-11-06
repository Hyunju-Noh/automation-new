# src/util_tools/login_utils.py
import os
from pages.account.loginpage import LoginPage  # 페이지 객체가 위치한 경로에 맞게 수정
from playwright.sync_api import Playwright

# 로그인 상태가 저장될 세션 디렉토리와 파일 설정
login_session_dir = "src/data/sessions"
login_session_file = "login_state.json"
login_session_path = os.path.join(login_session_dir, login_session_file)

def login_session(playwright: Playwright) -> str:
    """로그인 후 세션 상태를 파일에 저장하고 경로를 반환."""
    
    # 세션 디렉토리가 없으면 생성
    os.makedirs(login_session_dir, exist_ok=True)

    # 세션 파일이 없거나 비어있을 경우에만 로그인 동작 수행
    if not os.path.exists(login_session_path):
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # 로그인 동작 수행
        login_page = LoginPage(page)
        login_page.open()
        login_page.success({"username": "hjnoh@whatap.io", "password": "test1212!"})
        
        # 로그인된 상태를 저장
        context.storage_state(path=login_session_path)
        context.close()
        browser.close()

    return login_session_path  # 저장된 세션 파일 경로 반환