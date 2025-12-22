from playwright.sync_api import sync_playwright
from pathlib import Path
from pages.login_page import LoginPage
from config.pages import URLS, ENV
from data.login_data import LOGIN_USERS, LOGIN_SUCCESS_URL, SAVE_LOGIN_STATE_PATH, SAVE_LOGIN_STATE_FILE


def save_login_state():
    """生成登录态
        单独执行该脚本命令：python -m scripts.save_login_state
    """
    with sync_playwright() as p:
        # 启动浏览器
        headless = bool(os.getenv("CI", False)) # CI特殊配置
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()

        # 打开一个新页面
        page = context.new_page()

        # 使用 Page Object 登录
        login_page = LoginPage(page)
        login_page.open_login(URLS[ENV]["login"])
        login_page.login(LOGIN_USERS["success_login"]["username"], LOGIN_USERS["success_login"]["password"])
        login_page.verify_login_success(LOGIN_SUCCESS_URL)
        # if not login_page.verify_login_success(LOGIN_SUCCESS_URL):
        #     raise RuntimeError("‼️登录态生成失败，没有跳转到登录成功页面")


        Path("storage").mkdir(exist_ok=True) # 确保storage目录一直存在
        context.storage_state(path="storage/login.json")  # 保存登录态到login.json

        # 再次校验文件
        login_path = Path("storage/login.json")
        if not login_path.exists() or login_path.stat().st_size == 0:
            raise RuntimeError("‼️ login.json生成失败，请检查浏览器或账号")
        print("✅ login.json 已生成 -> storage/login.json")

        context.close()
        browser.close()


