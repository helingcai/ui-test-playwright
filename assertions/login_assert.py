class LoginAssert:

    @staticmethod
    def error_message(actual_msg: str, expect_msg: str):
        assert expect_msg in actual_msg, f"登录错误期望提示信息：{expect_msg}，登录错误实际提示信息：{actual_msg}"
