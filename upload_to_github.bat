@echo off
REM GermanMarket.AI GitHub 上传脚本
REM ================================

echo.
echo ========================================
echo   GermanMarket.AI - GitHub 上传工具
echo ========================================
echo.

REM 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Git未安装，请先安装 https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [✓] Git已安装
echo.

REM 检查是否已初始化
if not exist ".git" (
    echo [提示] 本地仓库未初始化，正在初始化...
    git init
    echo [✓] 仓库已初始化
    echo.
)

REM 显示当前状态
echo [当前状态]
git status
echo.

REM 询问是否继续
set /p continue="是否继续上传? (y/n): "
if /i not "%continue%"=="y" (
    echo 已取消
    exit /b 0
)

echo.
echo [步骤1] 添加所有文件...
git add .
echo [✓] 完成

echo.
echo [步骤2] 输入提交信息...
set /p message="提交信息 (默认: Update): "
if "%message%"=="" set message=Update

git commit -m "%message%"
if errorlevel 1 (
    echo [提示] 没有新的变更需要提交
) else (
    echo [✓] 提交完成
)

echo.
echo [步骤3] 推送到GitHub...
git push -u origin main
if errorlevel 1 (
    echo [错误] 推送失败，请检查：
    echo   1. 是否配置了远程仓库? git remote -v
    echo   2. SSH密钥是否正确?
    echo   3. 网络连接是否正常?
) else (
    echo [✓] 推送成功!
)

echo.
echo ========================================
echo   上传完成！
echo ========================================
echo.
pause

