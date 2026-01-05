"""项目配置管理"""
import os
import warnings
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / '.env'

# 如果 .env 文件不存在，尝试从 env.example 复制
if not ENV_FILE.exists():
    example_file = BASE_DIR / 'env.example'
    if example_file.exists():
        warnings.warn(
            f"⚠️  .env 文件不存在，请复制 env.example 为 .env 并配置：\n"
            f"   cp {example_file} {ENV_FILE}",
            UserWarning
        )

load_dotenv(ENV_FILE)

# 数据库配置（完全可配置化）
# 注意：所有敏感信息必须通过环境变量配置，不要使用默认值
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '0.0.0.0'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'life_insurance'),
    'charset': 'utf8mb4'
}

# 阿里云模型配置（完全可配置化）
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
MODEL_TYPE = os.getenv('MODEL_TYPE', 'api')  # api 或 local
MODEL_NAME = os.getenv('MODEL_NAME', 'qwen-turbo')

# LLM 参数配置（完全可配置化）
LLM_CONFIG = {
    'temperature': float(os.getenv('LLM_TEMPERATURE', '0.1')),
    'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '2000')),
}

# 数据文件路径
DATA_DIR = BASE_DIR.parent / 'Data'


def validate_config():
    """验证配置是否完整"""
    errors = []
    
    if not DASHSCOPE_API_KEY:
        errors.append("❌ DASHSCOPE_API_KEY 未配置，请在 .env 文件中设置")
    
    if not DB_CONFIG['password']:
        errors.append("❌ DB_PASSWORD 未配置，请在 .env 文件中设置")
    
    if errors:
        print("\n".join(errors))
        print(f"\n💡 提示：请参考 {BASE_DIR / 'env.example'} 创建 .env 文件")
        return False
    
    return True


def print_config():
    """打印当前配置（隐藏敏感信息）"""
    print("=" * 60)
    print("📋 当前配置")
    print("=" * 60)
    print(f"数据库主机: {DB_CONFIG['host']}")
    print(f"数据库端口: {DB_CONFIG['port']}")
    print(f"数据库用户: {DB_CONFIG['user']}")
    print(f"数据库名称: {DB_CONFIG['database']}")
    print(f"API Key: {'已配置' if DASHSCOPE_API_KEY else '❌ 未配置'}")
    print(f"模型类型: {MODEL_TYPE}")
    print(f"模型名称: {MODEL_NAME}")
    print(f"温度参数: {LLM_CONFIG['temperature']}")
    print(f"最大 Token: {LLM_CONFIG['max_tokens']}")
    print("=" * 60)

