import logging
import pytest
import util_tools.login_utils as login_utils
import util_tools.check_whiteout as whiteout
import util_tools.load_project_data as project_data
import util_tools.logging as log_utils
import util_tools.failures_utils as failures_utils
from pages.account.loginpage import LoginPage
from pages.projects.server_project.dashboard.resourceboardpage import 
from datetime import datetime

@pytest.fixture(scope="session", autouse=True)
def setup_logging_once():
    """테스트 실행 전 전체 설정"""
    log_utils.setup_logging_resourceboardpage()


@pytest.fixture(scope="session")
def login_session_fixture(playwright):
    """로그인 후 세션 상태를 저장한 파일의 경로를 반환"""
    return login_utils.login_session(playwright)


#webkit 브라우저 제외하고 진행
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


    @pytest.mark.usefixtures("setup_playwright_context")
    class Test_ResourceBoard:

        def setup_method(self):
            """ 각 테스트 메서드 전마다 whiteout_detected를 초기화 """
            self.whiteout_detected = False  # 클래스 속성으로 정의하고 각 테스트마다 초기화

        # 태그 값은 나중에 tc에 고유 번호 생성해서, 생성된 고유번호 넣어도 됨
        @pytest.mark.projectmenu
        @pytest.mark.order(1)
        def test_verify_project_menu(self):
            """프로젝트 메뉴 검증"""
            failures = []  # 실패 항목을 저장할 리스트 초기화