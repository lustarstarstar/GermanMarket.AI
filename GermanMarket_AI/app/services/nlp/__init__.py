# -*- coding: utf-8 -*-
"""
NLP服务模块
"""

from .sentiment import GermanSentimentAnalyzer, SentimentResult, SentimentLabel
from .absa import ABSAExtractor, ABSAResult, AspectSentiment
from .translator import GermanTranslator, TranslationResult
from .german_utils import (
    normalize_german_text,
    clean_review_text,
    extract_keywords,
    detect_sentiment_words,
    GERMAN_STOPWORDS
)

__all__ = [
    "GermanSentimentAnalyzer",
    "SentimentResult", 
    "SentimentLabel",
    "ABSAExtractor",
    "ABSAResult",
    "AspectSentiment",
    "GermanTranslator",
    "TranslationResult",
    "normalize_german_text",
    "clean_review_text",
    "extract_keywords",
    "detect_sentiment_words",
    "GERMAN_STOPWORDS"
]

