#!/bin/bash

# 后端启动脚本

echo "=========================================="
echo "时空胶囊后端服务启动"
echo "=========================================="

# 检查Python版本
echo "检查Python环境..."
python3 --version

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "提示: 建议使用虚拟环境"
    echo "创建虚拟环境: python3 -m venv venv"
    echo "激活虚拟环境: source venv/bin/activate"
fi

# 检查依赖是否安装
echo ""
echo "检查依赖..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
else
    echo "✓ 依赖已安装"
fi

# 检查MySQL连接
echo ""
echo "检查MySQL连接..."
python3 -c "
import os
import pymysql
try:
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password=os.environ["MYSQL_PASSWORD"])
    conn.close()
    print('✓ MySQL连接正常')
except Exception as e:
    print('✗ MySQL连接失败:', e)
    print('请确保MySQL服务已启动')
    exit(1)
"

# 启动服务
echo ""
echo "启动后端服务..."
echo "服务地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

python3 main.py

