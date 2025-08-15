#!/bin/bash

echo "🌱 农业物联网可视化平台启动中..."
echo "=================================================="

# 检查Python和依赖
echo "📋 检查依赖..."
python -c "import streamlit, plotly, pandas, folium" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 所有依赖已安装"
else
    echo "❌ 缺少依赖，正在安装..."
    pip install streamlit plotly pandas folium streamlit-folium numpy
fi

# 启动服务
echo "🚀 启动服务..."
echo ""
echo "🌐 访问地址: http://localhost:8502"
echo "📱 移动端: http://0.0.0.0:8502"
echo ""
echo "🔑 系统功能:"
echo "  📊 主页 - 数据总览和实时监控"
echo "  🏭 设备维护 - 设备列表和状态管理" 
echo "  📈 实时数据 - 实时数据流监控"
echo "  📹 视频监控 - 视频设备管理"
echo "  📋 数据展示 - 综合数据看板"
echo "  📚 历史数据 - 历史数据查询分析"
echo "  🗺️ 数字园区 - GIS地图和设备分布"
echo "  🤖 智能控制 - 设备智能控制"
echo "  📱 流量卡查询 - 物联网卡管理"
echo ""
echo "🛑 按 Ctrl+C 停止服务"
echo "=================================================="

# 启动Streamlit
streamlit run agricultural_iot_demo.py --server.address 0.0.0.0 --server.port 8502