import logging
from playwright.sync_api import Page

class ProjectPage:
    def __init__(self, page: Page):
        self.page = page
        self.menu_wrap_selector = 'div.Menustyles__MenuWrap-hRfo.hmTPnA'
        self.parent_elements_selector = 'div.Menustyles__MenuItemWrapCommon-cHqrwY.Menustyles__Parent-XgDRT'
        self.menu_item_selector = 'a[href^="/v2/project/"]'
        self.button_selector = 'div'

    def open_project(self, project_type, project_id):
        """프로젝트 URL로 이동하는 메서드"""
        project_url = f"https://service.whatap.io/v2/project/{project_type}/{project_id}"
        self.page.goto(project_url)
        self.page.wait_for_load_state('networkidle')

    def get_menu_wrap(self):
        """menu_wrap 요소 가져오기"""
        return self.page.query_selector(self.menu_wrap_selector)

    def get_parent_elements(self):
        """menu_wrap 내의 모든 상위 메뉴 요소를 가져오는 메서드"""
        menu_wrap = self.get_menu_wrap()
        if menu_wrap:
            return menu_wrap.query_selector_all(self.parent_elements_selector)
        else:
            logging.warning("menu_wrap 요소를 찾을 수 없습니다.")
            return []

    def open_sub_menus(self):
        """상위 메뉴 클릭하여 하위 메뉴 열기"""
        parent_elements = self.get_parent_elements()
        logging.info("상위 메뉴 클릭하여 하위 메뉴 오픈 중") 

        for element in parent_elements:
            try:
                element.click()  # 요소 클릭
                self.page.wait_for_load_state('networkidle', timeout=20000)  # 페이지 로드 대기
            except Exception as e:
                logging.error(f"클릭 중 오류 발생: {str(e)}")

        logging.info("하위 메뉴 오픈 후 페이지 로드 완료")

    def get_menu_items(self):
        """menu_wrap 내의 하위 메뉴 태그 요소를 가져옴"""
        menu_wrap = self.get_menu_wrap()
        elements = menu_wrap.query_selector_all(self.menu_item_selector)

        if len(elements) == 0:
            logging.warning("해당하는 링크를 찾을 수 없습니다.")
        return elements

    def click_menu_item(self, element):
        """단일 하위 메뉴 항목을 클릭하고 href 값을 반환"""
        href_value = element.get_attribute('href')
        element.click()
        logging.info(f"버튼 클릭 완료 - {href_value}")
        return href_value

    def check_modal_and_wait(self):
        """모달 감지 및 닫기 후 페이지 로드 대기"""
        self.page.wait_for_timeout(1000)  # 잠시 대기 후 모달 감지
        self.check_and_close_modal()  # 모달 감지 및 닫기
        self.wait_for_page_load()  # 페이지 로드 대기

    def check_modal_and_wait(self):
        """모달 감지 및 닫기 후 페이지 로드 대기"""
        self.page.wait_for_timeout(1000)  # 잠시 대기 후 모달 감지
        
        # 모달 감지 및 닫기
        close_selectors = [
            ".Styles__Wrapper-bZXaBP.dZPSDU",  # 첫 번째 모달 유형 닫기 버튼
            ".__floater__open .Styles__Wrapper-bZXaBP.cdnUPE",  # 두 번째 모달 유형 닫기 버튼
        ]
        
        for selector in close_selectors:
            close_button = self.page.locator(selector)
            if close_button.count() > 0:
                logging.info(f"모달 팝업 감지 - 닫기 버튼: {selector}")
                close_button.click()
                logging.info("모달 팝업 닫기 완료")
                break  # 모달이 닫혔으면 루프 탈출

        # 페이지 로드 대기
        self.wait_for_page_load()

