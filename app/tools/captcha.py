# Author: Q
# Date:   2023-4-12
# Desc:   图形验证码生成

import random
import io
import base64
import string
import asyncio
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
from app.conf import get_config

custom_config = get_config()


class GenerateCaptcha:
    """图形验证码生成类"""

    def __init__(self, width: int = custom_config.CUSTOM_CAPTCHA_WIDTH,
                 height: int = custom_config.CUSTOM_CAPTCHA_HEIGHT, length: int = custom_config.CUSTOM_CAPTCHA_LENGTH,
                 font: str = custom_config.CUSTOM_CAPTCHA_FONT):
        self.width = width
        self.height = height
        self.length = length
        self.font = font
        self.char_list = string.ascii_uppercase + string.digits

    def _generate_char(self) -> str:
        """生成随机字符"""
        self.char_res = ''.join(random.sample(self.char_list, self.length))

    def _random_point(self) -> Tuple[int, int]:
        """生成随机点"""
        return random.randint(1, self.width - 1), random.randint(1, self.width - 1)

    @staticmethod
    def _random_color() -> Tuple[int, int, int]:
        """生成随机颜色"""
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def _generate_image(self) -> None:
        font = ImageFont.truetype(self.font, 40)
        self.image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        draw = ImageDraw.Draw(self.image)
        self._generate_char()
        # 向画布上填写验证码
        for i in range(self.length):
            draw.text((40 * i + 10, 10), self.char_res[i], font=font, fill=self._random_color())
        # 向画布上填填充噪点
        for x in range(random.randint(200, 600)):
            draw.point(self._random_point(), fill=(0, 0, 0))

    def to_base64(self) -> Tuple[str, bytes]:
        self._generate_image()
        buffered = io.BytesIO()
        self.image.save(buffered, format="PNG")
        bs64_str = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
        return self.char_res, bs64_str


def get_captcha_base64() -> Tuple[str, bytes]:
    """生成图形验证码base64的工厂函数"""
    return GenerateCaptcha().to_base64()


async def aget_captcha_base64() -> Tuple[str, bytes]:
    """异步化生成图形验证码base64的工厂函数"""
    coro = asyncio.to_thread(get_captcha_base64)
    return await asyncio.create_task(coro)

