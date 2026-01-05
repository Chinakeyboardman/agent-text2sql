"""SQL Copilot CLI 交互界面"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.sql_copilot import SQLCopilot


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 SQL Copilot - 自然语言 SQL 查询工具")
    print("=" * 60)
    print("\n输入自然语言问题，系统将自动生成 SQL 并执行查询")
    print("输入 'exit' 或 'quit' 退出")
    print("输入 'history' 查看查询历史")
    print("输入 'tables' 查看所有表")
    print("输入 'help' 查看帮助\n")
    
    copilot = SQLCopilot()
    
    try:
        while True:
            try:
                question = input("\n💬 请输入您的问题: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 再见！")
                    break
                
                if question.lower() == 'history':
                    print("\n📜 查询历史:")
                    for i, item in enumerate(copilot.history, 1):
                        print(f"\n{i}. 问题: {item['question']}")
                        print(f"   结果: {copilot.format_result(item['result'])}")
                    continue
                
                if question.lower() == 'tables':
                    tables = copilot.get_table_suggestions()
                    print(f"\n📊 数据库中的表 ({len(tables)} 个):")
                    for table in tables:
                        print(f"  - {table}")
                    continue
                
                if question.lower() == 'help':
                    print("\n📖 帮助信息:")
                    print("  - 直接输入自然语言问题，如：'查询所有代理人的姓名'")
                    print("  - 'tables' - 查看所有表")
                    print("  - 'history' - 查看查询历史")
                    print("  - 'exit' - 退出程序")
                    continue
                
                # 执行查询
                print("\n⏳ 正在处理...")
                result = copilot.query(question)
                print(f"\n{copilot.format_result(result)}")
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {str(e)}")
    
    finally:
        copilot.close()


if __name__ == '__main__':
    main()

