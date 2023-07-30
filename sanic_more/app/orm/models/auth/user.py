# Author: Q
# Date:   2023-4-16
# Desc:   用户数据模型

import ujson
from typing import Set, List, Union
from datetime import datetime
from sanic import Sanic
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, select, update
from sqlalchemy.orm import relationship, selectinload, joinedload, subqueryload
from sanic_more.app.tools.password.psw_bcrypt import *
from sanic_more.app.orm.models.base import PkBaseModel, MixinTimeFiled
from sanic_more.app.orm.models.auth.role import Role

__all__ = ("User",)


class User(PkBaseModel):
    """权限验证系统用户模型"""
    username = fields.CharField(max_length=20, null=False, unique=True, index=True, description="用户名")
    hashed_psw = fields.CharField(max_length=256, null=True, description="密码哈希")
    description = fields.CharField(max_length=300, null=True, description="备注")
    can_use = fields.BooleanField(default=True, null=False, description="是否可用")
    psw_last_modified_datetime = fields.DatetimeField(null=False, description="密码最后更新时间")
    last_login_ip = fields.CharField(max_length=20, null=True, description="最后登录IP")
    last_login_dt = fields.DatetimeField(null=True, description="最后登录时间")
    create_datetime = fields.DatetimeField(auto_now_add=True, description='创建时间')
    info_last_modified_datetime = fields.DatetimeField(null=True, description='信息最后修改时间')

    # 与Role多对多关系
    roles = fields.ManyToManyField("all_models.Role", related_name="users", null=True, through="auth_user_role_rel",
                                   forward_key="role_id", backward_key="user_id", on_delete="CASCADE",
                                   description="用户的角色")
    user_role_rel: fields.ReverseRelation["UserRoleRel"]
    # 与采集模块的关系
    gather_objects: fields.ReverseRelation["GatherObject"]
    gather_models: fields.ReverseRelation["GatherModel"]
    dispose_models: fields.ReverseRelation["DisposeModel"]

    class Meta:
        table = 'auth_user'
        table_description = '权限系统中的用户数据模型'
        ordering = ('id',)

    async def set_psw(self, value: str, _async: bool = True):
        """异步设置密码hash"""
        # 更改密码最后更新时间
        self.psw_last_modified_datetime = datetime.now()
        if _async:
            self.hashed_psw = await ahash_psw(value)
            return
        self.hashed_psw = hash_psw(value)

    async def check_psw(self, value: str, _async: bool = True) -> bool:
        """验证密码"""
        if _async:
            return await acheckout_psw(value, self.hashed_psw)
        return checkout_psw(value, self.hashed_psw)

    async def auto_get_roles(self) -> List[int]:
        """配合缓存获取用户的角色"""
        # 读取用户的角色
        cache_redis = Sanic.get_app().ctx.cache_redis
        # 从缓存中读取用户的角色
        roles_cache, set_roles_cache = await cache_redis.auto_cache(f"user_{self.pk}_roles", return_type="dict")
        if roles_cache is None:
            roles_cache = await self.roles.all().values_list("id", flat=True)
            res_json = ujson.dumps(roles_cache)
            await set_roles_cache(res_json)
        return roles_cache

    async def auto_get_menu_permissions(self) -> Set[str]:
        """
        配合缓存获取用户的菜单权限
        为了利于缓存的更新，菜单权限缓存分为角色缓存和菜单权限缓存
        """
        # 读取用户的角色
        roles_cache = await self.auto_get_roles()
        # 从缓存中读取角色权限并整合
        cache_redis = Sanic.get_app().ctx.cache_redis
        temp_menu_permissions_set = set()
        for role in roles_cache:
            menu_permission_cache, set_menu_permission_cache = await cache_redis.auto_cache(
                f"role_{role}_menu_permissions", return_type="dict")
            if menu_permission_cache is None:
                role_ins = await Role.get_or_none(pk=role)
                if role_ins is None:
                    continue
                menu_permission_cache = await role_ins.menu_permissions.all().values_list("code", flat=True)
                menu_permission_json = ujson.dumps(menu_permission_cache)
                await set_menu_permission_cache(menu_permission_json)
            temp_menu_permissions_set.update(menu_permission_cache)
        return temp_menu_permissions_set

    async def clear_roles_cache(self):
        """删除用户的角色缓存"""
        cache_redis = Sanic.get_app().ctx.cache_redis
        await cache_redis.del_cache(f"user_{self.pk}_roles")

    async def update_roles(self, roles: Union[List[int], Set[int]]):
        """
        更新用户的角色
        为了保证数据库与缓存的一致性, 先清空角色及添加新指定的角色再清空对应缓存
        """
        # 先清空角色及添加新指定的角色再清空对应缓存
        await self.roles.clear()
        if roles:
            filter_role_id = [Q(pk=_id) for _id in roles]
            roles = await Role.filter(Q(*filter_role_id, join_type="OR"))
            await self.roles.add(*roles)
        await self.clear_roles_cache()
