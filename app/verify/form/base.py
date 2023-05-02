# Author: Q
# Date:   2023-4-4
# Desc:   表单验证

from typing import TypeVar, Type, Tuple, List, Union, Dict, Any
from copy import deepcopy
from pydantic import BaseModel, ValidationError
from sanic.request import Request
from app.tools.csrf_protect import validate_csrf_token

# 泛型, 用于注解, 表示SanicFormBaseModel类(Type[ValidateModel])或它的实例ValidateModel
ValidateModel = TypeVar("ValidateModel", bound="SanicFormBaseModel")


class SanicFormBaseModel(BaseModel):
    """可用于解析sanic表单的pydantic基础类
    1. 子类编写字段时,请务必使用Field的description进行备注。
    """
    @classmethod
    def validate_sanic_form(cls: Type[ValidateModel], request: Request) -> Tuple[bool, Union[ValidateModel, Dict[str, str]]]:
        """解析sanic的form"""
        # 验证csrf_token
        validate_csrf_token(request)
        sanic_form = request.form
        try:
            result = cls(**sanic_form)
        except ValidationError as e:
            temp_form = deepcopy(sanic_form)
            for err in e.errors():
                if err["type"].startswith("type_error"):
                    tmp_err_field = err["loc"][0]
                    temp_form[tmp_err_field] = sanic_form.get(tmp_err_field)
            try:
                again_result = cls(**temp_form)
            except ValidationError as again_e:
                err_res = {}
                properties = cls.schema()["properties"]
                for err in again_e.errors():
                    tmp_err_field = err["loc"][0]
                    err_res[tmp_err_field] = f"{properties[tmp_err_field]['description']}{err['msg']}"
                return False, err_res
            else:
                return True, again_result 
        else:
            return True, result

    class Config:
        error_msg_templates = {
            "value_error.email": "无效的邮箱地址",
            "value_error.missing": "为必填字段",
            "type_error.bool": "值无法解析为布尔值",
            "value_error.any_str.min_length": "长度不能小于 {limit_value} 个字符",
            "value_error.any_str.max_length": "长度不能大于 {limit_value} 个字符",
            "none.not_allowed": "None是不允许的值",
            "none.allowed": "值不是none",
            "not_none": "值不是none",
            "list.min_items": "长度不能小于{limit_value}",
            "list.max_items": "长度不能大于{limit_value}",
            "tuple.length": "错误的元组长度{actual_length}, 期望长度为 {expected_length}",
            "type_error.deque": "不是一个有效的deque",
            "type_error.frozenset": "不是一个有效的frozenset",
            "type_error.tuple": "不是一个有效的tuple",
            "type_error.set": "不是一个有效的set",
            "type_error.list": "不是一个有效的list",
            "type_error.iterable": "不是一个有效的iterable",
            "type_error.sequence": "不是一个有效的sequence",
            "type_error.pyobject": "请确保此值包含有效的导入路径或有效的可调用对象:{error_message}",
            "path.not_a_directory": "该路径不是一个目录: '{path}'",
            "path.not_a_file": "该路径不是一个文件: '{path}'",
        }
