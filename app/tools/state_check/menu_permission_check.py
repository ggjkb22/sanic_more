# Author: Q
# Date:   2023-5-17
# Desc:   菜单权限检查


from typing import Optional, Tuple, Dict
from app.orm.models.auth import User


async def menu_permission_check(user: User, menu_permission_code: str) -> bool:
    """
    菜单权限检查
    @Return: 权限不足则返回 False
    """
    # 验证参数类型
    if not isinstance(user, User) or not isinstance(menu_permission_code, str):
        return False
    # 获取用户权限
    menu_permissions = await user.auto_get_menu_permissions()
    return menu_permission_code in menu_permissions


async def dwz_menu_permission_check(user: User, menu_permission_code: str) -> Tuple[bool, Optional[Dict[str, str]]]:
    """适配DWZ前端框架的菜单权限检查"""
    allow = await menu_permission_check(user, menu_permission_code)
    if not allow:
        res_json = {
            "statusCode": "300",
            "message": "当前用户权限不足",
            "callbackType": "closeCurrent",
        }
        return False, res_json
    return True, None