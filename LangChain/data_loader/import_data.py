"""数据导入脚本 - 自动导入 Data 目录中的 SQL 文件"""
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict
from sqlalchemy import text

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader.db_manager import DatabaseManager
from data_loader.sql_parser import SQLParser
from config.settings import DATA_DIR


class DataImporter:
    """数据导入器"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.stats = {
            'total_files': 0,
            'imported': 0,
            'skipped': 0,
            'failed': 0,
            'errors': []
        }
    
    def check_table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            existing_tables = self.db_manager.get_table_names()
            return table_name.lower() in [t.lower() for t in existing_tables]
        except Exception as e:
            print(f"⚠️  检查表 {table_name} 时出错: {e}")
            return False
    
    def split_sql_statements(self, sql_content: str) -> List[str]:
        """将 SQL 文件内容分割成独立的 SQL 语句"""
        # 移除注释
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
        sql_content = re.sub(r'--.*?\n', '\n', sql_content)
        
        # 按分号分割，但要注意字符串中的分号
        statements = []
        current_statement = []
        in_string = False
        string_char = None
        
        for char in sql_content:
            if char in ("'", '"', '`') and not (current_statement and current_statement[-1] == '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
            
            current_statement.append(char)
            
            if not in_string and char == ';':
                stmt = ''.join(current_statement).strip()
                if stmt and not stmt.startswith('--'):
                    statements.append(stmt)
                current_statement = []
        
        # 添加最后一个语句（如果没有分号结尾）
        if current_statement:
            stmt = ''.join(current_statement).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
        
        return statements
    
    def execute_sql_file(self, sql_file: Path) -> Tuple[bool, str]:
        """执行 SQL 文件"""
        try:
            # 读取 SQL 文件
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 分割 SQL 语句
            statements = self.split_sql_statements(sql_content)
            
            if not statements:
                return False, "SQL 文件为空或格式错误"
            
            # 执行每个 SQL 语句
            with self.db_manager.engine.begin() as conn:
                for i, statement in enumerate(statements, 1):
                    statement = statement.strip()
                    if not statement or statement.startswith('--'):
                        continue
                    
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        # 忽略 DROP TABLE IF EXISTS 的错误（表不存在时）
                        if 'DROP TABLE' in statement.upper() and 'IF EXISTS' in statement.upper():
                            continue
                        # 其他错误需要记录
                        error_msg = f"执行第 {i} 条语句时出错: {str(e)}"
                        print(f"  ⚠️  {error_msg}")
                        # 继续执行下一条语句
            
            return True, "导入成功"
        
        except Exception as e:
            return False, f"导入失败: {str(e)}"
    
    def import_sql_file(self, sql_file: Path, force: bool = False) -> Dict:
        """导入单个 SQL 文件"""
        result = {
            'file': sql_file.name,
            'status': 'unknown',
            'message': '',
            'table_name': None
        }
        
        try:
            # 解析表名
            parser = SQLParser(sql_file)
            table_name = parser.get_table_name()
            result['table_name'] = table_name
            
            if not table_name:
                result['status'] = 'failed'
                result['message'] = '无法解析表名'
                return result
            
            # 检查表是否已存在
            if self.check_table_exists(table_name):
                if force:
                    print(f"  ⚠️  表 {table_name} 已存在，强制重新导入...")
                    # 删除现有表
                    with self.db_manager.engine.begin() as conn:
                        conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
                else:
                    result['status'] = 'skipped'
                    result['message'] = f'表 {table_name} 已存在，跳过导入'
                    return result
            
            # 执行导入
            print(f"  📥 正在导入 {sql_file.name}...")
            success, message = self.execute_sql_file(sql_file)
            
            if success:
                result['status'] = 'imported'
                result['message'] = message
            else:
                result['status'] = 'failed'
                result['message'] = message
        
        except Exception as e:
            result['status'] = 'failed'
            result['message'] = f'处理文件时出错: {str(e)}'
        
        return result
    
    def import_all(self, force: bool = False) -> Dict:
        """导入所有 SQL 文件"""
        print("=" * 60)
        print("📦 数据导入工具")
        print("=" * 60)
        
        # 获取所有 SQL 文件
        sql_files = sorted(DATA_DIR.glob('*.sql'))
        self.stats['total_files'] = len(sql_files)
        
        if not sql_files:
            print(f"❌ 在 {DATA_DIR} 目录中未找到 SQL 文件")
            return self.stats
        
        print(f"\n📂 找到 {len(sql_files)} 个 SQL 文件")
        print(f"📁 数据目录: {DATA_DIR}\n")
        
        # 检查数据库连接
        try:
            existing_tables = self.db_manager.get_table_names()
            print(f"📊 数据库中现有表: {len(existing_tables)} 个")
            if existing_tables:
                print(f"   表列表: {', '.join(existing_tables[:5])}{'...' if len(existing_tables) > 5 else ''}")
        except Exception as e:
            print(f"⚠️  无法连接数据库: {e}")
            return self.stats
        
        print("\n" + "-" * 60)
        
        # 导入每个文件
        for i, sql_file in enumerate(sql_files, 1):
            print(f"\n[{i}/{len(sql_files)}] 处理文件: {sql_file.name}")
            result = self.import_sql_file(sql_file, force=force)
            
            if result['status'] == 'imported':
                self.stats['imported'] += 1
                print(f"  ✅ {result['message']}")
            elif result['status'] == 'skipped':
                self.stats['skipped'] += 1
                print(f"  ⏭️  {result['message']}")
            else:
                self.stats['failed'] += 1
                self.stats['errors'].append({
                    'file': result['file'],
                    'error': result['message']
                })
                print(f"  ❌ {result['message']}")
        
        # 打印统计信息
        print("\n" + "=" * 60)
        print("📊 导入统计")
        print("=" * 60)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"✅ 成功导入: {self.stats['imported']}")
        print(f"⏭️  跳过: {self.stats['skipped']}")
        print(f"❌ 失败: {self.stats['failed']}")
        
        if self.stats['errors']:
            print("\n❌ 错误详情:")
            for error in self.stats['errors']:
                print(f"  - {error['file']}: {error['error']}")
        
        # 显示最终表列表
        try:
            final_tables = self.db_manager.get_table_names()
            print(f"\n📊 数据库中现有表: {len(final_tables)} 个")
            if final_tables:
                print(f"   表列表: {', '.join(final_tables)}")
        except:
            pass
        
        print("=" * 60)
        
        return self.stats
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='导入 Data 目录中的 SQL 文件到数据库')
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新导入已存在的表（会删除现有表）'
    )
    
    args = parser.parse_args()
    
    importer = DataImporter()
    
    try:
        stats = importer.import_all(force=args.force)
        
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
    finally:
        importer.close()


if __name__ == '__main__':
    main()

