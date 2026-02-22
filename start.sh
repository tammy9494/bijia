#!/bin/bash

# 汽车租赁比价网站启动脚本

echo "🚗 启动汽车租赁比价网站..."

# 检查 Python 虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 安装后端依赖..."
    pip install -r requirements.txt
    echo "🌐 安装 Playwright 浏览器..."
    playwright install chromium
fi

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "📥 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 启动后端（后台运行）
echo "🚀 启动后端服务..."
PYTHONPATH=/Users/luohongwenye/bijia python backend/run.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "🚀 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 服务已启动！"
echo "📊 后端 API: http://localhost:8000"
echo "📖 API 文档: http://localhost:8000/docs"
echo "🌐 前端界面: http://localhost:3000"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
