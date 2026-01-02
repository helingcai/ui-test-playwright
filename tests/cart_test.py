import pytest

from config.pages import URLS, ENV
from data.cart_data import (ADD_PRODUCT_COUNT,
                            DELETE_PRODUCT_COUNT,
                            FIRST_PRODUCT_COUNT,
                            SECOND_PRODUCT_COUNT)
from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage


@pytest.fixture(scope="function")
def cart_page(page):
    """每个测试方法提供新的 CartPage 实例"""
    inventory_page = InventoryPage(page)
    inventory_page.open_inventory(URLS[ENV]["inventory"])  # inventory_page

    return CartPage(page)  # 只做 cart 的事

@pytest.mark.ui
@pytest.mark.need_login
class TestCart:

    def test_add_product(self, cart_page):
        """验证从inventory页面添加商品"""
        cart_page.add_product(ADD_PRODUCT_COUNT)
        cart_page.verify_add_product(ADD_PRODUCT_COUNT)

    def test_delete_product_from_inventory(self, cart_page):
        """验证从inventory页面删除商品"""
        cart_page.add_product(ADD_PRODUCT_COUNT)
        cart_page.remove_product(DELETE_PRODUCT_COUNT)
        cart_page.verify_delete(ADD_PRODUCT_COUNT, DELETE_PRODUCT_COUNT)

    def test_delete_product_from_cart(self, cart_page):
        """验证从cart页面删除商品"""
        cart_page.add_product(ADD_PRODUCT_COUNT)
        cart_page.go_to_cart("cart.html")
        cart_page.remove_product(DELETE_PRODUCT_COUNT)
        cart_page.verify_delete(ADD_PRODUCT_COUNT, DELETE_PRODUCT_COUNT)

    def test_continue_shopping(self, cart_page):
        """验证继续购物"""
        cart_page.add_product(FIRST_PRODUCT_COUNT)
        cart_page.go_to_cart("cart.html")
        cart_page.continue_shopping("/inventory.html")
        cart_page.add_product(SECOND_PRODUCT_COUNT)
        cart_page.go_to_cart("cart.html")
        cart_page.verify_continue_shopping(FIRST_PRODUCT_COUNT, SECOND_PRODUCT_COUNT)

    def test_verify_cart_page_products_info(self, cart_page):
        """验证列表页加购的商品信息=购物车页面显示的商品信息"""
        added = cart_page.add_product(ADD_PRODUCT_COUNT)
        cart_page.go_to_cart("cart.html")
        cart_page.verify_cart_product_info_match_inventory(added)
