from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def close_popups(self):
        """발생하는 팝업을 감지하고 닫음."""
        try:
            popup_locator = self.page.locator(".Toastify__toast")
            close_button_locator = self.page.locator(".Toastify__close-button")

            if popup_locator.is_visible():
                close_button_locator.click()
        except Exception as e:
            pass

    def wait_for_network_idle(self):
        """네트워크 안정 상태까지 대기."""
        self.page.wait_for_load_state('networkidle')
