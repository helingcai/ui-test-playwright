class CartAssert:

    @staticmethod
    def cart_badge_count(actual: int, expect: int):
        """购物车图标显示数字"""
        assert actual == expect, f"购物车角标显示的加购商品数量错误：{actual}!={expect}"

    @staticmethod
    def remove_count(actual: int, expect: int):
        """购物车图标显示数字"""
        assert actual == expect, f"inventory页面可Remove的商品不符合预期：{actual}!={expect}"

    @staticmethod
    def added_product_count(added_products: list, cart_products: list):
        """加购商品=购物车页商品？"""
        assert len(
            added_products) == len(
            cart_products), f"已加购商品数量{len(added_products)} !=购物车页面商品数量 {len(cart_products)}"

    @staticmethod
    def product_detail_info(added_products: list, cart_products: list):
        """加购商品与购物车页商品一致性对比"""
        for added in added_products:
            assert added in cart_products, f"inventory加购的商品{added}，在购物车页面不存在"

        for cart in cart_products:
            assert cart in added_products, f"购物车页面的商品{cart}，不在inventory加购商品列表中"
