# Author: Q
# Date:   2023-4-16
# Desc:   异步队列测试


from app.conf import get_config
from app.tools.password.psw_bcrypt import ahash_psw, acheckout_psw


async def startup(ctx):
    print("异步队列开始")


async def shutdown(ctx):
    print("异步队列结束")


class WorkerSettings:
    redis_settings = get_config().CUSTOM_ARQ_REDIS_SETTINGS
    functions = [ahash_psw, acheckout_psw]
    on_startup = startup
    on_shutdown = shutdown
