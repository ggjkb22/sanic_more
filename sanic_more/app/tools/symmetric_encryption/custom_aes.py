# Author: Q
# Date:   2023-6-28
# Desc:   AES加密函数

import base64
import asyncio
from Crypto.Cipher import AES
from app.conf import get_config

__all__ = ("aes_encrypt", "aaes_encrypt", "aes_decrypt", "aaes_decrypt")

custom_config = get_config()


class AesCrypt:
    """AES对称加密对象"""

    def __init__(self):
        key = self.add_16(custom_config.CUSTOM_AES_KEY)
        iv = self.add_16(custom_config.CUSTOM_AES_IV)
        self.aes_obj = AES.new(key, AES.MODE_CBC, iv)

    def add_16(self, par: str) -> bytes:
        """填充加密文本"""
        par = par.encode()
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    def aes_encrypt(self, text: str) -> str:
        """AES加密"""
        text = self.add_16(text)
        encrtpt_text = self.aes_obj.encrypt(text)
        return base64.b64encode(encrtpt_text).decode()

    def aes_decrypt(self, encrtpt_text: str) -> str:
        """AES解密"""
        encrtpt_text = base64.b64decode(encrtpt_text.encode())
        decrtpt_text = self.aes_obj.decrypt(encrtpt_text)
        decrtpt_text = decrtpt_text.rstrip(b'\x00')
        return decrtpt_text.decode()


def aes_encrypt(text: str) -> str:
    """AES加密"""
    return AesCrypt().aes_encrypt(text)


async def aaes_encrypt(text: str) -> str:
    """异步化AES加密函数"""
    coro = asyncio.to_thread(aes_encrypt, text)  # 内部使用了functools.partial,可以直接传参
    return await asyncio.create_task(coro)


def aes_decrypt(text: str) -> str:
    """AES解密"""
    return AesCrypt().aes_decrypt(text)


async def aaes_decrypt(text: str) -> str:
    """异步化AES解密函数"""
    coro = asyncio.to_thread(aes_decrypt, text)  # 内部使用了functools.partial,可以直接传参
    return await asyncio.create_task(coro)
