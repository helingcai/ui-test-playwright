LOGIN_LOCATORS = {
    "username_input": "[data-test='username']",  # 用户名
    "password_input": "[data-test='password']",  # 用户密码
    "login_button": "[data-test='login-button']",  # 登录按钮
    "error_msg": "[data-test='error']",  # 登录错误提示信息
    "shopping_cart_visible": "[data-test='shopping-cart-link']"  # 登录成功页面购物车icon
}

INVENTORY_LOCATORS = {
    "item_product": "[data-test='inventory-item']",  # 商品列表
    "item_product_name": "[data-test='inventory-item-name']",  # 单商品名称
    "item_product_price": "[data-test='inventory-item-price']",  # 单商品价格
    "item_product_desc": "[data-test='inventory-item-desc']",  # 单商品描述
    "item_product_img": ".inventory_item_img img",  # 单商品图片
    "product_sort_type": "[data-test='product-sort-container']"  # 商品排序方式
}

CART_LOCATORS = {
    "add_product_button": "[data-test^='add-to-cart']",  # 商品添加按钮
    "remove_product_button": "[data-test^='remove']",  # 验证已添加商品按钮文字变为“Remove”
    "shopping_cart_visible_count": "[data-test='shopping-cart-badge']",  # 购物车显示商品数量
    "continue": "[data-test='continue-shopping']",  # 继续购物按钮
}

CHECKOUT_LOCATORS = {
    # 收货人信息
    "checkout_button": "[data-test='checkout']",  # 结算按钮
    "firstName_input": "[data-test='firstName']",  # firstName输入框
    "lastName_input": "[data-test='lastName']",  # lastName输入框
    "postalCode_input": "[data-test='postalCode']",  # postalCode输入框
    "container_error_msg": "[data-test='error']",  # 未填写收货人信息提交错误提示msg Error: First Name is required
    "step_one_cancel_button": "[data-test='cancel']",  # 取消按钮
    "continue_button": "[data-test='continue']",  # 继续按钮

    # --------checkout_step_two.html---------
    # 商品信息
    "item_list": "[data-test='inventory-item']",  # 订单确认页面商品列表
    "item_product_name": "[data-test='inventory-item-name']",  # 单商品名称
    "item_product_price": "[data-test='inventory-item-price']",  # 单商品价格
    "item_product_desc": "[data-test='inventory-item-desc']",  # 单商品描述
    # 订单价格
    "payment_information": "[data-test='payment-info-value']",  # 支付信息value
    "shipping_information": "[data-test='shipping-info-value']",  # 运费信息value
    "products_price": "[data-test='subtotal-label']",  # 商品价格
    "tax_price": "[data-test='tax-label']",  # 运费价格
    "order_price": "[data-test='total-label']",  # 订单价格
    # 操作步骤
    "step_two_cancel_button": "[data-test='cancel']",  # 取消按钮
    "finish_button": "[data-test='finish']",  # 完成按钮
    "finish_page_message":"[data-test='complete-header']" #完成页面提示信息
}
