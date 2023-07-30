# Author: Q
# Date:   2023-7-25
# Desc:   登录失败锁定策略枚举类

from enum import IntEnum, unique

__all__ = ("LoginFailLockPolicy",)


@unique
class LoginFailLockPolicy(IntEnum):
    """用户登录失败锁定策略"""
    no_lock = 0  # 不锁定
    lock_ip_user = 1  # 锁定IP与用户
    lock_ip = 2  # 锁定IP
