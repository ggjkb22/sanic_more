# Author: Q
# Date:   2023-5-3
# Desc:   后台系统相关视图函数

from sanic import Request, json
from sanic.views import HTTPMethodView
from tortoise.transactions import in_transaction
from app.tools.template import jinja2_async_render
from app.tools.state_check.login_state import login_check
from app.orm.models.system import SystemSetting
from app.verify.form.admin.system import SystemAuthSettingForm
from app.orm.models.auth import User
from app.tools.state_check.menu_permission_check import dwz_menu_permission_check

__all__ = ("SystemSettingsMenuView", "SystemAuthSettingsView")

# 用于返回给dwz框架用于前端显示的json汇总
res_json = {
    "statusCode": "200",
    "message": "",
    "navTabId": "",
    "reloadMethod": "",
    "rel": "",
    "callbackType": "",
    "forwardUrl": "",
    "confirmMsg": "",
    "errorMsg": ""
}


class SystemSettingsMenuView(HTTPMethodView):
    """管理界面系统设置侧边栏菜单视图"""

    async def get(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, res_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(res_json)
        temp_ctx = {
            "request": request,
        }
        return await jinja2_async_render("admin/system/system_menu.html", temp_ctx)


class SystemAuthSettingsView(HTTPMethodView):
    """系统设置下的认证配置视图"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["message"] = "认证配置修改成功"
        self.res_json["callbackType"] = "closeCurrent"

    async def get(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, res_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(res_json)
        # 从sql获取系统配置
        settings = await SystemSetting.get_or_init_settings_sql()
        temp_ctx = {
            "request": request,
            "settings": settings,
        }
        return await jinja2_async_render("admin/system/system_auth_modify.html", temp_ctx)

    async def post(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, res_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(res_json)
        # 验证表单
        success, data = SystemAuthSettingForm.validate_sanic_form(request)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = data
            return json(self.res_json)
        # 更新认证配置
        async with in_transaction() as connection:
            data = data.dict()
            await SystemSetting.update_settings(**data)
        return json(self.res_json)
