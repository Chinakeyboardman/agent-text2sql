"""SQL Copilot - 交互式 SQL 辅助工具"""
from typing import Optional, Dict, Any, List
from core.sql_agent import SQLAgent
from core.function_call import registry
from data_loader.db_manager import DatabaseManager
import json


class SQLCopilot:
    """SQL Copilot 主类"""
    
    def __init__(self, model_type: Optional[str] = None):
        self.agent = SQLAgent(model_type)
        self.db_manager = DatabaseManager()
        self.history: List[Dict] = []
    
    def query(self, question: str) -> Dict[str, Any]:
        """执行查询"""
        result = self.agent.query(question)
        
        # 记录历史
        self.history.append({
            'question': question,
            'result': result
        })
        
        return result
    
    def get_table_suggestions(self, prefix: str = "") -> List[str]:
        """获取表名建议"""
        tables = self.db_manager.get_table_names()
        if prefix:
            return [t for t in tables if t.lower().startswith(prefix.lower())]
        return tables
    
    def get_column_suggestions(self, table_name: str, prefix: str = "") -> List[str]:
        """获取字段名建议"""
        try:
            schema = self.db_manager.get_table_schema(table_name)
            columns = [col['name'] for col in schema['columns']]
            if prefix:
                return [c for c in columns if c.lower().startswith(prefix.lower())]
            return columns
        except:
            return []
    
    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """验证 SQL"""
        return registry.call_function('validate_sql', query=sql)
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """格式化查询结果"""
        if not result.get('success'):
            return f"❌ 错误: {result.get('error', 'Unknown error')}"
        
        answer = result.get('answer', '')
        return f"✅ {answer}"
    
    def export_history(self, format: str = 'json') -> str:
        """导出查询历史"""
        if format == 'json':
            return json.dumps(self.history, ensure_ascii=False, indent=2)
        elif format == 'csv':
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['问题', '结果'])
            for item in self.history:
                writer.writerow([item['question'], str(item['result'])])
            return output.getvalue()
        return str(self.history)
    
    def close(self):
        """关闭连接"""
        self.agent.close()

