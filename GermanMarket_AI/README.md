# 🇩🇪 GermanMarket.AI

**德国跨境电商智能运营平台** - 专为中国卖家打造的德国市场AI工具集

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 功能特性

### 已实现
- ✅ **德语评论情感分析** - 基于BERT，准确识别好评/差评
- ✅ **维度情感分析(ABSA)** - 分析物流、质量、价格等多个维度
- ✅ **红人评估器** - 三维度评分 + 德国市场关键词匹配
- ✅ **开发信生成** - 双模式(商务/亲和) + GDPR/TMG合规
- ✅ **Privacy_Check** - TMG §5 Impressum自动检查
- ✅ **差评风险检测** - 法律/安全/退款/投诉四类风险
- ✅ **道歉信生成** - Webhook触发自动生成补偿信草稿

### 待优化
- 🔄 评估权重调整：真实性45% / 相关度35% / 活跃度20%
- 🔄 德国特色关键词补充：Abmahnung, Verbraucherzentrale等
- 🔄 真实语料验证测试

## 🚀 快速开始

### 1. 安装依赖

```bash
cd GermanMarket_AI
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制配置文件
copy .env.example .env

# 编辑 .env 填入MySQL配置
```

### 3. 运行

**方式一：Streamlit界面（推荐）**
```bash
streamlit run streamlit_app.py
```

**方式二：FastAPI服务**
```bash
uvicorn main:app --reload
# 访问 http://localhost:8000/docs 查看API文档
```

**方式三：直接测试NLP**
```bash
python test_nlp.py --test all
```

## 📁 项目结构

```
GermanMarket_AI/
├── app/
│   ├── api/              # FastAPI路由
│   ├── core/             # 核心配置
│   └── services/         # 业务服务
│       ├── influencer/   # 红人评估模块
│       ├── content/      # 内容生成模块
│       ├── shopify/      # Shopify集成
│       └── nlp/          # NLP模块
├── tests/                # 测试文件
├── main.py               # FastAPI入口
├── streamlit_app.py      # Streamlit界面
└── requirements.txt      # 依赖
```

## 🗄️ MySQL云数据库配置

推荐使用云数据库，支持家里/公司多地访问：

| 服务 | 特点 | 免费额度 |
|------|------|----------|
| **PlanetScale** | Serverless, 快速 | 5GB存储 |
| **Railway** | 简单, 一键部署 | $5/月额度 |
| **TiDB Cloud** | 国内团队 | 5GB存储 |

配置示例：
```env
DB_HOST=aws.connect.psdb.cloud
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=german_market_ai
```

## 📖 API示例

### 分析单条评论
```bash
curl -X POST http://localhost:8000/api/v1/analyze/single \
  -H "Content-Type: application/json" \
  -d '{"text": "Das Produkt ist sehr gut!"}'
```

### 批量分析
```bash
curl -X POST http://localhost:8000/api/v1/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{"reviews": ["Sehr gut!", "Schlecht!", "Okay"]}'
```

## 🛠️ 技术栈

- **后端**: FastAPI + Python 3.9+
- **前端**: Streamlit
- **NLP**: Transformers + German-BERT
- **数据**: Pandas, CSV/JSON

## 📋 TODO (Gemini审核建议)

### 高优先级
- [ ] 调整评估权重：真实性45% / 相关度35% / 活跃度20%
- [ ] 补充关键词：Abmahnung, Verbraucherzentrale, Mangelhaft, Schrott
- [ ] 完善Impressum：USt-IdNr, Handelsregister, OS-Plattform

### 中优先级
- [ ] 真实语料测试（Amazon.de + 真实红人）
- [ ] 边缘情况测试（特殊字符、性别称呼）

## 📝 License

MIT

## 📧 联系方式

- GitHub: [@lustarstarstar](https://github.com/lustarstarstar)
- Email: luxingtao1997@163.com