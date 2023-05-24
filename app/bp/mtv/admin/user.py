# Author: Q
# Date:   2023-4-8
# Desc:   后台用户相关视图函数


from datetime import datetime
from sanic import Request, json, html
from sanic.views import HTTPMethodView
from tortoise.expressions import Q
from tortoise.transactions import in_transaction
from app.tools.template import jinja2_async_render
from app.tools.state_check.login_state import login_check
from app.orm.models.auth import User, Role
from app.orm.models.system import SystemSetting
from app.orm import t_queryset_serialize
from app.verify.form.admin import *
from app.tools.state_check.menu_permission_check import dwz_menu_permission_check

__all__ = ("UserMenuView", "UserTableView", "UserAddView", "UserDelView", "UserModifyView", "UserAdminModifyView",
           "UserInfoModifyView", "UserInfoAdminModifyView", "UserPswModifyView", "UserPswAdminModifyView")

# 用于返回给dwz框架用于前端显示的json汇总
res_json = {
    "statusCode": "200",
    "message": "",
    "navTabId": "admin_user_table",
    "reloadMethod": "get",
    "rel": "",
    "callbackType": "closeCurrent",
    "forwardUrl": "",
    "confirmMsg": "",
    "errorMsg": ""
}


class UserMenuView(HTTPMethodView):
    """用户侧边栏菜单视图"""

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
        return await jinja2_async_render("admin/user/user_menu.html", temp_ctx)


