@echo off
chcp 65001 >nul
echo ========================================
echo 配置Git用户信息
echo ========================================
echo.

echo 请输入你的名字（随便填，如：张三）
set /p USERNAME="名字: "

echo.
echo 请输入你的邮箱（随便填，如：test@example.com）
set /p EMAIL="邮箱: "

echo.
echo 正在配置...
git config --global user.name "%USERNAME%"
git config --global user.email "%EMAIL%"

echo.
echo ✓ 配置完成！
echo.
echo 用户名: %USERNAME%
echo 邮箱: %EMAIL%
echo.
pause
