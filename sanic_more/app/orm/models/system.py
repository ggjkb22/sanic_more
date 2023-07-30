# Author: Q
# Date:   2023-5-3
# Desc:   后台系统设置数据模型


from typing import Union, Dict, Type
from sanic import Sanic
from sqlalchemy import Column, SmallInteger, Boolean, Enum, select, update
from sanic_more.app.conf import get_config
from sanic_more.app.custom_enum import LoginFailLockPolicy
from sanic_more.app.tools.get_sqlalchemy_session import auto_get_sqlalchemy_session
from sanic_more.app.orm.schema.system import SystemSettingRes
from .base import *

__all__ = ("SystemSetting", )

custom_config = get_config()


class SystemSetting(PkBaseModel, MixinTimeFiled):
    """系统设置数据模型"""
    __tablename__ = "system_settings"
    min_psw_length = Column(SmallInteger(), default=custom_config.CUSTOM_DEFAULT_MIN_PSW_LENGTH, nullable=False,
                            comment="密码最小长度")
    max_psw_length = Column(SmallInteger(), default=custom_config.CUSTOM_DEFAULT_MAX_PSW_LENGTH, nullable=False,
                            comment="密码最大长度")
    psw_change_max_age_enable = Column(Boolean(), default=True, nullable=False, comment="开启密码使用期限")
    psw_change_max_age = Column(SmallInteger(), default=custom_config.CUSTOM_DEFAULT_PSW_CHANGE_MAX_AGE, nullable=False,
                                comment="密码使用期限(单位:天)")
    session_idle_logout_max_age = Column(SmallInteger(), default=custom_config.CUSTOM_SESSION_DEFAULT_MAX_AGE,
                                         nullable=False, comment="会话空闲登出时间(单位:分钟)")
    login_failed_lock_policy = Column(Enum(LoginFailLockPolicy), default=LoginFailLockPolicy.lock_ip_user,
                                      nullable=False, comment="用户登录失败锁定策略")
    login_failed_lock_number = Column(SmallInteger(), default=custom_config.CUSTOM_DEFAULT_LOGIN_FAILED_LOCK_NUMBER,
                                      nullable=False, comment="用户登录失败锁定次数")
    login_failed_lock_max_age = Column(SmallInteger(), default=custom_config.CUSTOM_DEFAULT_LOGIN_FAILED_LOCK_MAX_AGE,
                                       nullable=False, comment="用户登录失败锁定时间(单位:分钟)")

    @classmethod
    async def get_or_init_settings_sql(cls: Type["SystemSetting"]) -> "SystemSetting":
        """
        从sql获取系统配置
        如果未初始化则会先使用默认配置进行初始化
        """
        session = auto_get_sqlalchemy_session()
        async with session.begin():
            setting = await session.execute(select(cls))
            setting = setting.scalar_one_or_none()
            if setting is None:
                setting = cls()
                session.add(setting)
        return setting

    @classmethod
    async def update_settings(cls: Type["SystemSetting"], **kwargs) -> "SystemSetting":
        """更新sql中的系统配置信息,并将配置存入缓存中"""
        setting = await cls.get_or_init_settings_sql()
        session = auto_get_sqlalchemy_session()
        async with session.begin():
            await session.execute(update(cls).values(**kwargs))
        cache_redis = Sanic.get_app().ctx.cache_redis
        _, set_settings_cache = await cache_redis.auto_cache(custom_config.CUSTOM_APP_SETTINGS_KEY)
        setting_json = SystemSettingRes.model_validate(setting).model_dump_json()
        await set_settings_cache(setting_json)
        return setting

    @classmethod
    async def auto_get_settings(cls) -> Dict[str, str]:
        """
        从缓存中获取系统配置
        缓存中没有时会先去sql中取出并存进缓存
        """
        cache_redis = Sanic.get_app().ctx.cache_redis
        settings_cache, set_settings_cache = await cache_redis.auto_cache(custom_config.CUSTOM_APP_SETTINGS_KEY,
                                                                          return_type="dict")
        if settings_cache is None:
            setting = await cls.get_or_init_settings_sql()
            setting_json = SystemSettingRes.model_validate(setting).model_dump_json()
            await set_settings_cache(setting_json)
            settings_cache = SystemSettingRes.model_validate(setting).model_dump()
        return settings_cache
