#!/bin/bash
# 启动 Text2SQL Web 应用

echo "=========================================="
echo "🚀 启动 Text2SQL Web 应用"
echo "=========================================="
echo ""

# 切换到项目目录
cd "$(dirname "$0")"

# 检查是否安装了 streamlit
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit 未安装，正在安装..."
    pip3 install --user streamlit
fi

# 启动应用
echo "📱 正在启动 Web 应用..."
echo "💡 浏览器将自动打开 http://localhost:8501"
echo ""

# 使用 python3 -m streamlit 来运行，避免 PATH 问题
python3 -m streamlit run web_app.py

