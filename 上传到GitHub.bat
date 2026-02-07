@echo off
chcp 65001 >nul
echo ========================================
echo 上传代码到GitHub
echo ========================================
echo.

echo [提示] 请先在GitHub创建仓库: tcm-ai-assistant
echo [提示] 仓库地址示例: https://github.com/你的用户名/tcm-ai-assistant.git
echo.
pause

echo.
echo [1/5] 初始化Git仓库...
git init
if errorlevel 1 (
    echo [错误] Git未安装，请先安装Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo.
echo [2/5] 添加所有文件...
git add .

echo.
echo [3/5] 提交代码...
git commit -m "Initial commit: 中医AI助手Web版"

echo.
echo [4/5] 请输入你的GitHub仓库地址
echo 格式: https://github.com/用户名/tcm-ai-assistant.git
set /p REPO_URL="仓库地址: "

echo.
echo [5/5] 推送到GitHub...
git branch -M main
git remote add origin %REPO_URL%
git push -u origin main

if errorlevel 1 (
    echo.
    echo [错误] 推送失败，可能的原因:
    echo 1. 仓库地址错误
    echo 2. 没有权限
    echo 3. 需要输入用户名和密码
    echo.
    echo 请手动执行:
    echo git remote set-url origin %REPO_URL%
    echo git push -u origin main
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ 上传成功！
echo ========================================
echo.
echo 下一步:
echo 1. 访问 https://render.com
echo 2. 登录并创建 Web Service
echo 3. 连接你的GitHub仓库
echo 4. 等待部署完成
echo.
pause
