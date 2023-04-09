# Author: Q
# Date:   2023-4-8
# Desc:   Pydantic.ValidationError验证异常处理(不好用,停用)

from pydantic import ValidationError
from sanic import Request, json, redirect


async def mtv_verify_error_handler(request: Request, exception: ValidationError):
    """Pydantic验证失败异常处理(不好用,停用)"""
    return redirect(request.app.url_for(request.endpoint, **request.match_info))
