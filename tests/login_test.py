import pytest

from pages.login_page import LoginPage
from config.pages import URLS, ENV
from data.login_data import LOGIN_USERS, LOGIN_SUCCESS_URL


@pytest.fixture(scope="function")
def login_page(page):
    return LoginPage(page)

@pytest.mark.ui
class TestLogin:

    def test_login_success(self, login_page):
        login_page.open_login(URLS[ENV]["login"])
        login_page.login(LOGIN_USERS["success_login"]["username"], LOGIN_USERS["success_login"]["password"])
        login_page.verify_login_success(LOGIN_SUCCESS_URL)
        print("测试完成！")

    # 测试登录失败（场景参数化）
    @pytest.mark.parametrize(
        "case_key", [
            "wrong_username",
            "wrong_password",
            "empty_username_password",
            "empty_password",
            "inexistence_username"
        ]
    )
    def test_login_fail(self, login_page, case_key):
        login_page.open_login(URLS[ENV]["login"])
        data = LOGIN_USERS[case_key]
        login_page.login(data["username"], data["password"])
        login_page.verify_login_fail(data["error_msg"])
        print("测试完成！")
