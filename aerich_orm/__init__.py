# Author: Q
# Date:   2023-4-18
# Desc:   数据库迁移

from app.conf.config import get_config

custom_config = get_config()

TORTOISE_ORM_CONF = custom_config.CUSTOM_TORTOISE_ORM_CFG

