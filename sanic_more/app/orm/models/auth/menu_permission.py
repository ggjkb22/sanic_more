# Author: Q
# Date:   2023-5-14
# Desc:   菜单权限数据模型

import ujson
from datetime import datetime
from sanic import Sanic
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, select, update, UniqueConstraint
from sqlalchemy.orm import relationship, selectinload, joinedload, subqueryload
from sanic_more.app.orm.models.base import *

__all__ = ("MenuPermission", "RoleMenuPermissionRel")


class RoleMenuPermissionRel(PkBaseModel):
    """权限系统中的角色与菜单权限多对多关系中间表的数据模型"""
    __tablename__ = "auth_role_menupermission_rel"
    __table_args__ = (UniqueConstraint('role_id', 'menu_permission_id', name='_unique_role_menupermission'),)
    role_id = Column(Integer(), ForeignKey("auth_role.id", ondelete="CASCADE"), nullable=False, index=True,
                     comment="与角色关联的外键")
    menu_permission_id = Column(Integer(), ForeignKey("auth_menu_permission.id", ondelete="CASCADE"), nullable=False,
                                index=True, comment="与角色关联的外键")
    join_dt = Column(DateTime(), default=datetime.now, comment="赋予权限的时间")


class MenuPermission(PkBaseModel):
    """权限系统中的菜单权限数据模型"""
    __tablename__ = "auth_menu_permission"
    name = Column(String(50), nullable=False, comment="权限名称")
    code = Column(String(100), nullable=False, unique=True, index=True, comment="权限代码")
    # 自关联(父子)
    parent = Column(Integer(), ForeignKey("auth_menu_permission.id", ondelete="CASCADE"), nullable=True,
                    comment="所属父权限")
    childrens = relationship("MenuPermission", backref="parent")
    # 与 Role多对多关系(默认中间表)
    roles = relationship("Role", secondary="auth_role_menupermission_rel", back_populates="menu_permissions",
                         uselist=True)

    @classmethod
    async def clear_all_menu_permissions_cache(cls):
        """清空所有菜单权限的缓存"""
        cache_redis = Sanic.get_app().ctx.cache_redis
        await cache_redis.del_cache("all_menu_permissions")

    @classmethod
    async def auto_get_all_menu_permissions(cls, return_type="str"):
        """配合缓存获取所有菜单权限"""
        cache_redis = Sanic.get_app().ctx.cache_redis
        # 从缓存中读取所有菜单权限
        menu_permissions_cache, set_menu_permissions_cache = await cache_redis.auto_cache("all_menu_permissions",
                                                                                          return_type=return_type)
        # 缓存没有则去sql读取
        if menu_permissions_cache is None:
            menu_permissions_cache = await MenuPermission.all().values("id", "name", "code", "parent_id")
            res_json = ujson.dumps(menu_permissions_cache)
            await set_menu_permissions_cache(res_json)
            if return_type == "str":
                return res_json
            else:
                return menu_permissions_cache
        else:
            return menu_permissions_cache
