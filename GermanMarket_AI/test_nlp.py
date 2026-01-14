# -*- coding: utf-8 -*-
"""
快速测试NLP功能
===============
运行: python test_nlp.py
"""

import sys
sys.path.insert(0, '.')

def test_sentiment():
    """测试情感分析"""
    print("\n" + "="*50)
    print("测试情感分析")
    print("="*50)
    
    from app.services.nlp import GermanSentimentAnalyzer
    
    analyzer = GermanSentimentAnalyzer()
    
    test_cases = [
        "Das Produkt ist sehr gut! Ich bin sehr zufrieden.",
        "Leider ist die Qualität sehr schlecht. Totale Enttäuschung.",
        "Die Lieferung war okay, nichts Besonderes.",
    ]
    
    for text in test_cases:
        result = analyzer.analyze(text)
        print(f"\n📝 {text[:50]}...")
        print(f"   情感: {result.label.value} | 得分: {result.score:.3f} | 置信度: {result.confidence:.3f}")


def test_absa():
    """测试维度分析"""
    print("\n" + "="*50)
    print("测试维度分析 (ABSA)")
    print("="*50)
    
    from app.services.nlp import ABSAExtractor
    
    extractor = ABSAExtractor()
    
    text = """
    Die Lieferung war super schnell, nur 2 Tage!
    Aber die Qualität ist leider enttäuschend. 
    Das Material fühlt sich billig an.
    Der Preis war günstig, aber man bekommt was man bezahlt.
    """
    
    result = extractor.extract(text)
    
    print(f"\n📝 评论预览: {text[:100]}...")
    print(f"\n📊 维度得分:")
    for asp in result.aspects:
        emoji = "🟢" if asp.score > 0.6 else "🔴" if asp.score < 0.4 else "🟡"
        print(f"   {emoji} {asp.aspect_zh}: {asp.score:.3f} (关键词: {', '.join(asp.keywords_found[:3])})")
    
    print(f"\n📈 整体得分: {result.overall_score:.3f}")


def test_full_analysis():
    """测试完整分析流程"""
    print("\n" + "="*50)
    print("测试完整评论分析")
    print("="*50)
    
    from app.services import ReviewAnalyzer
    
    analyzer = ReviewAnalyzer(translate=True)
    
    text = "Die Verpackung war beschädigt, aber das Produkt selbst ist in Ordnung. Schnelle Lieferung!"
    
    result = analyzer.analyze_single(text)
    
    print(f"\n📝 原文: {result.original_text}")
    print(f"🇨🇳 翻译: {result.translated_text}")
    print(f"😊 情感: {result.sentiment} ({result.sentiment_score:.3f})")
    print(f"📊 维度: {result.aspects}")
    print(f"🔑 关键词: {result.keywords[:5]}")


if __name__ == "__main__":
    print("="*60)
    print("   GermanMarket.AI - NLP功能测试")
    print("="*60)
    
    # 选择测试项
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", choices=["sentiment", "absa", "full", "all"], default="all")
    args = parser.parse_args()
    
    if args.test in ["sentiment", "all"]:
        test_sentiment()
    
    if args.test in ["absa", "all"]:
        test_absa()
    
    if args.test in ["full", "all"]:
        test_full_analysis()
    
    print("\n" + "="*60)
    print("   测试完成!")
    print("="*60)

