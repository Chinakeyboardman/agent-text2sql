# Text2SQL 项目

本项目研究通过自然语言生成 SQL 并完成查询，提供了两种实现方案。

## 项目结构

### 📁 Data/
数据库结构和测试数据文件（SQL 格式）
- 包含保险业务相关的表结构：客户信息、保单信息、理赔信息、代理人信息等
- 用于演示和测试 Text2SQL 功能

### 📁 LangChain/
基于 **LangChain 框架**实现的 Text2SQL 方案
- **核心功能**：自然语言转 SQL、SQL 执行、结果展示
- **主要特性**：
  - 支持阿里云 DashScope API
  - SQL Copilot 交互式工具
  - LangChain SQL Agent
  - Web 界面（Streamlit）
- **快速开始**：`cd LangChain && python3 data_loader/init_db.py && streamlit run web_app.py`

### 📁 Vanna/
基于 **Vanna 框架**实现的 Text2SQL 方案
- **核心功能**：使用 Vanna 框架连接 MySQL，自动训练表结构，生成 SQL
- **主要特性**：
  - 使用 ChromaDB 向量存储
  - 支持 OpenAI 兼容接口
  - 简洁的代码结构
- **快速开始**：`cd Vanna && python3 vanna-aliyun.py`

## 技术栈

- **LangChain 方案**：LangChain + SQLAlchemy + Streamlit + DashScope API
- **Vanna 方案**：Vanna + ChromaDB + OpenAI API + MySQL

## 使用说明

1. **初始化数据库**：运行 `LangChain/data_loader/init_db.py` 导入测试数据
2. **配置环境**：复制 `LangChain/env.example` 为 `.env` 并配置数据库和 API Key
3. **选择方案**：根据需要选择 LangChain 或 Vanna 方案进行开发
