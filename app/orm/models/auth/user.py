# Author: Q
# Date:   2023-4-16
# Desc:   用户数据模型

from tortoise import fields
from app.orm.models.base import AbstractPKModel, MixinTimeFiled
from app.tools.password.psw_bcrypt import *

__all__ = ["User", "Group", "UserGroupRel"]


class User(AbstractPKModel, MixinTimeFiled):
    """
    权限验证系统用户模型
        1.与Group多对多关系
    """
    username = fields.CharField(max_length=20, null=False, unique=True, index=True, description='用户名')
    hashed_psw = fields.CharField(max_length=256, null=True, description='密码哈希')
    description = fields.CharField(max_length=300, null=True, description='备注')
    can_use = fields.BooleanField(default=True, null=False, description='是否可用')

    # 与Group多对多关系
    groups = fields.ManyToManyField("all_models.Group", related_name="users", null=True, through="auth_user_group_rel",
                                    forward_key="group_id", backward_key="user_id", description="用户的用户组")
    user_group_rel: fields.ReverseRelation["UserGroupRel"]  # 与auth_user_group_rel中间表一对多关系

    class Meta:
        table = 'auth_user'
        table_description = '权限系统中的用户数据模型'
        ordering = ('id',)

    async def set_psw(self, value: str, _async: bool = True):
        """异步设置密码hash"""
        if _async:
            self.hashed_psw = await ahash_psw(value)
            return
        self.hashed_psw = hash_psw(value)

    async def check_psw(self, value: str, _async: bool = True) -> bool:
        """验证密码"""
        if _async:
            return await acheckout_psw(value, self.hashed_psw)
        return checkout_psw(value, self.hashed_psw)


class Group(AbstractPKModel, MixinTimeFiled):
    """
    权限验证系统用户组模型
        1.与User多对多关系
    """
    name = fields.CharField(max_length=50, unique=True, null=False, index=True, description="用户组名")
    description = fields.CharField(max_length=300, null=True, description="备注")

    users: fields.ManyToManyRelation["User"]  # 与User多对多关系
    user_group_rel: fields.ReverseRelation["UserGroupRel"]  # 与auth_user_group_rel中间表一对多关系

    class Meta:
        table = 'auth_group'
        table_description = '权限系统中的用户组数据模型'
        ordering = ('id',)


class UserGroupRel(AbstractPKModel):
    """User与Group多对多关联表"""
    user = fields.ForeignKeyField("all_models.User", related_name="user_group_rel", null=False,
                                  on_delete=fields.CASCADE, description="与用户关联的外键")
    group = fields.ForeignKeyField("all_models.Group", related_name="user_group_rel", null=False,
                                   on_delete=fields.CASCADE,
                                   description="与标签关联的外键")
    join_datetime = fields.DatetimeField(auto_now_add=True, description="用户加入用户组的时间")

    class Meta:
        table = "auth_user_group_rel"
        table_description = '权限系统中的用户与用户组的多对多中间表'
        ordering = ('id',)
        unique_together = (('user', 'group'),)  # 联合唯一(用户ID与组ID)
