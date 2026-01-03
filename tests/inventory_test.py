# import pytest
#
# from config.pages import URLS, ENV
# from data.inventory_data import PRODUCT_COUNT, PRODUCT_SORT
# from pages.inventory_page import InventoryPage
#
#
# @pytest.fixture(scope="function")
# def inventory_page(page):
#     return InventoryPage(page)
#
#
# @pytest.mark.ui
# @pytest.mark.need_login
# class TestInventory:
#
#     def test_inventory_base_info(self, inventory_page):
#         """验证商品列表基础信息"""
#         inventory_page.open_inventory(URLS[ENV]["inventory"])
#         inventory_page.verify_base_info(PRODUCT_COUNT)  # 验证商品列表商品数量
#
#     def test_sort_by_name_asc(self, inventory_page):
#         """验证按商品名称正序排列"""
#         inventory_page.open_inventory(URLS[ENV]["inventory"])
#         inventory_page.sort_by(PRODUCT_SORT["name_asc"])
#         inventory_page.verify_name_asc()
#
#     def test_sort_by_name_desc(self, inventory_page):
#         """验证按商品名称倒叙排列"""
#         inventory_page.open_inventory(URLS[ENV]["inventory"])
#         inventory_page.sort_by(PRODUCT_SORT["name_desc"])
#         inventory_page.verify_name_desc()
#
#     def test_sort_by_price_asc(self, inventory_page):
#         """验证按商品价格正序排列"""
#         inventory_page.open_inventory(URLS[ENV]["inventory"])
#         inventory_page.sort_by(PRODUCT_SORT["price_asc"])
#         inventory_page.verify_price_asc()
#
#     def test_sort_by_price_desc(self, inventory_page):
#         """验证按商品价格倒叙排列"""
#         inventory_page.open_inventory(URLS[ENV]["inventory"])
#         inventory_page.sort_by(PRODUCT_SORT["price_desc"])
#         inventory_page.verify_price_desc()
