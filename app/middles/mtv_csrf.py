# Author: Q
# Date:   2023-3-22
# Desc:   MTV模式下的CSRF防御

from uuid import uuid4
from sanic.request import Request
from app.tools.csrf_protect import MtvCsrfValidateException


async def mtv_csrf_protect(request: Request):
    """已停用
    MTV模式下的CSRF防御
    1. 当一个路由的上下文中携带csrf参数且为True时, 就能开启MTV模式下的csrf防御
    2. 如果请求方法是GET, 则在session中保存一个随机生成的csrf_token
    3. 当请求方法为POST时, 则将表单中的csrf_token与session中的csrf_token进行比对,不相等则返回CSRF验证错误
    """
    # 当请求某个路由失败时(如404),request.route为None,需要先排除掉这种情况
    # 当路由未携带csrf上下文参数的情况也要排除
    if request.route is not None and hasattr(request.route.ctx, "csrf") and request.route.ctx.csrf:
        req_method = request.method
        if req_method == "GET":
            # 虽然生成UUID也是CPU密集型任务,但这个任务很简单,使用to_thread将其挂进线程池反而更慢
            request.ctx.session["csrf_token"] = uuid4().hex
        elif req_method in ["POST", "DELETE", "PUT", "PATCH"]:
            req_form_csrf_token = request.form.get("csrf_token")
            req_session_csrf_token = request.ctx.session.get("csrf_token")
            if req_form_csrf_token is None or req_session_csrf_token is None or req_form_csrf_token != req_session_csrf_token:
                raise MtvCsrfValidateException
