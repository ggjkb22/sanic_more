# Author: Q
# Date:   2023-3-20
# Desc:   监听器注册文件,将所有的监听器注册到 app 中

from sanic import Sanic
from .orm_listeners import register_tortoise_orm
from .arq_listeners import register_arq
from .cache_listeners import register_cache


def register_listener(app: Sanic):
    """统一注册监听器"""
    # 注册tortoise-orm数据库连接
    register_tortoise_orm(app)

    # 注册arq的redis连接池
    register_arq(app)

    # 注册缓存的redis连接池
    register_cache(app)

    