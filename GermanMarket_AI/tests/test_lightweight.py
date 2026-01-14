# -*- coding: utf-8 -*-
"""
GermanMarket.AI 核心模块轻量测试（无外部依赖）
直接导入新模块，绕过torch等依赖
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from datetime import datetime, timedelta

# 直接导入模块文件，避免触发__init__.py的连锁导入
import importlib.util

def load_module_direct(module_name, file_path):
    """直接加载模块文件"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# 加载新开发的模块
evaluator_module = load_module_direct(
    "evaluator",
    os.path.join(project_root, "app/services/influencer/evaluator.py")
)
outreach_module = load_module_direct(
    "outreach_generator",
    os.path.join(project_root, "app/services/content/outreach_generator.py")
)
shopify_module = load_module_direct(
    "shopify_integration",
    os.path.join(project_root, "app/services/shopify/__init__.py")
)

# 从模块中获取类
InfluencerEvaluator = evaluator_module.InfluencerEvaluator
InfluencerProfile = evaluator_module.InfluencerProfile
Platform = evaluator_module.Platform

OutreachGenerator = outreach_module.OutreachGenerator
OutreachContext = outreach_module.OutreachContext
ToneMode = outreach_module.ToneMode

# 新增功能
privacy_check = outreach_module.privacy_check
ApologyGenerator = outreach_module.ApologyGenerator
ApologyContext = outreach_module.ApologyContext
generate_apology_draft = outreach_module.generate_apology_draft

ShopifyDataImporter = shopify_module.ShopifyDataImporter
RiskDetector = shopify_module.RiskDetector
RiskLevel = shopify_module.RiskLevel
import_reviews_from_csv = shopify_module.import_reviews_from_csv
detect_review_risk = shopify_module.detect_review_risk


def test_influencer_evaluator():
    """测试红人评估器"""
    print("\n" + "="*50)
    print("测试1: 红人评估器 (Influencer Evaluator)")
    print("="*50)
    
    # 健康的德国时尚博主
    profile = InfluencerProfile(
        platform=Platform.INSTAGRAM,
        username="eco_fashion_berlin",
        followers=50000,
        following=500,
        posts_count=200,
        avg_likes=2500,
        avg_comments=150,
        bio="Nachhaltige Mode aus Berlin 🌿 | Qualität über Quantität | Umweltfreundlich leben",
        recent_captions=[
            "Mein neues nachhaltiges Outfit für den Herbst",
            "Qualität statt Quantität - meine Philosophie",
            "Umweltfreundlich und trotzdem stylisch"
        ],
        hashtags=["nachhaltig", "fashion", "berlin", "sustainable", "öko"],
        recent_post_dates=[datetime.now() - timedelta(days=i) for i in range(1, 11)]
    )
    
    evaluator = InfluencerEvaluator(target_niche="fashion")
    result = evaluator.evaluate(profile)
    
    print(f"\n红人: @{result.username} ({result.platform})")
    print(f"综合评分: {result.total_score:.1f}/100 (等级: {result.grade})")
    print(f"  - 活跃度: {result.activity_score:.1f}")
    print(f"  - 真实性: {result.authenticity_score:.1f}")
    print(f"  - 相关度: {result.relevance_score:.1f}")
    print(f"\n德国市场契合度:")
    print(f"  - 可持续性关注: {result.german_market_fit.get('sustainability_focus', False)}")
    print(f"  - 价值观关键词: {list(result.german_market_fit.get('keywords_found', {}).keys())}")
    print(f"\n建议: {result.recommendation}")
    
    # 测试可疑账号
    print("\n--- 测试可疑账号 ---")
    fake_profile = InfluencerProfile(
        platform=Platform.INSTAGRAM,
        username="buy_followers_123",
        followers=100000,
        following=9500,  # 互关党特征
        posts_count=30,
        avg_likes=150,   # 0.15%互动率
        avg_comments=3,
        bio="Follow 4 Follow | DM for promo",
        recent_post_dates=[datetime.now() - timedelta(days=60)]
    )
    
    fake_result = evaluator.evaluate(fake_profile)
    print(f"可疑账号: @{fake_result.username}")
    print(f"评分: {fake_result.total_score:.1f}/100 (等级: {fake_result.grade})")
    print(f"风险标记: {fake_result.risk_flags}")
    
    assert result.total_score > fake_result.total_score, "健康账号应该比可疑账号分数高"
    print("\n✅ 红人评估器测试通过!")


