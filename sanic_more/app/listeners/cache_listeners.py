# Author: Q
# Date:   2023-4-16
# Desc:   缓存监听器

from redis import asyncio as aioredis
from sanic import Sanic
from sanic_more.app.tools.cache_redis import CacheRedis


def register_cache(app: Sanic):
    """创建缓存中间件"""

    @app.listener("before_server_start")
    async def init_cache(app: Sanic):
        redis_pool = aioredis.from_url(
            url=app.config.CUSTOM_REDIS_URL,
            password=app.config.CUSTOM_REDIS_PSW,
            port=app.config.CUSTOM_REDIS_PORT,
            db=app.config.CUSTOM_REDIS_DB_ENUM.cache_db.value
        )
        app.ctx.cache_redis = CacheRedis(redis_pool)

    @app.listener("after_server_stop")
    async def close_cache(app: Sanic):
        await app.ctx.cache_redis.close()
