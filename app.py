#!/usr/bin/env python3
"""
农业物联网可视化平台 - Streamlit Cloud部署版
简化版本，专门为云部署优化
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import random
import numpy as np

# 页面配置
st.set_page_config(
    page_title="农业物联网平台",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 简化数据加载器
class SimpleDataLoader:
    def __init__(self):
        self.load_or_generate_data()
    
    def load_or_generate_data(self):
        """加载或生成简化数据"""
        # 13种设备类型
        self.device_types = {
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
        
        for device_type, config in self.device_types.items():
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
                    "status": random.choice(["在线", "在线", "在线", "离线"]),
                    "install_date": "2024-01-15",
                    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.devices.append(device)
                device_id += 1
        
        # 统计数据
        self.stats = {
            "total_devices": len(self.devices),
            "online_devices": len([d for d in self.devices if d["status"] == "在线"]),
            "device_types": len(self.device_types)
        }
        
        # 水质监测数据
        self.water_quality_data = {
            "ph": round(random.uniform(6.8, 7.2), 2),
            "turbidity": round(random.uniform(15, 25), 1),
            "dissolved_oxygen": round(random.uniform(6.5, 8.5), 2),
            "water_temp": round(random.uniform(18, 25), 1),
            "conductivity": round(random.uniform(180, 220), 0)
        }
    
    def get_devices_by_type(self, device_type=None):
        if device_type:
            return [d for d in self.devices if d["device_type"] == device_type]
        return self.devices
    
    def get_water_quality_data(self):
        # 添加轻微波动
        data = self.water_quality_data.copy()
        for key, value in data.items():
            variation = value * 0.05  # 5%波动
            data[key] = round(value + random.uniform(-variation, variation), 2)
        return data

# 初始化数据
@st.cache_resource
def get_data_loader():
    return SimpleDataLoader()

data_loader = get_data_loader()

# CSS样式
def load_custom_css():
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        max-width: none;
    }
    
    .page-title {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #0cbf75, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #0cbf75, #059669);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
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
    
    .device-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    .status-online {
        color: #10b981;
        font-weight: bold;
    }
    
    .status-offline {
        color: #ef4444;
        font-weight: bold;
    }
    
    .water-quality-param {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #0cbf75;
    }
    </style>
    """, unsafe_allow_html=True)

