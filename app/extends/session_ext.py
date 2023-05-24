# Author: Q
# Date:   2023-3-17
# Desc:   用于sanic_session拓展的配置

import aioredis
from typing import Union
from sanic import Sanic, Blueprint
from sanic.blueprint_group import BlueprintGroup
from sanic_session import Session, AIORedisSessionInterface, InMemorySessionInterface
from app.conf import get_config
from app.orm.models.system import SystemSetting

custom_config = get_config()


class CustomSession(Session):
    """
    改写Session类使其可以兼容mtv csrf代码
    主要改写部分为最后注册中间件部分的代码
    """

    def init_app(self, app: Union[Sanic, Blueprint], interface):
        self.interface = interface or InMemorySessionInterface()
        if not hasattr(app.ctx, "extensions"):
            app.ctx.extensions = {}

        app.ctx.extensions[self.interface.session_name] = self  # session_name defaults to 'session'

        @app.middleware("request")
        async def add_session_to_request(request):
            """Before each request initialize a session
            using the client's request."""
            await self.interface.open(request)

        @app.middleware("response")
        async def save_session(request, response):
            """After each request save the session, pass
            the response to set client cookies.
            """
            await self.interface.save(request, response)

        # app.register_middleware(add_session_to_request, "request")
        # app.register_middleware(save_session, "response")


class CustomAIORedisSessionInterface(AIORedisSessionInterface):
    """
    改写AIORedisSessionInterface类使其支持动态修改Session到期时间
    主要改写部分为_set_value方法
    """
    async def _set_value(self, key, data):
        """
        如果需要修改过期时间的key有值或者缓存中没有读取到过期时间, 则从sql中读取数据
        读取到值以后将需要修改过期时间的key删除
        """
        system_settings = await SystemSetting.auto_get_settings()
        expiry = system_settings["session_idle_logout_max_age"] * 60
        await self.redis.setex(key, expiry, data)


def register_session_extends(app: Union[Sanic, Blueprint, BlueprintGroup]):
    """注册sanic_session拓展(由sanic作者编写)
    创建redis连接池,用于session读写,同时将sanic_session插件注册到应用中
    """
    # 创建连接池
    redis_pool = aioredis.from_url(
        url=custom_config.CUSTOM_REDIS_URL,
        password=custom_config.CUSTOM_REDIS_PSW,
        port=custom_config.CUSTOM_REDIS_PORT,
        db=custom_config.CUSTOM_REDIS_DB_ENUM.session_db.value
    )
    # 注册插件
    # 对蓝图组注册插件时，需要逐个注册
    if isinstance(app, BlueprintGroup):
        for bp in app.blueprints:
            CustomSession(bp, interface=CustomAIORedisSessionInterface(redis=redis_pool))
    else:
        CustomSession(app, interface=CustomAIORedisSessionInterface(redis=redis_pool))
