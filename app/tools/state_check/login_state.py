# Author: Q
# Date:   2023-4-21
# Desc:   登录状态检查

from typing import Tuple, Union
from sanic import Request, redirect, HTTPResponse
from app.exception.login_state_exception import LoginCheckError, LogoutCheckError


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

