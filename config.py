import os

from dotenv import load_dotenv

load_dotenv()

# API配置 - 使用通义千问
API_PROVIDER = "qwen"  # qwen / deepseek / ernie
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "")
QWEN_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# DeepSeek配置（备用）
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Flask session 密钥（必须固定，否则重启后所有用户掉线）
SECRET_KEY = os.environ.get("SECRET_KEY", "")

# 自动切换配置
AUTO_SWITCH_ON_TIMEOUT = True  # 超时时自动切换到备用API

# 数据库配置
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
elif not DATABASE_URL:
    DATABASE_URL = 'sqlite:///data/users.db'

# 知识库配置
KNOWLEDGE_PATH = "data/knowledge.json"
PROMPTS_PATH = "data/prompts.json"

# AI配置
MAX_TOKENS = 2000
TEMPERATURE = 0.7
MODEL = "qwen3-max-2026-01-23"  # 使用免费额度的qwen3-max模型

# 免费版限制
FREE_DAILY_LIMIT = 5  # 免费用户每天5次
