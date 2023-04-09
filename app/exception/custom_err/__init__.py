# Author: Q
# Date:   2023-4-8
# Desc:   自定义Pydantic验证异常类

from pydantic import PydanticValueError


class XssProtectError(PydanticValueError):
    """Xss验证失败异常类"""
    code: str = "custom.xss_protect"
    msg_template: str = "{_hello}, 内容存在Xss风险!"

