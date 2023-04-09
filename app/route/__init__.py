# Author: Q
# Date:   2023-3-22
# Desc:   路由汇总导出


from sanic import Sanic


def register_static_route(app: Sanic):
    """注册应用的静态文件路由"""
    app.static(uri="/static", file_or_directory=app.config.CUSTOM_STATIC_PATH, name="static")
    