class UserTableView(HTTPMethodView):
    """用户列表视图"""

    async def get(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, res_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(res_json)
        users = User.all()
        user_total = await users.count()
        res = await t_queryset_serialize(User, users, exclude=("hashed_psw",), name="UserTableViewGET")
        temp_ctx = {
            "request": request,
            "users": res,
            "user_total": user_total,
        }
        return await jinja2_async_render("admin/user/user_table.html", temp_ctx)


class UserAddView(HTTPMethodView):
    """添加用户视图"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["message"] = "用户添加成功"
        self.res_json["callbackType"] = "closeCurrent"

    async def get(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, res_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(res_json)
        # 获取系统配置
        settings = await SystemSetting.auto_get_settings()
        # 获取所有角色
        roles = await Role.all().values("id", "name")
        temp_ctx = {
            "request": request,
            "min_psw": settings["min_psw_length"],
            "max_psw": settings["max_psw_length"],
            "roles": roles
        }
        return await jinja2_async_render("admin/user/user_add_form.html", temp_ctx)

    async def post(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, res_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(res_json)
        # 验证表单
        success, data = UserAddForm.validate_sanic_form(request)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = data
            return json(self.res_json)
        # 手动验证密码长度
        success, res = await validate_password_length(data.password)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"password": res}
            return json(self.res_json)
        # 验证用户名是否存在
        user_exists = await User.exists(username=data.username)
        if user_exists:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"username": "该用户名已存在"}
            return json(self.res_json)
        # 创建用户
        async with in_transaction() as connection:
            user = User(username=data.username, description=data.description, can_use=data.can_use)
            await user.set_psw(data.password)
            await user.save()
            # 更新用户角色
            await user.update_roles(data.roles)
        return json(self.res_json)


class UserDelView(HTTPMethodView):
    """用户删除视图"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["message"] = "用户删除成功"

    async def post(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, res_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(res_json)
        user_id = request.args.get("user_id")
        if user_id:
            request.form.update({"user_ids": [user_id]})
        # 验证表单
        success, data = UserDelForm.validate_sanic_form(request)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["callbackType"] = "forwardError"
            self.res_json["errorMsg"] = "表单参数错误"
            return json(self.res_json)
        if current_user_id in data.user_ids:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["callbackType"] = "forwardError"
            self.res_json["errorMsg"] = "不能删除当前登录的用户"
            return json(self.res_json)
        async with in_transaction() as connection:
            filter_q = [Q(pk=_id) for _id in data.user_ids]
            users = await User.filter(Q(*filter_q, join_type="OR")).delete()
            # 清空用户角色缓存
            for user_id in data.user_ids:
                await request.app.ctx.cache_redis.del_cache(f"user_{user_id}_roles")
        self.res_json["callbackType"] = ""
        return json(self.res_json)


class UserModifyView(HTTPMethodView):
    """用户修改表单视图(用户自身使用)"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["statusCode"] = "300"
        self.res_json["message"] = "该用户不存在"

    async def get(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        user = await User.get_or_none(pk=current_user_id)
        if user is None:
            return json(self.res_json)
        settings = await SystemSetting.auto_get_settings()
        temp_ctx = {
            "request": request,
            "user": user,
            "min_psw": settings["min_psw_length"],
            "max_psw": settings["max_psw_length"],
        }
        if request.args.get("mode") == "expired":
            return await jinja2_async_render("admin/user/user_psw_expired_modify.html", temp_ctx)
        return await jinja2_async_render("admin/user/user_modify_form.html", temp_ctx)


class UserAdminModifyView(HTTPMethodView):
    """用户修改表单视图(管理员使用)"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["statusCode"] = "300"
        self.res_json["message"] = "该用户不存在"

    async def get(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, res_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(res_json)
        # 用户ID验证
        user_id = request.args.get("user_id")
        if user_id is None:
            self.res_json["message"] = "未提供用户ID"
            return json(self.res_json)
        user = await User.get_or_none(pk=user_id)
        if user is None:
            return json(self.res_json)
        settings = await SystemSetting.auto_get_settings()
        # 获取所有角色
        roles = await Role.all().values("id", "name")
        # 获取用户当前角色
        current_user_roles = await user.auto_get_roles()
        temp_ctx = {
            "request": request,
            "user": user,
            "min_psw": settings["min_psw_length"],
            "max_psw": settings["max_psw_length"],
            "roles": roles,
            "current_user_roles": current_user_roles,
        }
        return await jinja2_async_render("admin/user/user_admin_modify_form.html", temp_ctx)


class UserInfoModifyView(HTTPMethodView):
    """用户信息修改视图(用户自身使用)"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["message"] = "个人信息修改成功"
        self.res_json["callbackType"] = "closeCurrent"

    async def post(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 表单验证
        success, data = UserInfoModifyForm.validate_sanic_form(request)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = data
            return json(self.res_json)
        # 用户是否存在
        user = await User.get_or_none(pk=current_user_id)
        if user is None:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"user_id": "该用户不存在"}
            return json(self.res_json)
        # 修改信息与信息最后更改时间
        async with in_transaction() as connection:
            await user.update_from_dict(data.dict())
            user.info_last_modified_datetime = datetime.now()
            await user.save()
        return json(self.res_json)


class UserInfoAdminModifyView(HTTPMethodView):
    """用户信息修改视图(管理员使用)"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["message"] = "用户信息修改成功"
        self.res_json["callbackType"] = "closeCurrent"

    async def post(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, res_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(res_json)
        # 表单验证
        success, data = UserInfoAdminModifyForm.validate_sanic_form(request)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = data
            return json(self.res_json)
        # 用户是否存在
        user = await User.get_or_none(pk=data.user_id)
        if user is None:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"user_id": "该用户不存在"}
            return json(self.res_json)
        # 修改信息与信息最后更改时间
        async with in_transaction() as connection:
            await user.update_from_dict(data.dict(exclude={"roles"}))
            user.info_last_modified_datetime = datetime.now()
            await user.save()
            # 更新用户角色
            await user.update_roles(data.roles)
        return json(self.res_json)


class UserPswModifyView(HTTPMethodView):
    """用户密码修改视图(用户自身使用)"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["message"] = "密码修改成功"
        self.res_json["callbackType"] = "closeCurrent"

    async def post(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        success, data = UserPswModifyForm.validate_sanic_form(request)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = data
            return json(self.res_json)
        # 手动验证密码长度
        success, res = await validate_password_length(data.new_password)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"new_password": res}
            return json(self.res_json)
        # 用户是否存在
        user = await User.get_or_none(pk=current_user_id)
        if user is None:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"user_id": "该用户不存在"}
            return json(self.res_json)
        # 验证旧密码是否正确
        if not await user.check_psw(data.old_password):
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"old_password": "旧密码错误"}
            return json(self.res_json)
        # 验证新密码与旧密码是否相同
        if data.new_password == data.old_password:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"new_password": "新密码不能与旧密码相同"}
            return json(self.res_json)
        # 修改密码
        await user.set_psw(data.new_password)
        await user.save()
        return json(self.res_json)


class UserPswAdminModifyView(HTTPMethodView):
    """用户密码修改视图(管理员使用)"""

    def __init__(self):
        self.res_json = res_json.copy()
        self.res_json["message"] = "用户密码修改成功"
        self.res_json["callbackType"] = "closeCurrent"

    async def post(self, request: Request):
        # 登录状态验证
        current_user_id = await login_check(request)
        # 用户权限检查
        current_user = await User.get_or_none(pk=current_user_id)
        allow, res_json = await dwz_menu_permission_check(current_user, request.name)
        if not allow:
            return json(res_json)
        success, data = UserPswAdminModifyForm.validate_sanic_form(request)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = data
            return json(self.res_json)
        # 手动验证密码长度
        success, res = await validate_password_length(data.password)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"password": res}
            return json(self.res_json)
        # 用户是否存在
        user = await User.get_or_none(pk=data.user_id)
        if user is None:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"user_id": "该用户不存在"}
            return json(self.res_json)
        # 修改密码
        await user.set_psw(data.password)
        await user.save()
        return json(self.res_json)
