"""数据库连接和管理"""
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from config.settings import DB_CONFIG


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine: Optional[Engine] = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        connection_string = (
            f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            f"?charset={DB_CONFIG['charset']}"
        )
        
        self.engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False
        )
    
    def execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        """执行 SQL 查询"""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def execute_update(self, sql: str) -> int:
        """执行更新操作（INSERT/UPDATE/DELETE）"""
        with self.engine.begin() as conn:
            result = conn.execute(text(sql))
            return result.rowcount
    
    def get_table_names(self) -> List[str]:
        """获取所有表名"""
        inspector = inspect(self.engine)
        return inspector.get_table_names()
    
    def get_table_schema(self, table_name: str) -> Dict:
        """获取表结构"""
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        return {
            'table_name': table_name,
            'columns': [
                {
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col['nullable'],
                    'default': col.get('default')
                }
                for col in columns
            ]
        }
    
    def get_all_schemas(self) -> Dict[str, Dict]:
        """获取所有表的结构"""
        tables = {}
        for table_name in self.get_table_names():
            tables[table_name] = self.get_table_schema(table_name)
        return tables
    
    def close(self):
        """关闭连接"""
        if self.engine:
            self.engine.dispose()

