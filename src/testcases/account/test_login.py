import logging
import pytest
import util_tools.check_whiteout as whiteout
import util_tools.load_project_data as project_data
import util_tools.logging as log_utils
from pages.account.loginpage import LoginPage
from pages.projects.projectpage import ProjectPage
from datetime import datetime

# 로그가 안찍혀,,,,
@pytest.fixture(scope="session", autouse=True)
def setup_logging_once():
    """테스트 실행 전 전체 설정"""
    log_utils.setup_logging_projectpage()

@pytest.fixture(scope="class", params=["chromium", "firefox", "webkit"])
def setup_playwright_context(request, playwright):
    """각 브라우저에서 Playwright 설정을 초기화."""

    # 브라우저 타입에 따라 설정
    browser_type = request.param
    browser = getattr(playwright, browser_type).launch(headless=False)
    logging.info(f"{browser_type} 브라우저 시작 중...")
    
    context = browser.new_context(locale="ko-KR", storage_state={})
    context.set_default_timeout(120000)
    request.cls.page = context.new_page()

    # 테스트 클래스에서 공통 사용되는 설정
    request.cls.WHITEOUT_TEXTS = whiteout.load_whiteout_texts()
    request.cls.save_path = whiteout.get_whiteout_save_path()
    request.cls.browser_type = browser_type

    yield
    context.close()
    #browser.close()


@pytest.mark.usefixtures("setup_playwright_context")
class Test_ProjectMenus:

    def setup_method(self):
        """각 테스트 메서드 전마다 whiteout_detected를 초기화"""
        self.whiteout_detected = False  # 클래스 속성으로 정의하고 각 테스트마다 초기화

    # 태그 값은 나중에 tc에 고유 번호 생성해서, 생성된 고유번호 넣어도 됨
    @pytest.mark.login
    @pytest.mark.order(1)
    def test_login_and_verify(self):
        login_page = LoginPage(self.page)
        
        # 로그인 페이지로 이동
        login_page.open()
        
        # 로그인 동작 수행
        login_page.success({"username": "hjnoh@whatap.io", "password": "shguswn980512!"})
        
        # 로그인 성공 검증
        expected_value = "account/project"
        assert expected_value in self.page.url, f"로그인 실패"
        logging.info("로그인 성공 확인")