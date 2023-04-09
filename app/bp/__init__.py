# Author: Q
# Date:   2023-4-8
# Desc:   蓝图组汇总与统一注册函数

from sanic import Sanic
from .mtv import mtv


def register_bp(app: Sanic):
    """统一注册函数"""
    # 注册MTV蓝图组
    app.blueprint(mtv)
    