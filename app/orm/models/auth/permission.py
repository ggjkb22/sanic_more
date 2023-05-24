# Author: Q
# Date:   2023-5-14
# Desc:   权限数据模型

import ujson
from sanic import Sanic
from tortoise import fields
from app.orm.models.base import AbstractPKModel
from app.orm.utils import t_queryset_serialize, t_instance_serialize

__all__ = ("MenuPermission",)


class MenuPermission(AbstractPKModel):
    """权限系统中的菜单权限数据模型"""
    name = fields.CharField(max_length=50, null=False, description="权限名称")
    code = fields.CharField(max_length=100, null=False, unique=True, index=True, description="权限代码")

    # 自关联(父子)
    parent = fields.ForeignKeyField("all_models.MenuPermission", related_name="childrens", on_delete="CASCADE",
                                    null=True, description="父权限")
    childrens: fields.ReverseRelation["MenuPermission"]
    # 与 Role多对多关系(默认中间表)
    roles: fields.ManyToManyRelation["Role"]

    class Meta:
        table = 'auth_menu_permission'
        table_description = '权限系统中的菜单权限数据模型'
        ordering = ('id',)

    @classmethod
    async def clear_all_menu_permissions_cache(cls):
        """清空所有菜单权限的缓存"""
        cache_redis = Sanic.get_app().ctx.cache_redis
        await cache_redis.del_cache("all_menu_permissions")

    @classmethod
    async def auto_get_all_menu_permissions(cls):
        """配合缓存获取所有菜单权限"""
        cache_redis = Sanic.get_app().ctx.cache_redis
        # 从缓存中读取所有菜单权限
        menu_permissions_cache, set_menu_permissions_cache = await cache_redis.auto_cache("all_menu_permissions",
                                                                                          return_type="dict")
        # 缓存没有则去sql读取
        if menu_permissions_cache is None:
            menu_permissions_cache = await t_queryset_serialize(cls, cls.filter(parent=None),
                                                                name="MenuPermission_auto_get_all_menu_permissions",
                                                                include=("code", "name", "childrens"),
                                                                allow_cycles=True, return_type="dict")
            res_json = ujson.dumps(menu_permissions_cache)
            await set_menu_permissions_cache(res_json)
        return menu_permissions_cache
