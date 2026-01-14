# -*- coding: utf-8 -*-
"""
德语情感分析服务
================
基于BERT的情感分析，支持单条和批量处理
"""

import torch
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline


class SentimentLabel(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    UNCERTAIN = "uncertain"


@dataclass
class SentimentResult:
    """情感分析结果"""
    text: str
    label: SentimentLabel
    score: float          # 0-1, 越高越正面
    confidence: float
    raw_output: dict = None
    
    def to_dict(self) -> dict:
        return {
            "text": self.text[:100] + "..." if len(self.text) > 100 else self.text,
            "label": self.label.value,
            "score": round(self.score, 4),
            "confidence": round(self.confidence, 4)
        }


class GermanSentimentAnalyzer:
    """德语情感分析器"""
    
    def __init__(
        self,
        model_name: str = "oliverguhr/german-sentiment-bert",
        device: str = "auto",
        threshold_positive: float = 0.6,
        threshold_negative: float = 0.4
    ):
        self.model_name = model_name
        self.device = "cuda" if device == "auto" and torch.cuda.is_available() else "cpu"
        self.threshold_positive = threshold_positive
        self.threshold_negative = threshold_negative
        
        # 懒加载
        self._pipeline = None
    
    def _load_model(self):
        """懒加载模型"""
        if self._pipeline is not None:
            return
        
        print(f"加载模型: {self.model_name} -> {self.device}")
        
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        
        self._pipeline = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=0 if self.device == "cuda" else -1,
            max_length=512,
            truncation=True
        )
        print("✓ 模型加载完成")

    def _score_to_label(self, score: float, confidence: float) -> SentimentLabel:
        """将得分转换为标签"""
        if confidence < 0.5:
            return SentimentLabel.UNCERTAIN
        if score >= self.threshold_positive:
            return SentimentLabel.POSITIVE
        elif score <= self.threshold_negative:
            return SentimentLabel.NEGATIVE
        return SentimentLabel.NEUTRAL

    def analyze(self, text: str) -> SentimentResult:
        """分析单条文本"""
        from .german_utils import clean_review_text, normalize_german_text

        self._load_model()

        # 预处理
        cleaned = clean_review_text(text)
        cleaned = normalize_german_text(cleaned, keep_umlauts=True)

        if not cleaned:
            return SentimentResult(
                text=text,
                label=SentimentLabel.UNCERTAIN,
                score=0.5,
                confidence=0.0
            )

        try:
            output = self._pipeline(cleaned)[0]
            label_str = output['label'].lower()
            confidence = output['score']

            # 转换为统一得分
            if label_str == 'positive':
                score = confidence
            elif label_str == 'negative':
                score = 1 - confidence
            else:
                score = 0.5

            final_label = self._score_to_label(score, confidence)

            return SentimentResult(
                text=text,
                label=final_label,
                score=score,
                confidence=confidence,
                raw_output=output
            )
        except Exception as e:
            print(f"分析失败: {e}")
            return SentimentResult(
                text=text,
                label=SentimentLabel.UNCERTAIN,
                score=0.5,
                confidence=0.0
            )

    def analyze_batch(self, texts: List[str], show_progress: bool = True) -> List[SentimentResult]:
        """批量分析"""
        from tqdm import tqdm

        self._load_model()
        results = []
        iterator = tqdm(texts, desc="情感分析") if show_progress else texts

        for text in iterator:
            results.append(self.analyze(text))

        return results

    def get_statistics(self, results: List[SentimentResult]) -> dict:
        """计算统计信息"""
        if not results:
            return {}

        total = len(results)
        pos = sum(1 for r in results if r.label == SentimentLabel.POSITIVE)
        neg = sum(1 for r in results if r.label == SentimentLabel.NEGATIVE)
        neu = sum(1 for r in results if r.label == SentimentLabel.NEUTRAL)

        return {
            "total": total,
            "positive": pos,
            "negative": neg,
            "neutral": neu,
            "positive_rate": round(pos / total * 100, 2),
            "negative_rate": round(neg / total * 100, 2),
            "avg_score": round(sum(r.score for r in results) / total, 4)
        }

