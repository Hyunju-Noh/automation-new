from pages.projects.basepage import BasePage
from pages.projects.server_project.dashboard.resourceboard_widgets import all_widgets
import logging

class ResourceBoardPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.widget_locator = "div.ResourceCards__CardDom-dzFtxX"  # 위젯 공통 선택자
        self.menu_wrap_selector = "div.Menustyles__MenuWrap-hRfo.hmTPnA"
        self.parent_elements_selector = "div.Menustyles__MenuItemWrapCommon-cHqrwY.Menustyles__Parent-XgDRT"
        self.widgets = all_widgets


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


    def verify_widget_ui(self, widget_name):
        """특정 위젯이 화면에 표시되는지 확인"""
        widget_selector = f"{self.widget_locator}:has(span:text('{widget_name}'))"
        assert self.page.locator(widget_selector).is_visible(), f"위젯 {widget_name}이 표시되지 않음"
        logging.info(f"위젯 {widget_name} UI 검증 성공")


    def get_widgets(self):
        """위젯 리스트 반환"""
        return self.widgets
