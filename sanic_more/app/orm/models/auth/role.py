# Author: Q
# Date:   2023-5-13
# Desc:   角色数据模型

from typing import List, Union, Set
from datetime import datetime
from sanic import Sanic
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, select, update, UniqueConstraint
from sqlalchemy.orm import relationship, selectinload, joinedload, subqueryload
from sanic_more.app.orm.models.base import PkBaseModel, MixinTimeFiled
from sanic_more.app.orm.models.auth.menu_permission import MenuPermission

__all__ = ("Role", "UserRoleRel")


class UserRoleRel(PkBaseModel):
    """User与Role多对多关系中间表的数据模型"""
    __tablename__ = "auth_user_role_rel"
    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='_unique_user_role'),)
    user_id = Column(Integer(), ForeignKey("auth_user.id", ondelete="CASCADE"), nullable=False, index=True,
                     comment="与用户关联的外键")
    role_id = Column(Integer(), ForeignKey("auth_role.id", ondelete="CASCADE"), nullable=False, index=True,
                     comment="与角色关联的外键")
    join_dt = Column(DateTime(), default=datetime.now, comment="用户设置为该角色的时间")


class Role(PkBaseModel, MixinTimeFiled):
    """权限验证系统角色数据模型"""
    __tablename__ = "auth_role"
    name = Column(String(50), nullable=False, unique=True, index=True, comment="角色名称")
    description = Column(String(300), nullable=True, comment="备注")
    # 与 MenuPermission 多对多关系
    menu_permissions = relationship("MenuPermission", secondary="auth_role_menupermission_rel",
                                    back_populates="roles", uselist=True)

    # 与User多对多关系
    users: relationship("User", secondary="auth_user_role_rel", back_populates="roles", uselist=True)


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
    # 先清空及添加新指定的角色的菜单权限再清空对应缓存
    await self.menu_permissions.clear()
    if new_menu_permissions:
        filter_new_menu_permissions_code = [Q(code=_code) for _code in new_menu_permissions]
        new_menu_permissions = await MenuPermission.filter(Q(*filter_new_menu_permissions_code, join_type="OR"))
        await self.menu_permissions.add(*new_menu_permissions)
    await self.clear_menu_permissions_cache()
