#!/bin/bash

# 农业物联网可视化系统停止脚本
echo "🛑 停止农业物联网可视化系统..."

# 设置环境变量
export COMPOSE_PROJECT_NAME=iot_platform

# 停止并删除容器
docker-compose down

echo ""
echo "✅ 系统已停止"
echo ""
echo "🗑️  如需完全清理数据:"
echo "   docker-compose down -v  # 删除数据卷"
echo "   docker system prune     # 清理未使用的镜像"
echo ""