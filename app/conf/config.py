# Author: Q
# Date:   2023-3-17
# Desc:   应用配置文件

import os
from typing import Optional, Dict, Union, List, Any
from dotenv import load_dotenv, find_dotenv
from functools import lru_cache
from enum import IntEnum, unique
from sanic.config import Config

# 读取环境变量
load_dotenv(dotenv_path=find_dotenv(), override=True)


@unique
class RedisDbNum(IntEnum):
    """redis数据库db的枚举类"""
    session_db = 0


class BaseConifg(Config):
    """ 基础配置文件
    1. 以CUSTOM开头的配置都是我们自定义的
    """
    CUSTOM_HOST: str = os.getenv("MY_APP_HOST", "127.0.0.1")
    CUSTOM_PORT: int = int(os.getenv("MY_APP_PORT", 8000))
    CUSTOM_DEBUG: bool = True  # 是否开启DEBUG模式
    ACCESS_LOG: bool = True  # 访问日志开关(关闭以获取最佳性能)
    AUTO_RELOAD: bool = True  # 自动重载开关
    AUTO_EXTEND: bool = True  # Sanic 拓展启用开关
    EVENT_AUTOREGISTER: bool = True  # 自动注册信号开关（开启后不存在的事件将会自动注册）
    FALLBACK_ERROR_FORMAT: str = "html"  # 异常的返回格式
    FORWARDED_SECRET: Optional[str] = os.getenv("MY_APP_FORWARDED_SECRET", "abcd_1234")  # 代理的安全码(用于安全地识别特定的代理服务器)
    NOISY_EXCEPTIONS: bool = False  # 强制禁止异常输出
    PROXIES_COUNT: Optional[int] = None  # 应用程序前代理服务器的数量
    REAL_IP_HEADER: Optional[str] = None  # 客户端真实 IP： X-Real-IP
    MOTD: bool = True  # 是否在启动时展示 MOTD 信息
    MOTD_DISPLAY: Dict[str, str] = {}  # 键/值对显示 MOTD 中的附加任意数据
    # Session配置
    CUSTOM_SESSION_EXPIRE_SECOND: int = 1800  # session过期时间,单位秒
    # Redis配置
    CUSTOM_REDIS_URL: str = os.getenv("MY_APP_REDIS_URL", "redis://127.0.0.1")  # redis的url
    CUSTOM_REDIS_PSW: str = os.getenv("MY_APP_REDIS_PSW", "123456")  # redis的password
    CUSTOM_REDIS_PORT: int = int(os.getenv("MY_APP_REDIS_PORT", 6379))
    CUSTOM_REDIS_DB_ENUM: RedisDbNum = RedisDbNum  # redis db的枚举类
    # 模板配置
    CUSTOM_JINJA2_TEM_FORMAT: List = ["html", ]
    CUSTOM_JINJA2_TEM_PATH: str = f"{os.getcwd()}/app/jinja2_templates"
    # 静态文件Path配置
    CUSTOM_STATIC_PATH: str = f"{os.getcwd()}/app/static"
    # Tortoise-ORM 配置
    CUSTOM_ORM_ENGINE: str = "tortoise.backends.mysql"  # ORM引擎
    CUSTOM_ORM_HOST: str = os.getenv("MY_APP_ORM_HOST", "127.0.0.1")
    CUSTOM_ORM_PORT: int = int(os.getenv("MY_APP_ORM_PORT", 3306))
    CUSTOM_ORM_USER: str = os.getenv("MY_APP_ORM_USER", "username")
    CUSTOM_ORM_PSW: str = os.getenv("MY_APP_ORM_PSW", "123456")
    CUSTOM_ORM_DB: str = os.getenv("MY_APP_ORM_DB", "test")
    CUSTOM_ORM_ECHO: bool = True  # 是否打印数据库操作信息
    CUSTOM_TORTOISE_ORM_CFG: Dict[str, Any] = {
        "connections": {
            # 可以配置多个不同的数据库连接(如主从、读写分离等)
            "master": {
                # 当需要配置连接细节时,需要使用如下类型的配置(使用Url只能定义简单的数据库连接)
                "engine": CUSTOM_ORM_ENGINE,
                "credentials": {
                    "host": CUSTOM_ORM_HOST,
                    "port": CUSTOM_ORM_PORT,
                    "user": CUSTOM_ORM_USER,
                    "password": CUSTOM_ORM_PSW,
                    "database": CUSTOM_ORM_DB,
                    "echo": CUSTOM_ORM_ECHO,
                },
            },
        },
        "apps": {
            # 配置模型的相对位置,orm会自动进行查找
            "all_models": {
                "models": ["app.orm.models.auth", "app.orm.models.article"],
                "default_connection": "master",
            },
        },
        # use_tz为False, timezone为Asia/Shanghai时
        # auto_now_add与auto_now参数将插入中国北京时间
        "use_tz": False,
        "timezone": "Asia/Shanghai",
    }


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
