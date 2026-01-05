"""Text2SQL Web 应用 - Streamlit 界面"""
import sys
import streamlit as st
from pathlib import Path
import pandas as pd
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.sql_copilot import SQLCopilot
from data_loader.db_manager import DatabaseManager
from config.settings import print_config, validate_config


# 页面配置
st.set_page_config(
    page_title="Text2SQL - 自然语言 SQL 查询",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 session state
if 'copilot' not in st.session_state:
    st.session_state.copilot = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = None
if 'generated_sql' not in st.session_state:
    st.session_state.generated_sql = ""
if 'sql_result' not in st.session_state:
    st.session_state.sql_result = None


def init_copilot():
    """初始化 SQL Copilot"""
    if st.session_state.copilot is None:
        try:
            with st.spinner("正在初始化 SQL Copilot..."):
                st.session_state.copilot = SQLCopilot()
                st.session_state.db_manager = DatabaseManager()
            return True
        except Exception as e:
            st.error(f"初始化失败: {str(e)}")
            return False
    return True


def get_table_info():
    """获取表信息"""
    if st.session_state.db_manager:
        try:
            tables = st.session_state.db_manager.get_table_names()
            return tables
        except:
            return []
    return []


def main():
    """主函数"""
    # 标题
    st.title("🚀 Text2SQL - 自然语言 SQL 查询工具")
    st.markdown("---")
    
    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 配置信息")
        
        # 显示配置
        if st.button("📋 查看配置"):
            try:
                with st.expander("当前配置", expanded=True):
                    print_config()
            except Exception as e:
                st.error(f"无法读取配置: {e}")
        
        # 验证配置
        if st.button("✅ 验证配置"):
            if validate_config():
                st.success("配置验证通过！")
            else:
                st.error("配置验证失败，请检查 .env 文件")
        
        st.markdown("---")
        
        # 数据库信息
        st.header("📊 数据库信息")
        if st.button("🔄 刷新表列表"):
            st.rerun()
        
        tables = get_table_info()
        if tables:
            st.success(f"已连接数据库，共 {len(tables)} 个表")
            with st.expander("表列表", expanded=True):
                for table in tables:
                    st.text(f"  • {table}")
        else:
            st.warning("未连接数据库或数据库为空")
        
        st.markdown("---")
        
        # 查询历史
        st.header("📜 查询历史")
        if st.session_state.history:
            st.info(f"共 {len(st.session_state.history)} 条记录")
            if st.button("🗑️ 清空历史"):
                st.session_state.history = []
                st.rerun()
        else:
            st.info("暂无查询历史")
    
    # 主内容区
    # 初始化检查
    if not init_copilot():
        st.error("请先配置 .env 文件并确保数据库连接正常")
        st.stop()
    
    # 输入区域
    st.header("💬 自然语言查询")
    
    # 示例问题
    example_questions = [
        "查询所有表的名称",
        "查询前10个代理人的姓名和邮箱",
        "统计每个表的记录数",
        "查询代理人的总数",
    ]
    
    # 初始化 session state
    if 'question_input' not in st.session_state:
        st.session_state.question_input = ""
    if 'set_question' not in st.session_state:
        st.session_state.set_question = None
    if 'clear_all' not in st.session_state:
        st.session_state.clear_all = False
    
    # 处理清空操作（必须在 widget 创建之前）
    if st.session_state.clear_all:
        st.session_state.question_input = ""
        st.session_state.set_question = None
        st.session_state.generated_sql = ""
        st.session_state.sql_result = None
        st.session_state.clear_all = False
    
    # 处理示例问题按钮点击
    example_clicked = None
    with st.expander("💡 示例问题", expanded=False):
        cols = st.columns(2)
        for i, example in enumerate(example_questions):
            with cols[i % 2]:
                if st.button(example, key=f"example_{i}", use_container_width=True):
                    example_clicked = example
    
    # 如果点击了示例问题，设置到 session state
    if example_clicked:
        st.session_state.set_question = example_clicked
        st.rerun()
    
    # 如果设置了问题，更新输入框的值
    if st.session_state.set_question:
        st.session_state.question_input = st.session_state.set_question
        st.session_state.set_question = None
    
    col1, col2 = st.columns([3, 1])
    with col1:
        question = st.text_input(
            "请输入您的问题：",
            placeholder="例如：查询所有代理人的姓名和邮箱",
            value=st.session_state.question_input,
            key="question_input"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎲 随机示例", use_container_width=True):
            import random
            selected = random.choice(example_questions)
            st.session_state.set_question = selected
            st.rerun()
    
    # 步骤一：生成 SQL
    st.markdown("---")
    st.header("📝 步骤一：生成 SQL")
    st.caption("💡 输入自然语言问题，点击「生成 SQL」按钮，系统将自动生成对应的 SQL 查询语句")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        generate_button = st.button("✨ 生成 SQL", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ 清空", use_container_width=True)
    
    # 处理清空操作
    if clear_button:
        st.session_state.clear_all = True
        st.rerun()
    
    # 生成 SQL
    if generate_button and question:
        with st.spinner("🤔 正在根据自然语言生成 SQL..."):
            try:
                # 使用 Agent 生成 SQL
                agent = st.session_state.copilot.agent
                sql_result = agent.generate_sql(question)
                
                if sql_result.get('success'):
                    st.session_state.generated_sql = sql_result.get('sql', '')
                    st.session_state.sql_result = None  # 清空之前的结果
                    st.success("✅ SQL 生成成功！")
                else:
                    st.error("❌ SQL 生成失败")
                    error_msg = sql_result.get('error', '未知错误')
                    st.error(f"错误信息: {error_msg}")
                    st.session_state.generated_sql = ""
            
            except Exception as e:
                st.error(f"发生错误: {str(e)}")
                import traceback
                with st.expander("🔍 查看错误详情", expanded=True):
                    st.code(traceback.format_exc(), language='text')
    
    # 显示生成的 SQL
    if st.session_state.generated_sql:
        st.markdown("### 📄 生成的 SQL 语句")
        
        # 可编辑的 SQL 输入框
        edited_sql = st.text_area(
            "SQL 语句（可以编辑）：",
            value=st.session_state.generated_sql,
            height=150,
            key="sql_editor",
            help="您可以修改生成的 SQL 语句后再执行"
        )
        
        # 更新 session state
        st.session_state.generated_sql = edited_sql
        
        # 步骤二：执行 SQL
        st.markdown("---")
        st.header("⚡ 步骤二：执行 SQL")
        st.caption("💡 检查生成的 SQL 语句，可以手动编辑修改，然后点击「执行 SQL」按钮查看查询结果")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            execute_button = st.button("🚀 执行 SQL", type="primary", use_container_width=True)
        
        # 执行 SQL
        if execute_button:
            with st.spinner("⏳ 正在执行 SQL 查询..."):
                try:
                    agent = st.session_state.copilot.agent
                    result = agent.execute_sql(edited_sql)
                    
                    st.session_state.sql_result = result
                    
                    # 记录历史
                    st.session_state.history.append({
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'question': question,
                        'sql': edited_sql,
                        'result': result
                    })
                    
                    # 显示结果
                    if result.get('success'):
                        st.success(f"✅ 查询成功！共返回 {result.get('row_count', 0)} 条记录")
                        
                        # 显示数据表格
                        data = result.get('data', [])
                        if data:
                            df = pd.DataFrame(data)
                            st.markdown("### 📊 查询结果")
                            st.dataframe(df, use_container_width=True)
                            
                            # 下载按钮
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 下载 CSV",
                                data=csv,
                                file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        else:
                            st.info("查询成功，但没有返回数据")
                    else:
                        st.error("❌ SQL 执行失败")
                        error_msg = result.get('error', '未知错误')
                        st.error(f"错误信息: {error_msg}")
                        
                        # 显示错误详情
                        with st.expander("🔍 查看错误详情", expanded=False):
                            st.code(str(error_msg), language='text')
                
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
                    import traceback
                    with st.expander("🔍 查看错误详情", expanded=True):
                        st.code(traceback.format_exc(), language='text')
        
        # 显示之前的结果（如果有）
        if st.session_state.sql_result and not execute_button:
            result = st.session_state.sql_result
            if result.get('success'):
                st.success(f"✅ 查询成功！共返回 {result.get('row_count', 0)} 条记录")
                data = result.get('data', [])
                if data:
                    df = pd.DataFrame(data)
                    st.markdown("### 📊 查询结果")
                    st.dataframe(df, use_container_width=True)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 下载 CSV",
                        data=csv,
                        file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
    
    # 查询历史显示
    if st.session_state.history:
        st.markdown("---")
        st.header("📜 查询历史")
        
        # 显示最近的历史记录
        for i, record in enumerate(reversed(st.session_state.history[-10:]), 1):
            with st.expander(f"{record['time']} - {record['question'][:50]}...", expanded=False):
                st.markdown("**问题:**")
                st.text(record['question'])
                
                if 'sql' in record:
                    st.markdown("**生成的 SQL:**")
                    st.code(record['sql'], language='sql')
                
                result = record.get('result', {})
                if result.get('success'):
                    st.success(f"✅ 成功 - 返回 {result.get('row_count', 0)} 条记录")
                    if result.get('data'):
                        df = pd.DataFrame(result['data'])
                        st.dataframe(df.head(10), use_container_width=True)
                        if len(result['data']) > 10:
                            st.caption(f"显示前 10 条，共 {len(result['data'])} 条记录")
                else:
                    st.error("❌ 失败")
                    st.text(result.get('error', '')[:200])
    
    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Text2SQL - 基于 LangChain 的自然语言 SQL 查询工具"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == '__main__':
    main()

