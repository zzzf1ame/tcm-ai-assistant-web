# 🌿 中医AI助手 Web版

> 你的私人中医顾问，记住你的所有信息，越用越懂你

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-red.svg)](https://flask.palletsprojects.com/)

## ✨ 功能特点

- ✅ **用户系统**: 注册、登录、Session管理
- ✅ **个人档案**: 年龄、性别、体质、地区
- ✅ **AI对话**: 基于通义千问Qwen3-max
- ✅ **知识增强**: 82条中医知识库
- ✅ **历史记忆**: 记住最近5条对话
- ✅ **Markdown渲染**: 支持标题、列表、加粗等
- ✅ **响应式设计**: 手机、平板、电脑全支持
- ✅ **使用限制**: 免费用户每天5次
- ✅ **防刷机制**: IP限制、设备指纹

## 🚀 快速开始

### 方式一：一键启动（Windows）

```bash
双击 启动.bat
```

### 方式二：命令行启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行应用
python app.py

# 3. 访问
浏览器打开 http://localhost:5000
```

### 方式三：部署到Render

详见 [部署指南.md](部署指南.md)

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| [开始使用.md](开始使用.md) | 快速入门指南 |
| [使用手册.md](使用手册.md) | 详细使用教程 |
| [部署指南.md](部署指南.md) | Render部署教程 |
| [项目说明.md](项目说明.md) | 技术架构文档 |
| [本地测试.md](本地测试.md) | 本地测试指南 |
| [上线检查清单.md](上线检查清单.md) | 上线前检查 |

## 🎯 使用流程

```
注册账号 → 登录系统 → 完善档案 → 开始对话 → 获得建议
```

## 🛠️ 技术栈

- **后端**: Flask 3.0 + SQLite
- **前端**: HTML + CSS + JavaScript
- **AI**: 通义千问 Qwen3-max
- **认证**: bcrypt + Flask-Session
- **部署**: Render

## 📊 项目结构

```
中医AI助手Web版/
├── app.py                 # Flask主应用
├── models.py              # 数据库模型
├── config.py              # 配置文件
├── ai_chat.py             # AI对话模块
├── knowledge_base.py      # 知识库管理
├── templates/             # HTML模板
│   ├── index.html        # 登录注册页
│   ├── chat.html         # 对话页面
│   └── profile.html      # 档案页面
├── static/css/           # 样式文件
├── data/                 # 数据目录
│   ├── knowledge.json    # 82条知识库
│   └── users.db          # 用户数据库
└── requirements.txt      # Python依赖
```

## ⚙️ 配置说明

编辑 `config.py`:

```python
# API配置
API_PROVIDER = "qwen"  # 主要使用通义千问
QWEN_API_KEY = "你的API密钥"
MODEL = "qwen3-max-2026-01-23"

# DeepSeek备用配置
DEEPSEEK_API_KEY = "你的DeepSeek密钥"

# 自动切换配置
AUTO_SWITCH_ON_TIMEOUT = True  # 超时时自动切换到备用API

# 使用限制
FREE_DAILY_LIMIT = 5  # 每天5次
```

**智能切换机制**：
- 当通义千问超时或连接失败时，自动切换到DeepSeek
- 当DeepSeek超时或连接失败时，自动切换到通义千问
- 切换成功后会在回复末尾显示提示
- 可通过 `AUTO_SWITCH_ON_TIMEOUT` 开关控制

## 🔒 安全特性

- ✅ 密码bcrypt加密
- ✅ Session安全管理
- ✅ SQL注入防护
- ✅ XSS防护
- ✅ IP限制（注册/使用）
- ✅ 设备指纹记录

## 💰 成本估算

### 免费方案
- **Render**: 免费（750小时/月）
- **通义千问**: 免费（100万tokens）
- **预计支持**: 200-500用户/月

### 付费方案（如需升级）
- **Render Starter**: $7/月
- **通义千问**: 按量付费

## 📈 功能路线图

### ✅ Phase 1: 核心功能（已完成）
- [x] 用户注册登录
- [x] 个人档案管理
- [x] AI对话功能
- [x] 使用限制
- [x] 响应式设计

### 📋 Phase 2: 增强功能
- [ ] 会员系统
- [ ] 支付功能
- [ ] 症状记录
- [ ] 健康档案
- [ ] 数据导出

### 🚀 Phase 3: 优化升级
- [ ] PostgreSQL数据库
- [ ] Redis缓存
- [ ] CDN加速
- [ ] 监控告警

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📝 许可证

MIT License

## 📞 联系方式

- GitHub: [项目地址]
- Email: [邮箱地址]

---

**版本**: v1.0.0  
**更新**: 2026-02-07  
**状态**: ✅ 可部署上线
