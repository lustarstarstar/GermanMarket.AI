# GitHub上传完整指南

## 📋 前置准备

### 1. 安装Git
- Windows: 下载 https://git-scm.com/download/win
- 安装时选择"Use Git from the Windows Command Prompt"

### 2. 创建GitHub账户
- 访问 https://github.com/signup
- 注册账户

### 3. 生成SSH密钥（推荐）
```bash
ssh-keygen -t ed25519 -C "your.email@github.com"
# 一路回车，使用默认设置
```

查看公钥：
```bash
cat ~/.ssh/id_ed25519.pub
```

在GitHub添加SSH密钥：
- 访问 https://github.com/settings/keys
- 点击"New SSH key"
- 粘贴公钥内容

---

## 🚀 上传步骤

### 第1步：在GitHub创建仓库

1. 登录 https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `GermanMarket.AI`
   - Description: `德国电商智能分析平台`
   - Public（公开）
   - 勾选 "Add a README file"（可选，我们已有）
   - 点击 "Create repository"

4. 复制仓库URL（SSH或HTTPS）
   - SSH: `git@github.com:your-username/GermanMarket.AI.git`
   - HTTPS: `https://github.com/your-username/GermanMarket.AI.git`

---

### 第2步：本地配置Git

```bash
# 进入项目目录
cd D:/pycharmproject/german2

# 配置用户信息（全局，只需一次）
git config --global user.name "Your Name"
git config --global user.email "your.email@github.com"

# 验证配置
git config --global user.name
git config --global user.email
```

---

### 第3步：添加远程仓库

```bash
# 添加远程仓库（选择一种）

# 方式A：SSH（推荐）
git remote add origin git@github.com:your-username/GermanMarket.AI.git

# 方式B：HTTPS
git remote add origin https://github.com/your-username/GermanMarket.AI.git

# 验证
git remote -v
```

---

### 第4步：提交代码

```bash
# 1. 查看状态
git status

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Initial commit: GermanMarket.AI v0.1.0

- 德语评论情感分析
- 维度分析(ABSA)
- 自动翻译
- Streamlit Web界面
- FastAPI接口
- MySQL数据库支持"

# 4. 推送到GitHub
git branch -M main
git push -u origin main
```

---

### 第5步：验证上传

访问 `https://github.com/your-username/GermanMarket.AI` 查看

---

## 🔄 后续更新

每次修改后：

```bash
# 查看变更
git status

# 添加变更
git add .

# 提交
git commit -m "描述你的改动"

# 推送
git push
```

---

## ⚠️ 常见问题

### Q1: 如何删除已上传的文件？
```bash
git rm --cached filename
git commit -m "Remove filename"
git push
```

### Q2: 如何修改最后一次提交？
```bash
git add .
git commit --amend --no-edit
git push --force-with-lease
```

### Q3: SSH连接失败？
```bash
# 测试连接
ssh -T git@github.com

# 如果失败，检查SSH密钥
ls ~/.ssh/
```

### Q4: 如何删除CrossBorder_AI_Nexus？
```bash
# 本地删除
rm -r CrossBorder_AI_Nexus

# 提交删除
git add .
git commit -m "Remove old CrossBorder_AI_Nexus project"
git push
```

---

## 📊 推荐的.gitignore已创建

文件位置：`.gitignore`

已排除：
- Python缓存
- 虚拟环境
- IDE配置
- 环境变量
- 模型文件
- 数据文件
- CrossBorder_AI_Nexus/

---

## 🎯 完成后的检查清单

- [ ] GitHub账户已创建
- [ ] SSH密钥已配置
- [ ] 本地仓库已初始化
- [ ] .gitignore已创建
- [ ] 代码已提交
- [ ] 代码已推送到GitHub
- [ ] README.md已上传
- [ ] 可以访问GitHub仓库

---

**需要帮助？** 在上传过程中遇到问题，告诉我具体错误信息！

