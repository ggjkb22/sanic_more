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
from app.orm import TOrmSerialize
from app.orm.models.auth import User
from app.orm.models.article import Article, Category, Tag, ArticleTag
from app.verify import test as test_schema

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
def testdb():
    """ORM测试"""

    async def inner():
        await Tortoise.init(config=custom_config.CUSTOM_TORTOISE_ORM_CFG)
        # # 事务
        # try:
        #     async with in_transaction() as connect:
        #         # category_1 = await Category.create(name="测试1")
        #         user_1 = await User.create(username="你好世界")
        #         article_1 = await Article.create(title="测试文章11111", author=user_1)
        #         tag_1 = await Tag.create(name="测试标签")
        #         at_1 = await ArticleTag.create(article=article_1, tag=tag_1, test_field="你好呀世界")
        # except Exception as e:
        #     print(e)
        # else:
        #     print("事务成功执行")
        # tag = await Tag.get_or_none(pk=1).prefetch_related("article_tag")
        # if tag is not None:
        #     async for i in tag.article_tag:
        #         i_article = await i.article
        #         print(i_article.title, i.test_field)
        # article = await Article.get_or_none(pk=1)
        # if article is not None:
        #     async for i in article.tags.all():
        #         print(i.name, i.article_tag.test_field)
        # async with in_transaction():
        #     category = await Category.create(name="初始分类")
        #     for i in range(10):
        #         if i == 0:
        #             parent = await Category.get(pk=1)
        #         else:
        #             parent = await Category.get(name=f"分类{i-1}")
        #         temp_category = await Category.create(name=f"分类{i}", parent_category=parent)
        category = await Category.get_or_none(pk=1).prefetch_related("child_categories").select_related(
            "parent_category")
        # print(category.name)
        # print(category.parent_category)
        # print(await category.child_categories)
        # try:
        # c = test_schema.Catesgory.from_orm(category)
        # except ValidationError as e:
        #     print("解析出错")
        #     pprint(e.errors())
        # else:
        #     print(c)
        # print(Category.__dict__)
        # user = User.get_or_none(pk=1)
        c = TOrmSerialize(Category, include=("id", "child_categories"))
        a = await c.from_torm_instance(category)
        print(a)
        category_query_set = Category.filter(pk__lte=2).prefetch_related("child_categories").select_related(
            "parent_category")
        b = await c.from_torm_queryset(category_query_set)
        print(b["__root__"])

    run_async(inner())


from typing import Iterator, Iterable
@cli.command()
def test_pydantic():
    """pydantic测试"""

    async def inner():
        print(dir(test_schema.TestForm))
        for i, v in test_schema.TestForm.__fields__.items():
            # print(v.type_, "**", v.outer_type_, "**", v.field_info, "**")
            print(i, v.type_)

    asyncio.run(inner())


if __name__ == "__main__":
    cli()
