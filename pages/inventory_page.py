import re
from time import sleep

from playwright.sync_api import Page, expect
from config.locators import INVENTORY_LOCATORS
from pages.base_page import BasePage
from assertions.inventory_assert import InventoryAssert
from decimal import Decimal


class InventoryPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # 商品列表
        self.item_product = page.locator(INVENTORY_LOCATORS["item_product"])

        # 商品明细
        self.item_product_name = page.locator(INVENTORY_LOCATORS["item_product_name"])
        self.item_product_price = page.locator(INVENTORY_LOCATORS["item_product_price"])
        self.item_product_desc = page.locator(INVENTORY_LOCATORS["item_product_desc"])
        self.item_product_img = page.locator(INVENTORY_LOCATORS["item_product_img"])

        # 排序下拉框
        self.product_sort_type = page.locator(INVENTORY_LOCATORS["product_sort_type"])

    # ================= 页面行为 =================
    def open_inventory(self, inventory_url: str):
        self.open(inventory_url)
        self.wait_visible(self.item_product.first)

    # 选择排序方式
    def sort_by(self, label: str):
        self.product_sort_type.select_option(label=label)

    # ================= 数据获取 =================
    def get_product_count(self) -> int:
        return self.get_count(self.item_product)

    def get_product_names(self) -> list[str]:
        return self.get_texts(self.item_product_name)

    def get_product_description(self) -> list[str]:
        return self.get_texts(self.item_product_desc)

    def get_product_imgs(self) -> list[str]:
        return self.get_attrs(self.item_product_img, "src")

    def get_product_prices(self) -> list[str]:
        return self.get_texts(self.item_product_price)

    def get_product_prices_as_number(self) -> list[Decimal]:
        return [Decimal(p.replace("$", "")) for p in self.get_product_prices()]

    def get_product_info_by_index(self, index: int):
        """保存单商品基本信息"""
        item = self.item_product.nth(index)
        return {
            "product_name": self.text(item.locator(self.item_product_name)),
            "product_price": self.text(item.locator(self.item_product_price)),
            "product_desc": self.text(item.locator(self.item_product_desc))
        }

    # ========== 基础校验 ==========
    def verify_base_info(self, expect_count: int):
        InventoryAssert.product_count(self.get_product_count(), expect_count)  # 商品数量一致
        InventoryAssert.column_not_empty(self.get_product_names())  # 商品名称非空
        InventoryAssert.column_not_empty(self.get_product_description())  # 商品描述非空
        InventoryAssert.column_not_empty(self.get_product_imgs())  # 商品图片非空
        InventoryAssert.product_price_format(self.get_product_prices())  # 商品价格非空
        InventoryAssert.product_price_is_decimal(self.get_product_prices_as_number())  # 商品价格是Decimal

    def verify_name_asc(self):
        InventoryAssert.sort_asc(self.get_product_names())

    def verify_name_desc(self):
        InventoryAssert.sort_desc(self.get_product_names())

    def verify_price_asc(self):
        InventoryAssert.sort_asc(self.get_product_prices_as_number())

    def verify_price_desc(self):
        InventoryAssert.sort_desc(self.get_product_prices_as_number())
