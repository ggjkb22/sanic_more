# Author: Q
# Date:   2023-4-16
# Desc:   arq监听器

import msgpack
from sanic import Sanic
from arq import create_pool


def register_arq(app: Sanic):
    """创建arq的redis连接池"""

    @app.listener("before_server_start")
    async def init_arq(app: Sanic):
        app.ctx.arq_redis = await create_pool(app.config.CUSTOM_ARQ_REDIS_SETTINGS, job_serializer=msgpack.packb,
                                              job_deserializer=lambda b: msgpack.unpackb(b, raw=False))

    @app.listener("after_server_stop")
    async def close_cache(app: Sanic):
        await app.ctx.arq_redis.close()
