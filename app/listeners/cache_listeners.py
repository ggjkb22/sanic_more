# Author: Q
# Date:   2023-4-16
# Desc:   缓存监听器

import aioredis
from sanic import Sanic
from app.conf import get_config


custom_config = get_config()


def register_cache(app: Sanic):
    """创建缓存的redis连接池"""
    @app.listener("before_server_start")
    async def init_cache(app: Sanic):
        app.ctx.cache_redis = aioredis.from_url(
            url=custom_config.CUSTOM_REDIS_URL,
            password=custom_config.CUSTOM_REDIS_PSW,
            port=custom_config.CUSTOM_REDIS_PORT,
            db=custom_config.CUSTOM_REDIS_DB_ENUM.cache_db.value
        )

    @app.listener("after_server_stop")
    async def close_cache(app: Sanic):
        await app.ctx.cache_redis.close()
