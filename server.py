# Author: Q
# Date:   2023-3-17
# Desc:   Sanic服务入口文件

from app import app, custom_config

if __name__ == "__main__":
    app.run(
        host=custom_config.CUSTOM_HOST,
        port=custom_config.CUSTOM_PORT,
        debug=custom_config.CUSTOM_DEBUG,
        access_log=custom_config.ACCESS_LOG,
        auto_reload=custom_config.AUTO_RELOAD,
        fast=True,
    )
