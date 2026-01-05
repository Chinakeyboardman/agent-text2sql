"""基本使用示例"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.sql_agent import SQLAgent
from core.sql_copilot import SQLCopilot


def example_agent():
    """SQL Agent 示例"""
    print("=" * 60)
    print("示例 1: 使用 SQL Agent")
    print("=" * 60)
    
    agent = SQLAgent()
    
    # 查询示例
    questions = [
        "数据库中有哪些表？",
        "查询前5个代理人的姓名和邮箱",
    ]
    
    for question in questions:
        print(f"\n问题: {question}")
        result = agent.query(question)
        print(f"结果: {result}")
    
    agent.close()


def example_copilot():
    """SQL Copilot 示例"""
    print("\n" + "=" * 60)
    print("示例 2: 使用 SQL Copilot")
    print("=" * 60)
    
    copilot = SQLCopilot()
    
    # 获取表建议
    tables = copilot.get_table_suggestions()
    print(f"\n数据库中的表: {tables}")
    
    # 查询示例
    question = "查询所有表的名称"
    print(f"\n问题: {question}")
    result = copilot.query(question)
    print(f"结果: {copilot.format_result(result)}")
    
    copilot.close()


if __name__ == '__main__':
    example_agent()
    example_copilot()

