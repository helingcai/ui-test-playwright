import re
from decimal import Decimal

from playwright.sync_api import Page, expect
from config.locators import CART_LOCATORS, INVENTORY_LOCATORS, LOGIN_LOCATORS
from pages.inventory_page import BasePage
from assertions.cart_assert import CartAssert
from utils.common_utils import parse_money


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # inventory 页
        self.products_list = page.locator(INVENTORY_LOCATORS["item_product"])  # 商品列表
        self.add_product_button = page.locator(CART_LOCATORS["add_product_button"])  # add商品按钮
        self.remove_product_button = page.locator(CART_LOCATORS["remove_product_button"])  # remove商品按钮
        self.shopping_cart_visible_count = page.locator(CART_LOCATORS["shopping_cart_visible_count"])  # 购物车显示商品数
        self.shopping_cart_button = page.locator(LOGIN_LOCATORS["shopping_cart_visible"])  # 购物车icon

        self.item_product_name = page.locator(INVENTORY_LOCATORS["item_product_name"])  # 单商品名称
        self.item_product_price = page.locator(INVENTORY_LOCATORS["item_product_price"])  # 单商品价格
        self.item_product_desc = page.locator(INVENTORY_LOCATORS["item_product_desc"])  # 商品描述

        # cart 页
        self.continue_shopping_button = page.locator(CART_LOCATORS["continue"])  # continue-shopping按钮

    # ================= 页面行为 =================
    def add_product(self, add_product_num: int) -> list:
        added_products = []  # 存储加购商品信息
        #     只添加当前仍可加购的商品（Add to cart 状态）
        assert self.get_count(self.add_product_button) >= add_product_num, f"可加购商品不足"
        for _ in range(add_product_num):
            add = self.add_product_button.first
            # ⚠️ 关键：从按钮反向定位商品容器
            product_item = add.locator("xpath=ancestor::div[@data-test='inventory-item']")
            added_products.append(
                {"product_name": self.text(product_item.locator(self.item_product_name)),
                 "product_price": parse_money(self.text(product_item.locator(self.item_product_price))),
                 "product_desc": self.text(product_item.locator(self.item_product_desc))})
            self.click(add)
        return added_products

    def remove_product(self, count: int):
        for i in range(count):
            self.click(self.remove_product_button.nth(i))

    def go_to_cart(self, pattern: str):
        self.click(self.shopping_cart_button)
        self.wait_url(pattern)

    def continue_shopping(self, pattern: str):
        self.click(self.continue_shopping_button)
        self.wait_url(pattern)

    # ================= 数据获取 =================
    def get_cart_badge_count(self) -> int:
        # 获取购物车显示的商品数字
        if self.shopping_cart_visible_count.count() == 0:
            return 0
        return int(self.text(self.shopping_cart_visible_count))

    def get_remove_count(self):
        return self.get_count(self.remove_product_button)

    def get_cart_products_info(self) -> list:
        """ 保存购物车页面商品信息list"""
        products = []
        for i in range(self.products_list.count()):
            product = self.products_list.nth(i)
            products.append({"product_name": self.text(product.locator(self.item_product_name)),
                             "product_price": parse_money(
                                 self.text(product.locator(self.item_product_price))),
                             "product_desc": self.text(product.locator(self.item_product_desc))})
        return products

    # ================= 基础验证 =================
    def verify_add_product(self, add_count: int):
        CartAssert.cart_badge_count(self.get_cart_badge_count(), add_count)
        CartAssert.remove_count(self.get_remove_count(), add_count)

    def verify_delete(self, add_count: int, delete_count: int):
        CartAssert.cart_badge_count(self.get_cart_badge_count(), add_count - delete_count)
        CartAssert.remove_count(self.get_remove_count(), add_count - delete_count)

    def verify_continue_shopping(self, first_add_count: int, second_add_count: int):
        CartAssert.cart_badge_count(self.get_cart_badge_count(), first_add_count + second_add_count)
        CartAssert.remove_count(self.get_remove_count(), first_add_count + second_add_count)

    def verify_cart_product_info_match_inventory(self, added_products: list):
        CartAssert.added_product_count(added_products, self.get_cart_products_info())
        CartAssert.product_detail_info(added_products, self.get_cart_products_info())
