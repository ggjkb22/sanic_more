# Author: Q
# Date:   2023-3-28
# Desc:   用户认证模型(测试)

from tortoise import fields
from .base import AbstractPKModel, MixinTimeFiled


class User(AbstractPKModel, MixinTimeFiled):
    username = fields.CharField(max_length=50, null=False, index=True, description='用户名')

    articles: fields.ReverseRelation["Article"]
