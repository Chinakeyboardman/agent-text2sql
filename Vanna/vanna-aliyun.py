"""
Vanna 连接阿里云 MySQL 数据库脚本
使用阿里云 DashScope API
"""
import os
from pathlib import Path
from dotenv import load_dotenv

from vanna.legacy.openai import OpenAI_Chat
from vanna.legacy.chromadb.chromadb_vector import ChromaDB_VectorStore
from openai import OpenAI
import mysql.connector

# 加载配置
ENV_FILE = Path(__file__).parent / '.env'
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

# 配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '0.0.0.0'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'chenjiawei'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'life_insurance'),
}

DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
MODEL_NAME = os.getenv('MODEL_NAME', 'qwen-turbo')
# 阿里云 DashScope OpenAI 兼容接口地址
# 根据 vanna 源码，使用 compatible-mode 路径
DASHSCOPE_BASE_URL = os.getenv('DASHSCOPE_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    """自定义 Vanna 类"""
    def __init__(self, config=None):
        chroma_config = config.copy() if config else {}
        openai_config = config.copy() if config else {}
        
        if config and 'client' in config:
            self.client = config['client']
        
        if 'client' in chroma_config:
            del chroma_config['client']
        
        ChromaDB_VectorStore.__init__(self, config=chroma_config)
        OpenAI_Chat.__init__(self, config=openai_config)


# 创建 OpenAI 客户端
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL
)

# 初始化 Vanna 实例
vn = MyVanna(config={
    'model': MODEL_NAME,
    'client': client
})

# 连接数据库
vn.connect_to_mysql(
    host=DB_CONFIG['host'],
    dbname=DB_CONFIG['database'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    port=DB_CONFIG['port']
)

# 连接到 MySQL 数据库
try:
    connection = mysql.connector.connect(**DB_CONFIG)
    print("成功连接到MySQL数据库")
    
    # 获取所有表名
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT TABLE_NAME 
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = '{DB_CONFIG['database']}'
    """)
    tables = cursor.fetchall()
    
    # 训练每个表的schema
    for (table_name,) in tables:
        try:
            cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            _, create_table = cursor.fetchone()
            print(f"正在训练表 {table_name} 的schema...")
            vn.train(ddl=create_table)
        except Exception as e:
            print(f"训练表 {table_name} 失败: {str(e)}")
            continue
    
    print("Schema训练完成")
    
    # 示例：使用Vanna进行自然语言查询
    question = "找出理赔金额最高的前5个理赔记录"
    vn.ask(question)
    
except mysql.connector.Error as err:
    print(f"数据库连接错误: {err}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL连接已关闭")
