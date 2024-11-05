import logging
import pytest
from utils import *
from src.pages.account.loginpage import LoginPage
from src.pages.projects.projectpage import ProjectPage
from datetime import datetime

@pytest.fixture(scope="class", params=["chromium", "firefox", "webkit"])
def setup_playwright_context(request, playwright):
    """각 브라우저에서 Playwright 설정을 초기화."""
    #프로젝트메뉴 진입에 사용되는 로깅 설정
    utils.setup_logging_projectpage()

    # 브라우저 타입에 따라 설정
    browser_type = request.param
    browser = getattr(playwright, browser_type).launch(headless=False)
    logging.info(f"{browser_type} 브라우저 시작 중...")
    
    context = browser.new_context(locale="ko-KR", storage_state={})
    context.set_default_timeout(120000)
    request.cls.page = context.new_page()

    # 테스트 클래스에서 공통 사용되는 설정
    request.cls.WHITEOUT_TEXTS = load_whiteout_texts()
    request.cls.save_path = get_whiteout_save_path()
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
        login_page.login_success({"username": "hjnoh@whatap.io", "password": "shguswn980512"})
        
        # 로그인 성공 검증
        expected_value = "account/project"
        assert expected_value in self.page.url, f"로그인 실패"
        logging.info("로그인 성공 확인")


    @pytest.mark.projectmenu
    @pytest.mark.order(2)
    def test_verify_project_menu(self):
        """프로젝트 메뉴 검증"""
        project_page = ProjectPage(self.page)

        # 프로젝트 데이터를 로드하고 메뉴 검증 수행
        projects = load_project_data()

        for project in projects:
            project_type = project["type"]
            project_id = project["id"]

            # 프로젝트 데이터 로드 후, 해당 프로젝트 화면으로 이동
            project_page.open(project_type, project_id)

            # 프로젝트 화면 화이트아웃 확인
            whiteout_detected = check_for_whiteout(self.page, f"{project_type} {project_id} 메인 화면", self.save_path)
            assert not whiteout_detected, f"화이트 아웃이 감지되었습니다: {project_type} {project_id} 메인 화면" 

            # 상위 메뉴 클릭하여 하위 메뉴 오픈
            project_page.open_sub_menus()

            # 하위 메뉴 태그 요소 가져오기
            menu_elements = project_page.get_menu_items()

            for element in menu_elements:
                href_value = project_page.click_menu_item(element)
                project_page.check_modal_and_wait()

                whiteout_detected = check_for_whiteout(self.page, href_value, self.save_path)
                assert not whiteout_detected, f"화이트 아웃이 감지되었습니다: {href_value} 버튼"


    @pytest.mark.projectmenu
    @pytest.mark.order(3)
    def test_sitemap_menu(self):
        project_page = ProjectPage(self.page)

        # 프로젝트 데이터를 로드하고 메뉴 검증 수행
        projects = load_project_data()

        for project in projects:
            project_type = project["type"]
            project_id = project["id"]

            # 프로젝트 데이터 로드 후, 해당 프로젝트 화면으로 이동
            project_page.open(project_type, project_id)

            # 프로젝트 화면 화이트아웃 확인
            whiteout_detected = check_for_whiteout(self.page, f"{project_type} {project_id} 메인 화면", self.save_path)
            assert not whiteout_detected, f"화이트 아웃이 감지되었습니다: {project_type} {project_id} 메인 화면" 

            project_page.click_sitemap_btn()

            sitemap_elements = project_page.get_sitemap_menu_items()

            for element in sitemap_elements:
                href_value = project_page.click_sitemap_menu_item(element)
                project_page.check_modal_and_wait()

                whiteout_detected = check_for_whiteout(self.page, href_value, self.save_path)
                assert not whiteout_detected, f"화이트 아웃이 감지되었습니다: {href_value} 버튼"


if __name__ == "__main__":
    # 실행 시각에 따라 보고서 파일명 동적으로 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"src/reports/test_report_project_menu_{timestamp}.html"

    # pytest.main 호출로 pytest 실행 및 보고서 경로 설정
    pytest.main(["--html", report_path, "--self-contained-html"])