# Author: Q
# Date:   2023-5-13
# Desc:   角色数据模型

import ujson
from typing import List, Union, Set
from sanic import Sanic
from tortoise import fields
from tortoise.expressions import Q
from tortoise.transactions import in_transaction
from app.orm.models.base import AbstractPKModel, MixinTimeFiled
from app.orm.models.auth.permission import MenuPermission

__all__ = ("Role", "UserRoleRel")


class Role(AbstractPKModel, MixinTimeFiled):
    """
    权限验证系统角色数据模型
    """
    name = fields.CharField(max_length=50, null=False, unique=True, index=True, description="角色名称")
    description = fields.CharField(max_length=300, null=True, description="备注")

    users: fields.ManyToManyRelation["User"]  # 与User多对多关系
    user_role_rel: fields.ReverseRelation["UserRoleRel"]  # 与auth_user_role_rel中间表一对多关系
    # 与 MenuPermission 多对多关系(使用默认中间表)
    menu_permissions = fields.ManyToManyField("all_models.MenuPermission", related_name="roles", on_delete="CASCADE",
                                              through="auth_role_menu_permission",
                                              description="角色的菜单权限")

    class Meta:
        table = 'auth_role'
        table_description = '权限系统中的角色数据模型'
        ordering = ('id',)

    async def auto_get_menu_permissions(self):
        """配合缓存获取角色的菜单权限"""
        # 读取角色的菜单权限
        cache_redis = Sanic.get_app().ctx.cache_redis
        # 从缓存中读取角色的菜单权限
        menu_permissions_cache, set_menu_permissions_cache = await cache_redis.auto_cache(
            f"role_{self.pk}_menu_permissions", return_type="dict")
        if menu_permissions_cache is None:
            menu_permissions_cache = await self.menu_permissions.all().values_list("code", flat=True)
            res_json = ujson.dumps(menu_permissions_cache)
            await set_menu_permissions_cache(res_json)
        return menu_permissions_cache

    async def clear_menu_permissions_cache(self):
        """清除角色的菜单权限缓存"""
        cache_redis = Sanic.get_app().ctx.cache_redis
        await cache_redis.del_cache(f"role_{self.pk}_menu_permissions")

    async def update_menu_permissions(self, new_menu_permissions: Union[List[str], Set[str]]):
        """
        更新角色的菜单权限
        为了保证数据库与缓存的一致性, 先清空及添加新指定的角色的菜单权限再清空对应缓存
        """
        async with in_transaction() as connect:
            # 先清空及添加新指定的角色的菜单权限再清空对应缓存
            await self.menu_permissions.clear()
            if new_menu_permissions:
                filter_new_menu_permissions_code = [Q(code=_code) for _code in new_menu_permissions]
                new_menu_permissions = await MenuPermission.filter(Q(*filter_new_menu_permissions_code, join_type="OR"))
                await self.menu_permissions.add(*new_menu_permissions)
            await self.clear_menu_permissions_cache()


class UserRoleRel(AbstractPKModel):
    """User与Role多对多关联表"""
    user = fields.ForeignKeyField("all_models.User", related_name="user_role_rel", null=False,
                                  on_delete=fields.CASCADE, description="与用户关联的外键")
    role = fields.ForeignKeyField("all_models.Role", related_name="user_role_rel", null=False,
                                  on_delete=fields.CASCADE, description="与角色关联的外键")
    join_datetime = fields.DatetimeField(auto_now_add=True, description="用户设置为该角色的时间")

    class Meta:
        table = "auth_user_role_rel"
        table_description = '权限系统中的用户与角色的多对多中间表'
        ordering = ('id',)
        unique_together = (('user', 'role'),)  # 联合唯一(用户ID与角色ID)
