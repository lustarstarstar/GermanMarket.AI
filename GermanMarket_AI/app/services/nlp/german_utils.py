# -*- coding: utf-8 -*-
"""
德语文本处理工具
================
从 CrossBorder_AI_Nexus 迁移并增强
"""

import re
import unicodedata
from typing import List, Set

# 德语特殊字符映射
UMLAUT_MAP = {
    'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
    'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
    'ß': 'ss'
}

# 德语停用词（扩展版）
GERMAN_STOPWORDS: Set[str] = {
    # 冠词
    'der', 'die', 'das', 'den', 'dem', 'des',
    'ein', 'eine', 'einer', 'einem', 'einen', 'eines',
    # 连词
    'und', 'oder', 'aber', 'doch', 'sondern', 'denn', 'weder', 'noch',
    # 动词
    'ist', 'sind', 'war', 'waren', 'sein', 'wird', 'werden', 'wurde', 'wurden',
    'hat', 'haben', 'hatte', 'hatten', 'bin', 'bist', 'seid',
    # 代词
    'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr',
    'mein', 'dein', 'sein', 'ihr', 'unser', 'euer', 'meine', 'deine', 'seine',
    'mir', 'dir', 'ihm', 'uns', 'euch', 'ihnen',
    # 否定
    'nicht', 'kein', 'keine', 'keiner', 'nichts', 'nie', 'niemals',
    # 介词
    'mit', 'bei', 'nach', 'von', 'zu', 'aus', 'für', 'über', 'unter',
    'vor', 'hinter', 'neben', 'zwischen', 'durch', 'gegen', 'ohne', 'um',
    # 副词
    'sehr', 'auch', 'nur', 'noch', 'schon', 'immer', 'wieder', 'dann', 'jetzt',
    'hier', 'dort', 'wo', 'wann', 'wie', 'was', 'wer', 'warum',
    # 情态动词
    'kann', 'muss', 'soll', 'will', 'möchte', 'darf', 'können', 'müssen',
    # 其他
    'ja', 'nein', 'vielleicht', 'mehr', 'weniger', 'alle', 'alles',
    'jeder', 'jede', 'jedes', 'dieser', 'diese', 'dieses', 'so', 'als', 'wenn'
}

# 电商评论常见表达（用于关键词提取增强）
ECOMMERCE_POSITIVE_WORDS = {
    'super', 'toll', 'perfekt', 'ausgezeichnet', 'hervorragend', 'fantastisch',
    'wunderbar', 'großartig', 'empfehlenswert', 'zufrieden', 'schnell', 'pünktlich'
}

ECOMMERCE_NEGATIVE_WORDS = {
    'schlecht', 'mangelhaft', 'enttäuscht', 'kaputt', 'defekt', 'langsam',
    'teuer', 'billig', 'schrecklich', 'furchtbar', 'ärgerlich', 'beschädigt'
}


def normalize_german_text(text: str, keep_umlauts: bool = True) -> str:
    """
    德语文本规范化
    
    Args:
        text: 输入文本
        keep_umlauts: 是否保留变音符 (True=用于BERT, False=用于关键词匹配)
    """
    if not text:
        return ""
    
    # Unicode规范化
    text = unicodedata.normalize('NFC', text)
    
    # 可选转换变音符
    if not keep_umlauts:
        for umlaut, replacement in UMLAUT_MAP.items():
            text = text.replace(umlaut, replacement)
    
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def clean_review_text(text: str) -> str:
    """清洗电商评论文本"""
    if not text:
        return ""
    
    # 移除HTML
    text = re.sub(r'<[^>]+>', '', text)
    # 移除URL
    text = re.sub(r'https?://\S+', '', text)
    # 移除邮箱
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    # 保留德语字符和基本标点
    text = re.sub(r'[^\w\s.,!?äöüÄÖÜß\-\'\"()]', ' ', text)
    # 修复多个点号
    text = re.sub(r'\.{2,}', '...', text)
    # 规范空白
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def remove_stopwords(tokens: List[str], custom_stopwords: Set[str] = None) -> List[str]:
    """移除停用词"""
    stopwords = GERMAN_STOPWORDS.copy()
    if custom_stopwords:
        stopwords.update(custom_stopwords)
    return [t for t in tokens if t.lower() not in stopwords and len(t) > 1]


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 20) -> List[str]:
    """
    提取德语关键词
    
    Returns:
        关键词列表(按出现顺序去重)
    """
    # 分词
    tokens = re.findall(r'\b[a-zA-ZäöüÄÖÜß]{%d,}\b' % min_length, text)
    # 移除停用词
    tokens = remove_stopwords(tokens)
    # 去重保序
    seen = set()
    result = []
    for token in tokens:
        lower = token.lower()
        if lower not in seen:
            seen.add(lower)
            result.append(lower)
    return result[:max_keywords]


def detect_sentiment_words(text: str) -> dict:
    """快速检测情感词"""
    text_lower = text.lower()
    positive = [w for w in ECOMMERCE_POSITIVE_WORDS if w in text_lower]
    negative = [w for w in ECOMMERCE_NEGATIVE_WORDS if w in text_lower]
    return {
        "positive_words": positive,
        "negative_words": negative,
        "sentiment_hint": "positive" if len(positive) > len(negative) else 
                         "negative" if len(negative) > len(positive) else "neutral"
    }

