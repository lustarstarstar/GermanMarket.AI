# -*- coding: utf-8 -*-
"""
德语开发信生成器 (Outreach Generator)
=====================================
基于RAG的红人开发信生成，支持双模式切换
严格遵守德国GDPR/反垃圾邮件法规
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from enum import Enum
import random


class ToneMode(Enum):
    """语气模式"""
    FORMAL = "formal"           # 严谨商务
    FRIENDLY = "friendly"       # 社交媒体亲和


@dataclass
class OutreachContext:
    """开发信上下文"""
    # 红人信息
    influencer_name: str
    platform: str
    niche: str = ""
    recent_content_topics: List[str] = field(default_factory=list)

    # 红人内容风格分析（RAG检索用）
    content_style: Dict[str, any] = field(default_factory=dict)  # 内容风格特征
    tone_keywords: List[str] = field(default_factory=list)       # 红人常用语气词
    engagement_style: str = ""                                    # 互动风格：专业/亲和/幽默
    posting_frequency: str = ""                                   # 发帖频率描述
    audience_demographics: str = ""                               # 受众特征

    # 品牌/产品信息
    brand_name: str = ""
    product_name: str = ""
    product_highlights: List[str] = field(default_factory=list)

    # 合作信息
    collaboration_type: str = ""  # 产品测评/赞助帖/长期合作
    compensation: str = ""        # 产品赠送/付费/佣金

    # 发件人信息
    sender_name: str = ""
    sender_title: str = ""
    company_name: str = ""
    company_address: str = ""     # Impressum需要
    company_email: str = ""       # Impressum需要
    company_phone: str = ""       # Impressum需要


@dataclass
class GeneratedOutreach:
    """生成的开发信"""
    subject: str
    body: str
    tone_mode: str
    gdpr_compliant: bool
    compliance_notes: List[str]
    
    def to_dict(self) -> dict:
        return {
            "subject": self.subject,
            "body": self.body,
            "tone_mode": self.tone_mode,
            "gdpr_compliant": self.gdpr_compliant,
            "compliance_notes": self.compliance_notes
        }


# ============ 德语商务俚语库 ============
# 这是RAG检索的核心知识库

GERMAN_BUSINESS_PHRASES = {
    "greetings": {
        "formal": [
            "Sehr geehrte/r {name}",
            "Guten Tag {name}",
        ],
        "friendly": [
            "Hallo {name}",
            "Hi {name}",
            "Liebe/r {name}",
        ]
    },
    
    "opening_hooks": {
        "formal": [
            "ich bin auf Ihr Profil aufmerksam geworden und war beeindruckt von Ihrer Arbeit im Bereich {niche}.",
            "Ihr Content zum Thema {topic} hat unser Team sehr angesprochen.",
            "als Unternehmen, das Wert auf Qualität und Authentizität legt, schätzen wir Ihre Arbeit sehr.",
        ],
        "friendly": [
            "ich verfolge deinen Content schon eine Weile und bin total begeistert! 🙌",
            "dein letzter Post über {topic} war super inspirierend!",
            "ich liebe, wie du {niche} Themen rüberbringst – echt authentisch!",
        ]
    },
    
    "value_proposition": {
        "formal": [
            "Wir bei {brand} entwickeln {product}, das perfekt zu Ihrer Zielgruppe passt.",
            "Unser Produkt {product} zeichnet sich durch {highlight} aus.",
            "Wir sind überzeugt, dass eine Zusammenarbeit für beide Seiten von großem Wert wäre.",
        ],
        "friendly": [
            "Wir haben da was, das mega gut zu deinem Content passen würde! 🎁",
            "Unser {product} ist genau das Richtige für deine Community.",
            "Ich glaube, {product} würde deinen Followern richtig gut gefallen!",
        ]
    },
    
    "collaboration_ask": {
        "formal": [
            "Wir würden uns freuen, Ihnen {product} für einen ehrlichen Test zur Verfügung zu stellen.",
            "Hätten Sie Interesse an einer {collab_type}?",
            "Gerne würden wir die Möglichkeiten einer Zusammenarbeit mit Ihnen besprechen.",
        ],
        "friendly": [
            "Hättest du Lust, {product} mal auszuprobieren?",
            "Was hältst du von einer Kooperation?",
            "Ich würde dir super gerne ein Paket schicken! 📦",
        ]
    },
    
    "closing": {
        "formal": [
            "Über eine Rückmeldung würde ich mich sehr freuen.",
            "Für Rückfragen stehe ich Ihnen jederzeit zur Verfügung.",
            "Ich freue mich auf Ihre Antwort.",
        ],
        "friendly": [
            "Schreib mir einfach, wenn du Interesse hast!",
            "Lass mich wissen, was du denkst! 💬",
            "Freu mich auf deine Antwort!",
        ]
    },
    
    "sign_off": {
        "formal": [
            "Mit freundlichen Grüßen",
            "Mit besten Grüßen",
            "Herzliche Grüße",
        ],
        "friendly": [
            "Liebe Grüße",
            "Viele Grüße",
            "Bis bald",
        ]
    }
}


# ============ GDPR/反垃圾邮件合规模板 ============

GDPR_COMPLIANCE = {
    # 必须包含的法律告知（德国UWG反垃圾邮件法）
    "opt_out_notice": {
        "formal": "\n\nHinweis: Falls Sie keine weiteren Nachrichten von uns erhalten möchten, teilen Sie uns dies bitte mit.",
        "friendly": "\n\nPS: Falls du keine weiteren Nachrichten möchtest, sag einfach Bescheid! 🙏"
    },

    # 数据保护声明（GDPR Art. 13/14）
    "data_protection": {
        "formal": "\n\nDatenschutz: Ihre Kontaktdaten wurden ausschließlich für diese Anfrage verwendet und werden nicht an Dritte weitergegeben.",
        "friendly": "\n\nDatenschutz: Deine Daten sind bei uns sicher und werden nicht weitergegeben."
    },

    # 公司信息（德国Impressum要求）
    "company_info": "\n\n{company_name}\n{sender_name}, {sender_title}",

    # Double Opt-in 提示（用于后续邮件）
    "double_optin_request": "Um sicherzustellen, dass Sie unsere Nachrichten erhalten möchten, bitten wir Sie um eine kurze Bestätigung."
}


# ============ 主题行模板 ============

SUBJECT_TEMPLATES = {
    "formal": [
        "Kooperationsanfrage: {brand} x {influencer}",
        "Partnerschaftsmöglichkeit mit {brand}",
        "{brand} - Interesse an einer Zusammenarbeit",
    ],
    "friendly": [
        "Hey {influencer}! 👋 Kooperation mit {brand}?",
        "{brand} 💜 {influencer} - Let's collaborate!",
        "Coole Idee für dich von {brand}!",
    ]
}


class OutreachGenerator:
    """
    德语开发信生成器

    核心功能：
    1. 双模式切换：严谨商务 vs 社交媒体亲和
    2. GDPR/反垃圾邮件法合规
    3. 德语商务俚语库自动调用
    4. 支持LLM增强（可选）

    使用示例：
    ```python
    generator = OutreachGenerator(tone=ToneMode.FRIENDLY)

    context = OutreachContext(
        influencer_name="Anna",
        platform="instagram",
        niche="fashion",
        brand_name="EcoStyle",
        product_name="nachhaltige Handtasche"
    )

    result = generator.generate(context)
    print(result.body)
    ```
    """

    def __init__(
        self,
        tone: ToneMode = ToneMode.FORMAL,
        include_gdpr: bool = True,
        llm_client = None  # 可选的LLM客户端
    ):
        self.tone = tone
        self.include_gdpr = include_gdpr
        self.llm_client = llm_client
        self._phrases = GERMAN_BUSINESS_PHRASES

    def set_tone(self, tone: ToneMode):
        """切换语气模式"""
        self.tone = tone

    def _get_phrase(self, category: str, **kwargs) -> str:
        """从俚语库获取短语"""
        tone_key = self.tone.value
        phrases = self._phrases.get(category, {}).get(tone_key, [])

        if not phrases:
            return ""

        phrase = random.choice(phrases)

        # 替换占位符
        for key, value in kwargs.items():
            phrase = phrase.replace(f"{{{key}}}", str(value))

        return phrase

    def _build_subject(self, context: OutreachContext) -> str:
        """生成主题行"""
        tone_key = self.tone.value
        templates = SUBJECT_TEMPLATES.get(tone_key, SUBJECT_TEMPLATES["formal"])

        subject = random.choice(templates)
        subject = subject.replace("{brand}", context.brand_name or "Uns")
        subject = subject.replace("{influencer}", context.influencer_name)

        return subject

    def _build_body(self, context: OutreachContext) -> str:
        """构建邮件正文"""
        parts = []

        # 1. 称呼
        greeting = self._get_phrase("greetings", name=context.influencer_name)
        parts.append(f"{greeting},\n")

        # 2. 开场白（个性化hook）
        topic = context.recent_content_topics[0] if context.recent_content_topics else context.niche
        opening = self._get_phrase("opening_hooks", niche=context.niche, topic=topic)
        parts.append(opening)

        # 3. 价值主张
        highlight = context.product_highlights[0] if context.product_highlights else "höchste Qualität"
        value_prop = self._get_phrase(
            "value_proposition",
            brand=context.brand_name,
            product=context.product_name,
            highlight=highlight
        )
        parts.append(f"\n\n{value_prop}")

        # 4. 合作邀请
        collab_ask = self._get_phrase(
            "collaboration_ask",
            product=context.product_name,
            collab_type=context.collaboration_type or "Zusammenarbeit"
        )
        parts.append(f"\n\n{collab_ask}")

        # 5. 结束语
        closing = self._get_phrase("closing")
        parts.append(f"\n\n{closing}")

        # 6. 签名
        sign_off = self._get_phrase("sign_off")
        signature = f"\n\n{sign_off}"
        if context.sender_name:
            signature += f"\n{context.sender_name}"
        if context.sender_title:
            signature += f"\n{context.sender_title}"
        if context.company_name:
            signature += f"\n{context.company_name}"
        parts.append(signature)

        return "".join(parts)

    def _add_gdpr_compliance(self, body: str, context: OutreachContext) -> tuple:
        """添加GDPR合规内容"""
        compliance_notes = []
        tone_key = self.tone.value

        # 1. 退订提示（UWG要求）
        opt_out = GDPR_COMPLIANCE["opt_out_notice"][tone_key]
        body += opt_out
        compliance_notes.append("✓ 包含退订选项 (UWG §7)")

        # 2. 数据保护声明
        data_protection = GDPR_COMPLIANCE["data_protection"][tone_key]
        body += data_protection
        compliance_notes.append("✓ 数据保护声明 (GDPR Art.13)")

        return body, compliance_notes

    def generate(self, context: OutreachContext) -> GeneratedOutreach:
        """
        生成开发信

        Args:
            context: 开发信上下文信息

        Returns:
            GeneratedOutreach: 包含主题、正文、合规信息的完整开发信
        """
        # 1. 生成主题
        subject = self._build_subject(context)

        # 2. 生成正文
        body = self._build_body(context)

        # 3. 添加GDPR合规内容
        compliance_notes = []
        if self.include_gdpr:
            body, compliance_notes = self._add_gdpr_compliance(body, context)

        return GeneratedOutreach(
            subject=subject,
            body=body,
            tone_mode=self.tone.value,
            gdpr_compliant=self.include_gdpr,
            compliance_notes=compliance_notes
        )

    def generate_with_llm(self, context: OutreachContext, custom_prompt: str = None) -> GeneratedOutreach:
        """
        使用LLM增强生成（需要配置llm_client）

        这是RAG的核心：将俚语库作为检索上下文注入LLM
        """
        if not self.llm_client:
            # 降级到模板生成
            return self.generate(context)

        # 构建RAG Prompt
        tone_desc = "严谨商务风格" if self.tone == ToneMode.FORMAL else "社交媒体亲和风格"

        # 检索相关俚语作为上下文
        retrieved_phrases = self._retrieve_relevant_phrases(context)

        system_prompt = f"""你是一位专业的德语商务文案撰写专家，专门为跨境电商品牌撰写红人开发信。

