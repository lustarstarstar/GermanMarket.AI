# GermanMarket.AI 🇩🇪

**德国电商智能分析平台** - 帮中国卖家看懂德国市场、说好德语故事

## 📌 项目定位

这是一个为**德国独立站运营**设计的AI工具集，旨在：
- 🔍 快速分析德语评论，发现消费者痛点
- 📊 生成竞品对标报告
- 👥 管理红人建联流程
- ✍️ 生成德语营销文案

**目标用户**：中国跨境电商运营、品牌方、代运营服务商

---

## ✨ 核心功能

### 已实现 ✅
- **德语评论分析** - 情感分类 + 维度分析
- **自动翻译** - 德语→中文
- **关键词提取** - 自动识别评论关键词
- **Streamlit界面** - 简单易用的Web工具
- **FastAPI接口** - 支持集成和二次开发

### 开发中 🚧
- 红人建联管理
- 德语内容生成
- 竞品分析报告

---

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-username/GermanMarket.AI.git
cd GermanMarket_AI
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行（选择一种）

**方式A：Streamlit界面（推荐给运营）**
```bash
streamlit run streamlit_app.py
```

**方式B：FastAPI服务**
```bash
uvicorn main:app --reload
# 访问 http://localhost:8000/docs
```

**方式C：测试NLP功能**
```bash
python test_nlp.py --test all
```

---

## 📁 项目结构

```
GermanMarket_AI/
├── app/
│   ├── api/              # FastAPI路由
│   ├── core/             # 配置、数据库
│   ├── models/           # 数据模型
│   └── services/
│       ├── nlp/          # NLP核心模块
│       └── review_analyzer.py
├── main.py               # FastAPI入口
├── streamlit_app.py      # Web界面
├── test_nlp.py           # 测试脚本
└── requirements.txt
```

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 前端界面 | Streamlit |
| NLP模型 | Transformers + german-sentiment-bert |
| 翻译 | Helsinki-NLP/opus-mt-de-zh |
| 数据库 | MySQL (云) |
| ORM | SQLAlchemy |

---

## 📖 使用示例

### Python API
```python
from app.services import ReviewAnalyzer

analyzer = ReviewAnalyzer(translate=True)

# 单条分析
result = analyzer.analyze_single("Das Produkt ist sehr gut!")
print(result.sentiment)  # positive
print(result.translated_text)  # 产品很好！

# 批量分析
report = analyzer.analyze_batch(reviews_list)
print(report.key_insights)  # 关键洞察
```

### REST API
```bash
curl -X POST http://localhost:8000/api/v1/analyze/single \
  -H "Content-Type: application/json" \
  -d '{"text": "Das Produkt ist sehr gut!"}'
```

---

## 🗄️ 数据库配置

推荐使用云MySQL（支持多地访问）：

| 服务 | 特点 | 免费额度 |
|------|------|----------|
| PlanetScale | Serverless | 5GB |
| Railway | 简单部署 | $5/月 |
| TiDB Cloud | 国内友好 | 5GB |

配置步骤见 `GermanMarket_AI/README.md`

---

## 📝 License

MIT License

---

## 🤝 贡献

欢迎提交Issue和PR！

---

**最后更新**: 2025年1月

