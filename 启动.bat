@echo off
chcp 65001 >nul
echo ================================
echo 中医AI助手Web版 - 本地启动
echo ================================
echo.

echo [1/3] 检查依赖...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask未安装，正在安装依赖...
    pip install -r requirements.txt
) else (
    echo 依赖已安装
)

echo.
echo [2/3] 初始化数据库...
if not exist "data" mkdir data
python -c "from models import Database; import config; Database(config.DATABASE_PATH)"
echo 数据库初始化完成

echo.
echo [3/3] 启动应用...
echo.
echo 应用地址: http://localhost:5000
echo 按 Ctrl+C 停止服务
echo.
python app.py
