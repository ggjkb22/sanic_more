# Author: Q
# Date:   2023-4-16
# Desc:   Bcrypt

import bcrypt
import asyncio
from app.conf import get_config

__all__ = [
    "hash_psw", "checkout_psw", "ahash_psw", "acheckout_psw"
]

custom_config = get_config()
salt = bcrypt.gensalt(rounds=custom_config.CUSTOM_BCRYPT_ROUNDS)


def hash_psw(psw: str) -> str:
    """对密码进行hash"""
    hashed = bcrypt.hashpw(psw.encode(), salt)
    return hashed.decode()


def checkout_psw(psw: str, hashed_psw: str) -> bool:
    """密码校验"""
    return bcrypt.checkpw(psw.encode(), hashed_psw.encode())


async def ahash_psw(psw: str) -> str:
    """异步化密码hash函数"""
    coro = asyncio.to_thread(hash_psw, psw)  # 内部使用了functools.partial,可以直接传参
    return await asyncio.create_task(coro)


async def acheckout_psw(psw: str, hashed_psw: str) -> bool:
    """异步化密码校验"""
    coro = asyncio.to_thread(checkout_psw, psw=psw, hashed_psw=hashed_psw)
    return await asyncio.create_task(coro)