def test_outreach_generator():
    """测试开发信生成器"""
    print("\n" + "="*50)
    print("测试2: 开发信生成器 (Outreach Generator)")
    print("="*50)
    
    context = OutreachContext(
        influencer_name="Frau Schmidt",
        platform="instagram",
        niche="fashion",
        recent_content_topics=["Nachhaltige Mode", "Herbst Outfits"],
        brand_name="EcoStyle",
        product_name="nachhaltige Lederhandtasche",
        product_highlights=["100% recyceltes Leder", "Made in Germany"],
        collaboration_type="Produkttest",
        sender_name="Li Wei",
        sender_title="Partnership Manager",
        company_name="EcoStyle GmbH"
    )
    
    # 测试严谨商务模式
    print("\n--- 严谨商务模式 (Formal) ---")
    formal_gen = OutreachGenerator(tone=ToneMode.FORMAL)
    formal_result = formal_gen.generate(context)
    
    print(f"主题: {formal_result.subject}")
    print(f"正文预览:\n{formal_result.body[:400]}...")
    print(f"\nGDPR合规: {formal_result.gdpr_compliant}")
    print(f"合规项: {formal_result.compliance_notes}")
    
    # 测试社交媒体亲和模式
    print("\n--- 社交媒体亲和模式 (Friendly) ---")
    context.influencer_name = "Anna"
    friendly_gen = OutreachGenerator(tone=ToneMode.FRIENDLY)
    friendly_result = friendly_gen.generate(context)
    
    print(f"主题: {friendly_result.subject}")
    print(f"正文预览:\n{friendly_result.body[:400]}...")
    
    assert "Datenschutz" in formal_result.body or "Nachrichten" in formal_result.body
    print("\n✅ 开发信生成器测试通过!")


def test_shopify_integration():
    """测试Shopify数据集成"""
    print("\n" + "="*50)
    print("测试3: Shopify数据集成 + 风险检测")
    print("="*50)
    
    # 测试CSV导入
    print("\n--- CSV导入测试 ---")
    csv_content = """review_id,content,rating,product_name,date
1,"Das Produkt ist super! Schnelle Lieferung und tolle Qualität.",5,Handtasche,2024-01-15
2,"Leider defekt angekommen. Sehr enttäuscht von der Qualität.",2,Handtasche,2024-01-16
3,"Preis-Leistung ist okay, nichts Besonderes.",3,Handtasche,2024-01-17
4,"Ich werde meinen Anwalt einschalten! Das ist Betrug! Täuschung!",1,Handtasche,2024-01-18
5,"Gefährlich! Das Produkt ist explodiert. Mein Kind musste ins Krankenhaus!",1,Spielzeug,2024-01-19
6,"Möchte Rückerstattung! Geld zurück bitte!",1,Elektronik,2024-01-20
"""
    
    result = import_reviews_from_csv(csv_content)
    print(f"导入结果: {result.imported_count}/{result.total_records} 条成功")
    
    # 统计风险分布
    risk_counts = {}
    for review in result.reviews:
        level = review.risk_level.value if review.risk_level else "unknown"
        risk_counts[level] = risk_counts.get(level, 0) + 1
    
    print(f"风险分布: {risk_counts}")
    
    # 测试单条风险检测
    print("\n--- 风险检测详情 ---")
    test_cases = [
        ("Ich werde meinen Anwalt einschalten! Betrug!", 1, "法律风险"),
        ("Gefährlich! Verletzung! Krankenhaus!", 1, "安全风险"),
        ("Rückerstattung! Geld zurück!", 2, "退款风险"),
        ("Das Produkt ist ganz okay.", 3, "正常评论"),
    ]
    
    for text, rating, desc in test_cases:
        risk = detect_review_risk(text, rating)
        print(f"{desc}: {risk['risk_level'].value} | 关键词: {list(risk['matched_keywords'].keys())}")
    
    # 生成风险报告
    print("\n--- 风险报告 ---")
    importer = ShopifyDataImporter()
    report = importer.generate_risk_report(result.reviews)
    
    print(f"总评论数: {report['summary']['total_reviews']}")
    print(f"紧急风险: {report['summary']['critical_count']} 条")
    print(f"高风险: {report['summary']['high_risk_count']} 条")
    
    if report['action_items']:
        print("\n行动建议:")
        for item in report['action_items']:
            print(f"  [{item['priority']}] {item['action']}")
    
    print("\n✅ Shopify集成测试通过!")


