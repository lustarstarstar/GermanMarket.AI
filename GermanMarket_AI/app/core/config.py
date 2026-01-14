# -*- coding: utf-8 -*-
"""
GermanMarket.AI 核心配置
========================
支持多环境配置，MySQL云数据库连接，API密钥管理
"""

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()


class DatabaseConfig(BaseSettings):
    """MySQL数据库配置 - 支持云端访问"""
    
    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=3306, alias="DB_PORT")
    user: str = Field(default="root", alias="DB_USER")
    password: str = Field(default="", alias="DB_PASSWORD")
    database: str = Field(default="german_market_ai", alias="DB_NAME")
    
    # 连接池配置
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)
    pool_timeout: int = Field(default=30)
    
    @property
    def url(self) -> str:
        """SQLAlchemy连接URL"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset=utf8mb4"
    
    @property
    def async_url(self) -> str:
        """异步连接URL"""
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset=utf8mb4"


class NLPConfig(BaseSettings):
    """NLP模型配置"""
    
    # 德语情感分析
    sentiment_model: str = Field(default="oliverguhr/german-sentiment-bert")
    
    # 翻译模型
    translation_de_zh: str = Field(default="Helsinki-NLP/opus-mt-de-zh")
    translation_de_en: str = Field(default="Helsinki-NLP/opus-mt-de-en")
    
    # LLM API (用于文案生成)
    llm_provider: str = Field(default="deepseek", description="deepseek/openai/claude")
    deepseek_api_key: Optional[str] = Field(default=None, alias="DEEPSEEK_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    claude_api_key: Optional[str] = Field(default=None, alias="CLAUDE_API_KEY")
    
    # 推理配置
    device: str = Field(default="auto")
    batch_size: int = Field(default=16)
    max_length: int = Field(default=512)
    cache_dir: Path = Field(default=PROJECT_ROOT / "cache" / "models")


class AppSettings(BaseSettings):
    """应用全局配置"""
    
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # 基础配置
    app_name: str = "GermanMarket.AI"
    version: str = "0.1.0"
    env: str = Field(default="dev", alias="ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # 子配置
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    nlp: NLPConfig = Field(default_factory=NLPConfig)
    
    # ========== 运营可调整的阈值 ==========
    # 情感分析阈值
    threshold_positive: float = 0.6  # 高于此值 = 好评
    threshold_negative: float = 0.4  # 低于此值 = 差评

    # 维度分析阈值
    aspect_good: float = 0.7    # 维度得分高于此值 = 优秀
    aspect_bad: float = 0.4     # 维度得分低于此值 = 需改进
    aspect_min_count: int = 3   # 维度至少被提及N次才统计

    # 报告警告阈值
    alert_neg_rate: float = 0.4   # 差评率超过此值 = 警告
    alert_pos_rate: float = 0.6   # 好评率超过此值 = 优秀

    # ABSA维度映射（德语 -> 中文）
    aspect_map: dict = Field(default={
        "Lieferung": "物流",
        "Qualität": "质量",
        "Aussehen": "外观",
        "Verpackung": "包装",
        "Preis": "价格",
        "Kundenservice": "客服",
        "Funktionalität": "功能性",
        "Material": "材质",
        "Größe": "尺码",
        "Passform": "合身度"
    })


@lru_cache()
def get_settings() -> AppSettings:
    """获取配置单例"""
    return AppSettings()


settings = get_settings()

