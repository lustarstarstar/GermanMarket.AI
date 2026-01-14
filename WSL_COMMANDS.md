# WSL GitHub上传命令 - 复制粘贴执行

## 第一步：配置Git用户信息
git config --global user.name "lustarstarstar"
git config --global user.email "luxingtao1997@163.com"

## 第二步：生成SSH密钥
ssh-keygen -t ed25519 -C "luxingtao1997@163.com"
# 一路回车，使用默认设置

## 第三步：查看公钥（复制这个内容）
cat ~/.ssh/id_ed25519.pub

## 第四步：添加SSH密钥到GitHub
# 访问 https://github.com/settings/keys
# 点击 "New SSH key"
# 粘贴上面的公钥内容
# 保存

## 第五步：测试SSH连接
ssh -T git@github.com

## 第六步：进入项目目录
cd /mnt/d/pycharmproject/german2

## 第七步：初始化Git仓库
git init

## 第八步：添加远程仓库
git remote add origin git@github.com:lustarstarstar/GermanMarket.AI.git

## 第九步：验证配置
git remote -v

## 第十步：添加所有文件
git add .

## 第十一步：提交代码
git commit -m "Initial commit: GermanMarket.AI v0.1.0

- 德语评论情感分析
- 维度分析(ABSA)
- 自动翻译
- Streamlit Web界面
- FastAPI接口
- MySQL数据库支持"

## 第十二步：推送到GitHub
git branch -M main
git push -u origin main

## 完成！访问查看
# https://github.com/lustarstarstar/GermanMarket.AI

