# Author: Q
# Date:   2023-5-17
# Desc:   菜单权限检查


from typing import Optional, Tuple, Dict
from sanic import Request, json, html
from sanic.exceptions import SanicException
from app.orm.models.auth import User
from app.tools.template import jinja2_async_render
from app.tools.permissions_custom_type import LevelPermissionDict


class PermissionDeniedError(SanicException):
    """权限不足错误"""
    status_code = 403
    message = "当前用户权限不足！"

    @staticmethod
    async def error_handler(request: Request, exception: SanicException):
        """权限不足异常处理"""
        res_json = {
            "status_code": 403,
            "message": "当前用户权限不足！",
        }
        return json(res_json)

    @staticmethod
    async def mvc_error_handler(request: Request, exception: SanicException):
        """MVC模式(带有toastr插件)的权限不足异常处理"""
        if request.method == "GET":
            response = await jinja2_async_render("hplus/admin/layer_iframe_warning.html", {"warn_msg": "当前用户权限不足！"})
        else:
            response = json({"status_code": 403, "message": "当前用户权限不足！"})
        return response


async def menu_permission_check(user: User, menu_permission_code: str) -> bool:
    """
    菜单权限检查
    @Params:
        user: 用户的数据实例
        menu_permission_code: 菜单权限代码
    @Return: 权限不足则返回 False
    """
    # 验证参数类型
    if not isinstance(user, User) or not isinstance(menu_permission_code, str):
        return False
    # 获取用户权限
    menu_permissions = await user.auto_get_menu_permissions()
    return menu_permission_code in menu_permissions


async def hplus_menu_permission_check(user: User, menu_permission_code: str):
    """适配Hplus前端框架的菜单权限检查"""
    allow = await menu_permission_check(user, menu_permission_code)
    if not allow:
        raise PermissionDeniedError()
    
