# Author: Q
# Date:   2023-4-19
# Desc:   MTV模式下的CSRF防御

from uuid import uuid4
from sanic.request import Request
from sanic.exceptions import SanicException
from sanic.response import HTTPResponse, html, json
from app.tools.template import jinja2_async_render
from app.tools.captcha import aget_captcha_base64


def generate_csrf_token(request: Request, response: HTTPResponse) -> HTTPResponse:
    """
    生成csrf_token
    服务端存储在session中
    客户端存储在httponly cookie中
    """

    def set_csrf_token(csrf_token):
        # 客户端存储在httponly的cookies中
        response.cookies["csrf_token"] = csrf_token
        response.cookies["csrf_token"]["httponly"] = True
        response.cookies["csrf_token"]["max-age"] = 31536000

    # 如何session中已经存在csrf_token,则直接复用该token
    req_session_csrf_token = request.ctx.session.get("csrf_token")
    if req_session_csrf_token:
        req_csrf_token = request.cookies.get("csrf_token")
        if req_csrf_token and req_csrf_token == req_session_csrf_token:
            return response
        set_csrf_token(req_session_csrf_token)
        return response
    # 否则重新生成并设置token
    csrf_token = uuid4().hex
    # 服务器端存储在session中
    request.ctx.session["csrf_token"] = csrf_token
    set_csrf_token(csrf_token)
    return response


class CsrfValidateException(SanicException):
    """MTV模式下的CSRF验证失败异常类"""
    status_code = 400
    message = "CsrfToken 验证失败"

    @staticmethod
    async def error_handler(request: Request, exception: SanicException):
        """CSRF验证失败异常处理"""
        try:
            del request.ctx.session[request.app.config.CUSTOM_SESSION_CURRENT_USER]
        except KeyError as e:
            pass
        request.ctx.session["captcha_str"], bs64_str = await aget_captcha_base64()
        temp_ctx = {
            "request": request,
            "captcha_bs64": bs64_str,
            "error": "Token验证失败, 请重新登录",
        }
        response = await jinja2_async_render("dwz/admin/login.html", ctx=temp_ctx)
        # 生成并向session中注入csrf_token
        generate_csrf_token(request, response)
        return response
    
    @staticmethod
    async def mvc_error_handler(request: Request, exception: SanicException):
        """适配MVC模式的CSRF验证失败异常处理"""
        try:
            del request.ctx.session[request.app.config.CUSTOM_SESSION_CURRENT_USER]
        except KeyError as e:
            pass
        rederect_url = request.url_for(request.app.config.CUSTOM_MVC_LOGIN_POINT)
        if request == "GET":
            response = html(f"<script>window.parent.location.href = '{rederect_url}'</script>")
        else:
            response = json({"status_code": 400, "message": "CsrfToken 验证失败", "url": rederect_url})
        # 生成并向session中注入csrf_token
        generate_csrf_token(request, response)
        return response


def validate_csrf_token(request: Request):
    """验证csrf_token
    将客户端cookie中的csrf_token与服务器端session中的csrf_token进行比较
    """
    req_csrf_token = request.cookies.get("csrf_token")
    req_session_csrf_token = request.ctx.session.get("csrf_token")
    if req_csrf_token is None or req_session_csrf_token is None or req_csrf_token != req_session_csrf_token:
        raise CsrfValidateException()
