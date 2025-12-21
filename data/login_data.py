"""login功能测试用例：测试数据、登录错误提示信息
测试正常登录流程
用户名错误
密码错误
用户名和密码都为空
密码为空
用户名不存在
"""

LOGIN_USERS = {
    "success_login": {"username": "standard_user", "password": "secret_sauce"},
    "wrong_username": {"username": "HAHAHA", "password": "secret_sauce",
                       "error_msg": "Username and password do not match any user in this service"},
    "wrong_password": {"username": "standard_user", "password": "12345",
                       "error_msg": "Username and password do not match any user in this service"},
    "empty_username_password": {"username": "", "password": "", "error_msg": "Username is required"},
    "empty_password": {"username": "standard_user", "password": "", "error_msg": "Password is required"},
    "inexistence_username": {"username": "test_user", "password": "secret_sauce",
                             "error_msg": "Username and password do not match any user in this service"}
}

LOGIN_SUCCESS_URL="/inventory.html"

SAVE_LOGIN_STATE_PATH="storage"
SAVE_LOGIN_STATE_FILE="/login.json"