# -*- coding: utf-8 -*-
"""
评论分析服务
============
整合NLP能力，提供完整的评论分析流程
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .nlp import (
    GermanSentimentAnalyzer,
    ABSAExtractor,
    GermanTranslator,
    extract_keywords,
    detect_sentiment_words
)


@dataclass
class ReviewInsight:
    """单条评论的完整分析结果"""
    original_text: str
    translated_text: str
    sentiment: str
    sentiment_score: float
    aspects: Dict[str, float]      # 维度 -> 得分
    keywords: List[str]
    sentiment_words: dict
    
    def to_dict(self) -> dict:
        return {
            "original": self.original_text[:200] + "..." if len(self.original_text) > 200 else self.original_text,
            "translation": self.translated_text,
            "sentiment": self.sentiment,
            "score": round(self.sentiment_score, 3),
            "aspects": {k: round(v, 2) for k, v in self.aspects.items()},
            "keywords": self.keywords[:10]
        }


@dataclass
class ReviewReport:
    """批量评论的分析报告"""
    total_reviews: int
    analyzed_at: datetime
    
    # 情感统计
    sentiment_distribution: Dict[str, int]
    average_score: float
    
    # 维度统计
    dimension_scores: Dict[str, dict]
    
    # 关键发现
    top_positive_keywords: List[str]
    top_negative_keywords: List[str]
    key_insights: List[str]
    
    # 详细数据
    reviews: List[ReviewInsight] = field(default_factory=list)


class ReviewAnalyzer:
    """
    评论分析器
    
    使用示例：
    ```python
    analyzer = ReviewAnalyzer()
    
    # 分析单条
    insight = analyzer.analyze_single("Das Produkt ist sehr gut!")
    print(insight.to_dict())
    
    # 批量分析
    report = analyzer.analyze_batch(reviews_list)
    print(report.key_insights)
    ```
    """
    
    def __init__(self, translate: bool = True):
        """
        Args:
            translate: 是否启用翻译功能
        """
        self.translate = translate
        
        # 懒加载
        self._sentiment = None
        self._absa = None
        self._translator = None
    
    @property
    def sentiment_analyzer(self):
        if self._sentiment is None:
            self._sentiment = GermanSentimentAnalyzer()
        return self._sentiment
    
    @property
    def absa_extractor(self):
        if self._absa is None:
            self._absa = ABSAExtractor(self.sentiment_analyzer)
        return self._absa
    
    @property
    def translator(self):
        if self._translator is None and self.translate:
            self._translator = GermanTranslator()
        return self._translator
    
    def analyze_single(self, text: str) -> ReviewInsight:
        """分析单条评论"""
        
        # 1. 情感分析
        sentiment_result = self.sentiment_analyzer.analyze(text)
        
        # 2. 维度分析
        absa_result = self.absa_extractor.extract(text)
        
        # 3. 关键词
        keywords = extract_keywords(text)
        
        # 4. 情感词检测
        sentiment_words = detect_sentiment_words(text)
        
        # 5. 翻译
        translated = ""
        if self.translate and self.translator:
            try:
                translated = self.translator.de_to_zh(text)
            except Exception as e:
                print(f"翻译失败: {e}")
                translated = "[翻译失败]"
        
        return ReviewInsight(
            original_text=text,
            translated_text=translated,
            sentiment=sentiment_result.label.value,
            sentiment_score=sentiment_result.score,
            aspects=absa_result.summary,
            keywords=keywords,
            sentiment_words=sentiment_words
        )
    
    def analyze_batch(
        self,
        texts: List[str],
        show_progress: bool = True
    ) -> ReviewReport:
        """批量分析并生成报告"""
        from tqdm import tqdm
        from collections import Counter
        
        reviews = []
        all_pos_words = []
        all_neg_words = []
        
        iterator = tqdm(texts, desc="分析评论") if show_progress else texts
        
        for text in iterator:
            insight = self.analyze_single(text)
            reviews.append(insight)
            all_pos_words.extend(insight.sentiment_words.get("positive_words", []))
            all_neg_words.extend(insight.sentiment_words.get("negative_words", []))

        # 统计情感分布
        sentiment_dist = Counter(r.sentiment for r in reviews)
        avg_score = sum(r.sentiment_score for r in reviews) / len(reviews)

        # 汇总维度得分
        all_absa = [self.absa_extractor.extract(t) for t in texts]
        dimension_scores = self.absa_extractor.aggregate(all_absa)

        # 关键词统计
        top_pos = [w for w, _ in Counter(all_pos_words).most_common(10)]
        top_neg = [w for w, _ in Counter(all_neg_words).most_common(10)]

        # 生成洞察
        insights = self._generate_insights(sentiment_dist, dimension_scores, len(texts))

        return ReviewReport(
            total_reviews=len(texts),
            analyzed_at=datetime.now(),
            sentiment_distribution=dict(sentiment_dist),
            average_score=round(avg_score, 3),
            dimension_scores=dimension_scores,
            top_positive_keywords=top_pos,
            top_negative_keywords=top_neg,
            key_insights=insights,
            reviews=reviews
        )

    def _generate_insights(
        self,
        sentiment_dist: dict,
        dimension_scores: dict,
        total: int
    ) -> List[str]:
        """生成关键洞察"""
        insights = []

        # 情感洞察
        pos_rate = sentiment_dist.get("positive", 0) / total * 100
        neg_rate = sentiment_dist.get("negative", 0) / total * 100

        if pos_rate > 60:
            insights.append(f"✅ 整体评价积极，好评率 {pos_rate:.1f}%")
        elif neg_rate > 40:
            insights.append(f"⚠️ 差评较多({neg_rate:.1f}%)，需要关注")

        # 维度洞察
        for dim, stats in dimension_scores.items():
            if stats["count"] >= 3:  # 至少被提及3次
                if stats["avg_score"] < 0.4:
                    insights.append(f"🔴 {dim}维度得分较低({stats['avg_score']:.2f})，是主要痛点")
                elif stats["avg_score"] > 0.7:
                    insights.append(f"🟢 {dim}维度表现优秀({stats['avg_score']:.2f})，是卖点")

        return insights

