#!/bin/bash

echo "🌱 农业物联网可视化平台 - 增强版启动中..."
echo "=================================================="

# 检查是否存在数据文件
if [ ! -d "data" ] || [ ! -f "data/devices.json" ]; then
    echo "📊 未找到演示数据，正在生成..."
    python data_generator.py
    if [ $? -eq 0 ]; then
        echo "✅ 演示数据生成完成"
    else
        echo "❌ 数据生成失败"
        exit 1
    fi
else
    echo "✅ 演示数据已存在"
fi

# 检查Python和依赖
echo "📋 检查依赖..."
python -c "import streamlit, plotly, pandas, folium, numpy" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 所有依赖已安装"
else
    echo "❌ 缺少依赖，正在安装..."
    pip install streamlit plotly pandas folium streamlit-folium numpy
fi

# 启动增强版服务
echo "🚀 启动增强版农业物联网平台..."
echo ""
echo "🌐 访问地址: http://localhost:8503"
echo "📱 移动端: http://0.0.0.0:8503"
echo ""
echo "🎯 增强版特性:"
echo "  📊 42台真实设备数据 (13种类型)"
echo "  💧 水质监测实时仪表盘"
echo "  📈 6700+历史数据点"
echo "  🗺️ 地理信息系统 (GIS地图)"
echo "  📱 25张SIM卡管理"
echo "  🎨 优美的UI界面和动画"
echo ""
echo "🆕 新增功能:"
echo "  ✨ 真实设备数据生成器"
echo "  📊 交互式仪表盘"
echo "  🌍 设备地理分布"
echo "  📈 历史趋势分析"
echo "  💰 流量卡费用管理"
echo ""
echo "🛑 按 Ctrl+C 停止服务"
echo "=================================================="

# 启动Streamlit增强版
streamlit run agricultural_iot_enhanced.py --server.address 0.0.0.0 --server.port 8503