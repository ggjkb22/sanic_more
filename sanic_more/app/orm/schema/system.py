# Author: Q
# Date:   2023-5-3
# Desc:   后台系统设置的Pydantic数据模型

from pydantic import BaseModel
from sanic_more.app.custom_enum import LoginFailLockPolicy

__all__ = ("SystemSettingRes",)


class SystemSettingRes(BaseModel):
    """后台系统设置返回值的Pydantic数据模型"""
    id: int
    min_psw_length: int
    max_psw_length: int
    psw_change_max_age_enable: bool
    psw_change_max_age: int
    session_idle_logout_max_age: int
    login_failed_lock_policy: LoginFailLockPolicy
    login_failed_lock_number: int
    login_failed_lock_max_age: int

    class Config:
        from_attributes = True
