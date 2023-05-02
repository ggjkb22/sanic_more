# Author: Q
# Date:   2023-4-8
# Desc:   后台管理首页路由

from sanic import Request
from sanic.views import HTTPMethodView
from app.orm import t_instance_serialize
from app.orm.models.auth import User
from app.tools.template import jinja2_async_render
from app.tools.state_check.login_state import login_check
from app.tools.csrf_protect import generate_csrf_token


class AdminIndexView(HTTPMethodView):
    """管理界面首页视图"""

    async def get(self, request: Request):
        # 登录状态验证
        current_user = await login_check(request)
        user = await User.get_or_none(pk=current_user)
        res = await t_instance_serialize(User, user, exclude=("hashed_psw",), return_type="dict")
        temp_ctx = {
            "request": request,
            "user": res,
        }
        return await jinja2_async_render("admin/index.html", temp_ctx)

