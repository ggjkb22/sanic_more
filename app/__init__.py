# Author: Q
# Date:   2023-3-17
# Desc:   App文件,用于Sanic实例的初始化与配置

from sanic import Sanic
from .conf import get_config
from .listeners import register_listener
from .route import register_static_route
from .bp import register_bp

# 获取定制的配置
custom_config = get_config()

# 初始化 Sanic 实例
app = Sanic(name="Sanic_Portal", config=custom_config)

# 注册全局监听器
register_listener(app)
# 注册蓝图
register_bp(app)
# 注册静态文件路由
register_static_route(app)

