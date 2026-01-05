"""数据库初始化脚本 - 导入 Data 目录中的 SQL 文件"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader.import_data import DataImporter
from config.settings import DB_CONFIG


def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    database_name = DB_CONFIG['database']
    
    # 创建不包含数据库名的连接字符串（连接到 MySQL 服务器）
    connection_string = (
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/"
        f"?charset={DB_CONFIG['charset']}"
    )
    
    try:
        print(f"🔍 检查数据库 '{database_name}' 是否存在...")
        
        # 连接到 MySQL 服务器（不指定数据库）
        engine = create_engine(connection_string, echo=False)
        
        with engine.connect() as conn:
            # 检查数据库是否已存在
            result = conn.execute(
                text(f"SHOW DATABASES LIKE '{database_name}'")
            )
            exists = result.fetchone() is not None
            
            if exists:
                print(f"✅ 数据库 '{database_name}' 已存在")
                return True
            
            # 创建数据库
            print(f"📝 正在创建数据库 '{database_name}'...")
            conn.execute(
                text(f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                     f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            )
            conn.commit()
            
            print(f"✅ 数据库 '{database_name}' 创建成功！")
            return True
    
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        print()
        print("💡 请检查：")
        print("   1. MySQL 服务是否正在运行")
        print("   2. .env 文件中的数据库配置是否正确")
        print("   3. 数据库用户是否有创建数据库的权限")
        print()
        print("📝 或者手动创建数据库：")
        print(f"   CREATE DATABASE `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        return False


def init_database(force: bool = False):
    """初始化数据库 - 导入所有 SQL 文件"""
    # 先检查并创建数据库（如果不存在）
    print("=" * 60)
    print("🗄️  数据库初始化")
    print("=" * 60)
    print()
    
    # 先检查数据库是否存在，如果不存在则创建
    if not create_database_if_not_exists():
        print("❌ 无法创建数据库，请手动创建或检查配置")
        return None
    
    print()
    
    # 验证数据库连接（连接到具体数据库）
    try:
        from data_loader.db_manager import DatabaseManager
        db = DatabaseManager()
        db.close()
        print("✅ 数据库连接成功")
        print()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("💡 请检查数据库配置和权限")
        return None
    
    # 导入数据
    importer = DataImporter()
    
    try:
        stats = importer.import_all(force=force)
        return stats
    finally:
        importer.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='初始化数据库 - 导入 Data 目录中的 SQL 文件')
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新导入已存在的表（会删除现有表）'
    )
    
    args = parser.parse_args()
    
    try:
        stats = init_database(force=args.force)
        
        if stats is None:
            print("❌ 初始化失败")
            sys.exit(1)
        
        if stats['failed'] > 0:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

