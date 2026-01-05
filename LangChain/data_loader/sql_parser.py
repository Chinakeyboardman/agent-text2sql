"""SQL 文件解析器"""
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class SQLParser:
    """解析 SQL 文件，提取表结构和数据"""
    
    def __init__(self, sql_file: Path):
        self.sql_file = sql_file
        self.content = self._read_file()
    
    def _read_file(self) -> str:
        """读取 SQL 文件内容"""
        with open(self.sql_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def parse_table_structure(self) -> Optional[Dict]:
        """解析表结构"""
        # 查找 CREATE TABLE 语句
        create_pattern = r'CREATE TABLE\s+`?(\w+)`?\s*\((.*?)\)\s*ENGINE'
        match = re.search(create_pattern, self.content, re.DOTALL | re.IGNORECASE)
        
        if not match:
            return None
        
        table_name = match.group(1)
        columns_text = match.group(2)
        
        # 解析字段
        columns = []
        column_pattern = r'`?(\w+)`?\s+(\w+(?:\([^)]+\))?)\s*(.*?)(?:,|$)'
        
        for col_match in re.finditer(column_pattern, columns_text, re.IGNORECASE):
            col_name = col_match.group(1)
            col_type = col_match.group(2)
            col_attrs = col_match.group(3)
            
            is_nullable = 'NOT NULL' not in col_attrs.upper()
            is_primary = 'PRIMARY KEY' in col_attrs.upper()
            
            columns.append({
                'name': col_name,
                'type': col_type,
                'nullable': is_nullable,
                'primary_key': is_primary
            })
        
        return {
            'table_name': table_name,
            'columns': columns
        }
    
    def get_table_name(self) -> Optional[str]:
        """获取表名"""
        structure = self.parse_table_structure()
        return structure['table_name'] if structure else None
    
    def get_columns_info(self) -> List[Dict]:
        """获取字段信息"""
        structure = self.parse_table_structure()
        return structure['columns'] if structure else []
    
    def get_schema_string(self) -> str:
        """获取表结构的字符串描述"""
        structure = self.parse_table_structure()
        if not structure:
            return ""
        
        lines = [f"表名: {structure['table_name']}"]
        lines.append("字段:")
        for col in structure['columns']:
            nullable = "可空" if col['nullable'] else "非空"
            pk = "主键" if col['primary_key'] else ""
            lines.append(f"  - {col['name']}: {col['type']} ({nullable}{', ' + pk if pk else ''})")
        
        return "\n".join(lines)


def parse_all_sql_files(data_dir: Path) -> Dict[str, Dict]:
    """解析所有 SQL 文件"""
    sql_files = list(data_dir.glob('*.sql'))
    tables_info = {}
    
    for sql_file in sql_files:
        parser = SQLParser(sql_file)
        table_name = parser.get_table_name()
        if table_name:
            tables_info[table_name] = {
                'file': sql_file.name,
                'structure': parser.parse_table_structure(),
                'schema_string': parser.get_schema_string()
            }
    
    return tables_info

