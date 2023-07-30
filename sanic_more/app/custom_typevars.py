# Author: Q
# Date:   2023-7-30
# Desc:   自定义泛型


from typing import TypeVar
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Session

__all__ = ("SqlalchemyEngine", "SqlalchemySession")

# 同步与异步的sqlalchemy的Engine的泛型
SqlalchemyEngine = TypeVar("SqlalchemyEngine", Engine, AsyncEngine)
# 同步与异步的sqlalchemy的Session的泛型
SqlalchemySession = TypeVar("SqlalchemySession", Session, AsyncSession)
