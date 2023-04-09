# Author: Q
# Date:   2023-4-4
# Desc:   表单验证

from typing import TypeVar, Type, Tuple, List, Union
from copy import deepcopy
from pydantic import BaseModel, ValidationError
from sanic.request import RequestParameters

# 用于注解,表示FormBaseModel类或其实例
ValidateModel = TypeVar("ValidateModel", bound="SanicBaseModel")


class SanicBaseModel(BaseModel):
    """可用于解析sanic表单的pydantic基础类"""
    @classmethod
    def validate_sanic_form(cls: Type[ValidateModel], sanic_form: RequestParameters) -> Tuple[bool, Union[ValidateModel, List]]:
        """解析sanic的form"""
        temp_form = deepcopy(sanic_form)
        try:
            result = cls(**sanic_form)
        except ValidationError as e:
            for err in e.errors():
                if err["type"].startswith("type_error"):
                    temp_form[err["loc"][0]] = sanic_form.get(err["loc"][0])
            try:
                again_result = cls(**temp_form)
            except ValidationError as again_e:
                err_res = {}
                for err in again_e.errors():
                    err_res[err["loc"][0]] = err["msg"]
                return False, err_res
            else:
                return True, again_result 
        else:
            return True, result

    class Config:
        error_msg_templates = {
            "value_error.email": "无效的邮箱地址"
        }
