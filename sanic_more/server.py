# Author: Q
# Date:   2023-3-17
# Desc:   Sanic服务入口文件

from app import app

if __name__ == "__main__":
    app.run(
        host=app.config.CUSTOM_HOST,
        port=app.config.CUSTOM_PORT,
        debug=app.config.CUSTOM_DEBUG,
        access_log=app.config.ACCESS_LOG,
        auto_reload=app.config.AUTO_RELOAD,
        fast=True,
    )