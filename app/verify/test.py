from typing import Optional, List, Union, Set, Dict
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator
from pydantic.errors import PydanticValueError
from .form import SanicBaseModel


class Catesgory(BaseModel):
    name: str
    parent_category: Optional["Catesgory"] = Field(default=None)
    child_categories: Union[List["Catesgory"], "Catesgory", None] = Field(default=None)

    class Config:
        orm_mode = True


class Tag(BaseModel):
    name: str
    articles: Union[List["Article"], "Article", None] = Field(default=None)


class Article(BaseModel):
    title: str
    author: "User"


class User(BaseModel):
    username: str
    articles: "Article"


from app.exception.custom_err import XssProtectError


class TestForm(SanicBaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    tests: Optional[List[str]] = Field(None, description="测试多选字段")
    date: Optional[datetime] = Field(None, description="时间")

    # @validator("email", pre=True)
    # def tttt(cls, v):
    #     raise XssProtectError(_hello="你好")
