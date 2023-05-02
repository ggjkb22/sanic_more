# Author: Q
# Date:   2023-4-4
# Desc:   Auth表单验证

from typing import Optional, List, Union, Set, Dict
from pydantic import Field, validator
from .base import SanicFormBaseModel
from .admin import validate_username


class LoginForm(SanicFormBaseModel):
    """
    登录验证表单
    字段声明的顺序和验证器的pre参数都是决定字段验证的关键,需要合理使用
    """
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=8, max_length=16, description="密码")
    captcha: str = Field(..., min_length=4, max_length=4, description="验证码")

    # 验证器
    _validate_username = validator("username", allow_reuse=True)(validate_username)