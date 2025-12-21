import re
from decimal import Decimal
from time import sleep

from playwright.sync_api import Page, expect

from config.locators import CHECKOUT_LOCATORS

from utils.common_utils import parse_money
from pages.base_page import BasePage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from assertions.check_out_assert import CheckOutAssert


class CheckOutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        #  step one 收货人信息
        self.checkout_button = page.locator(CHECKOUT_LOCATORS["checkout_button"])  # 结算按钮
        self.firstName_input = page.locator(CHECKOUT_LOCATORS["firstName_input"])  # firstName输入框
        self.lastName_input = page.locator(CHECKOUT_LOCATORS["lastName_input"])  # lastName输入框
        self.postalCode_input = page.locator(CHECKOUT_LOCATORS["postalCode_input"])  # postalCode输入框
        self.container_empty_error_msg = page.locator(CHECKOUT_LOCATORS["container_error_msg"])  # 收货人未填写点击下一步错误提示文案
        self.step_one_cancel_button = page.locator(CHECKOUT_LOCATORS["step_one_cancel_button"])  # 取消按钮
        self.continue_button = page.locator(CHECKOUT_LOCATORS["continue_button"])  # 继续按钮

        #  step two 商品信息
        self.item_product = page.locator(CHECKOUT_LOCATORS["item_list"])
        self.item_product_name = page.locator(CHECKOUT_LOCATORS["item_product_name"])
        self.item_product_price = page.locator(CHECKOUT_LOCATORS["item_product_price"])
        self.item_product_desc = page.locator(CHECKOUT_LOCATORS["item_product_desc"])
        # 订单价格
        self.payment_information = page.locator(CHECKOUT_LOCATORS["payment_information"])  # 支付信息value
        self.shipping_information = page.locator(CHECKOUT_LOCATORS["shipping_information"])  # 运费信息value
        self.item_total = page.locator(CHECKOUT_LOCATORS["products_price"])  # 商品总价格
        self.tax = page.locator(CHECKOUT_LOCATORS["tax_price"])  # 运费
        self.total = page.locator(CHECKOUT_LOCATORS["order_price"])  # 订单价格
        # 操作步骤
        self.step_two_cancel_button = page.locator(CHECKOUT_LOCATORS["step_two_cancel_button"])  # 取消按钮
        self.finish_button = page.locator(CHECKOUT_LOCATORS["finish_button"])  # 完成按钮
        self.finish_message = page.locator(CHECKOUT_LOCATORS["finish_page_message"])

        self.added_products: list[dict] = []  # 存储加购的商品

    # ========== 前提条件准备 ==========
    def prepare(self, inventory_url: str, add_count: int, cart_url: str, step_one_url: str):
        """
               checkout 模块前置条件：
               - inventory 加购
               - 进入 cart
               - 进入 checkout step one
               """
        InventoryPage(self.page).open_inventory(inventory_url)
        cart_page = CartPage(self.page)
        self.added_products = cart_page.add_product(add_count)
        cart_page.go_to_cart(cart_url)
        self.click_checkout(step_one_url)

    # ========== 页面行为 ==========
    def click_checkout(self, pattern: str):
        """点击购物车页面的Checkout按钮"""
        self.click(self.checkout_button)
        self.wait_url(pattern)

    def fill_container(self, first_name: str, last_name: str, postal_code: str):
        self.fill(self.firstName_input, first_name)
        self.fill(self.lastName_input, last_name)
        self.fill(self.postalCode_input, postal_code)

    def stet_one_continue(self, pattern: str):
        """点击Checkout-step-one页面continue按钮"""
        self.click(self.continue_button)
        self.wait_url(pattern)

    def stet_one_cancel(self, pattern: str):
        """点击Checkout-step-one页面cancel按钮"""
        self.click(self.step_one_cancel_button)
        self.wait_url(pattern)

    def step_two_cancel(self, pattern: str):
        self.click(self.step_two_cancel_button)
        self.wait_url(pattern)

    def step_two_submit(self, pattern: str):
        self.click(self.finish_button)
        self.wait_url(pattern)

    # ================= 数据获取 =================
    def get_step_two_products_info(self) -> list:
        expect(self.item_product).not_to_have_count(0)
        products = []
        for i in range(self.item_product.count()):
            item_product = self.item_product.nth(i)
            products.append({"product_name": self.text(item_product.locator(self.item_product_name)),
                             "product_price": parse_money(
                                 self.text(item_product.locator(self.item_product_price))),
                             "product_desc": self.text(item_product.locator(self.item_product_desc))})
        return products

    def get_payment_information(self) -> str:
        return self.text(self.payment_information)

    def get_shipping_information(self) -> str:
        return self.text(self.shipping_information)

    def get_item_total_price(self) -> str:
        return self.text(self.item_total)

    def get_tax_price(self) -> str:
        return self.text(self.tax)

    def get_total_price(self) -> str:
        return self.text(self.total)

    # ================= 手动计算 =================
    def sum_products_price(self) -> Decimal:
        # 显式指定 sum 初始值="0"
        return sum((p["product_price"] for p in self.get_step_two_products_info()), Decimal("0"))

    # ========== checkout-step-one 基本验证 ==========
    def verify_container_empty(self, expect_error_msg: str):
        CheckOutAssert.tips_message(self.text(self.container_empty_error_msg), expect_error_msg)
        # self.screenshot(screenshot_path)

    # ========== checkout-step-two 基本验证 ==========
    def verify_order_products_match_added(self):
        order_products = self.get_step_two_products_info()

        CheckOutAssert.product_count(self.added_products, order_products)
        CheckOutAssert.product_detail_match(self.added_products, order_products)

    def verify_order_base_info(self):
        CheckOutAssert.not_empty(self.get_payment_information())
        CheckOutAssert.not_empty(self.get_shipping_information())
        # 验证item total
        CheckOutAssert.price_format(self.get_item_total_price())
        # 验证tax
        CheckOutAssert.price_format(self.get_tax_price())
        # 验证total
        CheckOutAssert.price_format(self.get_total_price())

        # 验证商品总价格
        CheckOutAssert.price_equal(self.sum_products_price(), parse_money(self.get_item_total_price()))
        # 验证订单总价格
        CheckOutAssert.order_price(parse_money(self.get_item_total_price()), parse_money(self.get_tax_price()),
                                   parse_money(self.get_total_price()))

    # ========== 提交订单页面 ==========
    def verify_submit_order(self, finish_message: str):
        CheckOutAssert.tips_message(self.text(self.finish_message), finish_message)
        # self.screenshot(screenshot_path)
