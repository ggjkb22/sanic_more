# Author: Q
# Date:   2023-4-28
# Desc:   后台用户表单验证

from typing import Set
from pydantic import Field, conint
from app.verify.form.base import SanicFormBaseModel

__all__ = ("RoleAddForm", "RoleDelForm", "RoleModifyForm")


class RoleAddForm(SanicFormBaseModel):
    """角色添加表单"""
    name: str = Field(default=..., min_length=1, max_length=50, description="角色名")
    description: str = Field(default=None, max_length=300, description='备注')
    menu_permissions: Set[str] = Field(default=set(), description="拥有的菜单权限")


class RoleDelForm(SanicFormBaseModel):
    """角色删除表单"""
    role_ids: Set[conint(gt=0)] = Field(default=..., description="所选的角色ID")


class RoleModifyForm(SanicFormBaseModel):
    """角色修改表单"""
    role_id: int = Field(default=..., gt=0, description="所选的角色ID")
    name: str = Field(default=..., min_length=1, max_length=50, description="角色名")
    description: str = Field(default=None, max_length=300, description='备注')
    menu_permissions: Set[str] = Field(default=set(), description="拥有的菜单权限")
