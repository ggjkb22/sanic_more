# Author: Q
# Date:   2023-4-28
# Desc:   Admin表单验证

import re
from typing import Set
from pydantic import Field, conint, validator
from app.conf import get_config
from .base import SanicFormBaseModel


__all__ = ["UserAddForm", "UserDelForm", "UserInfoModifyForm", "UserPswModifyForm", "SystemSeetingForm"]


custom_config = get_config()


def validate_username(username: str):
    """用户名正则匹配"""
    re_res = re.match(r"^[a-zA-Z0-9_-]+$", username)
    if re_res is None:
        raise ValueError("只能包含字母数字下划线与横线")
    return username


def validate_password(psw: str):
    """密码强度正则匹配"""
    re_res = re.match(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$_%^&*-]).+$", psw)
    if re_res is None:
        raise ValueError("应包含至少1个大写与小写字母、数字和特殊字符")
    return psw


class UserAddForm(SanicFormBaseModel):
    """用户添加表单"""
    username: str = Field(default=..., min_length=3, max_length=20, description="用户名")
    password: str = Field(default=..., min_length=custom_config.CUSTOM_MIN_PSW_LENGTH, max_length=custom_config.CUSTOM_MAX_PSW_LENGTH, description="密码")
    description: str = Field(default=None, max_length=300, description='备注')
    can_use: bool = Field(default=True, description='是否可用')

    # 验证器
    _validate_username = validator("username", allow_reuse=True)(validate_username)
    _validate_password = validator("password", allow_reuse=True)(validate_password)


class UserDelForm(SanicFormBaseModel):
    """用户删除表单"""
    user_ids: Set[conint(gt=0)] = Field(default=..., description="所选的用户ID")


class UserInfoModifyForm(SanicFormBaseModel):
    """用户信息修改表单"""
    user_id: int = Field(default=..., gt=0, description="所选的用户ID")
    description: str = Field(default=None, max_length=300, description='备注')
    can_use: bool = Field(default=True, description='是否可用')


class UserPswModifyForm(SanicFormBaseModel):
    """用户密码修改表单(用户自身使用)"""
    user_id: int = Field(default=..., gt=0, description="所选的用户ID")
    old_password: str = Field(default=..., description="原密码")
    new_password: str = Field(default=..., min_length=custom_config.CUSTOM_MIN_PSW_LENGTH, max_length=custom_config.CUSTOM_MAX_PSW_LENGTH, description="新密码")

    # 验证器
    _validate_password = validator("new_password", allow_reuse=True)(validate_password)


class UserPswAdminModifyForm(SanicFormBaseModel):
    """用户密码修改表单(管理员使用)"""
    user_id: int = Field(default=..., gt=0, description="所选的用户ID")
    password: str = Field(default=..., min_length=custom_config.CUSTOM_MIN_PSW_LENGTH, max_length=custom_config.CUSTOM_MAX_PSW_LENGTH, description="新密码")

    # 验证器
    _validate_password = validator("password", allow_reuse=True)(validate_password)


class SystemSeetingForm(SanicFormBaseModel):
    """系统设置修改表单"""
    min_psw_length: int = Field(default=..., ge=6, le=16, description="密码最小长度")
    max_psw_length: int = Field(default=..., gt=0, le=16, description="密码最大长度")
    psw_change_max_age: int = Field(default=..., ge=0, le=90, description="密码使用期限")

    @validator("max_psw_length")
    def validate_psw_length(cls, v, values):
        if v < values["min_psw_length"]:
            raise ValueError("最大长度不能小于最小长度")
        return v



