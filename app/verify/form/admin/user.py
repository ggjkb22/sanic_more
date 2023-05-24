# Author: Q
# Date:   2023-4-28
# Desc:   后台用户表单验证

import re
from typing import Set, Tuple, Optional, Set
from pydantic import Field, conint, validator
from app.verify.form.base import SanicFormBaseModel
from app.orm.models.system import SystemSetting

__all__ = ["UserAddForm", "UserDelForm", "UserInfoModifyForm", "UserInfoAdminModifyForm", "UserPswModifyForm",
           "UserPswAdminModifyForm", "validate_username_regexp", "validate_password_length"]


def validate_username_regexp(username: str):
    """用户名正则匹配"""
    re_res = re.match(r"^[a-zA-Z0-9_-]+$", username)
    if re_res is None:
        raise ValueError("只能包含字母数字下划线与横线")
    return username


async def validate_password_length(psw: str) -> Tuple[bool, Optional[str]]:
    """
    密码长度验证
    因无法兼容异步(使用asyncio.run、create_task等会报错或存在无法等待的问题)
    所以使用classmethod的方式手动调用
    """
    psw_length = len(psw)
    system_setting = await SystemSetting.auto_get_settings()
    min_psw_length = system_setting["min_psw_length"]
    max_psw_length = system_setting["max_psw_length"]
    if psw_length < min_psw_length or psw_length > max_psw_length:
        return False, f"密码长度应为{min_psw_length}-{max_psw_length}个字符"
    return True, None


def validate_password_strength(psw: str):
    """密码强度正则匹配"""
    re_res = re.match(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$_%^&*-]).+$", psw)
    if re_res is None:
        raise ValueError("应包含至少1个大写与小写字母、数字和特殊字符")
    return psw


class UserAddForm(SanicFormBaseModel):
    """用户添加表单"""
    username: str = Field(default=..., min_length=3, max_length=20, description="用户名")
    password: str = Field(default=..., description="密码")
    description: str = Field(default=None, max_length=300, description='备注')
    can_use: bool = Field(default=True, description='是否可用')
    roles: Set[conint(gt=0)] = Field(default=set(), description="所属角色")

    # 验证器
    _validate_username_regexp = validator("username", allow_reuse=True)(validate_username_regexp)
    _validate_password_strength = validator("password", allow_reuse=True)(validate_password_strength)


class UserDelForm(SanicFormBaseModel):
    """用户删除表单"""
    user_ids: Set[conint(gt=0)] = Field(default=..., description="所选的用户ID")


class UserInfoModifyForm(SanicFormBaseModel):
    """用户信息修改表单(用户自身使用)"""
    description: str = Field(default=None, max_length=300, description='备注')


class UserInfoAdminModifyForm(SanicFormBaseModel):
    """用户信息修改表单(管理员使用)"""
    user_id: int = Field(default=..., gt=0, description="所选的用户ID")
    description: str = Field(default=None, max_length=300, description='备注')
    can_use: bool = Field(default=True, description='是否可用')
    roles: Set[conint(gt=0)] = Field(default=set(), description="所属角色")


class UserPswModifyForm(SanicFormBaseModel):
    """用户密码修改表单(用户自身使用)"""
    old_password: str = Field(default=..., description="原密码")
    new_password: str = Field(default=..., description="新密码")

    # 验证器
    _validate_new_password_strength = validator("new_password", allow_reuse=True)(validate_password_strength)


class UserPswAdminModifyForm(SanicFormBaseModel):
    """用户密码修改表单(管理员使用)"""
    user_id: int = Field(default=..., gt=0, description="所选的用户ID")
    password: str = Field(default=..., description="新密码")

    # 验证器
    _validate_password_strength = validator("password", allow_reuse=True)(validate_password_strength)

