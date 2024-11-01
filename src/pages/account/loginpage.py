from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.login_button = page.locator("#btn_login")
        self.input_email = page.locator("#d_email")
        self.input_password = page.locator("#id_password")


    def open_main_page(self):
        """
        와탭 메인 화면으로 이동하는 메서드
        사실 로그인 화면에서 사용되지는 않음
        """
        self.page.goto("https://www.whatap.io/")
        self.page.wait_for_load_state('networkidle')

    def open_login_page(self):
        """
        와탭 로그인 화면으로 이동하는 메서드
        """
        self.page.goto("https://service.whatap.io/account/login/")
        self.page.wait_for_load_state('networkidle')

    def fill_email(self, email_text):
        self.input_email.fill(email_text)  

    def fill_password(self, password_text):
        self.input_password.fill(password_text)  

    def click_login_btn(self):
        self.login_button.click()  

    def login_success(self, user):
        """
        [성공 케이스]
        이메일과 비밀번호를 입력하고 로그인 버튼을 클릭하는 메서드.
        user: {'username': 이메일, 'password': 비밀번호} 형식의 딕셔너리
        """
        self.fill_email(user["username"])
        self.fill_password(user["password"])
        self.page.wait_for_load_state('networkidle')
        self.click_login_btn()

    def login_fail(self, user):
        """
        [실패 케이스]
        이메일과 비밀번호를 입력하고 로그인 버튼을 클릭하는 메서드.
        user: {'username': 이메일, 'password': 비밀번호} 형식의 딕셔너리
        """
        self.fill_email(user["username"])
        self.fill_password(user["password"])
        self.page.wait_for_load_state('networkidle')
        self.click_login_btn()
