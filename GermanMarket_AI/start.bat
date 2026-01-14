@echo off
echo ========================================
echo   GermanMarket.AI 启动脚本
echo ========================================
echo.

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [OK] 虚拟环境已激活
) else (
    echo [提示] 未找到虚拟环境，使用全局Python
)

echo.
echo 选择启动模式:
echo   1. Streamlit界面 (推荐给运营使用)
echo   2. FastAPI服务 (开发调试)
echo   3. 运行NLP测试
echo.

set /p choice="请输入选项 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo 启动 Streamlit 界面...
    streamlit run streamlit_app.py
) else if "%choice%"=="2" (
    echo.
    echo 启动 FastAPI 服务...
    echo 访问地址: http://localhost:8000
    echo API文档: http://localhost:8000/docs
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
) else if "%choice%"=="3" (
    echo.
    echo 运行 NLP 测试...
    python test_nlp.py --test all
) else (
    echo 无效选项
)

pause

