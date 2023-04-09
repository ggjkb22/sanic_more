# Author: Q
# Date:   2023-3-17
# Desc:   用于sanic_session拓展的配置

import aioredis
from typing import Union
from sanic import Sanic, Blueprint
from sanic.blueprint_group import BlueprintGroup
from sanic_session import Session, AIORedisSessionInterface, InMemorySessionInterface
from app.conf import get_config

custom_config = get_config()

class CustomSession(Session):
    """改写Session类使其可以兼容mtv csrf代码
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
            CustomSession(bp, interface=AIORedisSessionInterface(redis=redis_pool,
                                                                expiry=custom_config.CUSTOM_SESSION_EXPIRE_SECOND))
    else:
        CustomSession(app, interface=AIORedisSessionInterface(redis=redis_pool,
                                                            expiry=custom_config.CUSTOM_SESSION_EXPIRE_SECOND))
