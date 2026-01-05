"""SQL 解析器测试"""
import unittest
from pathlib import Path
from data_loader.sql_parser import SQLParser
from config.settings import DATA_DIR


class TestSQLParser(unittest.TestCase):
    """SQL 解析器测试类"""
    
    def test_parse_table_structure(self):
        """测试表结构解析"""
        sql_file = DATA_DIR / 'agentinfo.sql'
        if sql_file.exists():
            parser = SQLParser(sql_file)
            structure = parser.parse_table_structure()
            self.assertIsNotNone(structure)
            self.assertIn('table_name', structure)
            self.assertIn('columns', structure)


if __name__ == '__main__':
    unittest.main()

