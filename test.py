# Author: Q
# Date:   2023-4-16
# Desc:   异步队列测试


from app.arq_tasks import arq_redis_settings
from app.tools.password import hash_psw, checkout_psw

async def startup(ctx):
    print("异步队列开始")

async def shutdown(ctx):
    print("异步队列结束")

class WorkerSettings:
    redis_settings = arq_redis_settings
    functions = [hash_psw, checkout_psw]
    on_startup  = startup
    on_shutdown  = shutdown
