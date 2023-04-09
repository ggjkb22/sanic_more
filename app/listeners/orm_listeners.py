# Author: Q
# Date:   2023-3-28
# Desc:   ORM监听器

from sanic import Sanic
from tortoise.contrib.sanic import register_tortoise


def register_tortoise_orm(app: Sanic):
    """创建Tortoise-orm的数据库连接
    1. 官方自带的register_tortoise已经写好了监听器,这边只是做了个暂时多余的二次封装
    """
    register_tortoise(app, config=app.config.CUSTOM_TORTOISE_ORM_CFG)
