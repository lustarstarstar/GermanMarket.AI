# -*- coding: utf-8 -*-
"""
GermanMarket.AI 核心模块测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta


class TestInfluencerEvaluator:
    """红人评估器测试"""
    
    def test_evaluator_basic(self):
        """基础评估流程"""
        from app.services.influencer import (
            InfluencerEvaluator, InfluencerProfile, Platform
        )
        
        # 构造测试数据：一个健康的德国时尚博主
        profile = InfluencerProfile(
            platform=Platform.INSTAGRAM,
            username="test_influencer",
            followers=50000,
            following=500,
            posts_count=200,
            avg_likes=2500,
            avg_comments=150,
            bio="Nachhaltige Mode aus Berlin 🌿 | Qualität über Quantität",
            recent_captions=["Mein neues nachhaltiges Outfit", "Umweltfreundlich und stylisch"],
            hashtags=["nachhaltig", "fashion", "berlin", "sustainable"],
            recent_post_dates=[datetime.now() - timedelta(days=i) for i in range(1, 11)]
        )
        
        evaluator = InfluencerEvaluator(target_niche="fashion")
        result = evaluator.evaluate(profile)
        
        # 验证结果结构
        assert result.username == "test_influencer"
        assert result.platform == "instagram"
        assert 0 <= result.activity_score <= 100
        assert 0 <= result.authenticity_score <= 100
        assert 0 <= result.relevance_score <= 100
        assert result.grade in ["S", "A", "B", "C", "D"]
        
        # 这个profile应该得到较高分（健康数据+德国关键词匹配）
        assert result.total_score >= 50
        
        # 应该检测到可持续性关键词
        assert result.german_market_fit.get("sustainability_focus") == True
        
        print(f"评估结果: {result.grade} ({result.total_score:.1f}分)")
        print(f"德国市场契合度: {result.german_market_fit}")

    def test_fake_influencer_detection(self):
        """检测疑似刷量账号"""
        from app.services.influencer import (
            InfluencerEvaluator, InfluencerProfile, Platform
        )
        
        # 构造可疑数据：粉丝多但互动异常低
        fake_profile = InfluencerProfile(
            platform=Platform.INSTAGRAM,
            username="suspicious_account",
            followers=100000,
            following=8000,  # 关注太多（互关党特征）
            posts_count=50,
            avg_likes=200,   # 10万粉只有200赞（0.2%互动率）
            avg_comments=5,
            bio="Follow for follow",
            recent_post_dates=[datetime.now() - timedelta(days=45)]  # 很久没更新
        )
        
        evaluator = InfluencerEvaluator()
        result = evaluator.evaluate(fake_profile)
        
        # 应该得到较低分
        assert result.total_score < 50
        # 应该有风险标记
        assert len(result.risk_flags) > 0
        
        print(f"可疑账号评分: {result.grade} ({result.total_score:.1f}分)")
        print(f"风险标记: {result.risk_flags}")


class TestOutreachGenerator:
    """开发信生成器测试"""
    
    def test_formal_mode(self):
        """严谨商务模式"""
        from app.services.content import (
            OutreachGenerator, OutreachContext, ToneMode
        )
        
        context = OutreachContext(
            influencer_name="Frau Schmidt",
            platform="instagram",
            niche="fashion",
            brand_name="EcoStyle",
            product_name="nachhaltige Handtasche",
            sender_name="Li Wei",
            sender_title="Partnership Manager",
            company_name="EcoStyle GmbH"
        )
        
        generator = OutreachGenerator(tone=ToneMode.FORMAL)
        result = generator.generate(context)
        
        # 验证结构
        assert result.subject
        assert result.body
        assert result.tone_mode == "formal"
        assert result.gdpr_compliant == True
        
        # 验证GDPR合规内容
        assert "Datenschutz" in result.body or "weiteren Nachrichten" in result.body
        assert len(result.compliance_notes) >= 2
        
        print("=== 严谨商务模式 ===")
        print(f"主题: {result.subject}")
        print(f"正文:\n{result.body[:500]}...")

    def test_friendly_mode(self):
        """社交媒体亲和模式"""
        from app.services.content import (
            OutreachGenerator, OutreachContext, ToneMode
        )
        
        context = OutreachContext(
            influencer_name="Anna",
            platform="tiktok",
            niche="beauty",
            recent_content_topics=["Skincare Routine", "Naturkosmetik"],
            brand_name="GlowUp",
            product_name="Bio-Serum"
        )
        
        generator = OutreachGenerator(tone=ToneMode.FRIENDLY)
        result = generator.generate(context)
        
        assert result.tone_mode == "friendly"
        # 友好模式应该有emoji或更轻松的用语
        
        print("\n=== 社交媒体亲和模式 ===")
        print(f"主题: {result.subject}")
        print(f"正文:\n{result.body[:500]}...")


class TestShopifyIntegration:
    """Shopify数据集成测试"""
    
    def test_csv_import(self):
        """CSV导入测试"""
        from app.services.shopify import import_reviews_from_csv
        
        # 模拟CSV内容
        csv_content = """review_id,content,rating,product_name,date
