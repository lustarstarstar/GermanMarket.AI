# -*- coding: utf-8 -*-
"""
数据库连接管理
==============
支持同步和异步两种模式，适配FastAPI
"""

from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from .config import settings


# 创建基类
Base = declarative_base()

# ============ 同步引擎 (用于脚本/迁移) ============
sync_engine = create_engine(
    settings.db.url,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
    pool_timeout=settings.db.pool_timeout,
    pool_pre_ping=True,  # 自动检测连接有效性
    echo=settings.debug
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)


# ============ 异步引擎 (用于FastAPI) ============
async_engine = create_async_engine(
    settings.db.async_url,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
    pool_timeout=settings.db.pool_timeout,
    pool_pre_ping=True,
    echo=settings.debug
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


# ============ 依赖注入 ============

@contextmanager
def get_sync_db() -> Generator[Session, None, None]:
    """同步数据库会话（用于脚本）"""
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """异步数据库会话（用于FastAPI依赖注入）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ============ 初始化函数 ============

def init_db():
    """初始化数据库表（同步）"""
    Base.metadata.create_all(bind=sync_engine)
    print("✓ 数据库表已创建")


async def init_async_db():
    """初始化数据库表（异步）"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ 数据库表已创建（异步）")

