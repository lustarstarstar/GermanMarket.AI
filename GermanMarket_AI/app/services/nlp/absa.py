# -*- coding: utf-8 -*-
"""
细粒度情感分析 (Aspect-Based Sentiment Analysis)
================================================
针对电商评论的多维度情感提取
"""

import re
from typing import List, Dict
from dataclasses import dataclass, field
from collections import defaultdict


# 维度关键词配置（德语 -> 中文）
ASPECT_CONFIG = {
    "Lieferung": {
        "zh": "物流",
        "keywords": ["versand", "lieferung", "lieferzeit", "zustellung", "paket", "dhl", "hermes", "post", "angekommen", "geliefert"]
    },
    "Qualität": {
        "zh": "质量",
        "keywords": ["qualität", "verarbeitung", "haltbar", "robust", "stabil", "billig", "minderwertig", "hochwertig"]
    },
    "Aussehen": {
        "zh": "外观",
        "keywords": ["design", "aussehen", "farbe", "optik", "schön", "hässlich", "elegant", "stil", "look"]
    },
    "Verpackung": {
        "zh": "包装",
        "keywords": ["verpackung", "karton", "schutz", "beschädigt", "verpackt", "schachtel", "box"]
    },
    "Preis": {
        "zh": "价格",
        "keywords": ["preis", "wert", "günstig", "teuer", "geld", "kosten", "bezahlt", "preiswert", "überteuert"]
    },
    "Kundenservice": {
        "zh": "客服",
        "keywords": ["kundenservice", "service", "kontakt", "antwort", "hilfe", "support", "erreichbar", "freundlich"]
    },
    "Größe": {
        "zh": "尺码",
        "keywords": ["größe", "size", "passt", "klein", "groß", "eng", "weit", "länge", "breite"]
    },
    "Material": {
        "zh": "材质",
        "keywords": ["material", "stoff", "leder", "kunststoff", "metall", "holz", "baumwolle", "polyester"]
    },
    "Funktionalität": {
        "zh": "功能",
        "keywords": ["funktion", "funktioniert", "funktional", "praktisch", "nützlich", "verwendung", "einfach"]
    }
}


@dataclass
class AspectSentiment:
    """单个维度的情感结果"""
    aspect_de: str
    aspect_zh: str
    score: float           # 0-1
    confidence: float
    evidence: List[str] = field(default_factory=list)
    keywords_found: List[str] = field(default_factory=list)


@dataclass 
class ABSAResult:
    """ABSA完整结果"""
    text: str
    aspects: List[AspectSentiment]
    overall_score: float
    summary: Dict[str, float]  # 维度 -> 得分
    
    def to_dict(self) -> dict:
        return {
            "text_preview": self.text[:100] + "..." if len(self.text) > 100 else self.text,
            "overall_score": round(self.overall_score, 3),
            "dimensions": {
                asp.aspect_zh: {
                    "score": round(asp.score, 3),
                    "keywords": asp.keywords_found[:3]
                } for asp in self.aspects
            }
        }


class ABSAExtractor:
    """维度情感提取器"""
    
    def __init__(self, sentiment_analyzer=None):
        self._sentiment_analyzer = sentiment_analyzer
        
        # 构建关键词索引
        self._keyword_to_aspect = {}
        for aspect, config in ASPECT_CONFIG.items():
            for kw in config["keywords"]:
                self._keyword_to_aspect[kw.lower()] = aspect
    
    @property
    def sentiment_analyzer(self):
        """懒加载情感分析器"""
        if self._sentiment_analyzer is None:
            from .sentiment import GermanSentimentAnalyzer
            self._sentiment_analyzer = GermanSentimentAnalyzer()
        return self._sentiment_analyzer
    
    def _split_sentences(self, text: str) -> List[str]:
        """分句"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _find_aspects(self, text: str) -> Dict[str, List[str]]:
        """查找文本中涉及的维度"""
        text_lower = text.lower()
        aspect_keywords = defaultdict(list)
        
        for keyword, aspect in self._keyword_to_aspect.items():
            if keyword in text_lower:
                aspect_keywords[aspect].append(keyword)
        
        return dict(aspect_keywords)
    
    def extract(self, text: str) -> ABSAResult:
        """提取维度情感"""
        from .german_utils import normalize_german_text
        
        text = normalize_german_text(text)
        sentences = self._split_sentences(text)
        
        # 1. 查找涉及的维度
        all_aspects = {}
        for sentence in sentences:
            found = self._find_aspects(sentence)
            for aspect, keywords in found.items():
                if aspect not in all_aspects:
                    all_aspects[aspect] = {"sentences": [], "keywords": set()}
                all_aspects[aspect]["sentences"].append(sentence)
                all_aspects[aspect]["keywords"].update(keywords)
        
        # 2. 对每个维度分析情感
        aspect_results = []
        for aspect, data in all_aspects.items():
            config = ASPECT_CONFIG[aspect]
            
            scores, confidences = [], []
            for sentence in data["sentences"]:
                result = self.sentiment_analyzer.analyze(sentence)
                scores.append(result.score)
                confidences.append(result.confidence)
            
            avg_score = sum(scores) / len(scores) if scores else 0.5
            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
            
            aspect_results.append(AspectSentiment(
                aspect_de=aspect,
                aspect_zh=config["zh"],
                score=avg_score,
                confidence=avg_conf,
                evidence=data["sentences"][:2],
                keywords_found=list(data["keywords"])
            ))

        # 3. 计算整体得分
        if aspect_results:
            overall = sum(a.score for a in aspect_results) / len(aspect_results)
        else:
            overall = self.sentiment_analyzer.analyze(text).score

        # 4. 构建汇总
        summary = {a.aspect_zh: a.score for a in aspect_results}

        return ABSAResult(
            text=text,
            aspects=aspect_results,
            overall_score=overall,
            summary=summary
        )

    def extract_batch(self, texts: List[str]) -> List[ABSAResult]:
        """批量提取"""
        from tqdm import tqdm
        return [self.extract(t) for t in tqdm(texts, desc="ABSA分析")]

    def aggregate(self, results: List[ABSAResult]) -> Dict[str, dict]:
        """汇总多条评论的维度统计"""
        dim_scores = defaultdict(list)

        for result in results:
            for asp in result.aspects:
                dim_scores[asp.aspect_zh].append(asp.score)

        summary = {}
        for dim, scores in dim_scores.items():
            summary[dim] = {
                "avg_score": round(sum(scores) / len(scores), 3),
                "count": len(scores),
                "positive_rate": round(sum(1 for s in scores if s > 0.6) / len(scores) * 100, 1)
            }

        return dict(sorted(summary.items(), key=lambda x: x[1]["count"], reverse=True))

