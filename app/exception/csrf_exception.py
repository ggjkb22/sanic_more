# Author: Q
# Date:   2023-3-22
# Desc:   自定义CSRF异常类

from uuid import uuid4
from sanic.exceptions import SanicException
from sanic import Request
from app.tools.template import jinja2_async_render
from app.tools.captcha import aget_captcha_base64


class MtvCsrfValidateException(SanicException):
    """MTV模式下的CSRF验证失败异常类"""
    status_code = 400
    message = "CsrfToken 验证失败"

    @staticmethod
    async def error_handler(request: Request, exception: SanicException):
        """CSRF验证失败异常处理"""
        csrf_token = uuid4().hex
        request.ctx.session["csrf_token"] = csrf_token
        request.ctx.session["captcha_str"], bs64_str = await aget_captcha_base64()
        del request.ctx.session[request.app.config.CUSTOM_SESSION_CURRENT_USER]
        temp_ctx = {
            "request": request,
            "csrf_token": csrf_token,
            "captcha_bs64": bs64_str,
            "error": "Token验证失败, 请重新登录",
        }
        return await jinja2_async_render("admin/login.html", ctx=temp_ctx)
