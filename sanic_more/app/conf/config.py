# Author: Q
# Date:   2023-3-17
# Desc:   应用配置文件

import os
from typing import Optional, Dict, Union, List, Any, Sequence
from dotenv import load_dotenv, find_dotenv
from functools import lru_cache
from arq.connections import RedisSettings
from sanic.config import Config
from sanic_more.app.custom_enum import *

# 读取环境变量
load_dotenv(dotenv_path=find_dotenv(), override=True)


class BaseConifg(Config):
    """ 基础配置文件
    1. 以CUSTOM开头的配置都是我们自定义的配置
    """
    SERVER_NAME: str = "SanicMore"
    CUSTOM_HOST: str = "0.0.0.0"
    CUSTOM_PORT: int = 59999
    CUSTOM_DEBUG: bool = True  # 是否开启DEBUG模式
    ACCESS_LOG: bool = True  # 访问日志开关(关闭以获取最佳性能)
    AUTO_RELOAD: bool = True  # 自动重载开关
    AUTO_EXTEND: bool = True  # Sanic 拓展启用开关
    EVENT_AUTOREGISTER: bool = True  # 自动注册信号开关（开启后不存在的事件将会自动注册）
    FALLBACK_ERROR_FORMAT: str = "html"  # 异常的返回格式
    FORWARDED_SECRET: Optional[str] = os.getenv("MY_APP_FORWARDED_SECRET", "abcd_1234")  # 代理的安全码(用于安全地识别特定的代理服务器)
    NOISY_EXCEPTIONS: bool = False  # 强制禁止异常输出
    MOTD: bool = True  # 是否在启动时展示 MOTD 信息
    MOTD_DISPLAY: Dict[str, str] = {}  # 键/值对显示 MOTD 中的附加任意数据
    # 响应超时配置(主要用于适配大文件传输时的超时问题)
    RESPONSE_TIMEOUT: int = 200
    # 代理配置
    PROXIES_COUNT: Optional[int] = None  # 应用程序前代理服务器的数量
    REAL_IP_HEADER: Optional[str] = None  # 客户端真实 IP： X-Real-IP
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://127.0.0.2", "http://172.16.34.9"]
    # OpenApi配置
    OAS_UI_DEFAULT = "swagger"  # 访问/docs时, 默认使用swagger
    OAS_UI_REDOC = False  # 关闭redoc
    OAS_UI_SWAGGER = True  # 开启swagger
    # 模板配置
    TEMPLATING_ENABLE_ASYNC: bool = True  # 开启jinja2异步
    TEMPLATING_PATH_TO_TEMPLATES: Union[
        str, os.PathLike, Sequence[Union[str, os.PathLike]]] = f"{os.getcwd()}/app/jinja2_templates"  # 存放模板的路径
    # 静态文件Path配置
    CUSTOM_STATIC_PATH: str = f"{os.getcwd()}/app/static"
    # Session配置
    CUSTOM_SESSION_CURRENT_USER: str = "current_user"  # Session中的当前登录用户标识
    CUSTOM_SESSION_PSW_EXPIRED: str = "psw_expired_current_user"  # Session中的密码过期的当前用户标识
    CUSTOM_SESSION_DEFAULT_MAX_AGE = 30  # 默认的session过期时间(分钟)(可运行时更改)
    # MVC的登录界面与管理界面首页路由端点
    CUSTOM_MVC_LOGIN_POINT: str = "auth.login"
    CUSTOM_MVC_ADMIN_INDEX_POINT: str = "admin.index"
    # 初始管理员用户名与密码
    CUSTOM_DEFAULT_ADMIN_USERNAME: str = os.getenv("MY_APP_DEFAULT_ADMIN_USERNAME", "qrj")
    CUSTOM_DEFAULT_ADMIN_PSW: str = os.getenv("MY_APP_DEFAULT_ADMIN_PSW", "hello_qrj")
    # 系统配置
    CUSTOM_APP_SETTINGS_KEY: str = "custom_app_settings"  # redis中系统配置的键名
    # 用户名密码配置(可运行时更改)
    CUSTOM_DEFAULT_MIN_PSW_LENGTH: int = 8  # 默认最小密码长度
    CUSTOM_DEFAULT_MAX_PSW_LENGTH: int = 16  # 默认最大密码长度
    CUSTOM_DEFAULT_PSW_CHANGE_MAX_AGE: int = 90  # 默认密码使用期限(天)
    # 用户登录失败锁定配置(可运行时更改)
    CUSTOM_DEFAULT_LOGIN_FAILED_LOCK_NUMBER: int = 10  # 默认用户登录失败锁定次数
    CUSTOM_DEFAULT_LOGIN_FAILED_LOCK_MAX_AGE: int = 5  # 用户登录失败锁定时间(分钟)
    # 验证码配置
    CUSTOM_CAPTCHA_WIDTH: int = 180  # 验证码宽度
    CUSTOM_CAPTCHA_HEIGHT: int = 60  # 验证码高度
    CUSTOM_CAPTCHA_LENGTH: int = 4  # 验证码字符个数
    CUSTOM_CAPTCHA_FONT: str = f"{CUSTOM_STATIC_PATH}/fonts/deja.ttf"  # 验证码字体
    # 分页配置(默认)
    CUSTOM_DEFAULT_PAGINATION_OFFSET: int = 0
    CUSTOM_DEFAULT_PAGINATION_LIMIT: int = 15
    CUSTOM_DEFAULT_PAGINATION_MAX_LIMIT: int = 2000
    CUSTOM_DEFAULT_DEFAULT_SORT_KEY: str = "id"  # 默认的排序字段
    # 导出配置
    CUSTOM_DEFAULT_EXPORT_MAX_NUM: int = 200000  # 默认导出的最大数据数量
    # 密码加密配置
    CUSTOM_BCRYPT_ROUNDS: int = 8  # 迭代次数,越大耗时越长(好在python的bcrypt是C库)
    # AES对称加密配置
    CUSTOM_AES_KEY: str = os.getenv("MY_APP_DEFAULT_AES_KEY", "fzxt-aes")
    CUSTOM_AES_IV: str = os.getenv("MY_APP_DEFAULT_AES_IV", "xxzx")
    # 采集程序配置
    CUSTOM_GATHER_PROCESS_DIR_PATH: str = f"{os.getcwd()}/gather_process"
    # 处置程序配置
    CUSTOM_DISPOSE_PROCESS_DIR_PATH: str = f"{os.getcwd()}/dispose_process"
    # Redis配置
    CUSTOM_REDIS_HOST: str = "127.0.0.1"
    CUSTOM_REDIS_URL: str = f"redis://{CUSTOM_REDIS_HOST}"  # redis的url
    CUSTOM_REDIS_PSW: str = os.getenv("MY_APP_REDIS_PSW", "123456")  # redis的password
    CUSTOM_REDIS_PORT: int = 16379
    CUSTOM_REDIS_DB_ENUM: RedisDbNum = RedisDbNum  # redis db的枚举类
    CUSTOM_USE_REDISEARCH: bool = False  # 是否使用redisearch
    # ORM 配置(Sqlalchemy)
    CUSTOM_ORM_SYNC_ENGINE_PREFIX: str = "mysql+pymysql"  # 同步ORM引擎前缀
    CUSTOM_ORM_ASYNC_ENGINE_PREFIX: str = "mysql+aiomysql"  # 异步ORM引擎前缀
    CUSTOM_ORM_HOST: str = "127.0.0.1"
    CUSTOM_ORM_PORT: int = 13306
    CUSTOM_ORM_USER: str = os.getenv("MY_APP_ORM_USER", "username")
    CUSTOM_ORM_PSW: str = os.getenv("MY_APP_ORM_PSW", "123456")
    CUSTOM_ORM_DB: str = "sanic_more"
    CUSTOM_ORM_FUTURE: bool = True  # 是否使用2.0接口
    CUSTOM_ORM_POOL_SIZE: int = 60  # 数据库连接池大小
    CUSTOM_ORM_EXPIRE_ON_COMMIT: bool = False  # sqlalchemy是否在提交后过期
    CUSTOM_ORM_ECHO: bool = True  # 是否打印数据库操作信息
    # arq 异步队列配置
    CUSTOM_USE_ARQ: bool = False  # 是否使用arq
    CUSTOM_ARQ_REDIS_SETTINGS = RedisSettings(host=CUSTOM_REDIS_HOST,
                                              password=CUSTOM_REDIS_PSW,
                                              port=CUSTOM_REDIS_PORT,
                                              database=CUSTOM_REDIS_DB_ENUM.arq_work_db.value)


class DevConfig(BaseConifg):
    """ 开发模式配置文件"""
    pass


class ProConfig(BaseConifg):
    """生产模式配置文件"""
    CUSTOM_DEBUG: bool = False  # 是否开启DEBUG模式
    ACCESS_LOG: bool = False  # 访问日志开关(关闭以获取最佳性能)
    AUTO_RELOAD: bool = False  # 自动重载开关
    MOTD: bool = False  # 是否在启动时展示 MOTD 信息
    CUSTOM_ORM_ECHO: bool = False  # 是否打印数据库操作信息


@lru_cache
def get_config() -> Union[ProConfig, DevConfig]:
    """返回当前模式的配置
    1.除了app,其他地方也会使用得到,因此使用lru_cache进行缓存
    """
    if os.getenv("MY_APP_MODE", "dev") == "dev":
        dev_config = DevConfig()
        return dev_config
    pro_config = ProConfig()
    return pro_config
