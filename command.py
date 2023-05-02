# Author: Q
# Date:   2023-3-26
# Desc:   数据库命令行文件

import click
import asyncio
from pprint import pprint
from tortoise import Tortoise, run_async
from tortoise.transactions import atomic, in_transaction
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from pydantic import ValidationError
from app.conf import get_config
from app.orm import t_instance_serialize, t_queryset_serialize
from app.orm.models.auth import *
from app.verify.form.auth import LoginForm

# 获取应用全局配置
custom_config = get_config()


# 开启SQL输出
# import logging
# logging.basicConfig()
# logging.getLogger('tortoise').setLevel(logging.DEBUG)


@click.group()
def cli():
    """命令行组"""
    pass


@cli.command()
def initdb():
    """初始化数据库"""

    async def inner_init():
        await Tortoise.init(config=custom_config.CUSTOM_TORTOISE_ORM_CFG)
        await Tortoise.generate_schemas()

    run_async(inner_init())
    click.echo("数据库创建成功!")


@cli.command()
def dropdb():
    """删除整个数据库"""
    drop_confirm = click.confirm("该操作会删除整个数据库,是否继续?")
    if not drop_confirm:
        return

    async def inner():
        await Tortoise.init(config=custom_config.CUSTOM_TORTOISE_ORM_CFG)
        await Tortoise._drop_databases()
        click.echo("数据库删除成功")

    run_async(inner())


@cli.command()
def create_amdin():
    """创建初始管理员用户"""
    async def inner():
        user = await User

@cli.command()
def testdb():
    """ORM测试"""

    async def inner():
        # category = await Category.get_or_none(pk=1).prefetch_related("child_categories").select_related(
        #     "parent_category")
        # c = TOrmSerialize(Category, include=("id", "child_categories"))
        # a = await c.from_torm_instance(category)
        # print(a)
        # category_query_set = Category.filter(pk__lte=2).prefetch_related("child_categories").select_related(
        #     "parent_category")
        # b = await c.from_torm_queryset(category_query_set)
        # print(b["__root__"])
        await Tortoise.init(config=custom_config.CUSTOM_TORTOISE_ORM_CFG)
        user = User(username="qrj", description="测试管理员")
        await user.set_psw("hello_qrj")
        await user.save()
        # user = await User.get_or_none(pk=1)
        # res = await t_instance_serialize(User, user, exclude=("hashed_psw",))
        # res = await t_queryset_serialize(User, User.all(), exclude=("hashed_psw", ))
        # print(res)
    run_async(inner())


if __name__ == "__main__":
    cli()
