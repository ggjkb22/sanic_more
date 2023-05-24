# Author: Q
# Date:   2023-4-8
# Desc:   后台管理首页路由

from datetime import datetime
from sanic import Request, redirect
from sanic.views import HTTPMethodView
from app.orm import t_instance_serialize
from app.orm.models.auth import User
from app.tools.template import jinja2_async_render
from app.tools.state_check.login_state import login_check
from app.orm.models.system import SystemSetting

__all__ = ("AdminIndexView", "AdminIndexMenuView")


class AdminIndexView(HTTPMethodView):
    """管理界面首页视图"""

    async def get(self, request: Request):
        # 登录状态验证
        current_user = await login_check(request)
        user = await User.get_or_none(pk=current_user)
        if user is None:
            return redirect(request.url_for("auth.logout"))
        # 检查密码是否过期
        psw_expired = False
        settings = await SystemSetting.auto_get_settings()
        if settings["psw_change_max_age_enable"]:
            psw_used = datetime.now() - user.psw_last_modified_datetime.replace(tzinfo=None)
            if psw_used.days >= settings["psw_change_max_age"]:
                psw_expired = True
        res = await t_instance_serialize(User, user, exclude=("hashed_psw",), name="AdminIndexViewGET",
                                         return_type="dict")
        menu_permissions = await user.auto_get_menu_permissions()
        temp_ctx = {
            "request": request,
            "user": res,
            "menu_permissions": menu_permissions,
            "psw_expired": psw_expired,
        }
        return await jinja2_async_render("admin/index.html", temp_ctx)


class AdminIndexMenuView(HTTPMethodView):
    """管理界面首页侧边栏菜单视图"""

    async def get(self, request: Request):
        # 登录状态验证
        await login_check(request)
        temp_ctx = {
            "request": request,
        }
        return await jinja2_async_render("admin/index_menu.html", temp_ctx)
