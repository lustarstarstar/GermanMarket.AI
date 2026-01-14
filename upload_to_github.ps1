# GermanMarket.AI GitHub 上传脚本 (PowerShell)
# =============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   GermanMarket.AI - GitHub 上传工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Git
try {
    git --version | Out-Null
    Write-Host "[✓] Git已安装" -ForegroundColor Green
} catch {
    Write-Host "[✗] Git未安装，请先安装 https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 检查仓库
if (-not (Test-Path ".git")) {
    Write-Host "[提示] 本地仓库未初始化，正在初始化..." -ForegroundColor Yellow
    git init
    Write-Host "[✓] 仓库已初始化" -ForegroundColor Green
    Write-Host ""
}

# 显示状态
Write-Host "[当前状态]" -ForegroundColor Cyan
git status
Write-Host ""

# 询问继续
$continue = Read-Host "是否继续上传? (y/n)"
if ($continue -ne "y" -and $continue -ne "Y") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[步骤1] 添加所有文件..." -ForegroundColor Cyan
git add .
Write-Host "[✓] 完成" -ForegroundColor Green

Write-Host ""
Write-Host "[步骤2] 输入提交信息..." -ForegroundColor Cyan
$message = Read-Host "提交信息 (默认: Update)"
if ([string]::IsNullOrWhiteSpace($message)) {
    $message = "Update"
}

git commit -m $message
if ($LASTEXITCODE -ne 0) {
    Write-Host "[提示] 没有新的变更需要提交" -ForegroundColor Yellow
} else {
    Write-Host "[✓] 提交完成" -ForegroundColor Green
}

Write-Host ""
Write-Host "[步骤3] 推送到GitHub..." -ForegroundColor Cyan
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "[✗] 推送失败，请检查：" -ForegroundColor Red
    Write-Host "   1. 是否配置了远程仓库? git remote -v" -ForegroundColor Yellow
    Write-Host "   2. SSH密钥是否正确?" -ForegroundColor Yellow
    Write-Host "   3. 网络连接是否正常?" -ForegroundColor Yellow
} else {
    Write-Host "[✓] 推送成功!" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   上传完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

