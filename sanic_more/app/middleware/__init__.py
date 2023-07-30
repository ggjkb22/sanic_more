# Author: Q
# Date:   2023-3-19
# Desc:   中间件模块

from sanic import Sanic
from .sqlalchemy_mid import register_sqlalchemy


def register_middleware(app: Sanic):
    """统一注册中间件"""
    # 注册sqlalchemy的中间件
    register_sqlalchemy(app)
