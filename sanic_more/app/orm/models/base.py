# Author: Q
# Date:   2023-3-28
# Desc:   sqlalchemy基类模型

from sqlalchemy import INTEGER, Column, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

__all__ = ("Base", "PkBaseModel", "MixinTimeFiled", "MixinViewCountFiled")

# 模型基类
Base = declarative_base()


class PkBaseModel(Base):
    """
    用于继承的主键的抽象类
        1.当表里所有属性都没设置pk时,默认生成一个INTEGER类型 id 的主键
    """
    __abstract__ = True
    id = Column(INTEGER(), primary_key=True, comment="主键")


class MixinTimeFiled:
    """
    用于继承时间的 MixIn
        1.创建时间与修改时间
    """
    create_datetime = Column(DateTime(), default=func.now(), nullable=False, comment="创建时间")
    modify_datetime = Column(DateTime(), default=func.now(), onupdate=func.now(), nullable=False, comment="修改时间")


class MixinViewCountFiled:
    """
    用于继承访问量字段的 MixIn
        1.通过中间件写入redis,再定期写入该数据库字段
    """
    views_total = Column(INTEGER(), default=0, nullable=False, comment="总访问量")
    views_month = Column(INTEGER(), default=0, nullable=False, comment="月访问量")
    views_week = Column(INTEGER(), default=0, nullable=False, comment="周访问量")
    views_today = Column(INTEGER(), default=0, nullable=False, comment="当日访问量")
