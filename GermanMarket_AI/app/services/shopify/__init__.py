# -*- coding: utf-8 -*-
"""
Shopify 数据集成模块
====================
支持 API 和 CSV 双通道导入评论数据
增强 ABSA 模块，自动识别高风险差评
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum
import re
import csv
import io


class ImportSource(Enum):
    """数据来源"""
    SHOPIFY_API = "shopify_api"
    CSV_UPLOAD = "csv_upload"
    MANUAL = "manual"


class RiskLevel(Enum):
    """风险等级"""
    CRITICAL = "critical"   # 紧急：法律/安全
    HIGH = "high"           # 高风险：退款/投诉
    MEDIUM = "medium"       # 中风险：不满意
    LOW = "low"             # 低风险：一般反馈


# ============ 数据 Schema 定义 ============

@dataclass
class ReviewSchema:
    """
    评论数据标准 Schema
    
    这是系统内部的统一数据格式，无论从 API 还是 CSV 导入，
    都会转换为此格式进行处理。
    """
    # 必填字段
    review_id: str                      # 唯一标识
    content: str                        # 评论内容
    rating: int                         # 评分 1-5
    
    # 时间信息
    created_at: datetime = None
    updated_at: datetime = None
    
    # 产品信息
    product_id: str = ""
    product_name: str = ""
    product_sku: str = ""
    
    # 客户信息（脱敏）
    customer_id: str = ""
    customer_name: str = ""             # 可选，用于回复
    is_verified_purchase: bool = False
    
    # 来源信息
    source: ImportSource = ImportSource.MANUAL
    source_url: str = ""
    
    # 分析结果（由系统填充）
    sentiment_score: float = None
    risk_level: RiskLevel = None
    risk_flags: List[str] = field(default_factory=list)
    aspects: Dict[str, float] = field(default_factory=dict)
    
    # 元数据
    language: str = "de"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "review_id": self.review_id,
            "content": self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "rating": self.rating,
            "product_name": self.product_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sentiment_score": self.sentiment_score,
            "risk_level": self.risk_level.value if self.risk_level else None,
            "risk_flags": self.risk_flags
        }


@dataclass
class ImportResult:
    """导入结果"""
    success: bool
    total_records: int
    imported_count: int
    failed_count: int
    errors: List[str] = field(default_factory=list)
    reviews: List[ReviewSchema] = field(default_factory=list)


# ============ 高风险关键词配置 ============

# 德语高风险关键词库
RISK_KEYWORDS = {
    "legal": {
        "keywords": [
            "anwalt", "rechtsanwalt", "klage", "gericht", "anzeige",
            "verbraucherschutz", "abmahnung", "schadensersatz", "haftung",
            "betrug", "täuschung", "irreführend", "falsch", "lüge"
        ],
        "risk_level": RiskLevel.CRITICAL,
        "alert_message": "⚠️ 法律风险：评论提及法律行动或欺诈指控"
    },
    "safety": {
        "keywords": [
            "gefährlich", "verletzung", "verletzt", "brand", "feuer",
            "explosion", "giftig", "allergie", "allergisch", "krankenhaus",
            "arzt", "notfall", "gesundheit", "schaden", "kaputt"
        ],
        "risk_level": RiskLevel.CRITICAL,
        "alert_message": "⚠️ 安全风险：评论提及产品安全问题或人身伤害"
    },
    "refund": {
        "keywords": [
            "rückerstattung", "geld zurück", "erstattung", "rücksendung",
            "widerruf", "stornierung", "paypal", "kreditkarte", "chargeback"
        ],
        "risk_level": RiskLevel.HIGH,
        "alert_message": "💰 退款风险：客户要求退款或提及支付争议"
    },
    "complaint": {
        "keywords": [
            "beschwerde", "reklamation", "kundenservice", "keine antwort",
            "ignoriert", "unverschämt", "frechheit", "niemals wieder"
        ],
        "risk_level": RiskLevel.HIGH,
        "alert_message": "📢 投诉风险：客户表达强烈不满或投诉意向"
    },
    "quality": {
        "keywords": [
            "defekt", "kaputt", "funktioniert nicht", "minderwertig",
            "billig", "schrott", "müll", "wegwerfen", "enttäuscht"
        ],
        "risk_level": RiskLevel.MEDIUM,
        "alert_message": "📦 质量问题：客户反馈产品质量不达标"
    }
}


class RiskDetector:
    """
    高风险差评检测器

    自动扫描评论内容，识别：
    - 法律风险（起诉、欺诈指控）
    - 安全风险（人身伤害、产品缺陷）
    - 退款风险（退款要求、支付争议）
    - 投诉风险（强烈不满、投诉意向）
    """

    def __init__(self, custom_keywords: Dict[str, List[str]] = None):
        self.risk_keywords = RISK_KEYWORDS.copy()
        if custom_keywords:
            for category, keywords in custom_keywords.items():
                if category in self.risk_keywords:
                    self.risk_keywords[category]["keywords"].extend(keywords)

    def detect(self, text: str, rating: int = None) -> Dict[str, Any]:
        """
        检测评论风险

        Args:
            text: 评论内容
            rating: 评分（1-5），低评分会提升风险等级

        Returns:
            {
                "risk_level": RiskLevel,
                "flags": ["flag1", "flag2"],
                "alerts": ["alert message 1"],
                "matched_keywords": {"category": ["keyword1"]}
            }
        """
        text_lower = text.lower()

        flags = []
        alerts = []
        matched = {}
        max_risk = RiskLevel.LOW

        # 扫描各类风险关键词
        for category, config in self.risk_keywords.items():
            found_keywords = [
                kw for kw in config["keywords"]
                if kw in text_lower
            ]

            if found_keywords:
                matched[category] = found_keywords
                flags.append(f"{category}:{len(found_keywords)}")
                alerts.append(config["alert_message"])

                # 更新最高风险等级
                if config["risk_level"].value == "critical":
                    max_risk = RiskLevel.CRITICAL
                elif config["risk_level"].value == "high" and max_risk != RiskLevel.CRITICAL:
                    max_risk = RiskLevel.HIGH
                elif config["risk_level"].value == "medium" and max_risk == RiskLevel.LOW:
                    max_risk = RiskLevel.MEDIUM

        # 低评分提升风险等级
        if rating is not None and rating <= 2:
            if max_risk == RiskLevel.LOW:
                max_risk = RiskLevel.MEDIUM
            elif max_risk == RiskLevel.MEDIUM:
                max_risk = RiskLevel.HIGH
            flags.append("low_rating")

        return {
            "risk_level": max_risk,
            "flags": flags,
            "alerts": alerts,
            "matched_keywords": matched
        }

    def batch_detect(self, reviews: List[ReviewSchema]) -> List[ReviewSchema]:
        """批量检测并更新评论的风险信息"""
        for review in reviews:
            result = self.detect(review.content, review.rating)
            review.risk_level = result["risk_level"]
            review.risk_flags = result["flags"]
        return reviews

    def get_critical_reviews(self, reviews: List[ReviewSchema]) -> List[ReviewSchema]:
        """筛选出紧急风险评论"""
        return [r for r in reviews if r.risk_level == RiskLevel.CRITICAL]

    def get_high_risk_reviews(self, reviews: List[ReviewSchema]) -> List[ReviewSchema]:
        """筛选出高风险评论"""
        return [r for r in reviews if r.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]


class ShopifyDataImporter:
    """
    Shopify 数据导入器

    支持两种导入方式：
    1. API 密钥直连
    2. CSV 文件上传
    """

    # CSV 列名映射（支持多种常见格式）
    CSV_COLUMN_MAPPING = {
        "review_id": ["id", "review_id", "ID", "Review ID"],
        "content": ["content", "body", "review", "text", "comment", "Bewertung", "Review"],
        "rating": ["rating", "stars", "score", "Bewertung", "Rating", "Stars"],
        "product_id": ["product_id", "ProductID", "product"],
        "product_name": ["product_name", "product", "Product", "Produkt"],
        "customer_name": ["customer", "name", "author", "Kunde", "Name"],
        "created_at": ["date", "created_at", "created", "Datum", "Date"],
    }

    def __init__(self, api_key: str = None, shop_domain: str = None):
        self.api_key = api_key
        self.shop_domain = shop_domain
        self.risk_detector = RiskDetector()

    def import_from_csv(
        self,
        csv_content: Union[str, bytes],
        delimiter: str = ",",
        encoding: str = "utf-8"
    ) -> ImportResult:
        """
        从 CSV 导入评论

        Args:
            csv_content: CSV 内容（字符串或字节）
            delimiter: 分隔符
            encoding: 编码
        """
        errors = []
        reviews = []

        try:
            # 处理字节输入
            if isinstance(csv_content, bytes):
                csv_content = csv_content.decode(encoding)

            # 解析 CSV
            reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)

            # 映射列名
            column_map = self._detect_columns(reader.fieldnames)

            for idx, row in enumerate(reader):
                try:
                    review = self._parse_csv_row(row, column_map, idx)
                    if review:
                        reviews.append(review)
                except Exception as e:
                    errors.append(f"行 {idx + 2}: {str(e)}")

            # 批量风险检测
            reviews = self.risk_detector.batch_detect(reviews)

            return ImportResult(
                success=len(errors) == 0,
                total_records=idx + 1 if 'idx' in locals() else 0,
                imported_count=len(reviews),
                failed_count=len(errors),
                errors=errors,
                reviews=reviews
            )

        except Exception as e:
            return ImportResult(
                success=False,
                total_records=0,
                imported_count=0,
                failed_count=1,
                errors=[f"CSV 解析失败: {str(e)}"]
            )

    def _detect_columns(self, fieldnames: List[str]) -> Dict[str, str]:
        """自动检测 CSV 列名映射"""
        column_map = {}

        for target_field, possible_names in self.CSV_COLUMN_MAPPING.items():
            for name in possible_names:
                if name in fieldnames:
                    column_map[target_field] = name
                    break

        return column_map

    def _parse_csv_row(self, row: dict, column_map: dict, idx: int) -> Optional[ReviewSchema]:
        """解析单行 CSV 数据"""
        # 获取内容（必填）
        content_col = column_map.get("content")
        if not content_col or not row.get(content_col):
            return None

        content = row[content_col].strip()
        if not content:
            return None

        # 获取评分
        rating_col = column_map.get("rating")
        rating = 3  # 默认中评
        if rating_col and row.get(rating_col):
            try:
                rating = int(float(row[rating_col]))
                rating = max(1, min(5, rating))  # 限制 1-5
            except:
                pass

        # 获取时间
        created_at = None
        date_col = column_map.get("created_at")
        if date_col and row.get(date_col):
            try:
                # 尝试多种日期格式
                date_str = row[date_col]
                for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        created_at = datetime.strptime(date_str, fmt)
                        break
                    except:
                        continue
            except:
                pass

        # 构建 ReviewSchema
        review_id_col = column_map.get("review_id")
        review_id = row.get(review_id_col, "") if review_id_col else f"csv_{idx}"

        return ReviewSchema(
            review_id=review_id or f"csv_{idx}",
            content=content,
            rating=rating,
            created_at=created_at,
            product_id=row.get(column_map.get("product_id", ""), ""),
            product_name=row.get(column_map.get("product_name", ""), ""),
            customer_name=row.get(column_map.get("customer_name", ""), ""),
            source=ImportSource.CSV_UPLOAD
        )

    def import_from_api(
        self,
        product_id: str = None,
        limit: int = 100,
        since_date: datetime = None
    ) -> ImportResult:
        """
        从 Shopify API 导入评论

        需要配置 api_key 和 shop_domain

        Args:
            product_id: 指定产品ID（可选）
            limit: 最大导入数量
            since_date: 只导入此日期之后的评论
        """
        if not self.api_key or not self.shop_domain:
            return ImportResult(
                success=False,
                total_records=0,
                imported_count=0,
                failed_count=0,
                errors=["未配置 Shopify API 密钥或店铺域名"]
            )

        # API 调用逻辑（需要实际实现）
        # 这里是接口预留

        # Shopify Product Reviews API 示例结构：
        # GET https://{shop}.myshopify.com/admin/api/2024-01/products/{product_id}/metafields.json
        # 或使用第三方评论应用 API（如 Judge.me, Loox, Yotpo）

        # 暂时返回空结果
        return ImportResult(
            success=True,
            total_records=0,
            imported_count=0,
            failed_count=0,
            errors=["API 导入功能待实现，请使用 CSV 导入"],
            reviews=[]
        )

    def generate_risk_report(self, reviews: List[ReviewSchema]) -> Dict[str, Any]:
        """
        生成风险报告

        Returns:
            {
                "summary": {...},
                "critical_reviews": [...],
                "high_risk_reviews": [...],
                "action_items": [...]
            }
        """
        # 统计各风险等级数量
        risk_counts = {
            RiskLevel.CRITICAL.value: 0,
            RiskLevel.HIGH.value: 0,
            RiskLevel.MEDIUM.value: 0,
            RiskLevel.LOW.value: 0
        }

        for review in reviews:
            if review.risk_level:
                risk_counts[review.risk_level.value] += 1

        # 筛选高风险评论
        critical = self.risk_detector.get_critical_reviews(reviews)
        high_risk = self.risk_detector.get_high_risk_reviews(reviews)

        # 生成行动建议
        action_items = []

        if critical:
            action_items.append({
                "priority": "紧急",
                "action": f"立即处理 {len(critical)} 条涉及法律/安全风险的评论",
                "reviews": [r.review_id for r in critical]
            })

        if len(high_risk) > len(critical):
            action_items.append({
                "priority": "高",
                "action": f"24小时内回复 {len(high_risk) - len(critical)} 条高风险差评",
                "reviews": [r.review_id for r in high_risk if r not in critical]
            })

        return {
            "summary": {
                "total_reviews": len(reviews),
                "risk_distribution": risk_counts,
                "critical_count": len(critical),
                "high_risk_count": len(high_risk)
            },
            "critical_reviews": [r.to_dict() for r in critical],
            "high_risk_reviews": [r.to_dict() for r in high_risk[:10]],  # 最多显示10条
            "action_items": action_items
        }


# ============ 便捷函数 ============

def import_reviews_from_csv(csv_content: Union[str, bytes], **kwargs) -> ImportResult:
    """快速从 CSV 导入评论"""
    importer = ShopifyDataImporter()
    return importer.import_from_csv(csv_content, **kwargs)


def detect_review_risk(text: str, rating: int = None) -> Dict[str, Any]:
    """快速检测单条评论风险"""
    detector = RiskDetector()
    return detector.detect(text, rating)

