# -*- coding: utf-8 -*-
"""
API路由定义
===========
FastAPI路由，提供RESTful接口
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.services.review_analyzer import ReviewAnalyzer
from .schemas import (
    ReviewAnalyzeRequest,
    ReviewBatchRequest,
    ReviewInsightResponse,
    ReviewReportResponse,
    InfluencerCreateRequest,
    InfluencerResponse,
    ContentGenerateRequest,
    ContentResponse,
    SuccessResponse,
    ErrorResponse
)


# 创建路由器
router = APIRouter()

# 全局分析器实例（复用模型）
_analyzer = None

def get_analyzer() -> ReviewAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = ReviewAnalyzer(translate=True)
    return _analyzer


# ============ 评论分析路由 ============

@router.post("/analyze/single", response_model=ReviewInsightResponse, tags=["评论分析"])
async def analyze_single_review(request: ReviewAnalyzeRequest):
    """
    分析单条德语评论
    
    返回情感分析、维度分析、关键词、翻译等完整结果
    """
    analyzer = get_analyzer()
    
    try:
        insight = analyzer.analyze_single(request.text)
        return insight.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/batch", response_model=ReviewReportResponse, tags=["评论分析"])
async def analyze_batch_reviews(request: ReviewBatchRequest):
    """
    批量分析德语评论
    
    返回汇总报告，包含情感分布、维度统计、关键洞察等
    """
    analyzer = get_analyzer()
    
    try:
        report = analyzer.analyze_batch(request.reviews, show_progress=False)
        return {
            "total_reviews": report.total_reviews,
            "analyzed_at": report.analyzed_at,
            "sentiment_distribution": report.sentiment_distribution,
            "average_score": report.average_score,
            "dimension_scores": report.dimension_scores,
            "top_positive_keywords": report.top_positive_keywords,
            "top_negative_keywords": report.top_negative_keywords,
            "key_insights": report.key_insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 红人管理路由 ============

@router.post("/influencers", response_model=InfluencerResponse, tags=["红人管理"])
async def create_influencer(
    request: InfluencerCreateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """创建红人档案"""
    from app.models.schema import Influencer
    
    influencer = Influencer(
        name=request.name,
        platform=request.platform,
        handle=request.handle,
        profile_url=request.profile_url,
        email=request.email,
        followers=request.followers,
        engagement_rate=request.engagement_rate,
        niche=request.niche,
        tags=request.tags,
        notes=request.notes
    )
    
    db.add(influencer)
    await db.commit()
    await db.refresh(influencer)
    
    return influencer


@router.get("/influencers", response_model=List[InfluencerResponse], tags=["红人管理"])
async def list_influencers(
    platform: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db)
):
    """获取红人列表"""
    from sqlalchemy import select
    from app.models.schema import Influencer
    
    query = select(Influencer)
    
    if platform:
        query = query.where(Influencer.platform == platform)
    if status:
        query = query.where(Influencer.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    
    return result.scalars().all()


@router.get("/influencers/{influencer_id}", response_model=InfluencerResponse, tags=["红人管理"])
async def get_influencer(
    influencer_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """获取单个红人详情"""
    from sqlalchemy import select
    from app.models.schema import Influencer
    
    result = await db.execute(
        select(Influencer).where(Influencer.id == influencer_id)
    )
    influencer = result.scalar_one_or_none()
    
    if not influencer:
        raise HTTPException(status_code=404, detail="红人不存在")
    
    return influencer


# ============ 健康检查 ============

@router.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "GermanMarket.AI"}

