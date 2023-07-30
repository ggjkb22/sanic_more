# Author: Q
# Date:   2023-4-16
# Desc:   argon2

import asyncio
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()


def argon2_hash_psw(psw: str) -> str:
    """对密码进行hash"""
    return ph.hash(psw)


def argon2_checkout_psw(hashed_psw: str, psw: str) -> bool:
    """密码校验"""
    try:
        result = ph.verify(hashed_psw, psw)
    except VerifyMismatchError as e:
        return False
    else:
        return result


def argon2_check_hash_need_rehash(hashed_psw: str) -> bool:
    """检查当前hash是否需要重新hash
    主要用于当PasswordHasher对象的参数改变时使用
    """
    if ph.check_needs_rehash(hashed_psw):
        return True
    return False


async def aargon2_hash_psw(psw: str) -> str:
    """异步化对密码进行hash"""
    coro = asyncio.to_thread(argon2_hash_psw, psw)
    return await asyncio.create_task(coro)


async def aargon2_checkout_psw(hashed_psw: str, psw: str) -> bool:
    """异步化密码校验"""
    coro = asyncio.to_thread(argon2_checkout_psw, psw=psw, hashed_psw=hashed_psw)
    return await asyncio.create_task(coro)