def render_main_dashboard():
    """主页仪表板"""
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
    
    # 水质监测数据
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💧 实时水质监测")
        st.markdown("**设备ID**: 865989071557605")
        
        water_data = data_loader.get_water_quality_data()
        
        # 使用简单的参数展示
        st.markdown(f"""
        <div class="water-quality-param">
            <strong>pH值</strong>: {water_data['ph']} pH
            <small style="color: {'green' if 6.5 <= water_data['ph'] <= 7.5 else 'red'};">
                {'✅ 正常' if 6.5 <= water_data['ph'] <= 7.5 else '⚠️ 异常'}
            </small>
        </div>
        <div class="water-quality-param">
            <strong>浊度</strong>: {water_data['turbidity']} NTU
            <small style="color: {'green' if water_data['turbidity'] <= 25 else 'red'};">
                {'✅ 正常' if water_data['turbidity'] <= 25 else '⚠️ 偏高'}
            </small>
        </div>
        <div class="water-quality-param">
            <strong>溶解氧</strong>: {water_data['dissolved_oxygen']} mg/L
            <small style="color: {'green' if water_data['dissolved_oxygen'] >= 6 else 'red'};">
                {'✅ 正常' if water_data['dissolved_oxygen'] >= 6 else '⚠️ 偏低'}
            </small>
        </div>
        <div class="water-quality-param">
            <strong>水温</strong>: {water_data['water_temp']} °C
            <small style="color: green;">✅ 正常</small>
        </div>
        <div class="water-quality-param">
            <strong>电导率</strong>: {water_data['conductivity']} μS/cm
            <small style="color: green;">✅ 正常</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 刷新数据"):
            st.rerun()
    
    with col2:
        st.markdown("### 🏭 设备分布")
        
        # 设备类型统计
        device_counts = {}
        for device in data_loader.devices:
            device_type = device["device_type"]
            device_counts[device_type] = device_counts.get(device_type, 0) + 1
        
        # 显示前8个设备类型
        for i, (device_type, count) in enumerate(list(device_counts.items())[:8]):
            icon = data_loader.device_types[device_type]["icon"]
            st.write(f"{icon} **{device_type}**: {count}台")
        
        if len(device_counts) > 8:
            st.write(f"... 还有 {len(device_counts) - 8} 种设备类型")

def render_device_maintenance():
    """设备维护页面"""
    st.markdown('<h2>🔧 设备维护</h2>', unsafe_allow_html=True)
    
    # 筛选选项
    col1, col2 = st.columns(2)
    
    with col1:
        device_types = ["全部"] + list(data_loader.device_types.keys())
        selected_type = st.selectbox("设备类型", device_types)
    
    with col2:
        status_options = ["全部", "在线", "离线"]
        selected_status = st.selectbox("设备状态", status_options)
    
    # 筛选设备
    filtered_devices = data_loader.devices.copy()
    
    if selected_type != "全部":
        filtered_devices = [d for d in filtered_devices if d["device_type"] == selected_type]
    
    if selected_status != "全部":
        filtered_devices = [d for d in filtered_devices if d["status"] == selected_status]
    
    st.markdown(f"**找到 {len(filtered_devices)} 个设备**")
    
    # 设备展示
    for device in filtered_devices:
        status_class = "status-online" if device["status"] == "在线" else "status-offline"
        status_icon = "🟢" if device["status"] == "在线" else "🔴"
        
        with st.expander(f"{device['icon']} {device['device_name']}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**设备ID**: {device['device_id']}")
                st.write(f"**设备类型**: {device['device_type']}")
                st.write(f"**安装日期**: {device['install_date']}")
            
            with col2:
                st.markdown(f"**状态**: <span class='{status_class}'>{status_icon} {device['status']}</span>", 
                           unsafe_allow_html=True)
                st.write(f"**最后更新**: {device['last_update']}")

def render_realtime_data():
    """实时数据页面"""
    st.markdown('<h2>⚡ 实时数据监控</h2>', unsafe_allow_html=True)
    
    # 设备类型选择
    device_types = list(data_loader.device_types.keys())
    selected_type = st.selectbox("选择设备类型", device_types)
    
    # 获取该类型设备
    type_devices = data_loader.get_devices_by_type(selected_type)
    online_devices = [d for d in type_devices if d["status"] == "在线"]
    
    if not online_devices:
        st.warning(f"该类型设备都处于离线状态")
        return
    
    st.info(f"📊 {selected_type} - 共 {len(online_devices)} 台设备在线")
    
    # 显示设备数据
    for device in online_devices:
        with st.container():
            st.markdown(f"### {device['icon']} {device['device_name']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("设备状态", "🟢 在线")
            
            with col2:
                if device["device_type"] == "水质监测":
                    water_data = data_loader.get_water_quality_data()
                    st.metric("pH值", f"{water_data['ph']}")
                else:
                    # 模拟其他设备数据
                    st.metric("运行状态", "正常")
            
            with col3:
                st.metric("最后更新", "刚刚")
            
            st.markdown("---")

def render_digital_park():
    """数字园区页面 - Streamlit Cloud优化版"""
    st.markdown('<h2>🗺️ 数字园区</h2>', unsafe_allow_html=True)
    
    # 简化版地图展示 - 不使用folium，改用文本和图表
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🏛️ 国科大深圳先进技术研究院")
        st.markdown("**地址**: 深圳市南山区西丽深圳大学城学苑大道1068号")
        st.markdown("**坐标**: 22.59163°N, 113.972654°E")
        
        # 创建设备分布图 - 使用散点图替代地图
        st.markdown("### 📍 设备分布图")
        
        # 生成设备位置数据
        np.random.seed(42)  # 固定随机种子
        base_lat, base_lng = 22.59163, 113.972654
        
        device_locations = []
        for device in data_loader.devices:
            # 在研究院周围1km范围内随机分布
            lat_offset = np.random.uniform(-0.005, 0.005)
            lng_offset = np.random.uniform(-0.005, 0.005)
            
            device_locations.append({
                "设备名称": device["device_name"],
                "设备类型": device["device_type"],
                "纬度": base_lat + lat_offset,
                "经度": base_lng + lng_offset,
                "状态": device["status"],
                "图标": device["icon"]
            })
        
        # 创建DataFrame
        df_locations = pd.DataFrame(device_locations)
        
        # 使用Streamlit内置的散点图
        try:
            chart_data = df_locations[["纬度", "经度"]].copy()
            chart_data["size"] = 20  # 点的大小
            
            st.scatter_chart(
                chart_data,
                x="经度",
                y="纬度",
                size="size",
                height=400
            )
            
            st.success("✅ 设备位置分布图已显示")
            
        except Exception as e:
            st.warning(f"地图组件加载中，显示简化版本")
            
            # 备选：文字版设备分布
            st.markdown("#### 🗺️ 设备区域分布")
            
            regions = {
                "北区": {"devices": [], "emoji": "🌾"},
                "南区": {"devices": [], "emoji": "🌿"}, 
                "东区": {"devices": [], "emoji": "🌱"},
                "西区": {"devices": [], "emoji": "🍃"},
                "中心区": {"devices": [], "emoji": "🏛️"}
            }
            
            # 随机分配设备到区域
            for i, device in enumerate(data_loader.devices):
                region_name = list(regions.keys())[i % len(regions)]
                regions[region_name]["devices"].append(device)
            
            # 显示各区域设备
            for region, info in regions.items():
                if info["devices"]:
                    st.markdown(f"**{info['emoji']} {region}** ({len(info['devices'])}台设备)")
                    device_types = {}
                    for device in info["devices"]:
                        device_type = device["device_type"]
                        device_types[device_type] = device_types.get(device_type, 0) + 1
                    
                    for device_type, count in device_types.items():
                        icon = data_loader.device_types[device_type]["icon"]
                        st.write(f"   {icon} {device_type}: {count}台")
    
    with col2:
        st.markdown("### 📊 园区统计")
        
        # 设备状态统计
        online_count = len([d for d in data_loader.devices if d["status"] == "在线"])
        offline_count = len([d for d in data_loader.devices if d["status"] == "离线"])
        
        st.metric("设备总数", len(data_loader.devices))
        st.metric("在线设备", online_count, delta=f"{online_count-offline_count}")
        st.metric("离线设备", offline_count)
        
        # 设备类型分布
        st.markdown("#### 🏭 设备类型分布")
        device_type_counts = {}
        for device in data_loader.devices:
            device_type = device["device_type"]
            device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1
        
        # 创建饼图数据
        chart_data = pd.DataFrame([
            {"类型": k, "数量": v, "图标": data_loader.device_types[k]["icon"]} 
            for k, v in device_type_counts.items()
        ])
        
        # 显示设备类型列表
        for _, row in chart_data.iterrows():
            percentage = round((row["数量"] / len(data_loader.devices)) * 100, 1)
            st.write(f"{row['图标']} **{row['类型']}**: {row['数量']}台 ({percentage}%)")
        
        # 园区范围信息
        st.markdown("#### 📏 园区信息")
        st.write("**园区面积**: ~3.14 km²")
        st.write("**覆盖范围**: 1km 半径")
        st.write("**设备密度**: 13.4台/km²")
        
    # 设备详细列表
    st.markdown("---")
    st.markdown("### 📋 设备详细信息")
    
    # 筛选选项
    col1, col2 = st.columns(2)
    
    with col1:
        device_types = ["全部"] + list(data_loader.device_types.keys())
        filter_type = st.selectbox("筛选设备类型", device_types, key="park_type_filter")
    
    with col2:
        status_options = ["全部", "在线", "离线"]
        filter_status = st.selectbox("筛选设备状态", status_options, key="park_status_filter")
    
    # 应用筛选
    filtered_devices = data_loader.devices.copy()
    
    if filter_type != "全部":
        filtered_devices = [d for d in filtered_devices if d["device_type"] == filter_type]
    
    if filter_status != "全部":
        filtered_devices = [d for d in filtered_devices if d["status"] == filter_status]
    
    # 创建设备表格
    if filtered_devices:
        device_table = []
        for device in filtered_devices:
            device_table.append({
                "设备名称": f"{device['icon']} {device['device_name']}",
                "设备ID": device["device_id"],
                "设备类型": device["device_type"],
                "状态": "🟢 在线" if device["status"] == "在线" else "🔴 离线",
                "安装日期": device["install_date"],
                "最后更新": device["last_update"]
            })
        
        df_devices = pd.DataFrame(device_table)
        st.dataframe(df_devices, use_container_width=True)
        
        st.info(f"📊 共找到 {len(filtered_devices)} 个设备")
    else:
        st.warning("没有找到符合条件的设备")

def render_sim_card_management():
    """SIM卡管理页面"""
    st.markdown('<h2>📱 流量卡管理</h2>', unsafe_allow_html=True)
    
    # 生成模拟SIM卡数据
    operators = ["中国移动", "中国联通", "中国电信"]
    sim_cards = []
    
    for i in range(25):
        total_data = random.randint(500, 2000)
        used_data = random.randint(50, int(total_data * 0.9))
        
        card = {
            "卡号": f"898600{random.randint(100000000, 999999999):09d}",
            "运营商": random.choice(operators),
            "总流量(MB)": total_data,
            "已用(MB)": used_data,
            "剩余(MB)": total_data - used_data,
            "使用率": f"{round((used_data / total_data) * 100, 1)}%",
            "状态": random.choice(["正常", "正常", "正常", "即将到期"])
        }
        sim_cards.append(card)
    
    # 统计信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("SIM卡总数", len(sim_cards))
    
    with col2:
        normal_cards = len([c for c in sim_cards if c["状态"] == "正常"])
        st.metric("正常状态", normal_cards)
    
    with col3:
        warning_cards = len([c for c in sim_cards if c["状态"] == "即将到期"])
        st.metric("即将到期", warning_cards)
    
    with col4:
        avg_usage = sum([float(c["使用率"].replace('%', '')) for c in sim_cards]) / len(sim_cards)
        st.metric("平均使用率", f"{avg_usage:.1f}%")
    
    # 显示SIM卡列表
    df = pd.DataFrame(sim_cards)
    st.dataframe(df, use_container_width=True)

def main():
    """主函数"""
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
    st.sidebar.success("🟢 系统正常运行")
    st.sidebar.info(f"📊 设备总数: {data_loader.stats['total_devices']}")
    st.sidebar.info(f"🔗 在线设备: {data_loader.stats['online_devices']}")
    
    # 渲染页面
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