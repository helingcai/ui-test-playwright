import re
from decimal import Decimal


class InventoryAssert:

    @staticmethod
    def product_count(actual_count: int, expect_count: int):
        assert actual_count == expect_count, f"期望商品数量：{expect_count}，实际商品数量：{actual_count}"

    @staticmethod
    def column_not_empty(names: list):
        assert names, "商品信息list为空"
        for name in names:
            assert name.strip(), "存在商品信息为空"

    @staticmethod
    def product_price_format(prices: list[str]):
        assert prices, "商品价格list为空"
        for price in prices:
            assert re.match(r"^\$\d+(\.\d{2})$", price), f"商品价格格式错误：{price}"

    @staticmethod
    def product_price_is_decimal(prices: list[Decimal]):
        for price in prices:
            assert isinstance(price, Decimal), f"价格不是 Decimal: {price}"
            assert price > 0, f"价格必须大于 0: {price}"

    @staticmethod
    def sort_asc(values: list):
        assert values == sorted(values), f"字段名称-{[values[0]]}未正序排列：{values}"

    @staticmethod
    def sort_desc(values: list):
        assert values == sorted(values, reverse=True), f"字段名称-{[values[0]]}未倒序排列：{values}"
