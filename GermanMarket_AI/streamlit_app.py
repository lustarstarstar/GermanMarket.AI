# -*- coding: utf-8 -*-
"""
GermanMarket.AI Streamlit 前端
==============================
简单易用的Web界面，供运营人员使用
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="GermanMarket.AI",
    page_icon="🇩🇪",
    layout="wide"
)

# 标题
st.title("🇩🇪 GermanMarket.AI")
st.caption("德国电商智能分析平台 - 帮中国卖家看懂德国市场")

# 侧边栏导航
page = st.sidebar.selectbox(
    "功能模块",
    ["📊 评论分析", "👥 红人管理", "✍️ 内容生成", "⚙️ 设置"]
)

# ============ 评论分析页面 ============
if page == "📊 评论分析":
    st.header("德语评论分析")
    
    tab1, tab2 = st.tabs(["单条分析", "批量分析"])
    
    with tab1:
        st.subheader("单条评论分析")
        
        # 示例评论
        example = "Die Lieferung war sehr schnell, aber die Qualität ist leider nicht so gut. Das Material fühlt sich billig an."
        
        text = st.text_area(
            "输入德语评论",
            value=example,
            height=100,
            help="粘贴德语评论文本"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            analyze_btn = st.button("🔍 分析", type="primary")
        with col2:
            translate_opt = st.checkbox("翻译为中文", value=True)
        
        if analyze_btn and text:
            with st.spinner("分析中..."):
                try:
                    # 导入分析器
                    from app.services import ReviewAnalyzer
                    analyzer = ReviewAnalyzer(translate=translate_opt)
                    result = analyzer.analyze_single(text)
                    
                    # 显示结果
                    st.success("分析完成!")
                    
                    # 情感结果
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        sentiment_emoji = {"positive": "😊", "negative": "😞", "neutral": "😐"}.get(result.sentiment, "❓")
                        st.metric("情感倾向", f"{sentiment_emoji} {result.sentiment}")
                    with col2:
                        st.metric("情感得分", f"{result.sentiment_score:.2f}")
                    with col3:
                        st.metric("关键词数", len(result.keywords))
                    
                    # 翻译
                    if translate_opt and result.translated_text:
                        st.info(f"**中文翻译**: {result.translated_text}")
                    
                    # 维度分析
                    if result.aspects:
                        st.subheader("维度分析")
                        df = pd.DataFrame([
                            {"维度": k, "得分": v, "评价": "👍" if v > 0.6 else "👎" if v < 0.4 else "➖"}
                            for k, v in result.aspects.items()
                        ])
                        st.dataframe(df, use_container_width=True)
                    
                    # 关键词
                    st.subheader("关键词")
                    st.write(" | ".join(result.keywords[:10]))
                    
                except Exception as e:
                    st.error(f"分析失败: {e}")

    with tab2:
        st.subheader("批量评论分析")

        uploaded_file = st.file_uploader(
            "上传评论文件 (CSV/TXT)",
            type=["csv", "txt"],
            help="CSV文件需包含'review'或'text'列"
        )

        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    # 查找评论列
                    text_col = None
                    for col in ['review', 'text', 'comment', 'Bewertung']:
                        if col in df.columns:
                            text_col = col
                            break
                    if text_col:
                        reviews = df[text_col].dropna().tolist()
                    else:
                        st.error("未找到评论列，请确保CSV包含'review'或'text'列")
                        reviews = []
                else:
                    content = uploaded_file.read().decode('utf-8')
                    reviews = [line.strip() for line in content.split('\n') if line.strip()]

                if reviews:
                    st.info(f"已加载 {len(reviews)} 条评论")

                    if st.button("🚀 开始批量分析", type="primary"):
                        with st.spinner(f"正在分析 {len(reviews)} 条评论..."):
                            from app.services import ReviewAnalyzer
                            analyzer = ReviewAnalyzer(translate=False)  # 批量不翻译
                            report = analyzer.analyze_batch(reviews[:50])  # 限制50条

                            st.success("分析完成!")

                            # 显示统计
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("总评论数", report.total_reviews)
                            with col2:
                                st.metric("平均得分", f"{report.average_score:.2f}")
                            with col3:
                                pos = report.sentiment_distribution.get('positive', 0)
                                st.metric("好评数", pos)
                            with col4:
                                neg = report.sentiment_distribution.get('negative', 0)
                                st.metric("差评数", neg)

                            # 关键洞察
                            st.subheader("📌 关键洞察")
                            for insight in report.key_insights:
                                st.write(insight)

                            # 维度统计
                            if report.dimension_scores:
                                st.subheader("📊 维度统计")
                                dim_df = pd.DataFrame([
                                    {"维度": k, "平均分": v["avg_score"], "提及次数": v["count"]}
                                    for k, v in report.dimension_scores.items()
                                ])
                                st.bar_chart(dim_df.set_index("维度")["平均分"])

            except Exception as e:
                st.error(f"处理失败: {e}")


# ============ 红人管理页面 ============
elif page == "👥 红人管理":
    st.header("红人建联管理")

    st.info("🚧 功能开发中... 即将支持红人档案管理、建联记录追踪")

    # 简单的红人录入表单
    with st.expander("➕ 添加红人", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("红人名称")
            platform = st.selectbox("平台", ["instagram", "tiktok", "youtube"])
            handle = st.text_input("用户名 (@)")
        with col2:
            followers = st.number_input("粉丝数", min_value=0, step=1000)
            engagement = st.number_input("互动率 (%)", min_value=0.0, max_value=100.0, step=0.1)
            niche = st.text_input("垂类 (如: fashion, tech)")

        notes = st.text_area("备注")

        if st.button("保存红人", type="primary"):
            st.success(f"✅ 已保存红人: {name}")
            st.caption("(数据库功能待连接)")


# ============ 内容生成页面 ============
elif page == "✍️ 内容生成":
    st.header("德语内容生成")

    st.info("🚧 功能开发中... 即将支持产品描述、广告文案、开发信生成")

    content_type = st.selectbox(
        "内容类型",
        ["产品描述", "广告文案", "红人开发信", "社媒帖子"]
    )

    product_name = st.text_input("产品名称", placeholder="如: 无线蓝牙耳机")
    product_info = st.text_area("产品信息", placeholder="输入产品卖点、特性等")

    tone = st.select_slider(
        "语气风格",
        options=["正式", "专业", "友好", "轻松"],
        value="专业"
    )

    if st.button("🪄 生成内容", type="primary"):
        st.warning("需要配置 LLM API 密钥才能使用此功能")


# ============ 设置页面 ============
elif page == "⚙️ 设置":
    st.header("系统设置")

    # ===== 分析阈值设置（运营可调整）=====
    st.subheader("📊 分析阈值设置")
    st.caption("调整这些参数来改变分析的判定标准")

    col1, col2 = st.columns(2)
    with col1:
        pos_threshold = st.slider(
            "好评阈值", 0.5, 0.9, 0.6, 0.05,
            help="情感得分高于此值判定为好评"
        )
        neg_threshold = st.slider(
            "差评阈值", 0.1, 0.5, 0.4, 0.05,
            help="情感得分低于此值判定为差评"
        )
    with col2:
        aspect_good = st.slider(
            "维度优秀阈值", 0.6, 0.9, 0.7, 0.05,
            help="维度得分高于此值显示为优秀"
        )
        aspect_bad = st.slider(
            "维度警告阈值", 0.2, 0.5, 0.4, 0.05,
            help="维度得分低于此值显示为需改进"
        )

    min_mentions = st.number_input(
        "维度最少提及次数", 1, 10, 3,
        help="维度至少被提及N次才纳入统计"
    )

    if st.button("💾 保存设置"):
        st.session_state['config'] = {
            'threshold_positive': pos_threshold,
            'threshold_negative': neg_threshold,
            'aspect_good': aspect_good,
            'aspect_bad': aspect_bad,
            'aspect_min_count': min_mentions
        }
        st.success("✅ 设置已保存")

    st.markdown("---")

    # ===== API密钥 =====
    st.subheader("🔑 API密钥")
    st.text_input("DeepSeek API Key", type="password", help="用于内容生成")


# 页脚
st.sidebar.markdown("---")
st.sidebar.caption("GermanMarket.AI v0.1.0")
st.sidebar.caption("© 2025")

