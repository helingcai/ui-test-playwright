import pytest

from config.pages import URLS, ENV
from data.checkout_data import (CONTAINER_EMPTY_ERROR_MSG, ADD_PRODUCT_NUM, CONTAINER_INFO, FINISH_PAGE_MESSAGE)
from pages.check_out_page import CheckOutPage


@pytest.fixture(scope="function")
def check_out_page(page):
    return CheckOutPage(page)

@pytest.mark.ui
@pytest.mark.need_login
class TestCheckOut:

    def test_step_one_container_empty(self, check_out_page):
        """验证checkout_step_one.html页面收货人空"""
        check_out_page.prepare(URLS[ENV]["inventory"], ADD_PRODUCT_NUM, "/cart.html", "/checkout-step-one.html")
        check_out_page.fill_container("", "", "")
        check_out_page.stet_one_continue("/checkout-step-one.html")
        check_out_page.verify_container_empty(CONTAINER_EMPTY_ERROR_MSG)

    def test_step_one_cancel(self, check_out_page):
        """验证checkout_step_one.html页面取消按钮"""
        check_out_page.prepare(URLS[ENV]["inventory"], ADD_PRODUCT_NUM, "/cart.html", "/checkout-step-one.html")
        check_out_page.fill_container(CONTAINER_INFO["first_name"], CONTAINER_INFO["last_name"],
                                      CONTAINER_INFO["postal"])
        check_out_page.stet_one_cancel("/cart.html")

    def test_cancel_submit_order(self, check_out_page):
        """验证取消订单"""
        check_out_page.prepare(URLS[ENV]["inventory"], ADD_PRODUCT_NUM, "/cart.html", "/checkout-step-one.html")
        check_out_page.fill_container(CONTAINER_INFO["first_name"], CONTAINER_INFO["last_name"],
                                      CONTAINER_INFO["postal"])
        check_out_page.stet_one_continue("/checkout-step-two.html")
        check_out_page.step_two_cancel("/inventory.html")

    def test_finish_submit_order(self, check_out_page):
        """验证提交订单"""
        check_out_page.prepare(URLS[ENV]["inventory"], ADD_PRODUCT_NUM, "/cart.html", "/checkout-step-one.html")
        check_out_page.fill_container(CONTAINER_INFO["first_name"], CONTAINER_INFO["last_name"],
                                      CONTAINER_INFO["postal"])
        check_out_page.stet_one_continue("/checkout-step-two.html")
        check_out_page.verify_order_products_match_added()
        check_out_page.verify_order_base_info()
        check_out_page.step_two_submit("/checkout-complete.html")
        check_out_page.verify_submit_order(FINISH_PAGE_MESSAGE)
