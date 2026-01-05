"""LangChain SQL Agent"""
import re
from typing import Optional, Dict, Any, List, Tuple
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from core.llm_adapter import LLMFactory
from data_loader.db_manager import DatabaseManager
from config.settings import LLM_CONFIG


class SQLAgent:
    """SQL Agent 封装类"""
    
    def __init__(self, model_type: Optional[str] = None):
        self.db_manager = DatabaseManager()
        self.llm = LLMFactory.create_llm(model_type)
        self._init_agent()
    
    def _init_agent(self):
        """初始化 Agent"""
        # 创建 SQLDatabase 实例
        db = SQLDatabase(
            self.db_manager.engine,
            include_tables=self.db_manager.get_table_names()
        )
        
        # 创建工具包
        toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
        
        # 保存工具包和数据库实例供后续使用
        self.toolkit = toolkit
        self.sql_db = db
        
        # 创建 Agent
        self.agent = create_sql_agent(
            llm=self.llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True
        )
    
    def _get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
        """获取表的示例数据"""
        try:
            result = self.db_manager.execute_sql(f"SELECT * FROM `{table_name}` LIMIT {limit}")
            return result
        except:
            return []
    
    def _get_distinct_values(self, table_name: str, column_name: str, limit: int = 20) -> List[str]:
        """获取字段的唯一值（用于状态字段等）"""
        try:
            result = self.db_manager.execute_sql(
                f"SELECT DISTINCT `{column_name}` FROM `{table_name}` WHERE `{column_name}` IS NOT NULL LIMIT {limit}"
            )
            return [str(row[column_name]) for row in result if row[column_name] is not None]
        except:
            return []
    
    def generate_sql(self, question: str) -> Dict[str, Any]:
        """根据自然语言生成 SQL（不执行）- 使用 LangChain SQL Agent 工具能力"""
        try:
            # 方法：使用 LangChain SQL Agent 的工具来帮助生成 SQL
            # 先让 Agent 查询表结构，然后基于结构生成 SQL
            
            # 获取数据库结构信息
            schema_info = self.get_schema_info()
            tables = schema_info['tables']
            
            if not tables:
                return {
                    'success': False,
                    'error': '数据库中没有任何表',
                    'sql': None
                }
            
            # 使用 SQLDatabase 的工具获取表结构描述
            try:
                # 获取表结构描述（LangChain SQLDatabase 提供的方法）
                db = SQLDatabase(
                    self.db_manager.engine,
                    include_tables=tables
                )
                # 获取所有表的描述
                table_info = db.get_table_info_no_throw()
            except:
                table_info = None
            
            # 构建详细的表结构信息，包括示例数据
            schema_parts = []
            schema_parts.append(f"数据库中有以下表：{', '.join(tables)}\n")
            
            # 添加所有表的完整结构信息和示例数据
            for table_name in tables:
                try:
                    schema = self.db_manager.get_table_schema(table_name)
                    schema_parts.append(f"\n表 {table_name} 的完整字段列表：")
                    
                    # 显示所有字段，包含完整类型信息
                    status_columns = []  # 记录可能是状态字段的列
                    date_columns = []    # 记录日期时间字段
                    
                    for col in schema['columns']:
                        col_name = col['name']
                        col_type = str(col['type'])
                        # 简化类型显示
                        if 'VARCHAR' in col_type or 'TEXT' in col_type:
                            type_desc = '文本'
                        elif 'INT' in col_type or 'BIGINT' in col_type:
                            type_desc = '数字'
                        elif 'DATETIME' in col_type or 'DATE' in col_type or 'TIMESTAMP' in col_type:
                            type_desc = '日期时间'
                            date_columns.append(col_name)
                        else:
                            type_desc = col_type
                        schema_parts.append(f"  {col_name} ({type_desc})")
                        
                        # 识别状态字段（包含 Status 的字段）
                        if 'Status' in col_name or 'State' in col_name:
                            status_columns.append(col_name)
                    
                    # 获取状态字段的实际值
                    for status_col in status_columns:
                        distinct_values = self._get_distinct_values(table_name, status_col, limit=10)
                        if distinct_values:
                            values_str = ', '.join([f"'{v}'" for v in distinct_values])
                            schema_parts.append(f"\n  字段 {status_col} 的可能值：{values_str}")
                    
                    # 获取示例数据帮助理解字段含义和可能的值
                    samples = self._get_sample_data(table_name, limit=2)
                    if samples:
                        schema_parts.append(f"\n  示例数据（帮助理解字段含义和可能的值）：")
                        for i, sample in enumerate(samples, 1):
                            sample_items = []
                            for k, v in list(sample.items())[:8]:  # 显示前8个字段
                                if v is not None:
                                    sample_items.append(f"{k}='{v}'")
                                else:
                                    sample_items.append(f"{k}=NULL")
                            schema_parts.append(f"    示例{i}: {', '.join(sample_items)}")
                
                except Exception as e:
                    schema_parts.append(f"\n表 {table_name}: 无法获取结构信息 ({str(e)})")
            
            schema_prompt = "\n".join(schema_parts)
            
            # 如果 LangChain 提供了表信息，也加入
            if table_info:
                schema_prompt += f"\n\nLangChain 表结构描述：\n{table_info}"
            
            # 添加 Few-shot 示例（基于实际表结构）
            few_shot_examples = """
参考示例（请严格按照这些示例的格式）：

问题1：查询所有代理人的姓名和邮箱
SQL：SELECT Name, EmailAddress FROM agentinfo

问题2：查询前10个代理人的姓名和邮箱  
SQL：SELECT Name, EmailAddress FROM agentinfo LIMIT 10

问题3：查询状态为"已批准"的理赔记录
SQL：SELECT * FROM claiminfo WHERE ClaimStatus = '已批准'

问题4：查询已审核但尚未支付的理赔记录，包括理赔号、审核人和审核日期
SQL：SELECT ClaimNumber, ClaimHandler, ReviewDate FROM claiminfo WHERE ClaimStatus IN ('已批准', '审核中') AND PaymentDate IS NULL

问题5：查询所有客户的信息
SQL：SELECT * FROM customerinfo

问题6：查看表结构或字段信息
SQL：DESCRIBE claiminfo 或 SHOW COLUMNS FROM claiminfo

问题7：查看数据库中的表列表
SQL：SHOW TABLES

重要规则：
1. 字段名必须完全匹配表结构中的字段名（注意大小写）
2. 状态值必须使用表结构中显示的实际值（不要自己编造值）
3. 对于日期时间字段（DATETIME/DATE/TIMESTAMP），判断是否为空只能使用 IS NULL，不能使用 = '' 或 = NULL
4. 如果问题提到"尚未支付"、"未支付"，使用 PaymentDate IS NULL（不要使用 PaymentDate = ''）
5. 可以生成 SELECT、DESCRIBE、SHOW、EXPLAIN 等只读查询语句
"""
            
            prompt = f"""你是一个专业的 SQL 专家。请根据用户的问题和数据库结构生成准确的 SQL 查询语句。

数据库结构（包含所有字段和示例数据）：
{schema_prompt}

{few_shot_examples}

用户问题：{question}

生成 SQL 的步骤：
1. 仔细分析用户问题中的关键词（如：审核人、审核日期、支付、状态、理赔号等）
2. 在表结构中找到包含这些关键词的字段名（字段名是英文的，如 ClaimHandler 对应"审核人"）
3. 查看表结构中显示的状态字段的可能值，使用实际的值（不要自己编造）
4. 根据问题要求构建 WHERE 条件：
   - "已审核但尚未支付" = ClaimStatus IN ('已批准', '审核中') AND PaymentDate IS NULL
   - "状态为X" = ClaimStatus = 'X'（X必须是表结构中显示的实际值）
   - "尚未支付"、"未支付" = PaymentDate IS NULL（注意：日期字段不能使用 = ''）
   - "前N个" = LIMIT N
5. 生成完整的 SQL 语句

重要要求：
- 只返回 SQL 语句，不要包含任何解释、注释或错误说明
- 使用标准的 MySQL 语法
- 字段名和表名必须完全匹配表结构中的名称（注意大小写）
- 状态值必须使用表结构中显示的实际值，不要自己编造（如：如果表结构显示 ClaimStatus 的值是 '已批准'、'审核中'、'已拒绝'，就不要使用 '已审核'）
- 对于日期时间字段（DATETIME/DATE/TIMESTAMP），判断是否为空只能使用 IS NULL，绝对不能使用 = '' 或 = NULL
- 如果问题提到"尚未支付"、"未支付"，必须使用 PaymentDate IS NULL（不要使用 PaymentDate = ''）
- 可以生成 SELECT、DESCRIBE、SHOW、EXPLAIN 等只读查询语句
- 如果用户询问表结构、字段信息，可以使用 DESCRIBE table_name 或 SHOW COLUMNS FROM table_name
- 如果用户询问数据库中的表列表，可以使用 SHOW TABLES
- 必须生成有效的 SQL 语句，不要返回错误信息

SQL 语句："""
            
            # 使用 LLM 生成 SQL
            sql_response = self.llm.invoke(prompt)
            sql = sql_response.strip()
            
            # 检查是否是错误信息
            if sql.upper().startswith("ERROR:") or sql.upper().startswith("错误") or "无法" in sql or "没有" in sql[:50]:
                return {
                    'success': False,
                    'error': sql,
                    'sql': None
                }
            
            # 清理 SQL（移除可能的代码块标记）
            if "```sql" in sql:
                start = sql.find("```sql") + 6
                end = sql.find("```", start)
                if end != -1:
                    sql = sql[start:end].strip()
            elif "```" in sql:
                parts = sql.split("```")
                if len(parts) >= 3:
                    sql = parts[1].strip()
                    if sql.startswith("sql"):
                        sql = sql[3:].strip()
            
            # 移除可能的解释文字
            lines = sql.split('\n')
            sql_lines = []
            in_sql = False
            # 允许的 SQL 关键字（只读查询）
            allowed_keywords = ['SELECT', 'DESCRIBE', 'DESC', 'SHOW', 'EXPLAIN', 'USE']
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 跳过注释和解释
                if line.startswith('--') or line.startswith('//') or line.startswith('/*'):
                    continue
                
                # 如果已经在 SQL 中，继续添加行直到遇到分号
                if in_sql:
                    sql_lines.append(line)
                    # 如果遇到分号，结束
                    if line.endswith(';'):
                        break
                    continue
                
                # 检查是否是允许的 SQL 语句开始
                line_upper = line.upper()
                for keyword in allowed_keywords:
                    if line_upper.startswith(keyword) or f' {keyword} ' in f' {line_upper} ':
                        in_sql = True
                        sql_lines.append(line)
                        # 如果遇到分号，结束
                        if line.endswith(';'):
                            break
                        break
            
            if sql_lines:
                sql = ' '.join(sql_lines).strip()
                # 移除末尾的分号（如果有）
                if sql.endswith(';'):
                    sql = sql[:-1].strip()
                
                # 检测并移除重复的 SQL 语句
                sql_upper = sql.upper()
                
                # 方法1: 检测整个 SQL 是否完全重复（整个字符串重复两次）
                sql_length = len(sql)
                if sql_length > 20:  # 只对较长的 SQL 进行检测
                    # 尝试找到重复点：查找第二个 SELECT/DESCRIBE/SHOW 的位置
                    for keyword in allowed_keywords:
                        # 查找第一个关键字的位置
                        first_pos = sql_upper.find(keyword)
                        if first_pos != -1:
                            # 查找第二个相同关键字的位置
                            second_pos = sql_upper.find(keyword, first_pos + len(keyword))
                            if second_pos != -1:
                                # 提取第一个 SQL 语句
                                first_sql = sql[:second_pos].strip()
                                second_sql = sql[second_pos:].strip()
                                
                                # 检查两个 SQL 是否相同（忽略大小写和空格）
                                first_sql_normalized = ' '.join(first_sql.upper().split())
                                second_sql_normalized = ' '.join(second_sql.upper().split())
                                
                                if first_sql_normalized == second_sql_normalized:
                                    # 完全重复，只保留第一个
                                    sql = first_sql
                                    break
                                else:
                                    # 检查第一个 SQL 是否完整
                                    # 对于 SELECT，必须包含 FROM
                                    # 对于 DESCRIBE/SHOW，检查长度
                                    is_complete = False
                                    if keyword == 'SELECT':
                                        is_complete = 'FROM' in first_sql.upper()
                                    elif keyword in ['DESCRIBE', 'DESC', 'SHOW']:
                                        # DESCRIBE/SHOW 语句通常较短
                                        is_complete = len(first_sql) > 5
                                    else:
                                        is_complete = len(first_sql) > 10
                                    
                                    if is_complete:
                                        sql = first_sql
                                        break
            else:
                # 如果没有找到允许的关键字，尝试直接使用
                sql = sql.strip()
            
            # 验证 SQL 是否是允许的查询类型
            sql_upper = sql.strip().upper()
            is_allowed = False
            for keyword in allowed_keywords:
                if sql_upper.startswith(keyword) or f' {keyword} ' in f' {sql_upper} ':
                    is_allowed = True
                    break
            
            if not is_allowed:
                # 尝试找到允许的关键字位置
                for keyword in allowed_keywords:
                    keyword_pos = sql_upper.find(keyword)
                    if keyword_pos != -1:
                        sql = sql[keyword_pos:].strip()
                        sql_upper = sql.strip().upper()
                        is_allowed = True
                        break
            
            # 如果仍然不是允许的查询，返回错误（但不阻止生成）
            # 因为执行阶段会进行安全检查
            if not is_allowed:
                # 允许生成，但会在执行时被拦截
                pass
            
            return {
                'success': True,
                'sql': sql.strip(),
                'question': question
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'sql': None
            }
    
    def _is_safe_sql(self, sql: str) -> Tuple[bool, str]:
        """检查 SQL 是否安全（只允许只读查询）"""
        sql_upper = sql.strip().upper()
        
        # 禁止的危险操作
        dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 
            'TRUNCATE', 'GRANT', 'REVOKE', 'FLUSH', 'KILL', 'LOCK',
            'UNLOCK', 'SET PASSWORD', 'SET GLOBAL', 'SET SESSION'
        ]
        
        # 检查是否包含危险关键字
        for keyword in dangerous_keywords:
            # 检查关键字是否在 SQL 中（作为独立单词）
            pattern = f'\\b{keyword}\\b'
            if re.search(pattern, sql_upper):
                return False, f'禁止执行危险操作：{keyword}'
        
        # 允许的只读查询关键字
        allowed_keywords = ['SELECT', 'DESCRIBE', 'DESC', 'SHOW', 'EXPLAIN']
        
        # 检查是否以允许的关键字开头
        is_allowed = False
        for keyword in allowed_keywords:
            if sql_upper.startswith(keyword) or f' {keyword} ' in f' {sql_upper} ':
                is_allowed = True
                break
        
        if not is_allowed:
            return False, '只允许执行只读查询（SELECT, DESCRIBE, SHOW, EXPLAIN）'
        
        return True, ''
    
    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """执行 SQL 查询（带安全检查）"""
        try:
            # 安全检查
            is_safe, error_msg = self._is_safe_sql(sql)
            if not is_safe:
                return {
                    'success': False,
                    'error': error_msg,
                    'data': None
                }
            
            # 执行 SQL
            result = self.db_manager.execute_sql(sql)
            
            return {
                'success': True,
                'data': result,
                'row_count': len(result)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def query(self, question: str) -> Dict[str, Any]:
        """执行自然语言查询（完整流程：生成+执行）"""
        try:
            result = self.agent.invoke({"input": question})
            return {
                'success': True,
                'answer': result.get('output', ''),
                'intermediate_steps': result.get('intermediate_steps', [])
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'answer': None
            }
    
    def get_schema_info(self) -> Dict[str, Any]:
        """获取数据库结构信息"""
        return {
            'tables': self.db_manager.get_table_names(),
            'schemas': self.db_manager.get_all_schemas()
        }
    
    def close(self):
        """关闭连接"""
        self.db_manager.close()

