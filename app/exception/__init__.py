# Author: Q
# Date:   2023-3-22
# Desc:   自定义异常类汇总

from typing import Union
from sanic import Sanic, Blueprint
from pydantic import ValidationError
from .csrf_exception import MtvCsrfValidateException
from .verify_exception import mtv_verify_error_handler


def register_mtv_error_handler(app: Union[Sanic, Blueprint]):
    """注册MTV蓝图组全局错误验证处理器"""
    # CSRF 验证错误处理
    # app.error_handler.add(MtvCsrfValidateException, MtvCsrfValidateException.error_handler) # 蓝图组不支持error_handler
    app.exception(MtvCsrfValidateException)(MtvCsrfValidateException.error_handler)

    # Pydantic 验证错误处理(不好用,停用)
    # app.error_handler.add(ValidationError, mtv_verify_error_handler)
