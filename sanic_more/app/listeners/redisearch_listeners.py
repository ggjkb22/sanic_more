# Author: Q
# Date:   2023-7-3
# Desc:   Redisearch监听器

from redis import asyncio as aioredis
from sanic import Sanic


def register_redisearch(app: Sanic):
    """创建缓存中间件"""

    @app.listener("before_server_start")
    async def init_cache(app: Sanic):
        redis_pool = aioredis.from_url(
            url=app.config.CUSTOM_REDIS_URL,
            password=app.config.CUSTOM_REDIS_PSW,
            port=app.config.CUSTOM_REDIS_PORT,
            db=app.config.CUSTOM_REDIS_DB_ENUM.search_db.value
        )
        app.ctx.redisearch = redis_pool

    @app.listener("after_server_stop")
    async def close_cache(app: Sanic):
        await app.ctx.redisearch.close()
