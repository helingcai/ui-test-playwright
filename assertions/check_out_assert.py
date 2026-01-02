from decimal import Decimal
import re


class CheckOutAssert:

    @staticmethod
    def tips_message(actual_msg: str, expect_msg: str):
        """收件人为空，点击continue按钮"""
        assert expect_msg in actual_msg, f"预期提示信息：{expect_msg}，不存在于{actual_msg}"

    @staticmethod
    def not_empty(column: str):
        assert column.strip() != "", f"{column}为空！"

    @staticmethod
    def price_format(price: str):
        """只关心price格式，不关心具体 label 文案
           UI 改文案测试不炸"""
        assert re.match(r"^[A-Za-z ]+: \$\d+(\.\d{2})$", price), f"价格格式错误：{price}"

    @staticmethod
    def price_equal(expect: Decimal, actual: Decimal):
        assert expect == actual, f"预期价格：{expect}!={actual}"

    @staticmethod
    def order_price(item_price: Decimal, tax: Decimal, order_price: Decimal):
        expect = item_price + tax
        """商品总价、订单总价"""
        assert order_price == expect, f"实际总金额{order_price}!=预期总金额{expect}"

    @staticmethod
    def product_count(added_products: list, checkout_products: list):
        """加购商品=结算页商品？"""
        assert len(
            added_products) == len(
            checkout_products), f"已加购商品数量{len(added_products)} !=结算页面商品数量 {len(checkout_products)}"

    @staticmethod
    def product_detail_match(added_products: list, checkout_products: list):
        """加购商品与结算页商品一致性对比"""
        for added in added_products:
            assert added in checkout_products, f"inventory加购的商品{added}，在结算页面不存在"

        for cart in checkout_products:
            assert cart in added_products, f"结算页面的商品{cart}，不在inventory加购商品列表中"
