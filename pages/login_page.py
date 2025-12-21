from encodings.punycode import selective_find

from playwright.sync_api import expect, Page
from config.locators import LOGIN_LOCATORS
from pages.base_page import BasePage
from assertions.login_assert import LoginAssert


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.username_input = page.locator(LOGIN_LOCATORS["username_input"])  # 用户名输入框
        self.password_input = page.locator(LOGIN_LOCATORS["password_input"])  # 密码输入框
        self.login_button = page.locator(LOGIN_LOCATORS["login_button"])  # 登录按钮
        self.error_message = page.locator(LOGIN_LOCATORS["error_msg"])  # 登录校验错误提示信息
        self.shopping_cart_visible = page.locator(LOGIN_LOCATORS["shopping_cart_visible"])  # 登录成功后显示购物车icon

    # ================= 页面行为 =================
    def open_login(self, login_url: str):
        self.open(login_url)
        self.wait_visible(self.username_input)

    def login(self, username, password):
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)

    # ================= 数据获取 =================
    def get_login_failure_message(self):
        return self.text(self.error_message)

    # ========== 登录校验 ==========
    def verify_login_success(self, pattern: str):
        self.wait_url(pattern)

    def verify_login_fail(self, expect_msg: str):
        LoginAssert.error_message(self.get_login_failure_message(), expect_msg)
