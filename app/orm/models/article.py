# Author: Q
# Date:   2023-3-28
# Desc:   用户文章模型(测试)

from tortoise import fields
from .base import AbstractPKModel, MixinTimeFiled


class Category(AbstractPKModel, MixinTimeFiled):
    name = fields.CharField(max_length=30, null=False, index=True, description="文章分类")

    parent_category = fields.ForeignKeyField("all_models.Category", related_name="child_categories", null=True,
                                             description="父分类")
    child_categories: fields.ReverseRelation["Category"]


class Tag(AbstractPKModel, MixinTimeFiled):
    name = fields.CharField(max_length=30, null=False, index=True, description="文章标签")
    articles = fields.ManyToManyField("all_models.Article", related_name="tags", null=True, through="article_tag",
                                      forward_key="article_id", backward_key="tag_id", description="标签下的文章")


class Article(AbstractPKModel, MixinTimeFiled):
    title = fields.CharField(max_length=100, null=False, index=True, description='文章标题')

    author = fields.ForeignKeyField("all_models.User", null=False, on_delete=fields.RESTRICT, related_name="articles",
                                    description="文章作者")

    tags: fields.ManyToManyRelation["Tag"]


class ArticleTag(AbstractPKModel, MixinTimeFiled):
    article = fields.ForeignKeyField("all_models.Article", related_name="article_tag", null=False,
                                     on_delete=fields.CASCADE, description="与文章关联的外键")
    tag = fields.ForeignKeyField("all_models.Tag", related_name="article_tag", null=False, on_delete=fields.CASCADE,
                                 description="与标签关联的外键")
    test_field = fields.CharField(max_length=100, null=False, description="中间表测试字段")

    class Meta:
        table = "article_tag"

