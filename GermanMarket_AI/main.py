# -*- coding: utf-8 -*-
"""
GermanMarket.AI 主应用
======================
FastAPI应用入口
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_async_db
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"🚀 启动 {settings.app_name} v{settings.version}")
    print(f"📊 环境: {settings.env}")
    print(f"🗄️ 数据库: {settings.db.host}:{settings.db.port}/{settings.db.database}")
    
    # 初始化数据库
    try:
        await init_async_db()
    except Exception as e:
        print(f"⚠️ 数据库初始化失败: {e}")
    
    yield
    
    # 关闭时
    print("👋 应用关闭")


# 创建应用
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="德国电商智能分析平台 - 帮中国卖家看懂德国市场",
    lifespan=lifespan
)

# CORS配置（允许前端跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

