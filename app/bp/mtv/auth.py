# Author: Q
# Date:   2023-4-8
# Desc:   用户认证蓝图

from typing import Dict, Any
from datetime import datetime
from sanic import Blueprint, Request, json, redirect
from sanic.views import HTTPMethodView
from app.tools.template import jinja2_async_render
from app.tools.captcha import aget_captcha_base64
from app.tools.csrf_protect import generate_csrf_token
from app.verify.form.auth import LoginForm
from app.orm.models.auth import User
from app.tools.state_check.login_state import logout_check, login_check
from app.tools.state_check.login_failed_lock import LoginFailedLock

auth_bp = Blueprint("auth", url_prefix="/auth")


class LoginView(HTTPMethodView):
    """用户登录视图"""

    async def _get_method_ctx(self, request: Request) -> Dict[str, Any]:
        """获取共同的模板上下文"""
        # 生成验证码,并将验证码答案与session绑定
        request.ctx.session["captcha_str"], bs64_str = await aget_captcha_base64()
        temp_ctx = {
            "request": request,
            "captcha_bs64": bs64_str,
        }
        return temp_ctx

    async def get(self, request: Request):
        """获取登录表单页面"""
        # 登出状态检查
        await logout_check(request)
        temp_ctx = await self._get_method_ctx(request=request)
        response = await jinja2_async_render("admin/login.html", temp_ctx)
        # 生成并向session中注入csrf_token
        response = generate_csrf_token(request, response)
        return response

    async def post(self, request: Request):
        """验证登录表单"""
        # 登出状态检查
        await logout_check(request)
        # 验证表单
        res, data = LoginForm.validate_sanic_form(request)
        if not res or data.captcha.lower() != request.ctx.session["captcha_str"].lower():
            temp_ctx = await self._get_method_ctx(request=request)
            error_msg = tuple(data.values())[0] if not res else "验证码错误"
            temp_ctx.update({"error": error_msg, "username": request.form.get("username"),
                             "password": request.form.get("password")})
            return await jinja2_async_render("admin/login.html", temp_ctx)
        else:
            # 用户登录失败锁定验证
            login_failed = await LoginFailedLock.auto_init(request, data.username)
            if login_failed:
                # 如果已开启锁定策略, 则进行锁定验证
                has_lock, err_msg = await login_failed.validate_lock()
                if has_lock:
                    # 如果已被锁定, 则返回错误信息
                    temp_ctx = await self._get_method_ctx(request=request)
                    temp_ctx.update({"error": err_msg, "username": data.username, "password": data.password})
                    return await jinja2_async_render("admin/login.html", temp_ctx)
            user = await User.get_or_none(username=data.username)
            if user is None or not (await user.check_psw(data.password)):
                temp_ctx = await self._get_method_ctx(request=request)
                # 用户登录失败锁定缓存更新
                if login_failed:
                    # 如果已开启锁定策略, 则进行锁定验证缓存更新
                    lock_msg = await login_failed.update_lock_num()
                    temp_ctx.update(
                        {"error": "用户名或密码错误，" + lock_msg, "username": data.username, "password": data.password})
                else:
                    temp_ctx.update({"error": "用户名或密码错误", "username": data.username, "password": data.password})
                return await jinja2_async_render("admin/login.html", temp_ctx)
            else:
                # 如果用户不可用则不允许登录
                if not user.can_use:
                    temp_ctx = await self._get_method_ctx(request=request)
                    temp_ctx.update({"error": "该用户已被禁用，请联系管理员启用"})
                    return await jinja2_async_render("admin/login.html", temp_ctx)
                # 如果账号密码验证成功,则将当前用户ID写入session
                request.ctx.session[request.app.config.CUSTOM_SESSION_CURRENT_USER] = user.pk
                # 用户登录失败锁定缓存更新
                if login_failed:
                    await login_failed.delete_lock_num()
                real_ip = request.remote_addr if request.remote_addr else request.ip
                user.last_login_ip = real_ip
                user.last_login_dt = datetime.now()
                await user.save()
                return redirect(request.url_for("admin.index"))


class LogoutView(HTTPMethodView):
    """用户登出视图"""

    async def get(self, request: Request):
        # 登录状态验证
        await login_check(request)
        # 删除session中的current_user
        del request.ctx.session[request.app.config.CUSTOM_SESSION_CURRENT_USER]
        return redirect(request.url_for(request.app.config.CUSTOM_MTV_LOGIN_POINT))


class CaptchaView(HTTPMethodView):
    """验证码生成视图"""

    async def get(self, request: Request):
        request.ctx.session["captcha_str"], bs64_str = await aget_captcha_base64()
        result = {
            "code": 200,
            "message": "请求成功",
            "data": {
                "captcha_bs64": bs64_str,
            },
        }
        return json(result)


# 注册路由
auth_bp.add_route(LoginView.as_view(), "/login", name="login")
auth_bp.add_route(LogoutView.as_view(), "/logout", name="logout")
auth_bp.add_route(CaptchaView.as_view(), "/captcha", name="captcha")
