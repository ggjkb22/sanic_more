# Author: Q
# Date:   2023-4-8
# Desc:   MTV蓝图组

from sanic import Blueprint
from app.exception import register_mtv_error_handler
from app.middles import register_mtv_middles
from app.extends import register_session_extends
from .auth import auth_bp
from .admin import admin_bp


mtv = Blueprint.group(auth_bp, admin_bp, url_prefix="/mtv")

# 注册MTV蓝图组全局错误验证处理器
register_mtv_error_handler(mtv)

# 将sanic_session注册到应用中(存储使用redis)
# 这个注册必须要在csrf中间件之前执行,因为csrf依赖于sanic_session
register_session_extends(mtv)

# 注册中间件
register_mtv_middles(mtv)