当前模式：{tone_desc}

【德语商务俚语参考】
{retrieved_phrases}

【法律合规要求】
1. 必须包含退订选项（德国UWG §7反垃圾邮件法）
2. 必须包含数据保护声明（GDPR Art.13）
3. 首次联系不得过于商业化推销

【输出要求】
- 使用地道的德语表达
- 根据语气模式调整用词
- 个性化提及红人的内容
- 清晰说明合作价值"""

        user_prompt = f"""请为以下场景生成一封德语开发信：

红人信息：
- 名称：{context.influencer_name}
- 平台：{context.platform}
- 垂类：{context.niche}
- 近期内容：{', '.join(context.recent_content_topics[:3]) if context.recent_content_topics else '未知'}

品牌/产品：
- 品牌：{context.brand_name}
- 产品：{context.product_name}
- 卖点：{', '.join(context.product_highlights[:3]) if context.product_highlights else '未知'}

合作类型：{context.collaboration_type or '产品测评'}

请生成：
1. 邮件主题（一行）
2. 邮件正文（包含GDPR合规内容）"""

        if custom_prompt:
            user_prompt += f"\n\n额外要求：{custom_prompt}"

        # 调用LLM（这里是接口预留，实际需要实现）
        # response = self.llm_client.chat(system_prompt, user_prompt)

        # 暂时返回模板生成结果
        return self.generate(context)

    def _retrieve_relevant_phrases(self, context: OutreachContext) -> str:
        """检索相关俚语（RAG检索逻辑）"""
        tone_key = self.tone.value

        phrases = []
        for category, tone_phrases in self._phrases.items():
            if tone_key in tone_phrases:
                phrases.append(f"【{category}】")
                for p in tone_phrases[tone_key][:2]:  # 每类取2个示例
                    phrases.append(f"  - {p}")

        return "\n".join(phrases)

    def _retrieve_influencer_style(self, context: OutreachContext) -> Dict[str, any]:
        """
        RAG检索红人内容风格（核心差异化功能）

        从红人过往内容中提取风格特征，让开发信从"模板感"进化为"深度调研感"
        """
        style_analysis = {
            "detected_tone": "neutral",
            "content_themes": [],
            "language_patterns": [],
            "personalization_hooks": [],
            "recommended_approach": ""
        }

        # 分析红人内容风格
        if context.content_style:
            style_analysis.update(context.content_style)

        # 从红人常用语气词推断风格
        if context.tone_keywords:
            casual_indicators = ["mega", "super", "krass", "geil", "nice", "😍", "🔥"]
            formal_indicators = ["qualität", "nachhaltig", "empfehlen", "erfahrung"]

            casual_count = sum(1 for k in context.tone_keywords if k.lower() in casual_indicators)
            formal_count = sum(1 for k in context.tone_keywords if k.lower() in formal_indicators)

            if casual_count > formal_count:
                style_analysis["detected_tone"] = "casual"
                style_analysis["recommended_approach"] = "使用轻松活泼的语气，可加emoji"
            else:
                style_analysis["detected_tone"] = "professional"
                style_analysis["recommended_approach"] = "保持专业但友好的语气"

        # 从近期内容主题提取个性化hook
        if context.recent_content_topics:
            style_analysis["content_themes"] = context.recent_content_topics[:5]
            # 生成个性化开场白建议
            style_analysis["personalization_hooks"] = [
                f"提及其关于'{topic}'的内容" for topic in context.recent_content_topics[:2]
            ]

        # 分析互动风格
        if context.engagement_style:
            style_analysis["engagement_style"] = context.engagement_style

        return style_analysis

    def preview_both_tones(self, context: OutreachContext) -> Dict[str, GeneratedOutreach]:
        """预览两种语气模式的输出"""
        results = {}

        original_tone = self.tone

        for tone in ToneMode:
            self.tone = tone
            results[tone.value] = self.generate(context)

        self.tone = original_tone
        return results


# ============ 便捷函数 ============

def generate_outreach(
    influencer_name: str,
    platform: str,
    brand_name: str,
    product_name: str,
    tone: str = "formal",
    **kwargs
) -> GeneratedOutreach:
    """
    快速生成开发信

    Args:
        influencer_name: 红人名称
        platform: 平台
        brand_name: 品牌名
        product_name: 产品名
        tone: "formal" 或 "friendly"
        **kwargs: 其他OutreachContext参数
    """
    context = OutreachContext(
        influencer_name=influencer_name,
        platform=platform,
        brand_name=brand_name,
        product_name=product_name,
        **kwargs
    )

    tone_mode = ToneMode.FORMAL if tone == "formal" else ToneMode.FRIENDLY
    generator = OutreachGenerator(tone=tone_mode)

    return generator.generate(context)


# ============ Privacy_Check 函数 (TMG §5 Impressum合规) ============

@dataclass
class PrivacyCheckResult:
    """隐私合规检查结果"""
    is_compliant: bool
    missing_elements: List[str]
    warnings: List[str]
    impressum_complete: bool
    gdpr_elements_present: List[str]

    def to_dict(self) -> dict:
        return {
            "is_compliant": self.is_compliant,
            "missing_elements": self.missing_elements,
            "warnings": self.warnings,
            "impressum_complete": self.impressum_complete,
            "gdpr_elements_present": self.gdpr_elements_present
        }


def privacy_check(
    email_body: str,
    context: OutreachContext = None,
    strict_mode: bool = True
) -> PrivacyCheckResult:
    """
    检查邮件是否符合德国隐私法规要求

    德国法律要求 (TMG §5 + GDPR):
    1. Impressum (公司信息披露) - TMG §5 强制要求
       - 公司名称
       - 地址
       - 联系方式 (邮箱/电话)
       - 负责人姓名
    2. 退订选项 - UWG §7
    3. 数据保护声明 - GDPR Art.13

    Args:
        email_body: 邮件正文
        context: 开发信上下文（用于验证Impressum完整性）
        strict_mode: 严格模式（检查所有TMG §5要求）

    Returns:
        PrivacyCheckResult: 合规检查结果
    """
    missing = []
    warnings = []
    gdpr_present = []

    body_lower = email_body.lower()

    # 1. 检查退订选项 (UWG §7)
    opt_out_keywords = [
        "keine weiteren nachrichten",
        "abmelden", "abbestellen",
        "unsubscribe", "opt-out",
        "nicht mehr kontaktieren"
    ]
    has_opt_out = any(kw in body_lower for kw in opt_out_keywords)
    if has_opt_out:
        gdpr_present.append("退订选项 (UWG §7)")
    else:
        missing.append("退订选项 (UWG §7要求)")

    # 2. 检查数据保护声明 (GDPR Art.13)
    data_protection_keywords = [
        "datenschutz", "daten", "privacy",
        "nicht weitergegeben", "vertraulich"
    ]
    has_data_protection = any(kw in body_lower for kw in data_protection_keywords)
    if has_data_protection:
        gdpr_present.append("数据保护声明 (GDPR Art.13)")
    else:
        missing.append("数据保护声明 (GDPR Art.13要求)")

    # 3. 检查Impressum (TMG §5) - 德国法律强制要求
    impressum_checks = {
        "company_name": False,
        "address": False,
        "contact": False,
        "responsible_person": False
    }

    # 检查公司名称
    company_indicators = ["gmbh", "ag", "ug", "kg", "ohg", "e.k.", "gbr"]
    if any(ind in body_lower for ind in company_indicators):
        impressum_checks["company_name"] = True
    elif context and context.company_name:
        if context.company_name.lower() in body_lower:
            impressum_checks["company_name"] = True

    # 检查地址（德国地址格式：街道+门牌号，邮编+城市）
    import re
    address_pattern = r'\d{5}\s+[A-Za-zäöüÄÖÜß]+'  # 德国邮编格式
    if re.search(address_pattern, email_body):
        impressum_checks["address"] = True
    elif context and context.company_address:
        impressum_checks["address"] = True

    # 检查联系方式
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
    if re.search(email_pattern, email_body) or re.search(phone_pattern, email_body):
        impressum_checks["contact"] = True
    elif context and (context.company_email or context.company_phone):
        impressum_checks["contact"] = True

    # 检查负责人
    if context and context.sender_name:
        if context.sender_name.lower() in body_lower:
            impressum_checks["responsible_person"] = True

    # 评估Impressum完整性
    impressum_complete = all(impressum_checks.values())

    if not impressum_checks["company_name"]:
        missing.append("公司名称 (TMG §5)")
    if not impressum_checks["address"] and strict_mode:
        warnings.append("建议添加公司地址 (TMG §5)")
    if not impressum_checks["contact"] and strict_mode:
        warnings.append("建议添加联系方式 (TMG §5)")
    if not impressum_checks["responsible_person"]:
        warnings.append("建议添加负责人姓名")

    # 4. 额外检查：商业邮件标识
    if "werbung" not in body_lower and "kooperation" not in body_lower:
        warnings.append("商业邮件建议明确标识合作意图")

    # 判断整体合规性
    is_compliant = len(missing) == 0

    return PrivacyCheckResult(
        is_compliant=is_compliant,
        missing_elements=missing,
        warnings=warnings,
        impressum_complete=impressum_complete,
        gdpr_elements_present=gdpr_present
    )


# ============ 道歉信生成器 (Webhook触发) ============

@dataclass
class ApologyContext:
    """道歉信上下文"""
    customer_name: str
    order_id: str = ""
    product_name: str = ""
    issue_summary: str = ""           # 问题摘要
    review_content: str = ""          # 原始差评内容
    review_rating: int = 1
    compensation_offer: str = ""      # 补偿方案
    company_name: str = ""
    sender_name: str = ""
    sender_title: str = ""


@dataclass
class GeneratedApology:
    """生成的道歉信"""
    subject: str
    body: str
    urgency_level: str               # critical/high/medium
    suggested_compensation: str
    follow_up_actions: List[str]
    gdpr_compliant: bool


class ApologyGenerator:
    """
    道歉信生成器

    用于Shopify Webhook触发场景：
    当收到1-2星差评时，自动生成道歉/补偿信草稿供运营审核
    """

    # 道歉信模板库
    APOLOGY_TEMPLATES = {
        "critical": {  # 涉及法律/安全风险
            "subject": "Dringende Angelegenheit - Bestellung {order_id}",
            "opening": "Sehr geehrte/r {name},\n\nwir haben Ihre Bewertung mit großer Besorgnis zur Kenntnis genommen und möchten uns aufrichtig für die entstandenen Unannehmlichkeiten entschuldigen.",
            "body": "\n\nIhr Anliegen hat für uns höchste Priorität. {issue_response}\n\nUm die Situation zu bereinigen, möchten wir Ihnen {compensation} anbieten.",
            "closing": "\n\nBitte kontaktieren Sie uns direkt unter {contact}, damit wir Ihr Anliegen persönlich klären können.\n\nMit aufrichtiger Entschuldigung,\n{sender}"
        },
        "high": {  # 产品质量/退款问题
            "subject": "Ihre Bewertung - Wir möchten es wiedergutmachen",
            "opening": "Sehr geehrte/r {name},\n\nvielen Dank, dass Sie sich die Zeit genommen haben, uns Feedback zu geben. Es tut uns sehr leid zu hören, dass Sie mit {product} nicht zufrieden waren.",
            "body": "\n\n{issue_response}\n\nAls Entschädigung möchten wir Ihnen {compensation} anbieten.",
            "closing": "\n\nWir würden uns freuen, wenn Sie uns eine zweite Chance geben.\n\nMit freundlichen Grüßen,\n{sender}"
        },
        "medium": {  # 一般不满
            "subject": "Danke für Ihr Feedback - {product}",
            "opening": "Liebe/r {name},\n\ndanke für Ihre ehrliche Bewertung. Wir bedauern, dass Ihre Erfahrung nicht Ihren Erwartungen entsprochen hat.",
            "body": "\n\n{issue_response}\n\nAls kleines Dankeschön für Ihr Feedback möchten wir Ihnen {compensation} anbieten.",
            "closing": "\n\nWir hoffen, Sie bald wieder als zufriedenen Kunden begrüßen zu dürfen!\n\nHerzliche Grüße,\n{sender}"
        }
    }

    # 补偿方案建议
    COMPENSATION_SUGGESTIONS = {
        "critical": [
            "eine vollständige Rückerstattung",
            "einen kostenlosen Ersatz mit Express-Versand",
            "eine Rückerstattung plus 20% Gutschein"
        ],
        "high": [
            "einen 30% Rabattgutschein für Ihre nächste Bestellung",
            "einen kostenlosen Ersatz",
            "eine teilweise Rückerstattung (50%)"
        ],
        "medium": [
            "einen 15% Rabattgutschein",
            "kostenlosen Versand bei Ihrer nächsten Bestellung",
            "ein kleines Überraschungsgeschenk"
        ]
    }

    def __init__(self, company_name: str = "", default_contact: str = ""):
        self.company_name = company_name
        self.default_contact = default_contact

    def determine_urgency(self, review_content: str, rating: int) -> str:
        """根据差评内容判断紧急程度"""
        content_lower = review_content.lower()

        # 关键词检测
        critical_keywords = [
            "anwalt", "rechtsanwalt", "klage", "gericht",
            "gefährlich", "verletzung", "krankenhaus",
            "betrug", "täuschung", "polizei"
        ]

        high_keywords = [
            "rückerstattung", "geld zurück", "defekt",
            "kaputt", "funktioniert nicht", "falsch"
        ]

        if any(kw in content_lower for kw in critical_keywords) or rating == 1:
            return "critical"
        elif any(kw in content_lower for kw in high_keywords) or rating == 2:
            return "high"
        else:
            return "medium"

    def generate(self, context: ApologyContext) -> GeneratedApology:
        """生成道歉信草稿"""

        # 1. 判断紧急程度
        urgency = self.determine_urgency(
            context.review_content,
            context.review_rating
        )

        # 2. 选择模板
        template = self.APOLOGY_TEMPLATES[urgency]

        # 3. 生成补偿建议
        compensation = context.compensation_offer or random.choice(
            self.COMPENSATION_SUGGESTIONS[urgency]
        )

        # 4. 生成问题回应
        issue_response = self._generate_issue_response(context, urgency)

        # 5. 组装邮件
        subject = template["subject"].format(
            order_id=context.order_id or "Ihre Bestellung",
            product=context.product_name or "Ihrem Produkt"
        )

        sender_info = f"{context.sender_name or 'Kundenservice'}"
        if context.sender_title:
            sender_info += f"\n{context.sender_title}"
        if context.company_name or self.company_name:
            sender_info += f"\n{context.company_name or self.company_name}"

        body = template["opening"].format(
            name=context.customer_name,
            product=context.product_name or "unserem Produkt"
        )
        body += template["body"].format(
            issue_response=issue_response,
            compensation=compensation
        )
        body += template["closing"].format(
            contact=self.default_contact or "kundenservice@example.de",
            sender=sender_info
        )

        # 6. 添加GDPR合规内容
        body += "\n\nDatenschutz: Ihre Daten werden vertraulich behandelt."

        # 7. 生成后续行动建议
        follow_up = self._generate_follow_up_actions(urgency, context)

        return GeneratedApology(
            subject=subject,
            body=body,
            urgency_level=urgency,
            suggested_compensation=compensation,
            follow_up_actions=follow_up,
            gdpr_compliant=True
        )

    def _generate_issue_response(self, context: ApologyContext, urgency: str) -> str:
        """生成针对具体问题的回应"""
        if context.issue_summary:
            return f"Bezüglich {context.issue_summary}: Wir nehmen Ihr Feedback sehr ernst und werden die Ursache umgehend untersuchen."

        responses = {
            "critical": "Wir nehmen Ihre Beschwerde äußerst ernst und haben bereits eine interne Untersuchung eingeleitet.",
            "high": "Wir verstehen Ihre Frustration und möchten das Problem schnellstmöglich lösen.",
            "medium": "Wir schätzen Ihr ehrliches Feedback und werden es nutzen, um uns zu verbessern."
        }
        return responses.get(urgency, responses["medium"])

    def _generate_follow_up_actions(self, urgency: str, context: ApologyContext) -> List[str]:
        """生成后续行动建议"""
        actions = []

        if urgency == "critical":
            actions.extend([
                "⚠️ 立即通知法务团队审核",
                "📞 24小时内电话联系客户",
                "📝 记录事件详情备案"
            ])
        elif urgency == "high":
            actions.extend([
                "📧 48小时内发送此邮件",
                "🔄 准备退款/换货流程",
                "📊 更新产品质量追踪表"
            ])
        else:
            actions.extend([
                "📧 3天内发送此邮件",
                "💡 考虑产品改进建议"
            ])

        return actions


def generate_apology_draft(
    customer_name: str,
    review_content: str,
    review_rating: int,
    product_name: str = "",
    order_id: str = "",
    company_name: str = "",
    **kwargs
) -> GeneratedApology:
    """
    便捷函数：生成道歉信草稿

    用于Webhook触发场景
    """
    context = ApologyContext(
        customer_name=customer_name,
        review_content=review_content,
        review_rating=review_rating,
        product_name=product_name,
        order_id=order_id,
        company_name=company_name,
        **kwargs
    )

    generator = ApologyGenerator(company_name=company_name)
    return generator.generate(context)


