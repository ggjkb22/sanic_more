# Author: Q
# Date:   2023-7-30
# Desc:   自动获取sqlalchemy的session


from typing import Type, Union
from sanic import Request, ServerError
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sanic_more.app.conf import get_config
from sanic_more.app.custom_typevars import SqlalchemySession, SqlalchemyEngine

__all__ = ("auto_get_sqlalchemy_engine", "auto_get_sqlalchemy_session")

# 获取应用配置
custom_conf = get_config()


def auto_get_sqlalchemy_engine(*, sync: bool = False) -> SqlalchemyEngine:
    """自动获取sqlalchemy的Engine
    :params
        sync： 用于确认自动生成的Engine对象是同步的还是异步的
    :return
        SqlalchemyEngine: 返回的Engine对象
    """
    sql_uri = f"://{custom_conf.CUSTOM_ORM_USER}:{custom_conf.CUSTOM_ORM_PSW}@{custom_conf.CUSTOM_ORM_HOST}:{custom_conf.CUSTOM_ORM_PORT}/{custom_conf.CUSTOM_ORM_DB}"
    if sync:
        bind = create_engine(custom_conf.CUSTOM_ORM_SYNC_ENGINE_PREFIX + sql_uri,
                             echo=custom_conf.CUSTOM_ORM_ECHO,
                             future=custom_conf.CUSTOM_ORM_FUTURE,
                             pool_size=custom_conf.CUSTOM_ORM_POOL_SIZE)
    else:
        bind = create_async_engine(custom_conf.CUSTOM_ORM_ASYNC_ENGINE_PREFIX + sql_uri,
                                   echo=custom_conf.CUSTOM_ORM_ECHO,
                                   future=custom_conf.CUSTOM_ORM_FUTURE,
                                   pool_size=custom_conf.CUSTOM_ORM_POOL_SIZE)
    return bind


def auto_get_sqlalchemy_session(*, sync: bool = False, instance: bool = True) -> Union[
    Type[SqlalchemySession], SqlalchemySession]:
    """自动获取sqlalchemy的session
    会先从Request中获取Session如果遇到ServerError或AttributeError则创建一个新的session并返回
    :params
        sync： 用于确认自动生成的session对象是同步的还是异步的
        instance: 是否返回Session实例, 只有在创建一个新的session时才发挥作用(从Reuqest中获取时只能获取到实例)
    :return
        SqlalchemySession: 返回的session对象
    """
    try:
        session = Request.get_current().ctx.session
    except (ServerError, AttributeError):
        bind = auto_get_sqlalchemy_engine(sync=sync)
        if sync:
            _sessionmaker = sessionmaker(bind, class_=Session, expire_on_commit=custom_conf.CUSTOM_ORM_EXPIRE_ON_COMMIT)
        else:
            _sessionmaker = async_sessionmaker(bind, class_=AsyncSession,
                                               expire_on_commit=custom_conf.CUSTOM_ORM_EXPIRE_ON_COMMIT)
        if instance:
            return _sessionmaker()
        return _sessionmaker
    else:
        return session
