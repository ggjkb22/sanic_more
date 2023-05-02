# Author: Q
# Date:   2023-4-19
# Desc:   MTV模式下的CSRF防御

from uuid import uuid4
from sanic.request import Request
from sanic.response import HTTPResponse
from app.exception.csrf_exception import MtvCsrfValidateException


def generate_csrf_token(request: Request, response: HTTPResponse) -> HTTPResponse:
    """生成csrf_token
    服务端存储在session中
    客户端存储在httponly cookie中
    """
    def set_csrf_token(csrf_token):
        # 客户端存储在httponly的cookies中
        response.cookies["csrf_token"] = csrf_token
        response.cookies["csrf_token"]["httponly"] = True
        response.cookies["csrf_token"]["max-age"] = 31536000
    # 如何session中已经存在csrf_token,则直接复用该token
    req_session_csrf_token = request.ctx.session.get("csrf_token")
    if req_session_csrf_token:
        req_csrf_token = request.cookies.get("csrf_token")
        if req_csrf_token and req_csrf_token == req_session_csrf_token:
            return response
        set_csrf_token(req_session_csrf_token)
        return response
    # 否则重新生成并设置token
    csrf_token = uuid4().hex
    # 服务器端存储在session中
    request.ctx.session["csrf_token"] = csrf_token
    set_csrf_token(csrf_token)
    return response


def validate_csrf_token(request: Request):
    """验证csrf_token
    将客户端cookie中的csrf_token与服务器端session中的csrf_token进行比较
    """
    req_csrf_token = request.cookies.get("csrf_token")
    req_session_csrf_token = request.ctx.session.get("csrf_token")
    if req_csrf_token is None or req_session_csrf_token is None or req_csrf_token != req_session_csrf_token:
        raise MtvCsrfValidateException()
