# Author: Q
# Date:   2023-4-21
# Desc:   登录状态检查

from sanic import Request, redirect, html, json
from sanic.exceptions import SanicException


class LoginCheckError(SanicException):
    """登录状态验证失败错误"""
    status_code = 403
    message = "当前用户未登录, 请先登录"

    @staticmethod
    async def error_handler(request: Request, exception: SanicException):
        """
        错误处理器
        直接重定向回登录界面
        """
        return redirect(request.url_for(request.app.config.CUSTOM_MVC_LOGIN_POINT))

    @staticmethod
    async def mvc_error_handler(request: Request, exception: SanicException):
        """适配MVC模式的处理"""
        rederect_url = request.url_for(request.app.config.CUSTOM_MVC_LOGIN_POINT)
        if request.method == "GET":
            response = html(f"<script>window.parent.location.href = '{rederect_url}'</script>")
        else:
            response = json({"status_code": 400, "message": "当前用户未登录, 请先登录", "url": rederect_url})
        return response


class LogoutCheckError(SanicException):
    """登出状态验证失败错误"""
    status_code = 403
    message = "用户已登录"

    @staticmethod
    async def error_handler(request: Request, exception: SanicException):
        """
        错误处理器
        直接重定向回后台管理界面首页
        """
        return redirect(request.url_for(request.app.config.CUSTOM_MVC_ADMIN_INDEX_POINT))

    @staticmethod
    async def mvc_error_handler(request: Request, exception: SanicException):
        """适配MVC模式的处理"""
        rederect_url = request.url_for(request.app.config.CUSTOM_MVC_ADMIN_INDEX_POINT)
        if request.method == "GET":
            response = html(f"<script>window.parent.location.href = '{rederect_url}'</script>")
        else:
            response = json({"status_code": 400, "message": "用户已登录", "url": rederect_url})
        return response


async def login_check(request: Request) -> int:
    """登录状态检查"""
    current_user = request.ctx.session.get(request.app.config.CUSTOM_SESSION_CURRENT_USER)
    if current_user is None:
        raise LoginCheckError
    return current_user


async def logout_check(request: Request):
    """登出状态检查"""
    current_user = request.ctx.session.get(request.app.config.CUSTOM_SESSION_CURRENT_USER)
    if current_user is not None:
        raise LogoutCheckError
