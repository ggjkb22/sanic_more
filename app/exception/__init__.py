# Author: Q
# Date:   2023-3-22
# Desc:   自定义异常类汇总

from typing import Union
from sanic import Sanic, Blueprint
from app.tools.csrf_protect import MtvCsrfValidateException
from app.tools.state_check.login_state import LoginCheckError, LogoutCheckError


def register_mtv_error_handler(app: Union[Sanic, Blueprint]):
    """注册MTV蓝图组全局错误验证处理器"""
    # CSRF 验证错误处理
    app.exception(MtvCsrfValidateException)(MtvCsrfValidateException.error_handler)
    # 登录登出验证错误处理
    app.exception(LoginCheckError)(LoginCheckError.error_handler)
    app.exception(LogoutCheckError)(LogoutCheckError.error_handler)

