# 🚀 快速上传GitHub - 5分钟指南

## 前置条件（一次性）

### 1️⃣ 安装Git
- 下载: https://git-scm.com/download/win
- 安装时选择"Use Git from the Windows Command Prompt"

### 2️⃣ 创建GitHub账户
- 访问: https://github.com/signup
- 注册账户

### 3️⃣ 生成SSH密钥
```bash
ssh-keygen -t ed25519 -C "your.email@github.com"
# 一路回车
```

### 4️⃣ 添加SSH密钥到GitHub
```bash
# 查看公钥
cat ~/.ssh/id_ed25519.pub

# 复制输出内容，访问 https://github.com/settings/keys
# 点击 "New SSH key"，粘贴公钥
```

---

## 创建GitHub仓库（一次性）

1. 登录 https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写：
   - Name: `GermanMarket.AI`
   - Description: `德国电商智能分析平台`
   - Public
   - 点击 "Create repository"
4. 复制SSH URL: `git@github.com:your-username/GermanMarket.AI.git`

---

## 本地配置（一次性）

```bash
cd D:/pycharmproject/german2

# 配置用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@github.com"

# 添加远程仓库
git remote add origin git@github.com:your-username/GermanMarket.AI.git

# 验证
git remote -v
```

---

## 上传代码（每次更新）

### 方式A：使用脚本（推荐）
```bash
# PowerShell
.\upload_to_github.ps1

# 或 CMD
upload_to_github.bat
```

### 方式B：手动命令
```bash
git add .
git commit -m "描述你的改动"
git push
```

---

## ✅ 完成检查

访问 `https://github.com/your-username/GermanMarket.AI` 查看

---

## ⚠️ 常见问题

| 问题 | 解决方案 |
|------|---------|
| SSH连接失败 | `ssh -T git@github.com` 测试连接 |
| 找不到远程仓库 | `git remote -v` 检查配置 |
| 推送失败 | 检查网络，或使用HTTPS: `git remote set-url origin https://...` |

---

**需要帮助？** 告诉我具体错误信息！

