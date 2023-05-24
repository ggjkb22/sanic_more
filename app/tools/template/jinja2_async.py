# Author: Q
# Date:   2023-3-17
# Desc:   异步jinja2模板装饰器

from typing import List, Dict, Any, TypeVar, Optional
from functools import wraps, lru_cache
from jinja2 import Environment, select_autoescape, FileSystemLoader
from sanic.response import html
from app.conf import get_config

__all__ = [
    "AsyncJinja2",
]

# 加载应用配置
custom_config = get_config()

HttpRes = TypeVar("HttpRes", bound="HTTPResponse")


class AsyncJinja2:
    """异步jinja2"""

    def __init__(self,
                 jinja2_tem_path: str = custom_config.CUSTOM_JINJA2_TEM_PATH,
                 jinja2_tem_format: List[str] = custom_config.CUSTOM_JINJA2_TEM_FORMAT
                 ):
        """
        @params
        :jinja2_tem_path: 模板的位置
        :jinja2_tem_format: 模板的格式
        """
        # 获取模板位置与模板格式
        self.jinja2_tem_path = jinja2_tem_path
        self.jinja2_tem_format = jinja2_tem_format
        # 从指定的文件系统目录中加载模板
        self.loader = FileSystemLoader(self.jinja2_tem_path)
        # 配置
        self.env = Environment(
            loader=self.loader,
            autoescape=select_autoescape(self.jinja2_tem_format),
            enable_async=True
        )

    # 异步渲染函数
    async def async_render(self, relative_path: str, ctx: Dict[str, Any] = {}, status: int = 200,
                           headers: Optional[Dict[str, str]] = None) -> HttpRes:
        """异步渲染模板
        @params
        :relative_path: 模板文件的相对于jinja2_tem_path的位置
        :ctx: 模板上下文
        """
        template = self.env.get_template(relative_path)  # 获取模板文件位置
        return html(await template.render_async(ctx), status=status, headers=headers)

    # 视图模板装饰器
    def template(self, template_name: str, status: int = 200, headers: Optional[Dict[str, str]] = None):
        def wrapper(func):
            @wraps(func)
            async def inner(request, *args, **kwargs):
                template = self.env.get_template(template_name)  # 获取模板
                content = await func(request, *args, **kwargs)  # 获取视图返回值
                return html(await template.render_async(content), status=status, headers=headers)

            return inner

        return wrapper

    # 类视图模板装饰器
    def cls_template(self, template_name: str, status: int = 200, headers: Optional[Dict[str, str]] = None):
        def wrapper(func):
            @wraps(func)
            async def inner(inner_self_or_cls, request, *args, **kwargs):
                template = self.env.get_template(template_name)  # 获取模板
                content = await func(inner_self_or_cls, request, *args, **kwargs)  # 获取视图返回值
                return html(await template.render_async(content), status=status, headers=headers)

            return inner

        return wrapper


@lru_cache
def get_async_jinja2():
    """返回jinja2异步模板实例"""
    return AsyncJinja2()


# 将异步渲染函数赋值给一个变量直接调用
jinja2_async_render = get_async_jinja2().async_render
