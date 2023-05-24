# Author: Q
# Date:   2023-5-15
# Desc:   后台角色相关视图函数

from sanic import Request, json, html
from sanic.views import HTTPMethodView
from tortoise.transactions import in_transaction
from tortoise.expressions import Q
from app.tools.template import jinja2_async_render
from app.tools.state_check.login_state import login_check
from app.orm.models.auth import Role, User, MenuPermission
from app.orm.utils import t_queryset_serialize
from app.tools.state_check.menu_permission_check import dwz_menu_permission_check
from app.verify.form.admin.role import *

__all__ = ("RoleTableView", "RoleAddView", "RoleDelView", "RoleModifyView")

res_json = {
    "statusCode": "200",
    "message": "",
    "navTabId": "admin_role_table",
    "reloadMethod": "get",
    "rel": "",
    "callbackType": "closeCurrent",
    "forwardUrl": "",
    "confirmMsg": "",
    "errorMsg": ""
}


class RoleTableView(HTTPMethodView):
    """角色列表视图"""

    async def get(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, result_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(result_json)
        roles = Role.all()
        role_total = await roles.count()
        res = await t_queryset_serialize(Role, roles, exclude=("users", "user_role_rel", "menu_permissions"),
                                         name="RoleTableViewGET")
        temp_ctx = {
            "request": request,
            "roles": res,
            "role_total": role_total,
        }
        return await jinja2_async_render("admin/role/role_table.html", temp_ctx)


class RoleAddView(HTTPMethodView):
    """添加角色视图"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["message"] = "角色添加成功"
        self.res_json["callbackType"] = "closeCurrent"

    async def get(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, result_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(result_json)
        # 获取所有菜单权限
        all_menu_permissions = await MenuPermission.auto_get_all_menu_permissions()
        temp_ctx = {
            "request": request,
            "all_menu_permissions": all_menu_permissions
        }
        return await jinja2_async_render("admin/role/role_add_form.html", temp_ctx)

    async def post(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, result_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(result_json)
        # 验证表单
        success, data = RoleAddForm.validate_sanic_form(request)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = data
            return json(self.res_json)
        # 验证角色名是否存在
        role_exists = await Role.exists(name=data.name)
        if role_exists:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"name": "该角色名已存在"}
            return json(self.res_json)
        # 创建角色
        async with in_transaction() as connection:
            role = await Role.create(name=data.name, description=data.description)
            # 更新角色权限
            await role.update_menu_permissions(data.menu_permissions)
        return json(self.res_json)


class RoleDelView(HTTPMethodView):
    """角色删除视图"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["message"] = "角色删除成功"

    async def post(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, result_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(result_json)
        role_id = request.args.get("role_id")
        if role_id:
            request.form.update({"role_ids": [role_id]})
        # 验证表单
        success, data = RoleDelForm.validate_sanic_form(request)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["callbackType"] = "forwardError"
            self.res_json["errorMsg"] = "表单参数错误"
            return json(self.res_json)
        async with in_transaction() as connection:
            filter_q = [Q(pk=_id) for _id in data.role_ids]
            roles = await Role.filter(Q(*filter_q, join_type="OR")).delete()
            # 清空用户角色缓存
            for role_id in data.role_ids:
                await request.app.ctx.cache_redis.del_cache(f"role_{role_id}_menu_permissions")
        self.res_json["callbackType"] = ""
        return json(self.res_json)


class RoleModifyView(HTTPMethodView):
    """角色修改表单视图"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["statusCode"] = "300"
        self.res_json["message"] = "该角色不存在"

    async def get(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, result_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(result_json)
        # 用户ID验证
        role_id = request.args.get("role_id")
        if role_id is None:
            self.res_json["message"] = "未提供角色ID"
            return json(self.res_json)
        role = await Role.get_or_none(pk=role_id)
        if role is None:
            return json(self.res_json)
        # 获取所有菜单权限
        all_menu_permissions = await MenuPermission.auto_get_all_menu_permissions()
        # 获取角色当前菜单权限
        current_role_menu_permissions = await role.auto_get_menu_permissions()
        temp_ctx = {
            "request": request,
            "role": role,
            "all_menu_permissions": all_menu_permissions,
            "current_role_menu_permissions": current_role_menu_permissions,
        }
        return await jinja2_async_render("admin/role/role_modify_form.html", temp_ctx)

    async def post(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, result_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(result_json)
        # 表单验证
        success, data = RoleModifyForm.validate_sanic_form(request)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = data
            return json(self.res_json)
        # 角色是否存在
        role = await Role.get_or_none(pk=data.role_id)
        if role is None:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"role_id": "该角色不存在"}
            return json(self.res_json)
        # 修改信息与信息最后更改时间
        async with in_transaction() as connection:
            await role.update_from_dict(data.dict(exclude={"menu_permissions"}))
            await role.save()
            # 更新用户角色
            await role.update_menu_permissions(data.menu_permissions)
        self.res_json["statusCode"] = "200"
        self.res_json["message"] = "角色修改成功"
        return json(self.res_json)
