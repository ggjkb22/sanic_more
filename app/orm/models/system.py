# Author: Q
# Date:   2023-5-3
# Desc:   后台系统设置数据模型


import ujson
from sanic import Sanic
from typing import Union, Dict
from tortoise import fields, Model
from tortoise.transactions import in_transaction
from app.orm.models.base import AbstractPKModel
from app.orm.utils import t_instance_serialize
from app.conf import get_config
from app.conf import LoginFieldLockPolicy

custom_config = get_config()


class SystemSetting(AbstractPKModel):
    """系统设置数据模型"""
    min_psw_length = fields.SmallIntField(default=custom_config.CUSTOM_DEFAULT_MIN_PSW_LENGTH, null=False,
                                          description='密码最小长度')
    max_psw_length = fields.SmallIntField(default=custom_config.CUSTOM_DEFAULT_MAX_PSW_LENGTH, null=False,
                                          description='密码最大长度')
    psw_change_max_age_enable = fields.BooleanField(default=True, null=False, description='开启密码使用期限')
    psw_change_max_age = fields.SmallIntField(default=custom_config.CUSTOM_DEFAULT_PSW_CHANGE_MAX_AGE, null=False,
                                              description='密码使用期限(单位:天)')
    session_idle_logout_max_age = fields.SmallIntField(default=custom_config.CUSTOM_SESSION_DEFAULT_MAX_AGE, null=False,
                                                       description='会话空闲登出时间(单位:分钟)')
    login_failed_lock_policy = fields.IntEnumField(LoginFieldLockPolicy, default=LoginFieldLockPolicy.lock_ip_user,
                                                   null=False, description="用户登录失败锁定策略")
    login_failed_lock_number = fields.SmallIntField(default=custom_config.CUSTOM_DEFAULT_LOGIN_FAILED_LOCK_NUMBER,
                                                    null=False, description='用户登录失败锁定次数')
    login_failed_lock_max_age = fields.SmallIntField(default=custom_config.CUSTOM_DEFAULT_LOGIN_FAILED_LOCK_MAX_AGE,
                                                     null=False, description='用户登录失败锁定时间(单位:分钟)')

    class Meta:
        table = 'system_settings'
        table_description = '系统设置数据模型'
        ordering = ('id',)

    @classmethod
    async def get_or_init_settings_sql(cls, serialize=True) -> Union[Dict[str, str], Model]:
        """
        从sql获取系统配置
        如果未初始化则会先使用默认配置进行初始化
        """
        setting = await cls.first()
        if setting is None:
            async with in_transaction() as connection:
                setting = await cls.create()
        if serialize:
            setting = await t_instance_serialize(cls, setting, name="system_get_or_init_settings_sql")
        return setting

    @classmethod
    async def update_settings(cls, **kwargs) -> Model:
        """更新sql中的系统配置信息,并将配置存入缓存中"""
        setting = await cls.get_or_init_settings_sql(serialize=False)
        async with in_transaction() as connection:
            setting = await setting.update_from_dict(kwargs)
            await setting.save()
            cache_redis = Sanic.get_app().ctx.cache_redis
            _, set_settings_cache = await cache_redis.auto_cache(custom_config.CUSTOM_APP_SETTINGS_KEY,
                                                                 return_type="dict")
            setting_json = await t_instance_serialize(cls, setting, name="system_update_settings", return_type="json")
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
            setting_json = ujson.dumps(setting)
            await set_settings_cache(setting_json)
            settings_cache, _ = await cache_redis.auto_cache(custom_config.CUSTOM_APP_SETTINGS_KEY, return_type="dict")
        return settings_cache
