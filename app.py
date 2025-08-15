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
import folium
from streamlit_folium import st_folium

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
        # 地理位置配置 (国科大深圳先进技术研究院)
        self.base_location = {"lat": 22.59163, "lng": 113.972654}
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
        np.random.seed(42)  # 固定随机种子保持一致性
        
        for device_type, config in self.device_types.items():
            for i in range(config["count"]):
                if device_type == "水质监测":
                    dev_id = "865989071557605"
                else:
                    dev_id = f"{device_id:012d}"
                
                # 在研究院周围1km范围内生成位置
                lat_offset = np.random.uniform(-0.01, 0.01)
                lng_offset = np.random.uniform(-0.01, 0.01)
                
                device = {
                    "device_id": dev_id,
                    "device_name": f"{config['icon']} {device_type}-{i+1:02d}",
                    "device_type": device_type,
                    "icon": config["icon"],
                    "status": random.choice(["在线", "在线", "在线", "离线"]),
                    "install_date": "2024-01-15",
                    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "location": {
                        "lat": self.base_location["lat"] + lat_offset,
                        "lng": self.base_location["lng"] + lng_offset
                    }
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
    """数字园区页面 - 使用真正的地图"""
    st.markdown('<h2>🗺️ 数字园区</h2>', unsafe_allow_html=True)
    
    # 地图选项
    col1, col2 = st.columns([3, 1])
    
    with col2:
        map_style = st.selectbox(
            "地图样式",
            ["标准地图", "简化地图"],
            index=0
        )
        
        show_devices = st.checkbox("显示设备标记", value=True)
        show_legend = st.checkbox("显示图例", value=True)
    
    # 创建地图
    center_lat = data_loader.base_location["lat"]
    center_lng = data_loader.base_location["lng"]
    
    try:
        if map_style == "简化地图":
            # 简化版地图 - 更稳定
            m = folium.Map(
                location=[center_lat, center_lng],
                zoom_start=15,
                tiles='OpenStreetMap'
            )
            
            # 只添加研究院标记
            folium.Marker(
                [center_lat, center_lng],
                popup="🏛️ 国科大深圳先进技术研究院<br>农业IoT示范园区",
                tooltip="国科大深圳先进技术研究院",
                icon=folium.Icon(color='red', icon='star')
            ).add_to(m)
            
            # 添加园区边界
            folium.Circle(
                location=[center_lat, center_lng],
                radius=1000,
                popup="农业IoT示范园区",
                color='green',
                fillColor='lightgreen',
                fillOpacity=0.2
            ).add_to(m)
            
        else:
            # 完整版地图
            m = folium.Map(
                location=[center_lat, center_lng],
                zoom_start=16,  # 更高放大级别显示详细信息
                tiles='OpenStreetMap'
            )
            
            # 设备颜色映射 - 使用Folium支持的颜色
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
                "杀虫灯": "beige",
                "一体化闸门": "darkblue",
                "积水传感器": "cadetblue",
                "植物生长记录仪": "darkgreen"
            }
            
            # 添加设备标记
            if show_devices:
                for device in data_loader.devices:
                    lat = device["location"]["lat"]
                    lng = device["location"]["lng"]
                    color = device_colors.get(device["device_type"], "gray")
                    
                    # 构建弹出信息
                    popup_content = f"""
                    <b>{device['icon']} {device['device_name']}</b><br>
                    <b>设备ID:</b> {device['device_id']}<br>
                    <b>状态:</b> {'🟢' if device['status'] == '在线' else '🔴'} {device['status']}<br>
                    <b>安装日期:</b> {device['install_date']}<br>
                    <b>坐标:</b> {lat:.5f}, {lng:.5f}
                    """
                    
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
                <div style="width:250px;">
                <h4>🏛️ 国科大深圳先进技术研究院</h4>
                <p><b>地址:</b> 深圳市南山区西丽深圳大学城学苑大道1068号</p>
                <p><b>农业IoT示范园区</b></p>
                <p><b>设备总数:</b> 42台</p>
                <p><b>坐标:</b> 22.59163°N, 113.972654°E</p>
                </div>
                """, max_width=300),
                tooltip="国科大深圳先进技术研究院",
                icon=folium.Icon(color='red', icon='star')
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
            if show_legend:
                legend_html = '''
                <div style="position: fixed; 
                            top: 10px; right: 10px; width: 200px; height: auto; 
                            background-color: white; border:2px solid grey; z-index:9999; 
                            font-size:12px; padding: 10px;">
                <h4>设备类型图例</h4>
                '''
                
                for device_type, color in device_colors.items():
                    count = len([d for d in data_loader.devices if d["device_type"] == device_type])
                    icon = data_loader.device_types[device_type]["icon"]
                    legend_html += f'<p><span style="color:{color};">●</span> {icon} {device_type} ({count})</p>'
                
                legend_html += '</div>'
                m.get_root().html.add_child(folium.Element(legend_html))
            
            # 添加图层控制器
            folium.LayerControl().add_to(m)
        
        # 显示地图
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        map_data = st_folium(m, width=700, height=500, returned_objects=["last_object_clicked"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 显示点击信息
        if map_data['last_object_clicked']:
            st.info(f"📍 最后点击位置: {map_data['last_object_clicked']}")
        
    except Exception as e:
        st.error(f"地图加载失败: {str(e)}")
        st.info("请刷新页面重试，或检查网络连接")
        
        # 创建简化版地图作为备选
        simple_map = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=14,
            tiles='OpenStreetMap'
        )
        folium.Marker(
            [center_lat, center_lng],
            popup="国科大深圳先进技术研究院",
            tooltip="研究院位置"
        ).add_to(simple_map)
        map_data = st_folium(simple_map, width=700, height=500)
    
    # 设备统计信息
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 设备分布统计")
        device_stats = {}
        for device in data_loader.devices:
            device_type = device["device_type"]
            device_stats[device_type] = device_stats.get(device_type, 0) + 1
        
        for device_type, count in device_stats.items():
            icon = data_loader.device_types[device_type]["icon"]
            percentage = round((count / len(data_loader.devices)) * 100, 1)
            st.write(f"{icon} **{device_type}**: {count}台 ({percentage}%)")
    
    with col2:
        st.markdown("### 📈 系统状态")
        
        online_count = len([d for d in data_loader.devices if d["status"] == "在线"])
        offline_count = len([d for d in data_loader.devices if d["status"] == "离线"])
        
        st.write(f"**设备总数**: {len(data_loader.devices)}台")
        st.write(f"**在线设备**: {online_count}台")
        st.write(f"**离线设备**: {offline_count}台") 
        st.write(f"**在线率**: {round((online_count/len(data_loader.devices))*100, 1)}%")
        
        # 园区信息
        st.markdown("#### 📏 园区信息")
        st.write("**园区面积**: ~3.14 km²")
        st.write("**设备密度**: 13.4台/km²")
        st.write("**覆盖范围**: 1km 半径")

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