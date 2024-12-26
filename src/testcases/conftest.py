import pytest
import logging
import util_tools.check_whiteout as whiteout
import util_tools.login_utils as login_utils

@pytest.fixture(scope="session")
def login_session_fixture(playwright):
    """로그인 후 세션 상태를 저장한 파일의 경로를 반환"""
    return login_utils.login_session(playwright)

@pytest.fixture(scope="class", params=["chromium", "firefox"])
def setup_playwright_context(request, playwright, login_session_fixture):
    """각 브라우저에서 Playwright 설정을 초기화."""
    
    # whiteout 텍스트 로드
    whiteout_texts = whiteout.load_whiteout_texts()

    # 브라우저 타입에 따라 설정
    browser_type = request.param
    browser = getattr(playwright, browser_type).launch(headless=False)
    logging.info(f"{browser_type} 브라우저 시작 중...")

    context = browser.new_context(
        locale="ko-KR",
        storage_state=login_session_fixture  # 저장된 로그인 상태를 불러오기
    )
    context.set_default_timeout(120000)
    request.cls.page = context.new_page()

    # 테스트 클래스에서 공통 사용되는 설정
    request.cls.whiteout_texts = whiteout_texts
    request.cls.save_path = whiteout.get_whiteout_save_path()
    request.cls.browser_type = browser_type

    yield
    context.close()
