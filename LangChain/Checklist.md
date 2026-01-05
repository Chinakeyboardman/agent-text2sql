# Text2SQL 项目开发清单

## 📋 项目目标

1. **项目根目录**：本文件位置作为根目录，设计项目目录结构，主要是用 LangChain 实现自助式数据报表开发（Text2SQL）
2. **LLM 模型选型**：优先选用阿里云的模型，本地部署优先，可切换阿里云 API
3. **易于维护的 FunctionCall**：设计可扩展的工具函数系统
4. **搭建 SQL Copilot**：实现交互式 SQL 辅助工具
5. **完善 LangChain SQL Agent**：增强 Agent 功能和智能性
6. **数据准备**：使用上级目录 Data 目录中的 SQL 文件（表结构和测试数据）来展示成果

---

## 📊 进度概览

- **总任务数**：78
- **已完成**：58
- **进行中**：0
- **待开始**：20
- **完成率**：74%

---

## 🚀 阶段一：项目基础搭建

### 1.1 项目目录结构设计
- [x] 创建项目根目录结构（LangChain/）
- [x] 创建配置文件目录（config/）
- [x] 创建核心代码目录（core/）
- [x] 创建工具函数目录（utils/）
- [x] 创建数据加载目录（data_loader/）
- [x] 创建测试目录（tests/）
- [x] 创建示例目录（examples/）
- [x] 创建 requirements.txt
- [x] 创建 README.md（项目说明）
- [x] 创建 .gitignore

### 1.2 依赖环境配置
- [x] 安装 langchain 核心库（已添加到 requirements.txt）
- [x] 安装 langchain-community（社区工具）（已添加到 requirements.txt）
- [x] 安装数据库连接库（pymysql/sqlalchemy）（已添加到 requirements.txt）
- [x] 安装阿里云 SDK（dashscope）（已添加到 requirements.txt）
- [x] 安装其他必要依赖（python-dotenv, pydantic 等）（已添加到 requirements.txt）
- [ ] 配置虚拟环境（需手动执行）

---

## 💾 阶段二：数据层准备

### 2.1 SQL 文件解析
- [x] 创建 SQL 文件解析器（解析 Data 目录下的 .sql 文件）
- [x] 提取表结构信息（CREATE TABLE）
- [x] 提取表数据信息（INSERT INTO）
- [x] 支持多表结构解析
- [x] 生成表结构元数据（表名、字段名、字段类型）

### 2.2 数据库连接与初始化
- [x] 设计数据库连接配置（支持 MySQL）
- [x] 实现数据库连接池
- [x] 实现表结构加载功能
- [x] 实现测试数据导入功能（自动导入 SQL 文件，支持跳过已存在表）
- [x] 创建数据库初始化脚本

### 2.3 数据源管理
- [ ] 实现多数据源支持
- [x] 实现数据源配置管理
- [ ] 实现表结构缓存机制

---

## 🤖 阶段三：LLM 模型集成

### 3.1 阿里云模型配置
- [x] 研究阿里云 DashScope API 文档（已集成 Tongyi）
- [x] 实现本地模型部署配置（如通义千问本地版）（接口已预留）
- [x] 实现 API 调用封装
- [x] 实现模型切换机制（本地/API）
- [x] 实现 API Key 配置管理（.env）
- [x] 创建 env.example 配置文件示例
- [x] 创建配置验证和提示功能

### 3.2 模型适配层
- [x] 创建统一的 LLM 接口
- [x] 实现阿里云模型适配器
- [x] 实现本地模型适配器（接口已实现，可扩展）
- [x] 实现模型参数配置（temperature, max_tokens 等）
- [x] 实现错误处理和重试机制

---

## 🔧 阶段四：FunctionCall 实现

### 4.1 FunctionCall 设计
- [x] 设计 FunctionCall 架构（易于维护）
- [x] 定义 SQL 相关工具函数接口
- [x] 实现函数注册机制
- [x] 实现函数调用路由

### 4.2 SQL 工具函数
- [x] 实现 `get_table_schema`（获取表结构）
- [x] 实现 `list_tables`（列出所有表）
- [x] 实现 `execute_sql`（执行 SQL 查询）
- [x] 实现 `validate_sql`（SQL 语法验证）
- [x] 实现 `explain_sql`（SQL 执行计划）

