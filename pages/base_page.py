from playwright.sync_api import Page, expect
import re
from pathlib import Path


class BasePage:
    # SCREENSHOT_DIR = Path("screenshots")

    def __init__(self, page: Page):
        self.page = page

    # ========= 基础动作 =========
    def open(self, url: str):
        self.page.goto(url)

    def click(self, locator):
        locator.scroll_into_view_if_needed()
        locator.click()

    def fill(self, locator, value: str):
        locator.fill(value)

    def text(self, locator) -> str:
        return locator.inner_text()

    def get_texts(self, locator) -> list[str]:
        return [locator.nth(i).inner_text() for i in range(locator.count())]

    def get_attrs(self, locator, attr: str) -> list[str]:
        return [locator.nth(i).get_attribute(attr) for i in range(locator.count())]

    def get_count(self, locator) -> int:
        return locator.count()

    # ========= 等待 =========
    def wait_visible(self, locator):
        expect(locator).to_be_visible()  # 有一个严格模式规则：expect 只能作用在「唯一元素」上，若locator定位到多个元素，则取第一个元素判断

    def wait_url(self, pattern: str):
        expect(self.page).to_have_url(re.compile(pattern))

    # ========= 辅助 =========
    # def screenshot(self, filename: str):
    #     path = self.SCREENSHOT_DIR / self.__class__.__name__
    #     path.mkdir(parents=True, exist_ok=True)
    #     # self.SCREENSHOT_DIR.mkdir(exist_ok=True)
    #     self.page.screenshot(path=path / filename, full_page=True)
