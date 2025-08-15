#!/usr/bin/env python3
"""
农业物联网可视化平台
基于原系统功能重构的Go Gin + Streamlit版本
专注农业物联网核心功能
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import time
import random
import json
import numpy as np

# 页面配置
st.set_page_config(
    page_title="农业物联网平台",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载自定义CSS
def load_custom_css():
    st.markdown("""
    <style>
    :root {
        --primary-color: #0cbf75;
        --secondary-color: #059669;
        --background-color: #f5f5f5;
        --card-background: #ffffff;
        --text-color: #333333;
        --border-color: #e0e0e0;
        --success-color: #0cbf75;
        --warning-color: #ff9f06;
        --error-color: #db5461;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: none;
    }
    
    /* 数据卡片样式 */
    .data-overview-card {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    
    .data-overview-card::before {
        content: '';
        position: absolute;
        top: -50px;
        right: -50px;
        width: 100px;
        height: 100px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
    }
    
    .data-overview-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .data-overview-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* 设备卡片样式 */
    .device-card {
        background: var(--card-background);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .device-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .device-status {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
    }
    
    .device-status.online {
        background-color: #d1fae5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }
    
    .device-status.offline {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    
    /* 实时数据标签样式 */
    .data-tag {
        display: inline-block;
        background: var(--primary-color);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-weight: 500;
        font-size: 0.9rem;
        box-shadow: 0 2px 4px rgba(12, 191, 117, 0.3);
    }
    
    .data-tag.warning {
        background: var(--warning-color);
        box-shadow: 0 2px 4px rgba(255, 159, 6, 0.3);
    }
    
    .data-tag.error {
        background: var(--error-color);
        box-shadow: 0 2px 4px rgba(219, 84, 97, 0.3);
    }
    
    /* 页面标题样式 */
    .page-title {
        text-align: center;
        color: var(--primary-color);
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .page-subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f0fdf4 0%, #ecfdf5 100%);
    }
    </style>
    """, unsafe_allow_html=True)

# 模拟数据生成函数
@st.cache_data
def get_device_types():
    """获取设备类型定义"""
    return {
        1: {"name": "气象站", "icon": "🌤️", "color": "#3B82F6", "unit": "multiple"},
        2: {"name": "土壤墒情", "icon": "🌱", "color": "#10B981", "unit": "%"},
        3: {"name": "水质监测", "icon": "💧", "color": "#06B6D4", "unit": "pH/TDS"},
        4: {"name": "视频监控", "icon": "📹", "color": "#8B5CF6", "unit": "status"},
        5: {"name": "配电柜", "icon": "⚡", "color": "#F59E0B", "unit": "V/A"},
        6: {"name": "虫情监测", "icon": "🐛", "color": "#EF4444", "unit": "count"},
        7: {"name": "孢子仪", "icon": "🦠", "color": "#84CC16", "unit": "count"},
        8: {"name": "环境监测", "icon": "🌡️", "color": "#6366F1", "unit": "°C/%"},
        9: {"name": "智能灌溉", "icon": "💦", "color": "#14B8A6", "unit": "L/min"},
        10: {"name": "杀虫灯", "icon": "💡", "color": "#F97316", "unit": "status"},
        11: {"name": "一体化闸门", "icon": "🚪", "color": "#64748B", "unit": "status"},
        12: {"name": "积水传感器", "icon": "🌊", "color": "#0EA5E9", "unit": "cm"},
        13: {"name": "植物生长记录仪", "icon": "📊", "color": "#22C55E", "unit": "mm"}
    }

def generate_device_stats():
    """生成设备统计数据（模拟原网站的数据总览）"""
    device_types = get_device_types()
    stats = []
    
    # 模拟原网站显示的数据（水质监测1台，其他为0）
    device_counts = {
        1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0, 
        8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0
    }
    
    for device_type, count in device_counts.items():
        type_info = device_types[device_type]
        stats.append({
            'type': device_type,
            'name': type_info['name'],
            'icon': type_info['icon'],
            'color': type_info['color'],
            'count': count,
            'online': 1 if device_type == 3 else 0,  # 只有水质监测在线
            'offline': count - (1 if device_type == 3 else 0)
        })
    
    return stats

def generate_realtime_data(device_id="865989071557605"):
    """生成实时数据（模拟水质3项数据）"""
    if device_id == "865989071557605":  # 水质监测设备
        return {
            "device_id": device_id,
            "device_name": "水质3项",
            "timestamp": datetime.now(),
            "data": {
                "pH值": round(6.8 + random.uniform(-0.5, 0.5), 2),
                "浊度": round(15 + random.uniform(-5, 5), 1),
                "溶解氧": round(8.2 + random.uniform(-1, 1), 2),
                "水温": round(22 + random.uniform(-2, 2), 1),
                "电导率": round(480 + random.uniform(-50, 50), 0)
            },
            "status": random.choice(["正常", "预警"]) if random.random() > 0.8 else "正常"
        }
    else:
        return None

def generate_history_data(device_id, hours=24):
    """生成历史数据"""
    data = []
    now = datetime.now()
    
    for i in range(hours * 6):  # 每10分钟一个数据点
        timestamp = now - timedelta(minutes=i*10)
        
        if device_id == "865989071557605":
            # 水质数据
            base_ph = 7.0
            base_turbidity = 15
            base_do = 8.5
            base_temp = 22
            
            # 添加时间相关的变化
            hour_factor = np.sin(timestamp.hour * np.pi / 12) * 0.3
            
            data.append({
                'datetime': timestamp.strftime('%H:%M'),
                'timestamp': timestamp,
                'pH值': round(base_ph + hour_factor + random.uniform(-0.3, 0.3), 2),
                '浊度': round(base_turbidity + random.uniform(-3, 3), 1),
                '溶解氧': round(base_do + hour_factor + random.uniform(-0.5, 0.5), 2),
                '水温': round(base_temp + hour_factor*2 + random.uniform(-1, 1), 1),
                '电导率': round(480 + random.uniform(-30, 30), 0)
            })
    
    return list(reversed(data))

def main():
    """主函数"""
    load_custom_css()
    
    # 页面标题
    st.markdown('<h1 class="page-title">🌱 农业物联网平台</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">现代化农业数据监控与管理系统</p>', unsafe_allow_html=True)
    
    # 侧边栏导航
    with st.sidebar:
        st.markdown("### 🧭 系统导航")
        page = st.radio(
            "选择功能模块",
            [
                "📊 主页",
                "🏭 设备维护", 
                "📈 实时数据",
                "📹 视频监控",
                "📋 数据展示",
                "📚 历史数据",
                "🗺️ 数字园区",
                "🤖 智能控制",
                "📱 流量卡查询"
            ],
            key="main_navigation"
        )
        
        st.markdown("---")
        st.markdown("### 📊 系统状态")
        
        # 系统状态指示器
        col1, col2 = st.columns(2)
        with col1:
            st.metric("在线设备", "1", delta="0")
        with col2:
            st.metric("总设备", "1", delta="0")
        
        st.markdown("### 💡 快速操作")
        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("⚙️ 系统设置", use_container_width=True):
            st.info("设置功能开发中...")

    # 主内容区域
    if page == "📊 主页":
        render_main_dashboard()
    elif page == "🏭 设备维护":
        render_device_maintenance()
    elif page == "📈 实时数据":
        render_realtime_data()
    elif page == "📹 视频监控":
        render_video_monitoring()
    elif page == "📋 数据展示":
        render_data_display()
    elif page == "📚 历史数据":
        render_historical_data()
    elif page == "🗺️ 数字园区":
        render_digital_park()
    elif page == "🤖 智能控制":
        render_smart_control()
    elif page == "📱 流量卡查询":
        render_sim_query()

def render_main_dashboard():
    """渲染主仪表板（对应原网站主页）"""
    st.header("📊 系统主页")
    
    # 数据总览（对应原网站的轮播卡片）
    st.subheader("📈 数据总览")
    
    # 使用列布局显示设备统计
    device_stats = generate_device_stats()
    
    # 分组显示设备类型（每行显示6个）
    for i in range(0, len(device_stats), 6):
        cols = st.columns(6)
        for j, col in enumerate(cols):
            if i + j < len(device_stats):
                stat = device_stats[i + j]
                with col:
                    st.markdown(f"""
                    <div class="data-overview-card" style="background: linear-gradient(135deg, {stat['color']}, {stat['color']}aa);">
                        <div style="font-size: 2rem;">{stat['icon']}</div>
                        <div class="data-overview-value">{stat['count']}</div>
                        <div class="data-overview-label">{stat['name']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 主要内容区域（分为左右两部分）
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.subheader("💧 实时数据")
        
        # 设备选择器
        device_options = ["865989071557605"]  # 只有一个设备
        selected_device = st.selectbox(
            "选择设备",
            device_options,
            format_func=lambda x: "水质3项" if x == "865989071557605" else x,
            key="main_device_select"
        )
        
        # 显示实时数据
        realtime_data = generate_realtime_data(selected_device)
        
        if realtime_data:
            st.success(f"✅ 设备在线 - 最后更新: {realtime_data['timestamp'].strftime('%H:%M:%S')}")
            
            # 显示数据标签
            data_html = ""
            for param, value in realtime_data['data'].items():
                status_class = ""
                if param == "pH值" and (value < 6.0 or value > 8.0):
                    status_class = "warning"
                elif param == "浊度" and value > 20:
                    status_class = "warning"
                
                data_html += f'<span class="data-tag {status_class}">{param}: {value}</span>'
            
            st.markdown(data_html, unsafe_allow_html=True)
        else:
            st.markdown('<div class="data-tag error">暂无数据</div>', unsafe_allow_html=True)
    
    with col_right:
        st.subheader("📹 视频监控")
        
        # 视频设备选择器
        video_devices = ["请选择"]
        selected_video = st.selectbox(
            "选择视频设备",
            video_devices,
            key="main_video_select"
        )
        
        # 视频播放区域（占位符）
        st.markdown("""
        <div style="
            width: 100%; 
            height: 240px; 
            background: #f5f5f5; 
            border: 2px dashed #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            color: #666;
            font-size: 1rem;
        ">
            📹 暂无视频设备
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 底部图表区域
    col_chart1, col_chart2 = st.columns([3, 2])
    
    with col_chart1:
        st.subheader("📊 历史数据趋势")
        
        # 生成历史数据图表
        history_data = generate_history_data("865989071557605", 12)  # 12小时数据
        
        if history_data:
            df = pd.DataFrame(history_data)
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("pH值变化", "浊度变化", "溶解氧变化", "水温变化"),
                vertical_spacing=0.15,
                horizontal_spacing=0.1
            )
            
            # pH值
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['pH值'], 
                         mode='lines+markers', name='pH值',
                         line=dict(color='#3B82F6')),
                row=1, col=1
            )
            
            # 浊度
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['浊度'], 
                         mode='lines+markers', name='浊度',
                         line=dict(color='#EF4444')),
                row=1, col=2
            )
            
            # 溶解氧
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['溶解氧'], 
                         mode='lines+markers', name='溶解氧',
                         line=dict(color='#10B981')),
                row=2, col=1
            )
            
            # 水温
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['水温'], 
                         mode='lines+markers', name='水温',
                         line=dict(color='#F59E0B')),
                row=2, col=2
            )
            
            fig.update_layout(height=400, showlegend=False, 
                            title_text="水质参数实时监控")
            fig.update_xaxes(tickangle=45)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无历史数据")
    
    with col_chart2:
        st.subheader("📊 设备统计")
        
        # 设备统计饼图
        active_stats = [stat for stat in device_stats if stat['count'] > 0]
        
        if active_stats:
            labels = [f"{stat['icon']} {stat['name']}" for stat in active_stats]
            values = [stat['count'] for stat in active_stats]
            colors = [stat['color'] for stat in active_stats]
            
            fig = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values,
                marker_colors=colors,
                textinfo='label+percent',
                textposition='auto',
            )])
            
            fig.update_layout(
                title="设备类型分布",
                height=400,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无设备统计数据")

def render_device_maintenance():
    """渲染设备维护页面"""
    st.header("🏭 设备维护")
    
    tab1, tab2 = st.tabs(["设备列表", "设备分享"])
    
    with tab1:
        st.subheader("设备列表")
        
        # 筛选器
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            device_types = get_device_types()
            type_filter = st.selectbox(
                "设备类型",
                ["请选择"] + [f"{info['icon']} {info['name']}" for info in device_types.values()]
            )
        
        with col2:
            name_filter = st.text_input("设备名称", placeholder="输入设备名称搜索")
        
        with col3:
            status_filter = st.selectbox("状态", ["全部", "在线", "离线"])
        
        with col4:
            if st.button("🔍 搜索", use_container_width=True):
                st.success("搜索完成")
        
        st.markdown("---")
        
        # 设备列表（模拟显示水质监测设备）
        st.markdown("""
        <div class="device-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4>💧 水质3项</h4>
                    <p><strong>设备ID:</strong> 865989071557605</p>
                    <p><strong>设备类型:</strong> 水质监测</p>
                    <p><strong>位置:</strong> 农场A区</p>
                </div>
                <div>
                    <span class="device-status offline">离线</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 查看数据", key="view_data"):
                st.success("正在跳转到数据页面...")
        with col2:
            if st.button("⚙️ 设备配置", key="device_config"):
                st.info("配置功能开发中...")
        with col3:
            if st.button("🔧 设备维护", key="device_maintenance"):
                st.info("维护功能开发中...")
    
    with tab2:
        st.subheader("设备分享")
        st.info("🚧 设备分享功能开发中，敬请期待！")

def render_realtime_data():
    """渲染实时数据页面"""
    st.header("📈 实时数据监控")
    
    # 设备类型筛选按钮组
    device_types = get_device_types()
    
    # 创建筛选按钮（模拟原网站的按钮组）
    st.markdown("### 设备类型筛选")
    
    button_cols = st.columns(7)
    with button_cols[0]:
        if st.button("全部", use_container_width=True):
            st.session_state.selected_type = "all"
    
    for i, (type_id, info) in enumerate(list(device_types.items())[:6]):
        with button_cols[i+1]:
            if st.button(f"{info['icon']} {info['name']}", use_container_width=True):
                st.session_state.selected_type = type_id
    
    st.markdown("---")
    
    # 主要内容区域
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("📱 设备列表")
        
        # 显示水质监测设备
        st.markdown("""
        <div class="device-card" style="background: #f8f9fa; border-left: 4px solid #0cbf75;">
            <div style="text-align: center;">
                <h4>💧 水质3项</h4>
                <p>865989071557605</p>
                <span class="device-status offline">离线</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("选择此设备", use_container_width=True):
            st.session_state.selected_device = "865989071557605"
    
    with col_right:
        st.subheader("📊 实时数据展示")
        
        # 检查是否选择了设备
        if hasattr(st.session_state, 'selected_device'):
            # 模拟实时数据更新
            placeholder = st.empty()
            
            # 启用自动刷新
            auto_refresh = st.checkbox("🔄 自动刷新 (每5秒)", value=False)
            
            if auto_refresh:
                # 实时数据流
                for i in range(10):
                    realtime_data = generate_realtime_data("865989071557605")
                    
                    with placeholder.container():
                        if realtime_data:
                            st.success(f"✅ 设备在线 - {realtime_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            # 显示关键指标
                            metric_cols = st.columns(3)
                            data_items = list(realtime_data['data'].items())
                            
                            for j, col in enumerate(metric_cols):
                                if j < len(data_items):
                                    param, value = data_items[j]
                                    with col:
                                        # 计算变化值（模拟）
                                        delta = round(random.uniform(-0.5, 0.5), 2)
                                        st.metric(param, value, delta)
                            
                            # 实时图表
                            if len(data_items) >= 3:
                                fig = go.Figure()
                                
                                # 生成模拟时间序列数据
                                times = [datetime.now() - timedelta(minutes=x) for x in range(30, 0, -1)]
                                
                                for param, current_value in data_items[:3]:
                                    # 生成历史数据点
                                    base_value = current_value if isinstance(current_value, (int, float)) else 7.0
                                    values = [base_value + random.uniform(-1, 1) for _ in times]
                                    values[-1] = current_value  # 最新值
                                    
                                    fig.add_trace(go.Scatter(
                                        x=times,
                                        y=values,
                                        mode='lines+markers',
                                        name=param,
                                        line=dict(width=2)
                                    ))
                                
                                fig.update_layout(
                                    title="实时数据趋势",
                                    xaxis_title="时间",
                                    yaxis_title="数值",
                                    height=300,
                                    hovermode='x unified'
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error("❌ 设备离线或无数据")
                    
                    time.sleep(5)
                    
            else:
                # 静态显示
                realtime_data = generate_realtime_data("865989071557605")
                if realtime_data:
                    st.info("💡 勾选自动刷新查看实时数据流")
                    
                    # 显示当前数据
                    data_html = ""
                    for param, value in realtime_data['data'].items():
                        data_html += f'<span class="data-tag">{param}: {value}</span>'
                    
                    st.markdown(data_html, unsafe_allow_html=True)
                else:
                    st.warning("暂无设备数据")
        else:
            st.info("👈 请先从左侧选择一个设备")

def render_video_monitoring():
    """渲染视频监控页面"""
    st.header("📹 视频监控")
    
    st.info("🚧 视频监控功能开发中")
    
    # 占位符内容
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📺 监控画面")
        st.markdown("""
        <div style="
            width: 100%; 
            height: 300px; 
            background: #f5f5f5; 
            border: 2px dashed #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            color: #666;
            font-size: 1.2rem;
        ">
            📹 暂无视频设备
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("⚙️ 监控设置")
        
        # 模拟视频设置选项
        video_quality = st.selectbox("视频质量", ["高清", "标清", "流畅"])
        record_enabled = st.checkbox("启用录制")
        alert_enabled = st.checkbox("运动检测告警")
        
        if st.button("保存设置"):
            st.success("设置已保存")

def render_data_display():
    """渲染数据展示页面"""
    st.header("📋 数据展示看板")
    
    # 综合数据展示
    realtime_data = generate_realtime_data("865989071557605")
    
    if realtime_data:
        st.success("🔗 数据连接正常")
        
        # 指标卡片展示
        st.subheader("📊 关键指标")
        
        metric_cols = st.columns(len(realtime_data['data']))
        for i, (param, value) in enumerate(realtime_data['data'].items()):
            with metric_cols[i]:
                # 设置指标颜色和状态
                color = "#0cbf75"  # 正常
                if param == "pH值" and (value < 6.0 or value > 8.0):
                    color = "#ff9f06"  # 警告
                elif param == "浊度" and value > 20:
                    color = "#db5461"  # 异常
                
                st.markdown(f"""
                <div class="data-overview-card" style="background: {color};">
                    <div class="data-overview-value">{value}</div>
                    <div class="data-overview-label">{param}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 数据分析图表
        st.subheader("📈 数据分析")
        
        tab1, tab2, tab3 = st.tabs(["实时监控", "趋势分析", "数据对比"])
        
        with tab1:
            # 实时仪表盘
            fig = make_subplots(
                rows=1, cols=3,
                specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                subplot_titles=["pH值", "溶解氧", "水温"]
            )
            
            # pH值仪表盘
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=realtime_data['data']['pH值'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "pH值"},
                delta={'reference': 7.0},
                gauge={
                    'axis': {'range': [None, 14]},
                    'bar': {'color': "#0cbf75"},
                    'steps': [
                        {'range': [0, 6], 'color': "#fee2e2"},
                        {'range': [6, 8], 'color': "#d1fae5"},
                        {'range': [8, 14], 'color': "#fee2e2"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 8.5
                    }
                }
            ), row=1, col=1)
            
            # 溶解氧
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=realtime_data['data']['溶解氧'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "溶解氧 (mg/L)"},
                gauge={
                    'axis': {'range': [None, 15]},
                    'bar': {'color': "#3B82F6"},
                    'steps': [
                        {'range': [0, 5], 'color': "#fee2e2"},
                        {'range': [5, 12], 'color': "#d1fae5"}
                    ]
                }
            ), row=1, col=2)
            
            # 水温
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=realtime_data['data']['水温'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "水温 (°C)"},
                gauge={
                    'axis': {'range': [0, 40]},
                    'bar': {'color': "#F59E0B"},
                    'steps': [
                        {'range': [0, 10], 'color': "#dbeafe"},
                        {'range': [10, 30], 'color': "#d1fae5"},
                        {'range': [30, 40], 'color': "#fee2e2"}
                    ]
                }
            ), row=1, col=3)
            
            fig.update_layout(height=400, title_text="实时水质监控仪表盘")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # 趋势分析
            history_data = generate_history_data("865989071557605", 24)
            df = pd.DataFrame(history_data)
            
            # 选择要分析的参数
            selected_params = st.multiselect(
                "选择分析参数",
                list(realtime_data['data'].keys()),
                default=list(realtime_data['data'].keys())[:3]
            )
            
            if selected_params:
                fig = go.Figure()
                
                for param in selected_params:
                    if param in df.columns:
                        fig.add_trace(go.Scatter(
                            x=df['timestamp'],
                            y=df[param],
                            mode='lines+markers',
                            name=param,
                            line=dict(width=2)
                        ))
                
                fig.update_layout(
                    title="24小时数据趋势分析",
                    xaxis_title="时间",
                    yaxis_title="数值",
                    height=400,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # 数据对比（今天vs昨天）
            st.subheader("数据对比分析")
            
            # 生成对比数据
            today_avg = {param: round(np.mean([row[param] for row in history_data[-144:]]), 2) 
                        for param in realtime_data['data'].keys() if param in df.columns}
            yesterday_avg = {param: round(today_avg[param] + random.uniform(-1, 1), 2) 
                            for param in today_avg.keys()}
            
            comparison_data = {
                '参数': list(today_avg.keys()),
                '今天平均': list(today_avg.values()),
                '昨天平均': list(yesterday_avg.values()),
                '变化': [round(today_avg[param] - yesterday_avg[param], 2) 
                        for param in today_avg.keys()]
            }
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)
    
    else:
        st.warning("暂无数据可显示")

def render_historical_data():
    """渲染历史数据页面"""
    st.header("📚 历史数据查询")
    
    # 查询条件
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input("开始日期", datetime.now() - timedelta(days=7))
    
    with col2:
        end_date = st.date_input("结束日期", datetime.now())
    
    with col3:
        data_type = st.selectbox("数据类型", ["水质监测", "气象数据", "土壤数据"])
    
    if st.button("🔍 查询历史数据"):
        st.success("查询成功！")
        
        # 生成历史数据
        days_diff = (end_date - start_date).days + 1
        history_data = generate_history_data("865989071557605", days_diff * 24)
        
        if history_data:
            df = pd.DataFrame(history_data)
            
            # 数据表格
            st.subheader("📋 数据记录")
            st.dataframe(df[['datetime', 'pH值', '浊度', '溶解氧', '水温']].head(20), 
                        use_container_width=True)
            
            # 数据图表
            st.subheader("📊 数据图表")
            
            selected_param = st.selectbox("选择参数", ['pH值', '浊度', '溶解氧', '水温'])
            
            fig = px.line(df, x='timestamp', y=selected_param, 
                         title=f'{selected_param} 历史趋势')
            st.plotly_chart(fig, use_container_width=True)
            
            # 数据统计
            st.subheader("📈 数据统计")
            stats_cols = st.columns(4)
            
            with stats_cols[0]:
                st.metric("平均值", f"{df[selected_param].mean():.2f}")
            with stats_cols[1]:
                st.metric("最大值", f"{df[selected_param].max():.2f}")
            with stats_cols[2]:
                st.metric("最小值", f"{df[selected_param].min():.2f}")
            with stats_cols[3]:
                st.metric("标准差", f"{df[selected_param].std():.2f}")
        
        # 数据导出
        if st.button("📥 导出数据"):
            st.success("数据导出功能开发中...")

def render_digital_park():
    """渲染数字园区页面（地图功能）"""
    st.header("🗺️ 数字园区")
    
    # 地图配置
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("🎛️ 地图控制")
        
        # 地图工具
        if st.button("📍 企业位置", use_container_width=True):
            st.info("企业位置标记功能")
        
        if st.button("📏 绘制线段", use_container_width=True):
            st.info("线段绘制功能")
        
        if st.button("🔲 圈定地块", use_container_width=True):
            st.info("地块圈定功能")
        
        st.markdown("---")
        st.subheader("🏭 设备标记")
        
        device_types = get_device_types()
        for type_id, info in device_types.items():
            if st.button(f"{info['icon']} {info['name']}", 
                        use_container_width=True, key=f"map_device_{type_id}"):
                st.info(f"标记{info['name']}功能")
    
    with col1:
        # 创建地图
        center_lat, center_lng = 39.9042, 116.4074  # 北京坐标
        
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # 添加设备位置标记（水质监测设备）
        device_lat = center_lat + 0.01
        device_lng = center_lng + 0.01
        
        folium.Marker(
            [device_lat, device_lng],
            popup="💧 水质监测设备\nID: 865989071557605\n状态: 离线",
            tooltip="水质3项",
            icon=folium.Icon(color='blue', icon='tint', prefix='fa')
        ).add_to(m)
        
        # 添加企业位置
        folium.Marker(
            [center_lat, center_lng],
            popup="🏢 农业物联网控制中心",
            tooltip="控制中心",
            icon=folium.Icon(color='green', icon='building', prefix='fa')
        ).add_to(m)
        
        # 添加地块示例
        folium.Rectangle(
            bounds=[[center_lat-0.005, center_lng-0.005], 
                   [center_lat+0.005, center_lng+0.005]],
            popup="农场A区",
            tooltip="农场A区 - 主要种植区域",
            color='green',
            fill=True,
            fillOpacity=0.2
        ).add_to(m)
        
        # 显示地图
        map_data = st_folium(m, width=700, height=500)
        
        # 显示地图信息
        if map_data['last_object_clicked_popup']:
            st.success(f"已选择: {map_data['last_object_clicked_popup']}")

def render_smart_control():
    """渲染智能控制页面"""
    st.header("🤖 智能控制")
    
    st.info("🚧 智能控制功能开发中")
    
    # 占位符功能
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ 设备控制")
        
        # 模拟控制界面
        irrigation_enabled = st.checkbox("🌊 自动灌溉", value=False)
        lighting_enabled = st.checkbox("💡 智能照明", value=False)
        ventilation_level = st.slider("🌀 通风等级", 0, 10, 5)
        
        if st.button("应用设置", use_container_width=True):
            st.success("控制指令已发送")
    
    with col2:
        st.subheader("📊 控制日志")
        
        # 模拟控制日志
        control_logs = [
            {"时间": "2024-08-14 16:30", "操作": "开启灌溉", "状态": "成功"},
            {"时间": "2024-08-14 15:45", "操作": "调整通风", "状态": "成功"},
            {"时间": "2024-08-14 14:20", "操作": "关闭照明", "状态": "成功"},
        ]
        
        st.dataframe(pd.DataFrame(control_logs), use_container_width=True)

def render_sim_query():
    """渲染流量卡查询页面"""
    st.header("📱 流量卡查询")
    
    # 模拟流量卡信息
    sim_data = [
        {
            "卡号": "898602B2091900000001",
            "设备": "水质监测设备",
            "运营商": "中国移动",
            "套餐": "10GB/月",
            "已用流量": "6.8GB",
            "剩余流量": "3.2GB",
            "到期日期": "2024-09-14",
            "状态": "正常"
        }
    ]
    
    # 查询条件
    col1, col2, col3 = st.columns(3)
    
    with col1:
        card_number = st.text_input("流量卡号", placeholder="输入完整卡号")
    
    with col2:
        operator = st.selectbox("运营商", ["全部", "中国移动", "中国联通", "中国电信"])
    
    with col3:
        if st.button("🔍 查询", use_container_width=True):
            st.success("查询成功！")
    
    # 显示流量卡信息
    st.subheader("📋 流量卡信息")
    
    for sim in sim_data:
        with st.expander(f"📱 {sim['卡号']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**设备:** {sim['设备']}")
                st.write(f"**运营商:** {sim['运营商']}")
                st.write(f"**套餐:** {sim['套餐']}")
            
            with col2:
                st.write(f"**已用流量:** {sim['已用流量']}")
                st.write(f"**剩余流量:** {sim['剩余流量']}")
                st.write(f"**状态:** {sim['状态']}")
            
            with col3:
                st.write(f"**到期日期:** {sim['到期日期']}")
                
                # 流量使用进度条
                used = 6.8
                total = 10
                progress = used / total
                st.progress(progress, text=f"流量使用: {progress:.1%}")
                
                # 预警提醒
                if progress > 0.8:
                    st.warning("⚠️ 流量使用即将超限")
    
    # 统计信息
    st.subheader("📊 流量统计")
    
    stats_cols = st.columns(4)
    
    with stats_cols[0]:
        st.metric("总卡数", "1")
    
    with stats_cols[1]:
        st.metric("正常卡数", "1")
    
    with stats_cols[2]:
        st.metric("即将到期", "0")
    
    with stats_cols[3]:
        st.metric("流量预警", "1")

if __name__ == "__main__":
    main()