# -*- coding: utf-8 -*-
"""
红人评估器 (Influencer Evaluator)
================================
算法化评估红人价值：活跃度、粉丝真实性、类目相关度
特别针对德国市场关键词过滤
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import re


class Platform(Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


@dataclass
class InfluencerProfile:
    """红人基础数据（从HTML/API解析后的结构化数据）"""
    platform: Platform
    username: str
    followers: int
    following: int
    posts_count: int
    
    # 近期互动数据（最近10-20条帖子的平均值）
    avg_likes: float = 0
    avg_comments: float = 0
    avg_views: float = 0  # 视频平台
    
    # 内容数据
    bio: str = ""
    recent_captions: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    
    # 时间数据
    recent_post_dates: List[datetime] = field(default_factory=list)
    
    # 原始数据（用于调试）
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """评估结果"""
    username: str
    platform: str
    
    # 三大核心指标 (0-100分)
    activity_score: float        # 活跃度
    authenticity_score: float    # 粉丝真实性
    relevance_score: float       # 类目相关度
    
    # 综合得分
    total_score: float
    grade: str  # S/A/B/C/D
    
    # 详细分析
    activity_details: Dict[str, Any] = field(default_factory=dict)
    authenticity_details: Dict[str, Any] = field(default_factory=dict)
    relevance_details: Dict[str, Any] = field(default_factory=dict)
    
    # 德国市场特征
    german_market_fit: Dict[str, Any] = field(default_factory=dict)
    
    # 建议
    recommendation: str = ""
    risk_flags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "platform": self.platform,
            "scores": {
                "activity": round(self.activity_score, 1),
                "authenticity": round(self.authenticity_score, 1),
                "relevance": round(self.relevance_score, 1),
                "total": round(self.total_score, 1),
                "grade": self.grade
            },
            "german_market_fit": self.german_market_fit,
            "recommendation": self.recommendation,
            "risk_flags": self.risk_flags
        }


# ============ 德国市场关键词配置 ============

# 德国消费者高度关注的价值观关键词
GERMAN_VALUE_KEYWORDS = {
    # 可持续性 (Nachhaltigkeit) - 德国消费者核心关注点
    "sustainability": {
        "de": ["nachhaltig", "nachhaltigkeit", "umweltfreundlich", "öko", "bio", 
               "klimaneutral", "recycling", "plastikfrei", "fair trade", "grün"],
        "en": ["sustainable", "eco", "green", "organic", "climate"],
        "weight": 1.5  # 权重加成
    },
    # 可靠性/质量 (Zuverlässigkeit/Qualität)
    "reliability": {
        "de": ["qualität", "zuverlässig", "hochwertig", "langlebig", "robust",
               "made in germany", "deutsche qualität", "präzision", "sorgfalt"],
        "en": ["quality", "reliable", "durable", "premium"],
        "weight": 1.3
    },
    # 性价比 (Preis-Leistung)
    "value": {
        "de": ["preis-leistung", "günstig", "sparen", "angebot", "rabatt", "deal"],
        "en": ["value", "affordable", "deal", "discount"],
        "weight": 1.0
    },
    # 测评/诚实 (Ehrlichkeit)
    "honesty": {
        "de": ["ehrlich", "test", "erfahrung", "meinung", "review", "bewertung",
               "unboxing", "vergleich"],
        "en": ["honest", "review", "test", "opinion", "comparison"],
        "weight": 1.2
    }
}

# 垂类关键词（可扩展）
NICHE_KEYWORDS = {
    "fashion": {
        "de": ["mode", "outfit", "style", "kleidung", "fashion", "look", "trend"],
        "en": ["fashion", "style", "outfit", "ootd", "clothing"]
    },
    "tech": {
        "de": ["technik", "gadget", "smartphone", "computer", "digital", "app"],
        "en": ["tech", "gadget", "smartphone", "digital", "app", "software"]
    },
    "beauty": {
        "de": ["beauty", "kosmetik", "makeup", "hautpflege", "skincare", "schönheit"],
        "en": ["beauty", "makeup", "skincare", "cosmetics"]
    },
    "fitness": {
        "de": ["fitness", "sport", "training", "gesundheit", "workout", "gym"],
        "en": ["fitness", "workout", "gym", "health", "training"]
    },
    "food": {
        "de": ["essen", "kochen", "rezept", "food", "küche", "lecker", "vegan"],
        "en": ["food", "recipe", "cooking", "foodie", "vegan"]
    },
    "home": {
        "de": ["wohnen", "einrichtung", "deko", "interior", "zuhause", "möbel"],
        "en": ["home", "interior", "decor", "furniture", "living"]
    }
}


class InfluencerEvaluator:
    """
    红人评估器

    核心算法：
    1. 活跃度评估 - 发帖频率、互动趋势
    2. 粉丝真实性 - 互动率异常检测、粉丝/关注比
    3. 类目相关度 - 内容关键词匹配、德国市场契合度

    使用示例：
    ```python
    evaluator = InfluencerEvaluator(target_niche="fashion")
    profile = InfluencerProfile(...)
    result = evaluator.evaluate(profile)
    print(result.total_score, result.grade)
    ```
    """

    def __init__(
        self,
        target_niche: str = None,
        weights: Dict[str, float] = None
    ):
        """
        Args:
            target_niche: 目标垂类 (fashion/tech/beauty/fitness/food/home)
            weights: 自定义权重 {"activity": 0.3, "authenticity": 0.4, "relevance": 0.3}
        """
        self.target_niche = target_niche
        self.weights = weights or {
            "activity": 0.25,
            "authenticity": 0.40,  # 真实性最重要
            "relevance": 0.35
        }

    def evaluate(self, profile: InfluencerProfile) -> EvaluationResult:
        """执行完整评估"""

        # 1. 活跃度评估
        activity_score, activity_details = self._evaluate_activity(profile)

        # 2. 粉丝真实性评估
        auth_score, auth_details = self._evaluate_authenticity(profile)

        # 3. 类目相关度评估（含德国市场关键词）
        relevance_score, relevance_details, german_fit = self._evaluate_relevance(profile)

        # 4. 计算综合得分
        total_score = (
            activity_score * self.weights["activity"] +
            auth_score * self.weights["authenticity"] +
            relevance_score * self.weights["relevance"]
        )

        # 5. 评级
        grade = self._calculate_grade(total_score)

        # 6. 风险标记
        risk_flags = self._identify_risks(profile, auth_details)

        # 7. 生成建议
        recommendation = self._generate_recommendation(
            grade, activity_details, auth_details, relevance_details, german_fit
        )

        return EvaluationResult(
            username=profile.username,
            platform=profile.platform.value,
            activity_score=activity_score,
            authenticity_score=auth_score,
            relevance_score=relevance_score,
            total_score=total_score,
            grade=grade,
            activity_details=activity_details,
            authenticity_details=auth_details,
            relevance_details=relevance_details,
            german_market_fit=german_fit,
            recommendation=recommendation,
            risk_flags=risk_flags
        )

    def _evaluate_activity(self, profile: InfluencerProfile) -> tuple:
        """
        活跃度评估算法

        考量因素：
        - 发帖频率（近30天）
        - 发帖规律性
        - 最近一次发帖时间
        """
        details = {}
        score = 0

        # 1. 发帖频率 (40分)
        if profile.recent_post_dates:
            now = datetime.now()
            posts_last_30d = sum(
                1 for d in profile.recent_post_dates
                if (now - d).days <= 30
            )

            # Instagram/TikTok: 理想频率 8-15条/月
            # YouTube: 理想频率 4-8条/月
            if profile.platform == Platform.YOUTUBE:
                ideal_min, ideal_max = 4, 8
            else:
                ideal_min, ideal_max = 8, 15

            if ideal_min <= posts_last_30d <= ideal_max:
                freq_score = 40
            elif posts_last_30d > ideal_max:
                freq_score = 35  # 过于频繁可能质量下降
            elif posts_last_30d >= ideal_min * 0.5:
                freq_score = 25
            else:
                freq_score = 10

            details["posts_last_30d"] = posts_last_30d
            details["frequency_score"] = freq_score
            score += freq_score

            # 2. 最近发帖时间 (30分)
            latest_post = max(profile.recent_post_dates)
            days_since_post = (now - latest_post).days

            if days_since_post <= 3:
                recency_score = 30
            elif days_since_post <= 7:
                recency_score = 25
            elif days_since_post <= 14:
                recency_score = 15
            else:
                recency_score = 5

            details["days_since_last_post"] = days_since_post
            details["recency_score"] = recency_score
            score += recency_score
        else:
            details["warning"] = "无发帖时间数据"
            score += 20  # 给个基础分

        # 3. 内容产出量 (30分)
        if profile.posts_count > 0:
            if profile.posts_count >= 100:
                content_score = 30
            elif profile.posts_count >= 50:
                content_score = 25
            elif profile.posts_count >= 20:
                content_score = 15
            else:
                content_score = 10

            details["total_posts"] = profile.posts_count
            details["content_score"] = content_score
            score += content_score

        return score, details

    def _evaluate_authenticity(self, profile: InfluencerProfile) -> tuple:
        """
        粉丝真实性评估算法

        核心逻辑：
        - 互动率是否在合理区间（过高/过低都可疑）
        - 粉丝/关注比（正常KOL应该粉丝远大于关注）
        - 评论质量（如有数据）
        """
        details = {}
        score = 0

        # 1. 互动率评估 (50分)
        if profile.followers > 0 and profile.avg_likes > 0:
            engagement_rate = (profile.avg_likes + profile.avg_comments) / profile.followers * 100
            details["engagement_rate"] = round(engagement_rate, 2)

            # 互动率合理区间（按平台和粉丝量级）
            # Instagram: 1-5% 正常, <1% 可疑, >10% 可疑
            # TikTok: 3-10% 正常（算法推荐机制不同）
            # YouTube: 2-8% 正常

            if profile.platform == Platform.TIKTOK:
                normal_min, normal_max = 3.0, 12.0
            elif profile.platform == Platform.YOUTUBE:
                normal_min, normal_max = 2.0, 8.0
            else:  # Instagram
                # 粉丝量级影响互动率
                if profile.followers > 1000000:
                    normal_min, normal_max = 0.5, 3.0
                elif profile.followers > 100000:
                    normal_min, normal_max = 1.0, 5.0
                else:
                    normal_min, normal_max = 2.0, 8.0

            if normal_min <= engagement_rate <= normal_max:
                eng_score = 50
                details["engagement_status"] = "正常"
            elif engagement_rate < normal_min:
                eng_score = 20
                details["engagement_status"] = "偏低（可能僵尸粉）"
            elif engagement_rate > normal_max * 1.5:
                eng_score = 15
                details["engagement_status"] = "异常高（可能刷量）"
            else:
                eng_score = 35
                details["engagement_status"] = "略高"

            details["engagement_score"] = eng_score
            score += eng_score
        else:
            details["warning"] = "缺少互动数据"
            score += 25

        # 2. 粉丝/关注比 (30分)
        if profile.followers > 0 and profile.following > 0:
            ff_ratio = profile.followers / profile.following
            details["follower_following_ratio"] = round(ff_ratio, 2)

            # 正常KOL: 粉丝应该是关注的5倍以上
            # 互关党: 比例接近1
            if ff_ratio >= 10:
                ff_score = 30
                details["ff_status"] = "优秀（真实影响力）"
            elif ff_ratio >= 5:
                ff_score = 25
                details["ff_status"] = "良好"
            elif ff_ratio >= 2:
                ff_score = 15
                details["ff_status"] = "一般（可能互关）"
            else:
                ff_score = 5
                details["ff_status"] = "可疑（互关党特征）"

            details["ff_score"] = ff_score
            score += ff_score
        else:
            score += 15

        # 3. 评论/点赞比 (20分) - 检测刷量
        if profile.avg_likes > 0 and profile.avg_comments > 0:
            comment_like_ratio = profile.avg_comments / profile.avg_likes * 100
            details["comment_like_ratio"] = round(comment_like_ratio, 2)

            # 正常比例: 1-5%
            if 1 <= comment_like_ratio <= 5:
                cl_score = 20
                details["cl_status"] = "正常"
            elif comment_like_ratio < 1:
                cl_score = 10
                details["cl_status"] = "评论偏少"
            else:
                cl_score = 15
                details["cl_status"] = "评论活跃"

            details["cl_score"] = cl_score
            score += cl_score
        else:
            score += 10

        return score, details

    def _evaluate_relevance(self, profile: InfluencerProfile) -> tuple:
        """
        类目相关度评估 + 德国市场关键词匹配

        这是德国市场特化的核心算法
        """
        details = {}
        german_fit = {}
        score = 0

        # 合并所有文本内容
        all_text = " ".join([
            profile.bio,
            " ".join(profile.recent_captions),
            " ".join(profile.hashtags)
        ]).lower()

        # 1. 德国市场价值观关键词匹配 (40分)
        german_keywords_found = {}
        german_score = 0

        for category, config in GERMAN_VALUE_KEYWORDS.items():
            found_de = [kw for kw in config["de"] if kw in all_text]
            found_en = [kw for kw in config["en"] if kw in all_text]

            if found_de or found_en:
                german_keywords_found[category] = {
                    "de": found_de,
                    "en": found_en,
                    "weight": config["weight"]
                }
                # 德语关键词权重更高
                german_score += len(found_de) * 5 * config["weight"]
                german_score += len(found_en) * 3 * config["weight"]

        german_score = min(40, german_score)  # 上限40分
        german_fit["keywords_found"] = german_keywords_found
        german_fit["german_value_score"] = round(german_score, 1)

        # 特别标记：可持续性关键词（德国消费者最关注）
        if "sustainability" in german_keywords_found:
            german_fit["sustainability_focus"] = True
            german_fit["recommendation"] = "该红人关注可持续性，契合德国消费者核心价值观"

        score += german_score

        # 2. 垂类匹配 (40分)
        if self.target_niche and self.target_niche in NICHE_KEYWORDS:
            niche_config = NICHE_KEYWORDS[self.target_niche]
            found_de = [kw for kw in niche_config["de"] if kw in all_text]
            found_en = [kw for kw in niche_config["en"] if kw in all_text]

            niche_match_count = len(found_de) + len(found_en)

            if niche_match_count >= 5:
                niche_score = 40
                details["niche_match"] = "高度匹配"
            elif niche_match_count >= 3:
                niche_score = 30
                details["niche_match"] = "匹配"
            elif niche_match_count >= 1:
                niche_score = 20
                details["niche_match"] = "部分匹配"
            else:
                niche_score = 5
                details["niche_match"] = "不匹配"

            details["niche_keywords_found"] = {"de": found_de, "en": found_en}
            details["niche_score"] = niche_score
            score += niche_score
        else:
            score += 20  # 未指定垂类，给基础分

        # 3. 内容语言检测 (20分)
        # 检测是否有德语内容
        german_indicators = ["ich", "und", "der", "die", "das", "ist", "für", "mit"]
        german_word_count = sum(1 for word in german_indicators if f" {word} " in f" {all_text} ")

        if german_word_count >= 5:
            lang_score = 20
            details["language"] = "德语内容为主"
        elif german_word_count >= 2:
            lang_score = 15
            details["language"] = "包含德语内容"
        else:
            lang_score = 10
            details["language"] = "非德语内容"

        details["german_word_indicators"] = german_word_count
        score += lang_score

        return score, details, german_fit

    def _calculate_grade(self, total_score: float) -> str:
        """评级"""
        if total_score >= 85:
            return "S"
        elif total_score >= 70:
            return "A"
        elif total_score >= 55:
            return "B"
        elif total_score >= 40:
            return "C"
        else:
            return "D"

    def _identify_risks(self, profile: InfluencerProfile, auth_details: dict) -> List[str]:
        """识别风险标记"""
        risks = []

        # 互动率异常
        if auth_details.get("engagement_status") == "异常高（可能刷量）":
            risks.append("⚠️ 互动率异常高，疑似刷量")
        elif auth_details.get("engagement_status") == "偏低（可能僵尸粉）":
            risks.append("⚠️ 互动率偏低，可能存在僵尸粉")

        # 互关党特征
        if auth_details.get("ff_status") == "可疑（互关党特征）":
            risks.append("⚠️ 粉丝/关注比异常，互关党特征")

        # 粉丝量级与互动不匹配
        if profile.followers > 100000 and profile.avg_likes < 500:
            risks.append("⚠️ 大号低互动，粉丝质量存疑")

        # 长期不更新
        if auth_details.get("days_since_last_post", 0) > 30:
            risks.append("⚠️ 超过30天未更新，活跃度存疑")

        return risks

    def _generate_recommendation(
        self,
        grade: str,
        activity: dict,
        auth: dict,
        relevance: dict,
        german_fit: dict
    ) -> str:
        """生成建议"""

        if grade == "S":
            base = "🌟 强烈推荐合作！"
        elif grade == "A":
            base = "✅ 推荐合作"
        elif grade == "B":
            base = "👍 可以考虑合作"
        elif grade == "C":
            base = "⚠️ 谨慎考虑"
        else:
            base = "❌ 不建议合作"

        # 添加具体建议
        details = []

        if german_fit.get("sustainability_focus"):
            details.append("适合推广环保/可持续产品")

        if relevance.get("niche_match") == "高度匹配":
            details.append(f"与目标垂类高度匹配")

        if auth.get("engagement_status") == "正常":
            details.append("粉丝互动健康")

        if activity.get("posts_last_30d", 0) >= 8:
            details.append("更新频率稳定")

        if details:
            return f"{base}。{'; '.join(details)}。"
        return base

    def evaluate_batch(self, profiles: List[InfluencerProfile]) -> List[EvaluationResult]:
        """批量评估"""
        return [self.evaluate(p) for p in profiles]

    def rank_influencers(self, results: List[EvaluationResult]) -> List[EvaluationResult]:
        """按综合得分排序"""
        return sorted(results, key=lambda x: x.total_score, reverse=True)


# ============ 数据解析辅助函数 ============

def parse_instagram_data(raw_data: dict) -> InfluencerProfile:
    """
    从Instagram API/爬虫数据解析为标准Profile

    Args:
        raw_data: Instagram原始数据（API响应或爬虫结果）
    """
    # 这里是示例结构，实际需要根据数据源调整
    return InfluencerProfile(
        platform=Platform.INSTAGRAM,
        username=raw_data.get("username", ""),
        followers=raw_data.get("followers_count", 0),
        following=raw_data.get("following_count", 0),
        posts_count=raw_data.get("media_count", 0),
        avg_likes=raw_data.get("avg_likes", 0),
        avg_comments=raw_data.get("avg_comments", 0),
        bio=raw_data.get("biography", ""),
        recent_captions=raw_data.get("recent_captions", []),
        hashtags=raw_data.get("hashtags", []),
        raw_data=raw_data
    )


def parse_tiktok_data(raw_data: dict) -> InfluencerProfile:
    """从TikTok数据解析"""
    return InfluencerProfile(
        platform=Platform.TIKTOK,
        username=raw_data.get("username", ""),
        followers=raw_data.get("follower_count", 0),
        following=raw_data.get("following_count", 0),
        posts_count=raw_data.get("video_count", 0),
        avg_likes=raw_data.get("avg_likes", 0),
        avg_comments=raw_data.get("avg_comments", 0),
        avg_views=raw_data.get("avg_views", 0),
        bio=raw_data.get("signature", ""),
        recent_captions=raw_data.get("recent_captions", []),
        hashtags=raw_data.get("hashtags", []),
        raw_data=raw_data
    )


