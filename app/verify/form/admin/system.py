# Author: Q
# Date:   2023-5-3
# Desc:   后台系统设置表单验证


from pydantic import Field, validator
from app.verify.form.base import SanicFormBaseModel
from app.conf import LoginFieldLockPolicy

__all__ = ["SystemAuthSettingForm", ]


class SystemAuthSettingForm(SanicFormBaseModel):
    """系统设置下的认证设置的修改表单"""
    min_psw_length: int = Field(default=..., ge=6, le=16, description="密码最小长度")
    max_psw_length: int = Field(default=..., ge=6, le=16, description="密码最大长度")
    psw_change_max_age_enable: bool = Field(default=..., description="开启密码使用期限")
    psw_change_max_age: int = Field(default=..., ge=0, le=90, description="密码使用期限")  # 单位:天
    session_idle_logout_max_age: int = Field(default=..., ge=1, le=43200, description="会话空闲登出时间")  # 单位:分钟
    login_failed_lock_policy: LoginFieldLockPolicy = Field(default=..., description="用户登录失败锁定策略")
    login_failed_lock_number: int = Field(default=..., ge=1, le=20, description="用户登录失败锁定次数")
    login_failed_lock_max_age: int = Field(default=..., ge=1, le=60, description="用户登录失败锁定时间")  # 单位:分钟

    @validator("max_psw_length")
    def validate_psw_length(cls, v, values):
        if v < values["min_psw_length"]:
            raise ValueError("最大长度不能小于最小长度")
        return v
