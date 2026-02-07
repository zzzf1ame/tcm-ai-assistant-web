@echo off
chcp 65001 >nul
echo ========================================
echo 上传代码到GitHub - 简化版
echo ========================================
echo.

echo [步骤1] 配置Git用户信息
echo.
git config --global user.name "zzzflame"
git config --global user.email "zzzflame@example.com"
echo ✓ 配置完成
echo.

echo [步骤2] 初始化Git仓库
git init
echo.

echo [步骤3] 添加所有文件
git add .
echo.

echo [步骤4] 提交代码
git commit -m "Initial commit"
echo.

echo [步骤5] 设置远程仓库
git branch -M main
git remote add origin https://github.com/zzzflame/tcm-ai-assistant.git
echo.

echo [步骤6] 推送到GitHub
echo.
echo ========================================
echo 重要提示：
echo 1. 接下来会要求输入GitHub用户名和密码
echo 2. 用户名: zzzflame
echo 3. 密码: 不是你的GitHub登录密码！
echo    需要使用 Personal Access Token
echo.
echo 如何获取Token:
echo 1. 访问 https://github.com/settings/tokens
echo 2. 点击 "Generate new token" - "Classic"
echo 3. 勾选 "repo" 权限
echo 4. 点击 "Generate token"
echo 5. 复制生成的token（以ghp_开头）
echo 6. 在下面提示输入密码时，粘贴这个token
echo ========================================
echo.
pause

git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo 推送失败！
    echo ========================================
    echo.
    echo 可能的原因：
    echo 1. 没有输入正确的Token
    echo 2. Token权限不足
    echo 3. 网络问题
    echo.
    echo 解决方法：
    echo 方法1: 使用GitHub Desktop（推荐）
    echo   下载: https://desktop.github.com/
    echo   安装后直接拖拽文件夹上传
    echo.
    echo 方法2: 重新获取Token
    echo   访问: https://github.com/settings/tokens
    echo   生成新token，勾选repo权限
    echo   重新运行本脚本
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ 上传成功！
echo ========================================
echo.
echo 下一步：部署到Render
echo 1. 访问 https://render.com
echo 2. 用GitHub账号登录
echo 3. 创建 Web Service
echo 4. 选择 tcm-ai-assistant 仓库
echo.
pause