### 4.3 FunctionCall 管理
- [x] 实现函数描述自动生成
- [ ] 实现函数版本管理
- [ ] 实现函数文档生成
- [ ] 实现函数测试用例

---

## 💡 阶段五：SQL Copilot 搭建

### 5.1 SQL Copilot 核心功能
- [x] 实现自然语言到 SQL 的转换
- [x] 优化 SQL 生成准确性（添加示例数据、Few-shot 示例、改进提示词）
- [ ] 实现 SQL 自动补全
- [x] 实现 SQL 语法检查
- [ ] 实现 SQL 优化建议
- [x] 实现查询结果格式化

### 5.2 交互式界面
- [x] 设计命令行交互界面（CLI）
- [x] 实现对话式查询（支持多轮对话）
- [x] 实现查询历史记录
- [x] 实现查询结果导出（CSV/JSON）

### 5.3 智能提示
- [x] 实现表名自动提示
- [x] 实现字段名自动提示
- [ ] 实现 SQL 关键词提示
- [x] 实现错误提示和修复建议

---

## 🎯 阶段六：LangChain SQL Agent 完善

### 6.1 Agent 基础架构
- [x] 集成 LangChain SQL Agent
- [x] 配置 SQLDatabase 工具
- [x] 配置 SQLDatabaseChain（使用 create_sql_agent）
- [x] 实现 Agent 执行器

### 6.2 Agent 功能增强
- [x] 实现多步骤查询规划（Agent 自动处理）
- [x] 实现查询结果验证（Agent 自动处理）
- [x] 实现错误自动修复（handle_parsing_errors）
- [ ] 实现查询优化建议
- [x] 实现复杂查询分解（Agent 自动处理）

### 6.3 Agent 提示词优化
- [ ] 设计系统提示词（System Prompt）
- [ ] 优化 Few-shot 示例
- [ ] 实现动态提示词生成
- [ ] 实现提示词模板管理

---

## ✅ 阶段七：测试与验证

### 7.1 单元测试
- [x] 测试 SQL 文件解析（已创建测试文件）
- [ ] 测试数据库连接（需数据库环境）
- [ ] 测试 LLM 模型调用（需 API Key）
- [ ] 测试 FunctionCall（需数据库环境）
- [ ] 测试 SQL Copilot 功能（需完整环境）
- [ ] 测试 SQL Agent（需完整环境）

### 7.2 集成测试
- [ ] 测试端到端流程（自然语言 -> SQL -> 结果）
- [ ] 测试多表关联查询
- [ ] 测试复杂查询场景
- [ ] 测试错误处理机制

### 7.3 数据验证
- [ ] 使用 Data 目录中的 SQL 文件进行测试
- [ ] 验证各表的查询准确性
- [ ] 验证复杂业务场景查询
- [ ] 性能测试和优化

---

## 📚 阶段八：文档与部署

### 8.1 项目文档
- [x] 编写项目 README
- [ ] 编写 API 文档
- [x] 编写使用示例
- [x] 编写配置说明（.env.example）

### 8.2 部署准备
- [x] 创建启动脚本（copilot_cli.py）
- [ ] 创建 Docker 配置（可选）
- [ ] 创建部署文档
- [ ] 创建故障排查指南

---

## 📝 开发注意事项

- ✅ 优先完成核心功能，再完善细节
- ✅ 每个阶段完成后进行测试验证
- ✅ 保持代码可维护性和可扩展性
- ✅ 遵循 Python 编码规范（PEP 8）
- ✅ 添加必要的注释和文档字符串

---

## 🔗 相关资源

- **数据文件**：`../Data/` 目录包含以下 SQL 文件：
  - agentinfo.sql
  - beneficiaryinfo.sql
  - claiminfo.sql
  - crs_orders.sql
  - customerinfo.sql
  - employeeinfo.sql
  - heros.sql
  - policyinfo.sql
  - productinfo.sql

---

**最后更新**：2025-01-XX
**当前状态**：核心功能已完成，待测试验证
