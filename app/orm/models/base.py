# Author: Q
# Date:   2023-3-28
# Desc:   orm基类模型

from tortoise import fields, models


class AbstractPKModel(models.Model):
    """
    用于继承的主键的抽象类
        1.当表里所有属性都没设置pk时,默认生成一个IntField类型 id 的主键
    """
    # 
    id = fields.IntField(pk=True)

    class Meta:
        # 抽象模型，不生成表
        abstract = True


class MixinTimeFiled:
    """
    用于继承时间的 MixIn
        1.创建时间与修改时间
        2.Tortoise的auto_now与auto_now_add参数,插入的是UTC时间
    """
    create_datetime = fields.DatetimeField(auto_now_add=True, description='创建时间')
    modify_datetime = fields.DatetimeField(auto_now=True, description='修改时间')
