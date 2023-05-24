# Author: Q
# Date:   2023-4-5
# Desc:   tortoise-orm通过pydantic进行序列化

from typing import TypeVar, Type, Dict, Union, Tuple, Optional
from tortoise.contrib.pydantic.creator import pydantic_model_creator, pydantic_queryset_creator
from tortoise.queryset import QuerySet

__all__ = ("t_instance_serialize", "t_queryset_serialize")

TModel = TypeVar('TModel', bound='Model')


async def t_instance_serialize(t_model: Type['TModel'], instance: TModel, *, name: Optional[str] = None,
                               exclude: Tuple[str, ...] = (), include: Tuple[str, ...] = (),
                               computed: Tuple[str, ...] = (), allow_cycles: bool = False,
                               max_recursion: Optional[int] = None, return_type: str = "dict") -> Union[Dict, str]:
    """
    序列化ORM实例的工厂函数
    存在的问题:
        在修改数据模型中的PydanticMeta类时, 有可能出现竞态问题
    """
    # 修改数据模型中的PydanticMeta类
    if not hasattr(t_model, "PydanticMeta"):
        # 新建一个类,防止竞态条件问题
        PydanticMeta = type("PydanticMeta", (object,), {})
        setattr(t_model, "PydanticMeta", PydanticMeta)
    t_model.PydanticMeta.include = include
    t_model.PydanticMeta.exclude = exclude
    t_model.PydanticMeta.computed = computed
    t_model.PydanticMeta.allow_cycles = allow_cycles
    if max_recursion:
        t_model.PydanticMeta.max_recursion = max_recursion
    tem_pydantic_model = pydantic_model_creator(t_model, name=name)
    result = await tem_pydantic_model.from_tortoise_orm(instance)
    if return_type == "dict":
        return result.dict()
    return result.json()


async def t_queryset_serialize(t_model: Type['TModel'], queryset: QuerySet, *, name: Optional[str] = None,
                               exclude: Tuple[str, ...] = (), include: Tuple[str, ...] = (),
                               computed: Tuple[str, ...] = (), allow_cycles: bool = False,
                               max_recursion: Optional[int] = None, return_type: str = "dict") -> Union[Dict, str]:
    """
    序列化ORM 的queryset的工厂函数
    存在的问题:
        在修改数据模型中的PydanticMeta类时, 有可能出现竞态问题
    """
    # 修改数据模型中的PydanticMeta类(这么做还是有可能出现竞态问题)
    if not hasattr(t_model, "PydanticMeta"):
        # 新建一个类, 减小竞态条件问题的概率
        PydanticMeta = type("PydanticMeta", (object,), {})
        setattr(t_model, "PydanticMeta", PydanticMeta)
    t_model.PydanticMeta.include = include
    t_model.PydanticMeta.exclude = exclude
    t_model.PydanticMeta.computed = computed
    t_model.PydanticMeta.allow_cycles = allow_cycles
    if max_recursion:
        t_model.PydanticMeta.max_recursion = max_recursion
    tem_pydantic_queryset = pydantic_queryset_creator(t_model, name=name)
    result = await tem_pydantic_queryset.from_queryset(queryset)
    if return_type == "dict":
        return result.dict()["__root__"]
    return result.json()
