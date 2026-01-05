# Vanna 连接阿里云 MySQL

基于 Vanna 框架，使用阿里云 DashScope API 连接 MySQL 数据库。

## 安装依赖

```bash
pip3 install -r requirements.txt
# 或
pip3 install 'vanna[openai,chromadb,mysql]' python-dotenv mysql-connector-python
```

## 配置

在 `LangChain/.env` 文件中配置：

```env
# 请从阿里云控制台获取：https://dashscope.console.aliyun.com/apiKey
DASHSCOPE_API_KEY=sk-your-dashscope-api-key-here
MODEL_NAME=qwen-turbo
DB_HOST=0.0.0.0
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=life_insurance
```

## 运行

```bash
python3 vanna-aliyun.py
```

## 功能

- 连接阿里云 MySQL 数据库
- 自动训练数据库表结构
- 使用阿里云 DashScope API 生成 SQL
