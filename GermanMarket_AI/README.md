# 🇩🇪 GermanMarket.AI

**德国电商智能分析平台** - 帮中国卖家看懂德国市场

## ✨ 功能特性

### 已实现
- ✅ **德语评论情感分析** - 基于BERT，准确识别好评/差评
- ✅ **维度情感分析(ABSA)** - 分析物流、质量、价格等多个维度
- ✅ **德语翻译** - 德语→中文自动翻译
- ✅ **关键词提取** - 自动提取评论关键词
- ✅ **Streamlit界面** - 简单易用的Web界面
- ✅ **FastAPI接口** - RESTful API支持

### 开发中
- 🚧 红人建联管理
- 🚧 德语内容生成
- 🚧 竞品分析报告

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
│   ├── core/             # 核心配置、数据库
│   ├── models/           # 数据模型
│   └── services/         # 业务服务
│       └── nlp/          # NLP模块
├── main.py               # FastAPI入口
├── streamlit_app.py      # Streamlit界面
├── test_nlp.py           # 测试脚本
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

- **后端**: FastAPI + SQLAlchemy
- **前端**: Streamlit
- **NLP**: Transformers + german-sentiment-bert
- **数据库**: MySQL

## 📝 License

MIT