def test_privacy_check():
    """测试Privacy_Check函数 (TMG §5合规)"""
    print("\n" + "="*50)
    print("测试4: Privacy_Check (TMG §5 Impressum合规)")
    print("="*50)

    # 测试合规邮件
    compliant_email = """
Sehr geehrte Frau Schmidt,

wir möchten Ihnen eine Kooperation anbieten.

Mit freundlichen Grüßen
Li Wei
Partnership Manager
EcoStyle GmbH
Musterstraße 123
12345 Berlin
kontakt@ecostyle.de

Falls Sie keine weiteren Nachrichten möchten, teilen Sie uns dies bitte mit.
Datenschutz: Ihre Daten werden nicht weitergegeben.
"""

    context = OutreachContext(
        influencer_name="Frau Schmidt",
        platform="instagram",
        company_name="EcoStyle GmbH",
        company_address="Musterstraße 123, 12345 Berlin",
        company_email="kontakt@ecostyle.de",
        sender_name="Li Wei"
    )

    result = privacy_check(compliant_email, context)
    print(f"\n合规邮件检查:")
    print(f"  整体合规: {result.is_compliant}")
    print(f"  Impressum完整: {result.impressum_complete}")
    print(f"  已包含: {result.gdpr_elements_present}")

    # 测试不合规邮件
    non_compliant_email = """
Hi Anna,

Willst du mit uns zusammenarbeiten?

Grüße
"""

    result2 = privacy_check(non_compliant_email)
    print(f"\n不合规邮件检查:")
    print(f"  整体合规: {result2.is_compliant}")
    print(f"  缺失项: {result2.missing_elements}")
    print(f"  警告: {result2.warnings}")

    assert result.is_compliant == True
    assert result2.is_compliant == False
    print("\n✅ Privacy_Check测试通过!")


def test_apology_generator():
    """测试道歉信生成器 (Webhook触发场景)"""
    print("\n" + "="*50)
    print("测试5: 道歉信生成器 (Webhook触发)")
    print("="*50)

    # 测试紧急级别（法律风险）
    print("\n--- 紧急级别 (Critical) ---")
    critical_apology = generate_apology_draft(
        customer_name="Herr Müller",
        review_content="Ich werde meinen Anwalt einschalten! Das ist Betrug!",
        review_rating=1,
        product_name="Elektronikgerät",
        order_id="ORD-12345",
        company_name="TechShop GmbH"
    )

    print(f"紧急程度: {critical_apology.urgency_level}")
    print(f"主题: {critical_apology.subject}")
    print(f"建议补偿: {critical_apology.suggested_compensation}")
    print(f"后续行动: {critical_apology.follow_up_actions}")

    # 测试高风险级别
    print("\n--- 高风险级别 (High) ---")
    high_apology = generate_apology_draft(
        customer_name="Frau Weber",
        review_content="Produkt defekt! Möchte Rückerstattung!",
        review_rating=2,
        product_name="Handtasche"
    )

    print(f"紧急程度: {high_apology.urgency_level}")
    print(f"主题: {high_apology.subject}")

    assert critical_apology.urgency_level == "critical"
    assert high_apology.urgency_level in ["high", "critical"]
    print("\n✅ 道歉信生成器测试通过!")


if __name__ == "__main__":
    print("="*60)
    print("GermanMarket.AI 核心模块测试")
    print("="*60)

    try:
        test_influencer_evaluator()
        test_outreach_generator()
        test_shopify_integration()
        test_privacy_check()
        test_apology_generator()

        print("\n" + "="*60)
        print("🎉 所有测试通过!")
        print("="*60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

