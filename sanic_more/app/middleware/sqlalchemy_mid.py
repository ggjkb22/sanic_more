# Author: Q
# Date:   2023-4-16
# Desc:   Sqlalchemy中间件

from sanic import Sanic
from contextvars import ContextVar
from sanic_more.app.tools.get_sqlalchemy_session import auto_get_sqlalchemy_session

__all__ = ("register_sqlalchemy",)


def register_sqlalchemy(app: Sanic):
    """将sqlalchemy的session注册到每一次请求中"""
    # 创建Session对象
    _sessionmaker = auto_get_sqlalchemy_session(instance=False)
    # 创建协程的上下文(用于判断session是否成功注册到请求中)
    _base_model_session_ctx = ContextVar("orm_session")

    @app.middleware("request")
    async def inject_session(request):
        """将session注入到请求中"""
        request.ctx.session = _sessionmaker()
        request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)

    @app.middleware("response")
    async def close_session(request, response):
        """判断session是否成功注册到请求中并将其关闭"""
        if hasattr(request.ctx, "session_ctx_token"):
            _base_model_session_ctx.reset(request.ctx.session_ctx_token)
            await request.ctx.session.close()
