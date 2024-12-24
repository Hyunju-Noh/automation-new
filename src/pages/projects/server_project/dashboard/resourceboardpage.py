from pages.projects.basepage import BasePage

class ResourceBoardPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.widget_locator = "div.ResourceCards__CardDom-dzFtxX"  # 위젯 공통 선택자
        self.menu_wrap_selector = "div.Menustyles__MenuWrap-hRfo.hmTPnA"
        self.parent_elements_selector = "div.Menustyles__MenuItemWrapCommon-cHqrwY.Menustyles__Parent-XgDRT"

    def open_resourceboard(self, project_type, project_id):
        """프로젝트 URL로 이동."""
        project_url = f"https://service.whatap.io/v2/project/{project_type}/{project_id}"
        self.page.goto(project_url)
        self.wait_for_network_idle()

    def open_side_menus(self):
        """왼쪽 메뉴의 상위 메뉴 클릭."""
        menu_wrap = self.page.query_selector(self.menu_wrap_selector)
        parent_elements = menu_wrap.query_selector_all(self.parent_elements_selector)

        for element in parent_elements:
            element.click()
            self.wait_for_network_idle()

    def verify_widget(self, widget_name):
        """위젯의 표시 여부 확인."""
        widget_selector = f"{self.widget_locator}:has(span:text('{widget_name}'))"
        assert self.page.locator(widget_selector).is_visible(), f"위젯 {widget_name}가 표시되지 않음"
