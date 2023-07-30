# Author: Q
# Date:   2023-3-17
# Desc:   Redis DB枚举类

from enum import IntEnum, unique


__all__ = ("RedisDbNum", )

@unique
class RedisDbNum(IntEnum):
    """redis数据库db的枚举类"""
    search_db = 0
    session_db = 1
    cache_db = 2
    gather_process_db = 3
    arq_work_db = 4
