import subprocess
import sys

print("=" * 50)
print("中医AI助手Web版 - 依赖检查")
print("=" * 50)
print()

required_packages = [
    'flask',
    'flask_cors',
    'bcrypt',
    'requests'
]

missing_packages = []

for package in required_packages:
    try:
        __import__(package)
        print(f"✓ {package} 已安装")
    except ImportError:
        print(f"✗ {package} 未安装")
        missing_packages.append(package)

print()

if missing_packages:
    print(f"发现 {len(missing_packages)} 个缺失的包")
    print("正在安装...")
    print()
    
    try:
        subprocess.check_call([
            sys.executable, 
            '-m', 
            'pip', 
            'install', 
            '-r', 
            'requirements.txt'
        ])
        print()
        print("✓ 所有依赖安装成功！")
    except subprocess.CalledProcessError:
        print()
        print("✗ 安装失败，请手动运行:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
else:
    print("✓ 所有依赖已安装")

print()
print("=" * 50)
print("测试数据库初始化...")
print("=" * 50)
print()

try:
    from models import Database
    import config
    
    db = Database(config.DATABASE_PATH)
    print("✓ 数据库初始化成功")
    print(f"  数据库路径: {config.DATABASE_PATH}")
    
except Exception as e:
    print(f"✗ 数据库初始化失败: {e}")
    sys.exit(1)

print()
print("=" * 50)
print("测试AI模块...")
print("=" * 50)
print()

try:
    from ai_chat import TCMAIChat
    from knowledge_base import KnowledgeBase
    
    ai = TCMAIChat()
    kb = KnowledgeBase(config.KNOWLEDGE_PATH)
    
    print("✓ AI模块加载成功")
    print(f"  API提供商: {config.API_PROVIDER}")
    print(f"  模型: {config.MODEL}")
    
    knowledge = kb.knowledge
    total_items = sum(len(items) for items in knowledge.values())
    print(f"  知识库条目: {total_items}条")
    
except Exception as e:
    print(f"✗ AI模块加载失败: {e}")
    sys.exit(1)

print()
print("=" * 50)
print("✓ 所有测试通过！")
print("=" * 50)
print()
print("现在可以运行应用:")
print("  python app.py")
print()
print("或使用启动脚本:")
print("  启动.bat (Windows)")
print()
