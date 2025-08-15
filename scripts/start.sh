#!/bin/bash

# 农业物联网可视化系统启动脚本
echo "🌱 启动农业物联网可视化系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis

# 设置环境变量
export COMPOSE_PROJECT_NAME=iot_platform

echo "🔧 准备启动服务..."

# 启动服务
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "🎉 系统启动完成！"
echo ""
echo "📱 访问地址:"
echo "  前端界面: http://localhost:8501"
echo "  后端API:  http://localhost:8080"
echo "  健康检查: http://localhost:8080/health"
echo ""
echo "🔑 演示账号:"
echo "  用户名: 18823870097"
echo "  密码:   yaohongming"
echo ""
echo "🛠️ 管理工具 (可选):"
echo "  数据库管理: http://localhost:5050"
echo "  Redis管理:  http://localhost:8081"
echo ""
echo "📖 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
echo ""