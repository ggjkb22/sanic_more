# Author: Q
# Date:   2023-3-19
# Desc:   中间件注册文件,将所有的中间件注册到 app 中

from typing import Union
from sanic import Sanic, Blueprint
from .mtv_csrf import mtv_csrf_protect


def register_mtv_middles(app: Union[Sanic, Blueprint]):
    """注册mtv所需中间件
    需要注意中间件的执行顺序
    """
    # app.register_middleware(mtv_csrf_protect, "request")    # 蓝图组没有register_middleware方法
    app.middleware("request")(mtv_csrf_protect)
