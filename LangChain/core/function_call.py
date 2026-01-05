"""FunctionCall 系统"""
from typing import Dict, List, Any, Callable, Optional
from functools import wraps
from data_loader.db_manager import DatabaseManager


class FunctionRegistry:
    """函数注册表"""
    
    def __init__(self):
        self.functions: Dict[str, Dict] = {}
        self.db_manager = DatabaseManager()
    
    def register(self, name: str, description: str = ""):
        """注册函数装饰器"""
        def decorator(func: Callable):
            self.functions[name] = {
                'function': func,
                'name': name,
                'description': description or func.__doc__ or "",
                'signature': self._get_signature(func)
            }
            return func
        return decorator
    
    def _get_signature(self, func: Callable) -> str:
        """获取函数签名"""
        import inspect
        sig = inspect.signature(func)
        return str(sig)
    
    def get_function(self, name: str) -> Optional[Callable]:
        """获取函数"""
        if name in self.functions:
            return self.functions[name]['function']
        return None
    
    def list_functions(self) -> List[Dict]:
        """列出所有函数"""
        return [
            {
                'name': info['name'],
                'description': info['description'],
                'signature': info['signature']
            }
            for info in self.functions.values()
        ]
    
    def call_function(self, name: str, **kwargs) -> Any:
        """调用函数"""
        func = self.get_function(name)
        if func:
            return func(**kwargs)
        raise ValueError(f"Function {name} not found")


# 全局函数注册表
registry = FunctionRegistry()


@registry.register(
    name="get_table_schema",
    description="获取指定表的结构信息，包括表名和所有字段的详细信息"
)
def get_table_schema(table_name: str) -> Dict:
    """获取表结构"""
    return registry.db_manager.get_table_schema(table_name)


@registry.register(
    name="list_tables",
    description="列出数据库中所有表的名称"
)
def list_tables() -> List[str]:
    """列出所有表"""
    return registry.db_manager.get_table_names()


@registry.register(
    name="execute_sql",
    description="执行 SQL 查询语句并返回结果"
)
def execute_sql(query: str) -> List[Dict[str, Any]]:
    """执行 SQL 查询"""
    return registry.db_manager.execute_sql(query)


@registry.register(
    name="validate_sql",
    description="验证 SQL 语句的语法是否正确"
)
def validate_sql(query: str) -> Dict[str, Any]:
    """验证 SQL 语法"""
    try:
        # 简单验证：尝试解析 SQL
        registry.db_manager.execute_sql(f"EXPLAIN {query}")
        return {'valid': True, 'message': 'SQL syntax is valid'}
    except Exception as e:
        return {'valid': False, 'message': str(e)}


@registry.register(
    name="explain_sql",
    description="获取 SQL 查询的执行计划"
)
def explain_sql(query: str) -> List[Dict[str, Any]]:
    """获取 SQL 执行计划"""
    try:
        return registry.db_manager.execute_sql(f"EXPLAIN {query}")
    except Exception as e:
        return [{'error': str(e)}]

