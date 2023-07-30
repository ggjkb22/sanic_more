# Author: Q
# Date:   2023-3-20
# Desc:   监听器模块

from sanic import Sanic
from .arq_listeners import register_arq
from .cache_listeners import register_cache
from .redisearch_listeners import register_redisearch


def register_listener(app: Sanic):
    """统一注册监听器"""
    # 注册缓存的redis连接池
    register_cache(app)
    if app.config.CUSTOM_USE_REDISEARCH:
        # 注册redisearch的reids连接池
        register_redisearch(app)
    if app.config.CUSTOM_USE_ARQ:
        # 注册arq的redis连接池
        register_arq(app)

    