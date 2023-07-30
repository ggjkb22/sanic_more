# Author: Q
# Date:   2023-5-3
# Desc:   缓存便捷使用器

import ujson
from typing import Optional, Tuple, Callable, Union


class CacheRedis:
    """缓存系统"""

    def __init__(self, redis_connect_pool):
        """
        :params
            redis_connect_pool: Redis连接池对象
        """
        self.redis = redis_connect_pool

    async def _get_data(self, key: str) -> Optional[bytes]:
        """从缓存中读取
        :params
            key: redis键
        """
        return await self.redis.get(key)

    async def _set_data(self, key: str, data: str, expiry: Optional[int] = None):
        """写入缓存
        :params
            key: redis键
            data: 需写入的数据
            expiry: 过期时间
        """
        if expiry:
            await self.redis.setex(key, expiry, data)
            return
        await self.redis.set(key, data)

    async def del_cache(self, key: str):
        """删除缓存
        :params
            key: redis键
        """
        await self.redis.delete(key)

    async def _auto_cache(self, key: str):
        """
        自动存取缓存(生成器)
        先从缓存中读取数据, 读不到的数据再去sql中拿, 拿到后存入缓存中
        传入data则会从sql中更新数据到缓存中
        :params
            key: redis键
        """
        data = yield await self._get_data(key)
        if isinstance(data, str):
            await self._set_data(key, data)
        elif isinstance(data, tuple):
            data_value, expiry = data
            await self._set_data(key, data_value, expiry=expiry)

    async def auto_cache(self, key: str, return_type: str = "bytes") -> Tuple[Optional[str], Callable]:
        """自动存取缓存(调用生成器)
        :params
            key: redis键
            return_type: 返回的类型(bytes/str/dict)
        """
        _cache_data = self._auto_cache(key)

        async def set_cache_data_inner(set_data: Union[str, Tuple[str, int]]):
            """设置缓存值
            :params
                set_data：传入str类型则调用set, 传入str与expiry(单位:秒)的元组则调用setex
            """
            try:
                await _cache_data.asend(set_data)
            except StopAsyncIteration as e:
                pass

        cache_data = await anext(_cache_data)
        # 当缓存中的值不为None时,根据return_type参数进行返回值类型转换
        if cache_data is not None:
            if return_type == "str":
                cache_data = cache_data.decode()
            elif return_type == "dict":
                cache_data = ujson.loads(cache_data)
        return cache_data, set_cache_data_inner

    async def close(self):
        """关闭redis连接池"""
        await self.redis.close()

    async def flushdb(self):
        """清空redis的当前db"""
        await self.redis.execute_command("flushdb")
