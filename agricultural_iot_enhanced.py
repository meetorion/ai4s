#!/usr/bin/env python3
"""
农业物联网可视化平台 - 增强版
集成真实的农业设备数据用于更好的演示效果
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
import os

# 页面配置
st.set_page_config(
    page_title="农业物联网平台",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 数据加载类
class DataLoader:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        # 地理位置配置 (国科大深圳先进技术研究院)
        self.base_location = {"lat": 22.59163, "lng": 113.972654}  # 深圳大学城
        self._load_all_data()
    
    def _load_all_data(self):
        """加载所有数据"""
        try:
            # 加载设备列表
            with open(f"{self.data_dir}/devices.json", "r", encoding="utf-8") as f:
                self.devices = json.load(f)
            
            # 加载当前数据
            with open(f"{self.data_dir}/current_data.json", "r", encoding="utf-8") as f:
                self.current_data = json.load(f)
            
            # 加载历史数据
            self.historical_data = pd.read_csv(f"{self.data_dir}/historical_data.csv")
            
            # 加载SIM卡数据
            with open(f"{self.data_dir}/sim_cards.json", "r", encoding="utf-8") as f:
                self.sim_cards = json.load(f)
            
            # 加载统计数据
            with open(f"{self.data_dir}/stats.json", "r", encoding="utf-8") as f:
                self.stats = json.load(f)
                
        except FileNotFoundError:
            # 当数据文件不存在时，创建基础数据
            self._create_fallback_data()
    
    def _create_fallback_data(self):
        """创建基础数据作为后备方案"""
        import random
        from datetime import datetime, timedelta
        
        # 13种设备类型
        device_types = {
            "气象站": {"icon": "🌤️", "count": 3},
            "土壤墒情": {"icon": "🌱", "count": 5},
            "水质监测": {"icon": "💧", "count": 1},
            "视频监控": {"icon": "📹", "count": 4},
            "配电柜": {"icon": "⚡", "count": 2},
            "虫情监测": {"icon": "🐛", "count": 3},
            "孢子仪": {"icon": "🦠", "count": 2},
            "环境监测": {"icon": "🌡️", "count": 4},
            "智能灌溉": {"icon": "💦", "count": 6},
            "杀虫灯": {"icon": "💡", "count": 4},
            "一体化闸门": {"icon": "🚪", "count": 2},
            "积水传感器": {"icon": "🌊", "count": 3},
            "植物生长记录仪": {"icon": "📊", "count": 3}
        }
        
        # 生成设备列表
        self.devices = []
        device_id = 1001
        
        for device_type, config in device_types.items():
            for i in range(config["count"]):
                if device_type == "水质监测":
                    dev_id = "865989071557605"
                else:
                    dev_id = f"{device_id:012d}"
                
                device = {
                    "device_id": dev_id,
                    "device_name": f"{config['icon']} {device_type}-{i+1:02d}",
                    "device_type": device_type,
                    "icon": config["icon"],
                    "location": {
                        "lat": self.base_location["lat"] + random.uniform(-0.01, 0.01),
                        "lng": self.base_location["lng"] + random.uniform(-0.01, 0.01)
                    },
                    "status": random.choice(["在线", "在线", "在线", "离线"]),
                    "install_date": "2024-01-15",
                    "last_update": datetime.now().isoformat(),
                    "parameters": {
                        "ph": {"range": [6.8, 7.2], "unit": "pH", "name": "pH值"},
                        "turbidity": {"range": [15, 25], "unit": "NTU", "name": "浊度"},
                        "dissolved_oxygen": {"range": [6.5, 8.5], "unit": "mg/L", "name": "溶解氧"},
                        "water_temp": {"range": [18, 25], "unit": "°C", "name": "水温"},
                        "conductivity": {"range": [180, 220], "unit": "μS/cm", "name": "电导率"}
                    }
                }
                self.devices.append(device)
                device_id += 1
        
        # 生成当前数据
        self.current_data = {}
        for device in self.devices:
            if device["status"] == "在线":
                data = {"timestamp": datetime.now().isoformat()}
                if device["device_type"] == "水质监测":
                    data.update({
                        "ph": round(random.uniform(6.8, 7.2), 2),
                        "turbidity": round(random.uniform(15, 25), 1),
                        "dissolved_oxygen": round(random.uniform(6.5, 8.5), 2),
                        "water_temp": round(random.uniform(18, 25), 1),
                        "conductivity": round(random.uniform(180, 220), 0)
                    })
                self.current_data[device["device_id"]] = data
        
        # 生成历史数据
        historical_records = []
        for i in range(24):  # 24小时数据
            timestamp = datetime.now() - timedelta(hours=i)
            for device in self.devices[:5]:  # 前5台设备
                if device["device_type"] == "水质监测":
                    record = {
                        "device_id": device["device_id"],
                        "device_type": device["device_type"],
                        "timestamp": timestamp.isoformat(),
                        "ph": round(random.uniform(6.8, 7.2), 2),
                        "turbidity": round(random.uniform(15, 25), 1),
                        "dissolved_oxygen": round(random.uniform(6.5, 8.5), 2),
                        "water_temp": round(random.uniform(18, 25), 1),
                        "conductivity": round(random.uniform(180, 220), 0)
                    }
                    historical_records.append(record)
        
        self.historical_data = pd.DataFrame(historical_records)
        
        # 生成SIM卡数据
        operators = ["中国移动", "中国联通", "中国电信"]
        self.sim_cards = []
        
        for i in range(25):
            total_data = random.randint(500, 2000)
            used_data = random.randint(50, int(total_data * 0.9))
            
            card = {
                "card_number": f"898600{random.randint(100000000, 999999999):09d}",
                "operator": random.choice(operators),
                "total_data": total_data,
                "used_data": used_data,
                "remaining_data": total_data - used_data,
                "usage_percent": round((used_data / total_data) * 100, 1),
                "expire_date": (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
                "status": random.choice(["正常", "正常", "正常", "即将到期", "欠费"]),
                "monthly_fee": random.choice([15, 20, 30, 50]),
                "device_binding": random.choice([None, f"设备{random.randint(1001, 1050):04d}"])
            }
            self.sim_cards.append(card)
        
        # 生成统计数据
        self.stats = {
            "total_devices": len(self.devices),
            "online_devices": len([d for d in self.devices if d["status"] == "在线"]),
            "device_types": len(device_types),
            "data_points": len(historical_records),
            "sim_cards": len(self.sim_cards),
            "last_update": datetime.now().isoformat()
        }
    
    def get_devices_by_type(self, device_type=None):
        """按类型获取设备"""
        if device_type:
            return [d for d in self.devices if d["device_type"] == device_type]
        return self.devices
    
    def get_device_by_id(self, device_id):
        """根据ID获取设备"""
        return next((d for d in self.devices if d["device_id"] == device_id), None)
    
    def get_real_time_data(self, device_id):
        """获取实时数据（加入随机波动）"""
        if device_id in self.current_data:
            data = self.current_data[device_id].copy()
            device = self.get_device_by_id(device_id)
            
            # 对数值型参数添加轻微波动
            for param, value in data.items():
                if param == "timestamp":
                    data[param] = datetime.now().isoformat()
                    continue
                    
                if isinstance(value, (int, float)) and param in device["parameters"]:
                    config = device["parameters"][param]
                    if "range" in config:
                        min_val, max_val = config["range"]
                        variation = (max_val - min_val) * 0.05  # 5%的波动
                        new_value = value + random.uniform(-variation, variation)
                        data[param] = round(max(min_val, min(max_val, new_value)), 2)
            
            return data
        return None
    
    def get_historical_data_by_device(self, device_id, hours=24):
        """获取指定设备的历史数据"""
        device_data = self.historical_data[self.historical_data["device_id"] == device_id]
        
        # 获取最近N小时的数据
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        device_data = device_data.copy()
        device_data["timestamp"] = pd.to_datetime(device_data["timestamp"])
        device_data = device_data[
            (device_data["timestamp"] >= start_time) & 
            (device_data["timestamp"] <= end_time)
        ].sort_values("timestamp")
        
        return device_data

# 初始化数据加载器
@st.cache_resource
def get_data_loader():
    return DataLoader()

data_loader = get_data_loader()

# 加载自定义CSS
def load_custom_css():
    st.markdown("""
    <style>
    :root {
        --primary-color: #0cbf75;
        --secondary-color: #059669;
        --background-color: #f8fafc;
        --card-background: #ffffff;
        --text-color: #1f2937;
        --border-color: #e5e7eb;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: none;
    }
    
    /* 顶部标题样式 */
    .page-title {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    /* 数据卡片样式 */
    .metric-card {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50px;
        right: -50px;
        width: 100px;
        height: 100px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* 设备状态指示器 */
    .status-online {
        color: var(--success-color);
        font-weight: bold;
    }
    
    .status-offline {
        color: var(--error-color);
        font-weight: bold;
    }
    
    /* 实时数据表格 */
    .realtime-table {
        background: var(--card-background);
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .realtime-table th {
        background: var(--primary-color);
        color: white;
        padding: 1rem;
        text-align: left;
    }
    
    .realtime-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    /* 设备卡片 */
    .device-card {
        background: var(--card-background);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .device-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .device-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .device-icon {
        font-size: 2rem;
        margin-right: 0.5rem;
    }
    
    .device-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: var(--text-color);
    }
    
    /* 仪表盘样式 */
    .gauge-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1rem 0;
    }
    
    /* 地图容器 */
    .map-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* 数据表格样式 */
    .data-table {
        font-size: 0.9rem;
    }
    
    .data-table th {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background-color: var(--background-color);
    }
    
    .css-1d391kg .css-1d391kg {
        background-color: var(--card-background);
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 选择框样式 */
    .stSelectbox > div > div {
        background-color: var(--card-background);
        border: 2px solid var(--border-color);
        border-radius: 8px;
    }
    
    /* 警告框样式 */
    .alert-warning {
        background-color: rgba(245, 158, 11, 0.1);
        border-left: 4px solid var(--warning-color);
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    .alert-success {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 4px solid var(--success-color);
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    .alert-error {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid var(--error-color);
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def render_main_dashboard():
    """渲染主页仪表板"""
    st.markdown('<h2>📊 数据总览</h2>', unsafe_allow_html=True)
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{data_loader.stats['total_devices']}</div>
            <div class="metric-label">设备总数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{data_loader.stats['online_devices']}</div>
            <div class="metric-label">在线设备</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        online_rate = round((data_loader.stats['online_devices'] / data_loader.stats['total_devices']) * 100, 1)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{online_rate}%</div>
            <div class="metric-label">在线率</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{data_loader.stats['device_types']}</div>
            <div class="metric-label">设备类型</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 主要内容区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💧 实时水质监测")
        
        # 获取水质监测设备
        water_devices = data_loader.get_devices_by_type("水质监测")
        if water_devices:
            device = water_devices[0]
            device_id = device["device_id"]
            
            # 获取实时数据
            current_data = data_loader.get_real_time_data(device_id)
            
            if current_data:
                # 创建仪表盘
                fig = make_subplots(
                    rows=2, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                           [{"type": "indicator"}, {"type": "indicator"}, {"type": "xy"}]],
                    subplot_titles=["pH值", "浊度", "溶解氧", "水温", "电导率", "实时趋势"]
                )
                
                # pH值仪表盘
                fig.add_trace(go.Indicator(
                    mode = "gauge+number",
                    value = current_data.get('ph', 7.0),
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "pH"},
                    gauge = {
                        'axis': {'range': [6.0, 8.0]},
                        'bar': {'color': "#0cbf75"},
                        'steps': [
                            {'range': [6.0, 6.5], 'color': "#fee2e2"},
                            {'range': [6.5, 7.5], 'color': "#dcfce7"},
                            {'range': [7.5, 8.0], 'color': "#fee2e2"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 7.5
                        }
                    }
                ), row=1, col=1)
                
                # 浊度仪表盘
                fig.add_trace(go.Indicator(
                    mode = "gauge+number",
                    value = current_data.get('turbidity', 20),
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "浊度 (NTU)"},
                    gauge = {
                        'axis': {'range': [0, 50]},
                        'bar': {'color': "#3b82f6"},
                        'steps': [
                            {'range': [0, 25], 'color': "#dcfce7"},
                            {'range': [25, 40], 'color': "#fef3c7"},
                            {'range': [40, 50], 'color': "#fee2e2"}
                        ]
                    }
                ), row=1, col=2)
                
                # 溶解氧仪表盘
                fig.add_trace(go.Indicator(
                    mode = "gauge+number",
                    value = current_data.get('dissolved_oxygen', 7.5),
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "溶解氧 (mg/L)"},
                    gauge = {
                        'axis': {'range': [0, 15]},
                        'bar': {'color': "#8b5cf6"},
                        'steps': [
                            {'range': [0, 5], 'color': "#fee2e2"},
                            {'range': [5, 10], 'color': "#dcfce7"},
                            {'range': [10, 15], 'color': "#fef3c7"}
                        ]
                    }
                ), row=1, col=3)
                
                # 水温仪表盘
                fig.add_trace(go.Indicator(
                    mode = "gauge+number",
                    value = current_data.get('water_temp', 22),
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "水温 (°C)"},
                    gauge = {
                        'axis': {'range': [0, 40]},
                        'bar': {'color': "#f59e0b"},
                        'steps': [
                            {'range': [0, 15], 'color': "#dbeafe"},
                            {'range': [15, 30], 'color': "#dcfce7"},
                            {'range': [30, 40], 'color': "#fee2e2"}
                        ]
                    }
                ), row=2, col=1)
                
                # 电导率仪表盘
                fig.add_trace(go.Indicator(
                    mode = "gauge+number",
                    value = current_data.get('conductivity', 200),
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "电导率 (μS/cm)"},
                    gauge = {
                        'axis': {'range': [0, 500]},
                        'bar': {'color': "#ef4444"},
                        'steps': [
                            {'range': [0, 100], 'color': "#fee2e2"},
                            {'range': [100, 300], 'color': "#dcfce7"},
                            {'range': [300, 500], 'color': "#fef3c7"}
                        ]
                    }
                ), row=2, col=2)
                
                # 24小时趋势图
                historical_data = data_loader.get_historical_data_by_device(device_id, 24)
                if not historical_data.empty:
                    fig.add_trace(go.Scatter(
                        x=historical_data['timestamp'],
                        y=historical_data['ph'],
                        mode='lines+markers',
                        name='pH值',
                        line=dict(color='#0cbf75', width=2),
                        marker=dict(size=4)
                    ), row=2, col=3)
                
                fig.update_layout(
                    height=600,
                    showlegend=False,
                    title_text="水质监测实时数据",
                    title_x=0.5
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 显示最新数据时间
                st.info(f"📊 数据更新时间: {current_data.get('timestamp', '未知')}")
                
                # 自动刷新
                if st.button("🔄 刷新数据", key="refresh_water"):
                    st.experimental_rerun()
    
    with col2:
        st.markdown("### 🏭 设备类型分布")
        
        # 统计各类型设备数量
        device_counts = {}
        for device in data_loader.devices:
            device_type = device["device_type"]
            if device_type in device_counts:
                device_counts[device_type] += 1
            else:
                device_counts[device_type] = 1
        
        # 创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=list(device_counts.keys()),
            values=list(device_counts.values()),
            hole=0.4,
            textinfo='label+percent',
            textposition='outside',
            marker=dict(
                colors=px.colors.qualitative.Set3,
                line=dict(color='white', width=2)
            )
        )])
        
        fig.update_layout(
            title="设备类型分布",
            title_x=0.5,
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 在线状态统计
        st.markdown("### 📈 设备状态统计")
        online_count = len([d for d in data_loader.devices if d["status"] == "在线"])
        offline_count = len([d for d in data_loader.devices if d["status"] == "离线"])
        
        status_fig = go.Figure(data=[go.Bar(
            x=['在线', '离线'],
            y=[online_count, offline_count],
            marker=dict(color=['#10b981', '#ef4444'])
        )])
        
        status_fig.update_layout(
            title="设备在线状态",
            title_x=0.5,
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(status_fig, use_container_width=True)

def render_device_maintenance():
    """渲染设备维护页面"""
    st.markdown('<h2>🔧 设备维护</h2>', unsafe_allow_html=True)
    
    # 筛选选项
    col1, col2, col3 = st.columns(3)
    
    with col1:
        device_types = ["全部"] + list(set([d["device_type"] for d in data_loader.devices]))
        selected_type = st.selectbox("设备类型", device_types)
    
    with col2:
        status_options = ["全部", "在线", "离线"]
        selected_status = st.selectbox("设备状态", status_options)
    
    with col3:
        search_term = st.text_input("设备名称搜索", placeholder="输入设备名称...")
    
    # 筛选设备
    filtered_devices = data_loader.devices.copy()
    
    if selected_type != "全部":
        filtered_devices = [d for d in filtered_devices if d["device_type"] == selected_type]
    
    if selected_status != "全部":
        filtered_devices = [d for d in filtered_devices if d["status"] == selected_status]
    
    if search_term:
        filtered_devices = [d for d in filtered_devices if search_term.lower() in d["device_name"].lower()]
    
    st.markdown(f"**找到 {len(filtered_devices)} 个设备**")
    
    # 设备卡片展示
    for i in range(0, len(filtered_devices), 3):
        cols = st.columns(3)
        for j, device in enumerate(filtered_devices[i:i+3]):
            with cols[j]:
                status_class = "status-online" if device["status"] == "在线" else "status-offline"
                status_icon = "🟢" if device["status"] == "在线" else "🔴"
                
                st.markdown(f"""
                <div class="device-card">
                    <div class="device-header">
                        <div>
                            <span class="device-icon">{device['icon']}</span>
                            <span class="device-name">{device['device_name']}</span>
                        </div>
                        <span class="{status_class}">{status_icon} {device['status']}</span>
                    </div>
                    <p><strong>设备ID:</strong> {device['device_id']}</p>
                    <p><strong>安装日期:</strong> {device['install_date']}</p>
                    <p><strong>最后更新:</strong> {device['last_update'][:19].replace('T', ' ')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 显示实时数据按钮
                if st.button(f"查看数据", key=f"view_{device['device_id']}"):
                    current_data = data_loader.get_real_time_data(device['device_id'])
                    if current_data:
                        with st.expander(f"{device['device_name']} 实时数据", expanded=True):
                            for param, value in current_data.items():
                                if param != "timestamp":
                                    param_config = device["parameters"].get(param, {})
                                    unit = param_config.get("unit", "")
                                    name = param_config.get("name", param)
                                    st.write(f"**{name}**: {value} {unit}")
                    else:
                        st.warning("该设备当前无数据")

def render_realtime_data():
    """渲染实时数据页面"""
    st.markdown('<h2>⚡ 实时数据监控</h2>', unsafe_allow_html=True)
    
    # 设备选择
    device_types = list(set([d["device_type"] for d in data_loader.devices]))
    selected_type = st.selectbox("选择设备类型", device_types)
    
    # 获取该类型的设备
    type_devices = data_loader.get_devices_by_type(selected_type)
    online_devices = [d for d in type_devices if d["status"] == "在线"]
    
    if not online_devices:
        st.warning(f"该类型设备都处于离线状态")
        return
    
    st.info(f"📊 {selected_type} - 共 {len(online_devices)} 台设备在线")
    
    # 实时数据展示
    for device in online_devices:
        with st.expander(f"{device['icon']} {device['device_name']}", expanded=True):
            current_data = data_loader.get_real_time_data(device['device_id'])
            
            if current_data:
                # 数据表格
                data_rows = []
                for param, value in current_data.items():
                    if param != "timestamp":
                        param_config = device["parameters"].get(param, {})
                        unit = param_config.get("unit", "")
                        name = param_config.get("name", param)
                        data_rows.append({"参数": name, "数值": f"{value} {unit}"})
                
                if data_rows:
                    df = pd.DataFrame(data_rows)
                    st.dataframe(df, use_container_width=True)
                
                # 历史趋势图
                historical_data = data_loader.get_historical_data_by_device(device['device_id'], 6)
                if not historical_data.empty:
                    st.markdown("**6小时趋势**")
                    
                    # 选择数值型参数绘图
                    numeric_params = []
                    for col in historical_data.columns:
                        if col not in ["device_id", "device_type", "timestamp"] and historical_data[col].dtype in ['float64', 'int64']:
                            numeric_params.append(col)
                    
                    if numeric_params:
                        fig = go.Figure()
                        
                        for param in numeric_params[:3]:  # 最多显示3个参数
                            param_config = device["parameters"].get(param, {})
                            name = param_config.get("name", param)
                            unit = param_config.get("unit", "")
                            
                            fig.add_trace(go.Scatter(
                                x=historical_data['timestamp'],
                                y=historical_data[param],
                                mode='lines+markers',
                                name=f"{name} ({unit})",
                                line=dict(width=2),
                                marker=dict(size=4)
                            ))
                        
                        fig.update_layout(
                            height=300,
                            xaxis_title="时间",
                            yaxis_title="数值",
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("暂无实时数据")
    
    # 自动刷新
    if st.button("🔄 刷新所有数据"):
        st.experimental_rerun()

def render_digital_park():
    """渲染数字园区页面"""
    st.markdown('<h2>🗺️ 数字园区</h2>', unsafe_allow_html=True)
    
    # 创建地图
    center_lat = data_loader.base_location["lat"]
    center_lng = data_loader.base_location["lng"]
    
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=16,  # 更高放大级别显示详细信息
        tiles='OpenStreetMap'
    )
    
    # 添加卫星图层
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='卫星地图',
        overlay=False,
        control=True
    ).add_to(m)
    
    # 添加设备标记
    device_colors = {
        "气象站": "blue",
        "土壤墒情": "green",
        "水质监测": "lightblue",
        "视频监控": "red",
        "配电柜": "orange",
        "虫情监测": "purple",
        "孢子仪": "pink",
        "环境监测": "gray",
        "智能灌溉": "lightgreen",
        "杀虫灯": "yellow",
        "一体化闸门": "darkblue",
        "积水传感器": "cadetblue",
        "植物生长记录仪": "darkgreen"
    }
    
    for device in data_loader.devices:
        lat = device["location"]["lat"]
        lng = device["location"]["lng"]
        color = device_colors.get(device["device_type"], "gray")
        
        # 获取实时数据
        current_data = data_loader.get_real_time_data(device["device_id"])
        popup_content = f"""
        <b>{device['icon']} {device['device_name']}</b><br>
        <b>设备ID:</b> {device['device_id']}<br>
        <b>状态:</b> {'🟢' if device['status'] == '在线' else '🔴'} {device['status']}<br>
        <b>安装日期:</b> {device['install_date']}<br>
        """
        
        if current_data:
            popup_content += "<br><b>实时数据:</b><br>"
            count = 0
            for param, value in current_data.items():
                if param != "timestamp" and count < 3:  # 只显示前3个参数
                    param_config = device["parameters"].get(param, {})
                    name = param_config.get("name", param)
                    unit = param_config.get("unit", "")
                    popup_content += f"{name}: {value} {unit}<br>"
                    count += 1
        
        folium.Marker(
            [lat, lng],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{device['icon']} {device['device_name']}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    
    # 添加研究院中心标记
    folium.Marker(
        [center_lat, center_lng],
        popup=folium.Popup("""
        <div style="width:200px;">
        <h4>🏛️ 国科大深圳先进技术研究院</h4>
        <p><b>地址:</b> 深圳市南山区西丽深圳大学城学苑大道1068号</p>
        <p><b>农业IoT示范园区</b></p>
        <p><b>设备总数:</b> 42台</p>
        </div>
        """, max_width=250),
        tooltip="国科大深圳先进技术研究院",
        icon=folium.Icon(color='red', icon='university', prefix='fa')
    ).add_to(m)
    
    # 添加研究院边界 (约1km半径)
    folium.Circle(
        location=[center_lat, center_lng],
        radius=1000,  # 1km半径，适合研究院规模
        popup="农业IoT示范园区",
        color='darkgreen',
        fillColor='lightgreen',
        fillOpacity=0.15,
        weight=2,
        dashArray='5, 5'
    ).add_to(m)
    
    # 添加图例
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px;">
    <h4>设备类型图例</h4>
    '''
    
    for device_type, color in device_colors.items():
        count = len([d for d in data_loader.devices if d["device_type"] == device_type])
        icon_map = {device["device_type"]: device["icon"] for device in data_loader.devices}
        icon = icon_map.get(device_type, "📍")
        legend_html += f'<p><span style="color:{color};">●</span> {icon} {device_type} ({count})</p>'
    
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # 添加图层控制器
    folium.LayerControl().add_to(m)
    
    # 显示地图
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    map_data = st_folium(m, width=700, height=500)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 设备统计
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 设备分布统计")
        device_stats = {}
        for device in data_loader.devices:
            device_type = device["device_type"]
            if device_type not in device_stats:
                device_stats[device_type] = {"total": 0, "online": 0}
            device_stats[device_type]["total"] += 1
            if device["status"] == "在线":
                device_stats[device_type]["online"] += 1
        
        for device_type, stats in device_stats.items():
            icon = next((d["icon"] for d in data_loader.devices if d["device_type"] == device_type), "📍")
            online_rate = (stats["online"] / stats["total"] * 100) if stats["total"] > 0 else 0
            st.write(f"{icon} **{device_type}**: {stats['online']}/{stats['total']} ({online_rate:.1f}%)")
    
    with col2:
        st.markdown("### 🎯 园区信息")
        st.write("**园区名称**: 国科大深圳先进技术研究院")
        st.write("**园区地址**: 深圳市南山区西丽深圳大学城学苑大道1068号")
        st.write("**示范区域**: 农业IoT技术验证园区")
        st.write("**覆盖范围**: 约3.14平方公里")
        st.write(f"**设备总数**: {len(data_loader.devices)}台")
        st.write(f"**在线设备**: {len([d for d in data_loader.devices if d['status'] == '在线'])}台")
        st.write("**管理单位**: 中科院深圳先进技术研究院")
        st.write("**坐标**: 22.59163°N, 113.972654°E")

def render_sim_card_management():
    """渲染流量卡查询页面"""
    st.markdown('<h2>📱 流量卡管理</h2>', unsafe_allow_html=True)
    
    # 筛选选项
    col1, col2, col3 = st.columns(3)
    
    with col1:
        operators = ["全部"] + list(set([card["operator"] for card in data_loader.sim_cards]))
        selected_operator = st.selectbox("运营商", operators)
    
    with col2:
        status_options = ["全部"] + list(set([card["status"] for card in data_loader.sim_cards]))
        selected_status = st.selectbox("卡状态", status_options)
    
    with col3:
        card_search = st.text_input("卡号搜索", placeholder="输入卡号...")
    
    # 筛选数据
    filtered_cards = data_loader.sim_cards.copy()
    
    if selected_operator != "全部":
        filtered_cards = [c for c in filtered_cards if c["operator"] == selected_operator]
    
    if selected_status != "全部":
        filtered_cards = [c for c in filtered_cards if c["status"] == selected_status]
    
    if card_search:
        filtered_cards = [c for c in filtered_cards if card_search in c["card_number"]]
    
    # 统计信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(filtered_cards)}</div>
            <div class="metric-label">SIM卡总数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        normal_cards = len([c for c in filtered_cards if c["status"] == "正常"])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{normal_cards}</div>
            <div class="metric-label">正常状态</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        warning_cards = len([c for c in filtered_cards if c["status"] == "即将到期"])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{warning_cards}</div>
            <div class="metric-label">即将到期</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_usage = sum([c["usage_percent"] for c in filtered_cards]) / len(filtered_cards) if filtered_cards else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_usage:.1f}%</div>
            <div class="metric-label">平均使用率</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SIM卡列表
    if filtered_cards:
        # 创建数据表
        card_data = []
        for card in filtered_cards:
            card_data.append({
                "卡号": card["card_number"],
                "运营商": card["operator"],
                "总流量(MB)": card["total_data"],
                "已用(MB)": card["used_data"],
                "剩余(MB)": card["remaining_data"],
                "使用率": f"{card['usage_percent']}%",
                "到期日期": card["expire_date"],
                "月费(元)": card["monthly_fee"],
                "状态": card["status"],
                "绑定设备": card["device_binding"] or "未绑定"
            })
        
        df = pd.DataFrame(card_data)
        
        # 状态颜色标记
        def highlight_status(val):
            if val == "正常":
                return 'background-color: #dcfce7'
            elif val == "即将到期":
                return 'background-color: #fef3c7'
            elif val == "欠费":
                return 'background-color: #fee2e2'
            return ''
        
        styled_df = df.style.map(highlight_status, subset=['状态'])
        st.dataframe(styled_df, use_container_width=True)
        
        # 流量使用分析
        st.markdown("### 📊 流量使用分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 运营商分布
            operator_counts = {}
            for card in filtered_cards:
                op = card["operator"]
                if op in operator_counts:
                    operator_counts[op] += 1
                else:
                    operator_counts[op] = 1
            
            fig_operator = go.Figure(data=[go.Pie(
                labels=list(operator_counts.keys()),
                values=list(operator_counts.values()),
                hole=0.4
            )])
            
            fig_operator.update_layout(
                title="运营商分布",
                title_x=0.5,
                height=300
            )
            
            st.plotly_chart(fig_operator, use_container_width=True)
        
        with col2:
            # 使用率分布
            usage_ranges = {"0-25%": 0, "25-50%": 0, "50-75%": 0, "75-100%": 0}
            
            for card in filtered_cards:
                usage = card["usage_percent"]
                if usage <= 25:
                    usage_ranges["0-25%"] += 1
                elif usage <= 50:
                    usage_ranges["25-50%"] += 1
                elif usage <= 75:
                    usage_ranges["50-75%"] += 1
                else:
                    usage_ranges["75-100%"] += 1
            
            fig_usage = go.Figure(data=[go.Bar(
                x=list(usage_ranges.keys()),
                y=list(usage_ranges.values()),
                marker=dict(color=['#10b981', '#f59e0b', '#ef4444', '#dc2626'])
            )])
            
            fig_usage.update_layout(
                title="流量使用率分布",
                title_x=0.5,
                height=300,
                xaxis_title="使用率范围",
                yaxis_title="卡数量"
            )
            
            st.plotly_chart(fig_usage, use_container_width=True)
    
    else:
        st.warning("没有找到符合条件的SIM卡")

def main():
    """主函数"""
    # 加载CSS
    load_custom_css()
    
    # 标题
    st.markdown('<h1 class="page-title">🌱 农业物联网平台</h1>', unsafe_allow_html=True)
    
    # 侧边栏导航
    st.sidebar.title("🌾 导航菜单")
    
    pages = {
        "📊 主页": render_main_dashboard,
        "🏭 设备维护": render_device_maintenance,
        "📈 实时数据": render_realtime_data,
        "🗺️ 数字园区": render_digital_park,
        "📱 流量卡查询": render_sim_card_management,
    }
    
    page = st.sidebar.selectbox("选择页面", list(pages.keys()))
    
    # 系统信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 系统状态")
    st.sidebar.success(f"🟢 系统正常运行")
    st.sidebar.info(f"📊 设备总数: {data_loader.stats['total_devices']}")
    st.sidebar.info(f"🔗 在线设备: {data_loader.stats['online_devices']}")
    st.sidebar.info(f"📱 SIM卡: {data_loader.stats['sim_cards']}")
    
    # 渲染选中页面
    pages[page]()
    
    # 页脚
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: gray; padding: 1rem;">'
        '🌱 农业物联网可视化平台 | 基于 Go Gin + Streamlit 构建'
        '</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()