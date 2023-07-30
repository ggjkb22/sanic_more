# Author: Q
# Date:   2023-3-17
# Desc:   App文件,用于Sanic实例的初始化与配置

from sanic import Sanic
from .conf import get_config
from .listeners import register_listener
from .middleware import register_middleware

# 获取定制的配置
custom_config = get_config()

# 初始化 Sanic 实例
app = Sanic(name=custom_config.SERVER_NAME, config=custom_config)

# 注册全局监听器
register_listener(app)
# 注册中间件
register_middleware(app)

# 静态文件路由
app.static(uri="/static", file_or_directory=app.config.CUSTOM_STATIC_PATH, name="static")
