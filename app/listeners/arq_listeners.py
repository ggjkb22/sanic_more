# Author: Q
# Date:   2023-4-16
# Desc:   arq监听器

from sanic import Sanic
from arq import create_pool
from app.conf import get_config


def register_arq(app: Sanic):
    """创建arq的redis连接池"""
    @app.listener("before_server_start")
    async def init_arq(app: Sanic):
        app.ctx.arq_redis = await create_pool(get_config().CUSTOM_ARQ_REDIS_SETTINGS)


