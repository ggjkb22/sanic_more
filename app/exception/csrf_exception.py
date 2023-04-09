# Author: Q
# Date:   2023-3-22
# Desc:   自定义CSRF异常类

from sanic.exceptions import SanicException
from sanic import Request, json


class MtvCsrfValidateException(SanicException):
    """MTV模式下的CSRF验证失败异常类"""
    status_code = 403
    message = "CsrfToken 验证失败"

    @staticmethod
    async def error_handler(request: Request, exception: SanicException):
        """CSRF验证失败异常处理"""
        return json({"code": exception.status_code, "msg": exception.message}, status=exception.status_code)
