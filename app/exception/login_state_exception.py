# Author: Q
# Date:   2023-3-22
# Desc:   自定义登录状态异常类


from sanic import Request, redirect


class LoginCheckError(Exception):
    """登录状态验证失败错误"""

    @staticmethod
    async def error_handler(request: Request, exception: Exception):
        """
        错误处理器
        直接重定向回登录界面
        """
        return redirect(request.url_for(request.app.config.CUSTOM_MTV_LOGIN_POINT))


class LogoutCheckError(Exception):
    """登出状态验证失败错误"""

    @staticmethod
    async def error_handler(request: Request, exception: Exception):
        """
        错误处理器
        直接重定向回后台管理界面首页
        """
        return redirect(request.url_for(request.app.config.CUSTOM_MTV_ADMIN_INDEX_POINT))