1,"Das Produkt ist super! Schnelle Lieferung.",5,Handtasche,2024-01-15
2,"Leider defekt angekommen. Sehr enttäuscht.",1,Handtasche,2024-01-16
3,"Qualität ist okay, aber teuer.",3,Handtasche,2024-01-17
4,"Ich werde meinen Anwalt einschalten! Betrug!",1,Handtasche,2024-01-18
5,"Gefährlich! Mein Kind hat sich verletzt.",1,Spielzeug,2024-01-19
"""
        
        result = import_reviews_from_csv(csv_content)
        
        assert result.success == True
        assert result.imported_count == 5
        assert len(result.reviews) == 5
        
        print(f"\n=== CSV导入测试 ===")
        print(f"导入成功: {result.imported_count} 条")

    def test_risk_detection(self):
        """高风险差评检测"""
        from app.services.shopify import detect_review_risk, RiskLevel
        
        # 测试法律风险
        legal_risk = detect_review_risk(
            "Ich werde meinen Anwalt einschalten! Das ist Betrug!",
            rating=1
        )
        assert legal_risk["risk_level"] == RiskLevel.CRITICAL
        assert "legal" in str(legal_risk["matched_keywords"])
        
        # 测试安全风险
        safety_risk = detect_review_risk(
            "Gefährlich! Das Produkt ist explodiert und ich musste ins Krankenhaus.",
            rating=1
        )
        assert safety_risk["risk_level"] == RiskLevel.CRITICAL
        
        # 测试退款风险
        refund_risk = detect_review_risk(
            "Ich möchte eine Rückerstattung! Geld zurück!",
            rating=2
        )
        assert refund_risk["risk_level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # 测试正常评论
        normal = detect_review_risk(
            "Das Produkt ist ganz okay, nichts Besonderes.",
            rating=3
        )
        assert normal["risk_level"] == RiskLevel.LOW
        
        print("\n=== 风险检测测试 ===")
        print(f"法律风险: {legal_risk['risk_level'].value} - {legal_risk['alerts']}")
        print(f"安全风险: {safety_risk['risk_level'].value}")
        print(f"退款风险: {refund_risk['risk_level'].value}")
        print(f"正常评论: {normal['risk_level'].value}")


if __name__ == "__main__":
    # 快速运行测试
    print("=" * 60)
    print("GermanMarket.AI 核心模块测试")
    print("=" * 60)
    
    # 红人评估测试
    test_influencer = TestInfluencerEvaluator()
    test_influencer.test_evaluator_basic()
    test_influencer.test_fake_influencer_detection()
    
    # 开发信生成测试
    test_outreach = TestOutreachGenerator()
    test_outreach.test_formal_mode()
    test_outreach.test_friendly_mode()
    
    # Shopify集成测试
    test_shopify = TestShopifyIntegration()
    test_shopify.test_csv_import()
    test_shopify.test_risk_detection()
    
    print("\n" + "=" * 60)
    print("所有测试完成!")
    print("=" * 60)

