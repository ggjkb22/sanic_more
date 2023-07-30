# Author: Q
# Date:   2023-3-26
# Desc:   命令行文件

import os
import time
import click
import asyncio
from pprint import pprint
from random import randint
from datetime import datetime
from sqlalchemy import Table, MetaData, create_engine, Column, INTEGER, DateTime, String, ForeignKey, select, insert, \
    update, delete, UniqueConstraint, bindparam, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship, selectinload, joinedload, subqueryload
from sanic_more.app.orm.models import *
from sanic_more.app.orm.schema import *
from sanic_more.app.tools.get_sqlalchemy_session import *


# # 公共基类
# Base = declarative_base()
#
#
# class PkBaseModel(Base):
#     """
#     用于继承的主键的抽象类
#         1.当表里所有属性都没设置pk时,默认生成一个INTEGER类型 id 的主键
#     """
#     __abstract__ = True
#     id = Column(INTEGER(), primary_key=True, comment="主键")
#
#
# class MixinTimeFiled:
#     """
#     用于继承时间的 MixIn
#         1.创建时间与修改时间
#     """
#     create_datetime = Column(DateTime(), default=datetime.now, nullable=False, comment="创建时间")
#     modify_datetime = Column(DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False,
#                              comment="修改时间")
#
#
# class UserRoleRel(PkBaseModel):
#     """用户与角色多对多关系中间表"""
#     __tablename__ = "auth_user_role_rel"
#     __table_args__ = (UniqueConstraint('user_id', 'role_id', name='_unique_user_role'),)
#     user_id = Column(INTEGER(), ForeignKey("auth_user.id", ondelete="CASCADE"), nullable=False, index=True,
#                      comment="与用户关联的外键")
#     role_id = Column(INTEGER(), ForeignKey("auth_role.id", ondelete="CASCADE"), nullable=False, index=True,
#                      comment="与角色关联的外键")
#     join_dt = Column(DateTime(), default=datetime.now, comment="加入时间")
#
#
# class User(PkBaseModel, MixinTimeFiled):
#     """用户测试"""
#     __tablename__ = "auth_user"
#     username = Column(String(20), nullable=False, unique=True, index=True, comment="用户名")
#     roles = relationship("Role", secondary="auth_user_role_rel", back_populates="users", uselist=True)
#
#
# class Role(PkBaseModel, MixinTimeFiled):
#     """角色测试"""
#     __tablename__ = "auth_role"
#     name = Column(String(50), nullable=False, unique=True, index=True, comment="角色名")
#     users = relationship("User", secondary="auth_user_role_rel", back_populates="roles", uselist=True)


@click.group()
def cli():
    """命令行组"""
    pass


@cli.command()
def test_db_init():
    """初始化数据库"""
    bind = auto_get_sqlalchemy_engine(sync=True)
    Base.metadata.create_all(bind)


@cli.command()
def test_db():
    """测试数据库"""

    async def cor():
        setting = await SystemSetting.get_or_init_settings_sql()
        settings_cache = SystemSettingRes.model_validate(setting).model_dump()
        print(settings_cache)

    asyncio.run(cor())


# @cli.command()
# def test_db():
#     """测试数据库"""
#
#     async def cor():
#         try:
#             bind = create_async_engine(
#                 f"mysql+aiomysql://qrj:hello_qrj@127.0.0.1:13306/sanic_more",
#                 echo=False, future=True, pool_size=1000)
#             _sessionmaker = async_sessionmaker(bind, class_=AsyncSession, expire_on_commit=False)
#             session = _sessionmaker()
#             # start = time.time()
#             # del_user_sql = delete(User)
#             # del_role_sql = delete(Role)
#             # async with session.begin():
#             #     await session.execute(del_user_sql)
#             #     await session.execute(del_role_sql)
#             # print(time.time() - start, "秒")
#             # # 增
#             # start = time.time()
#             # u_list = []
#             # r_list = []
#             # for i in range(10000):
#             #     u_list.append({"username": f"用户{i}"})
#             #     r_list.append({"name": f"角色{i}"})
#             # user_insert_sql = insert(User).values(username=bindparam("username"))
#             # role_insert_sql = insert(Role).values(name=bindparam("name"))
#             # async with session.begin():
#             #     user_res = await session.execute(user_insert_sql, u_list)
#             #     role_res = await session.execute(role_insert_sql, r_list)
#             # print(time.time() - start, "秒")
#             # 改
#             start = time.time()
#             async with session.begin():
#                 res = await session.execute(
#                     select(User).options(joinedload(User.roles)).where(and_(User.id >= 1, User.id <= 100)))
#                 for i in res.unique().scalars():
#                     # role_res = await session.execute(
#                     #     select(Role).where(or_(*{Role.id == randint(1, 10000) for r in range(500)})))
#                     # for j in role_res.scalars():
#                     #     i.roles.append(j)
#                     i.roles = []
#             print(time.time() - start, "秒")
#             # # 删
#             # async with session.begin():
#             #     await session.execute(delete(Role).where(Role.id == 1))
#         finally:
#             await session.close()
#             await bind.dispose()
#
#     asyncio.run(cor())


if __name__ == "__main__":
    cli()
