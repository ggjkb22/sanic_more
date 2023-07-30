# Author: Q
# Date:   2023-4-21
# Desc:   状态检查
#         关于为什么不使用依赖注入来实现状态检查:因为Sanic的依赖注入会在sanic_session注册以前执行，导致报request.ctx中没有session
#         参数的错误

from .login_state import login_check, logout_check
from .login_failed_lock import LoginFailedLock
from .permission_check import hplus_menu_permission_check
