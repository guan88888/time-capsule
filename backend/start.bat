@echo off
REM Windows 启动脚本

echo ==========================================
echo 时空胶囊后端服务启动
echo ==========================================

REM 检查Python
python --version
if errorlevel 1 (
    echo Python未安装或未添加到PATH
    pause
    exit /b 1
)

REM 检查依赖
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

REM 启动服务
echo.
echo 启动后端服务...
echo 服务地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ==========================================
echo.

python main.py

pause

