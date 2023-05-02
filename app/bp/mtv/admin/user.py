# Author: Q
# Date:   2023-4-8
# Desc:   后台视图函数


from sanic import Request, json, html
from sanic.views import HTTPMethodView
from tortoise.expressions import Q
from app.tools.template import jinja2_async_render
from app.tools.state_check.login_state import login_check
from app.orm.models.auth import User
from app.orm import t_queryset_serialize, t_instance_serialize
from app.verify.form.admin import *

__all__ = ["UserTableView", "UserAddView", "UserDelView", "UserModifyView", "UserInfoModifyView", "UserPswModifyView", "UserPswAdminModifyView"]

class UserTableView(HTTPMethodView):
    """用户列表视图"""

    async def get(self, request: Request):
        # 登录状态验证
        await login_check(request)
        users = User.all()
        user_total = await users.count()
        res = await t_queryset_serialize(User, users, exclude=("hashed_psw",))
        temp_ctx = {
            "request": request,
            "users": res,
            "user_total": user_total,
        }
        return await jinja2_async_render("admin/user/user_table.html", temp_ctx)


class UserAddView(HTTPMethodView):
    """添加用户视图"""
    def __init__(self):
        self.res_json = {
            "statusCode": "200",
            "message": "用户添加成功",
            "navTabId": "admin_user_table",
            "reloadMethod": "get",
            "rel": "",
            "callbackType": "closeCurrent",
            "forwardUrl": "",
            "confirmMsg": ""
        }

    async def get(self, request: Request):
        # 登录状态验证
        await login_check(request)
        temp_ctx = {
            "request": request,
        }
        return await jinja2_async_render("admin/user/user_add_form.html", temp_ctx)

    async def post(self, request: Request):
        # 登录状态验证
        await login_check(request)
        # 验证表单
        success, data = UserAddForm.validate_sanic_form(request)
        if not success:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = data
            return json(self.res_json)
        # 验证用户名是否存在
        user_exists = await User.exists(username=data.username)
        if user_exists:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["validateError"] = {"username": "该用户名已存在"}
            return json(self.res_json)
        # 创建用户
        user = User(username=data.username, description=data.description, can_use=data.can_use)
        await user.set_psw(data.password)
        await user.save()
        return json(self.res_json)


class UserDelView(HTTPMethodView):
    """用户删除视图"""
    def __init__(self):
        self.res_json = {
            "statusCode": "200",
            "message": "用户删除成功",
            "navTabId": "admin_user_table",
            "reloadMethod": "get",
            "rel": "",
            "callbackType": "",
            "forwardUrl": "",
            "confirmMsg": "",
            "errorMsg": ""
        }

    async def post(self, request: Request):
        # 登录状态验证
        current_user = await login_check(request)
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
        if current_user in data.user_ids:
            self.res_json["statusCode"] = "406"
            self.res_json["message"] = "表单验证失败"
            self.res_json["callbackType"] = "forwardError"
            self.res_json["errorMsg"] = "不能删除当前登录的用户"
            return json(self.res_json)
        filter_q = [Q(pk=_id) for _id in data.user_ids]
        users = await User.filter(Q(*filter_q, join_type="OR")).delete()
        return json(self.res_json)
    

class UserModifyView(HTTPMethodView):
    """用户修改表单视图"""
    async def get(self, request: Request):
        # 登录状态验证
        await login_check(request)
        # 用户ID验证
        user_id = request.args.get("user_id")
        if user_id is None:
            return html("<h1 style=\"font-size:20px;\">未提供用户ID</h1>")
        user = await User.get_or_none(pk=user_id)
        if user is None:
            return html("<h1 style=\"font-size:20px;\">该用户不存在</h1>")
        temp_ctx = {
            "request": request,
            "user": user,
        }
        return await jinja2_async_render("admin/user/user_modify_form.html", temp_ctx)
    

class UserInfoModifyView(HTTPMethodView):
    """用户信息修改视图(用户自身使用)"""
    async def post(self, request: Request):
        # 登录状态验证
        await login_check(request)


class UserPswModifyView(HTTPMethodView):
    """用户密码修改视图(用户自身使用)"""
    pass


class UserPswAdminModifyView(HTTPMethodView):
    """用户密码修改视图(管理员使用)"""
    pass