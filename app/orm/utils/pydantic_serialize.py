# Author: Q
# Date:   2023-4-5
# Desc:   tortoise-orm通过pydantic进行序列化

from typing import TypeVar, Type, Dict, Union, Tuple
from copy import deepcopy
from tortoise.contrib.pydantic.creator import pydantic_model_creator, pydantic_queryset_creator, PydanticMeta
from tortoise.models import Model
from tortoise.queryset import QuerySet

TModel = TypeVar('TModel', bound='Model')


class TOrmSerialize:
    """tortoise-orm通过pydantic进行序列化"""

    def __init__(self, t_model: Type['TModel'], *, exclude: Tuple[str, ...] = (), include: Tuple[str, ...] = (),
                 computed: Tuple[str, ...] = ()):
        self.t_model = deepcopy(t_model)
        tem_meta = getattr(self.t_model, "PydanticMeta", PydanticMeta)
        tem_meta.include = include
        tem_meta.exclude = exclude
        tem_meta.computed = computed
        setattr(self.t_model, "PydanticMeta", tem_meta)

    async def from_torm_instance(self, instance: TModel, *, return_type: str = "dict") -> Union[Dict, str]:
        """对一个模型实例进行序列化"""
        self.tem_pydantic_model = pydantic_model_creator(self.t_model)
        result = await self.tem_pydantic_model.from_tortoise_orm(instance)
        if return_type == "dict":
            return result.dict()
        return result.json()

    async def from_torm_queryset(self, queryset: QuerySet, return_type: str = "dict") -> Union[Dict, str]:
        """对一个模型QuerySet进行序列化"""
        self.tem_pydantic_queryset = pydantic_queryset_creator(self.t_model)
        result = await self.tem_pydantic_queryset.from_queryset(queryset)
        if return_type == "dict":
            return result.dict()
        return result.json()


async def t_instance_serialize(t_model: Type['TModel'], instance: TModel, *,
                               exclude: Tuple[str, ...] = (), include: Tuple[str, ...] = (),
                               computed: Tuple[str, ...] = (), return_type: str = "dict") -> Union[Dict, str]:
    """序列化ORM实例的工厂函数"""
    temp_serialize = TOrmSerialize(t_model, exclude=exclude, include=include, computed=computed)
    return await temp_serialize.from_torm_instance(instance, return_type=return_type)


async def t_queryset_serialize(t_model: Type['TModel'], queryset: QuerySet, *,
                               exclude: Tuple[str, ...] = (), include: Tuple[str, ...] = (),
                               computed: Tuple[str, ...] = (), return_type: str = "dict") -> Union[Dict, str]:
    """序列化ORM 的queryset的工厂函数"""
    temp_serialize = TOrmSerialize(t_model, exclude=exclude, include=include, computed=computed)
    res = await temp_serialize.from_torm_queryset(queryset, return_type=return_type)
    if return_type == "dict":
        return res["__root__"]
    return res
