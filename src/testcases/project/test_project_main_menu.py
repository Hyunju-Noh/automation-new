import logging
import pytest
import util_tools.login_utils as login_utils
import util_tools.check_whiteout as whiteout
import util_tools.load_project_data as project_data
import util_tools.logging as log_utils
import util_tools.failures_utils as failures_utils
from pages.account.loginpage import LoginPage
from pages.projects.projectpage import ProjectPage
from datetime import datetime 

@pytest.fixture(scope="session", autouse=True)
def setup_logging_once():
    """테스트 실행 전 전체 설정"""
    log_utils.setup_logging_projectpage()


@pytest.fixture(scope="session")
def login_session_fixture(playwright):
    """로그인 후 세션 상태를 저장한 파일의 경로를 반환"""
    return login_utils.login_session(playwright)


@pytest.fixture(scope="class", params=["chromium", "firefox", "webkit"])
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
    #browser.close()


@pytest.mark.usefixtures("setup_playwright_context")
class Test_ProjectMenus:

    def setup_method(self):
        """각 테스트 메서드 전마다 whiteout_detected를 초기화"""
        self.whiteout_detected = False  # 클래스 속성으로 정의하고 각 테스트마다 초기화

    # 태그값은 나중에 tc마다 고유 번호 설정한 다음, 번호로도 설정 가능
    @pytest.mark.projectmenu
    @pytest.mark.order(1)
    def test_verify_project_menu(self):
        failures = []  # 실패 항목을 저장할 리스트 초기화

        project_page = ProjectPage(self.page)

        # 프로젝트 데이터를 로드하고 메뉴 검증 수행
        projects = project_data.load_project_data()

        for project in projects:
            # 여기가 문제임 여기서 그냥 패스 때림
            project_type = project["project_type"]
            project_id = project["project_id"]

            # 프로젝트 데이터 로드 후, 해당 프로젝트 화면으로 이동
            project_page.open(project_type, project_id)

            # 프로젝트 화면 화이트아웃 확인
            try:
                whiteout_detected = whiteout.check_for_whiteout(self.page, f"{project_type} {project_id} 메인 화면", self.save_path, self.whiteout_texts)
                assert not whiteout_detected, f"화이트 아웃이 감지되었습니다: {project_type} {project_id} 메인 화면"
            except AssertionError as e:
                failures.append(str(e))  # 실패 내용을 기록하고 계속 진행 

            """
            사이드 메뉴 검증 부분
            """
            # 상위 메뉴 클릭하여 하위 메뉴 오픈
            project_page.open_sub_menus()

            # 하위 메뉴 태그 요소 가져오기
            menu_elements = project_page.get_menu_items()

            for element in menu_elements:
                href_value = project_page.click_menu_item(element)
                project_page.check_modal_and_wait()

                try:
                    whiteout_detected = whiteout.check_for_whiteout(self.page, href_value, self.save_path, self.whiteout_texts)
                    assert not whiteout_detected, f"화이트 아웃이 감지되었습니다: {href_value} 버튼"
                except AssertionError as e:
                    failures.append(str(e))  # 실패 내용을 기록하고 계속 진행

            """
            사이트맵 메뉴 검증 부분
            """
            project_page.click_sitemap_btn()

            sitemap_elements = project_page.get_sitemap_menu_items()

            for element in sitemap_elements:
                href_value = project_page.click_sitemap_menu_item(element)
                project_page.check_modal_and_wait()

                try:
                    whiteout_detected = whiteout.check_for_whiteout(self.page, href_value, self.save_path, self.whiteout_texts)
                    assert not whiteout_detected, f"화이트 아웃이 감지되었습니다: {href_value} 버튼"
                except AssertionError as e:
                    failures.append(str(e))  # 실패 내용을 기록하고 계속 진행
        
        # 실패 항목 보고
        failures_utils.report(failures)


# if __name__ == "__main__":
#     # 실행 시각에 따라 보고서 파일명 동적으로 생성
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     report_path = f"src/reports/test_report_project_menu_{timestamp}.html"

#     # pytest.main 호출로 pytest 실행 및 보고서 경로 설정
#     pytest.main(["--html", report_path, "--self-contained-html"])