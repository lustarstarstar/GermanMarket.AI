# -*- coding: utf-8 -*-
"""
API请求/响应模型
================
使用Pydantic定义API数据结构
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ============ 评论分析 ============

class ReviewAnalyzeRequest(BaseModel):
    """单条评论分析请求"""
    text: str = Field(..., min_length=1, description="德语评论文本")
    translate: bool = Field(default=True, description="是否翻译为中文")


class ReviewBatchRequest(BaseModel):
    """批量评论分析请求"""
    reviews: List[str] = Field(..., min_items=1, max_items=100)
    translate: bool = Field(default=True)


class ReviewInsightResponse(BaseModel):
    """单条评论分析响应"""
    original: str
    translation: str
    sentiment: str
    score: float
    aspects: Dict[str, float]
    keywords: List[str]


class ReviewReportResponse(BaseModel):
    """批量分析报告响应"""
    total_reviews: int
    analyzed_at: datetime
    sentiment_distribution: Dict[str, int]
    average_score: float
    dimension_scores: Dict[str, dict]
    top_positive_keywords: List[str]
    top_negative_keywords: List[str]
    key_insights: List[str]


# ============ 红人管理 ============

class InfluencerCreateRequest(BaseModel):
    """创建红人请求"""
    name: str = Field(..., min_length=1)
    platform: str = Field(..., pattern="^(instagram|tiktok|youtube)$")
    handle: Optional[str] = None
    profile_url: Optional[str] = None
    email: Optional[str] = None
    followers: Optional[int] = None
    engagement_rate: Optional[float] = None
    niche: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class InfluencerResponse(BaseModel):
    """红人信息响应"""
    id: int
    name: str
    platform: str
    handle: Optional[str]
    followers: Optional[int]
    engagement_rate: Optional[float]
    status: str
    score: Optional[float]
    
    class Config:
        from_attributes = True


class ContactRecordRequest(BaseModel):
    """创建建联记录请求"""
    influencer_id: int
    contact_type: str = Field(default="email", pattern="^(email|dm|comment)$")
    subject: Optional[str] = None
    content: str


# ============ 内容生成 ============

class ContentGenerateRequest(BaseModel):
    """内容生成请求"""
    content_type: str = Field(..., pattern="^(product_desc|ad_copy|outreach_email|social_post)$")
    product_name: str
    product_info: Optional[str] = None
    target_audience: Optional[str] = Field(default="德国消费者")
    tone: Optional[str] = Field(default="professional", description="professional/casual/friendly")
    language: str = Field(default="de", pattern="^(de|en)$")


class ContentResponse(BaseModel):
    """生成内容响应"""
    id: Optional[int] = None
    content_type: str
    content_de: str
    content_zh: Optional[str] = None
    model_used: str


# ============ 通用 ============

class SuccessResponse(BaseModel):
    """通用成功响应"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str
    detail: Optional[str] = None

