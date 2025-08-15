#!/usr/bin/env python3
"""
农业物联网可视化系统 - 演示版
Go Gin + Streamlit 现代化IoT平台
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import json

# 页面配置
st.set_page_config(
    page_title="农业物联网可视化平台 v2.0",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载自定义CSS
def load_custom_css():
    st.markdown("""
    <style>
    :root {
        --primary-color: #10B981;
        --secondary-color: #059669;
        --accent-color: #34D399;
        --background-color: #F0FDF4;
        --text-color: #1F2937;
        --border-color: #E5E7EB;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--border-color);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .device-status {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    
    .status-online {
        background-color: #D1FAE5;
        color: #065F46;
        border: 1px solid #A7F3D0;
    }
    
    .status-offline {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FECACA;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    .data-card {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .data-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        transform: translate(30%, -30%);
    }
    
    .data-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .data-label {
        font-size: 1rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    .project-card {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
        position: relative;
    }
    
    .project-card:hover {
        border-color: var(--primary-color);
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .project-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 0.5rem;
    }
    
    .project-tag {
        display: inline-block;
        background: var(--background-color);
        color: var(--primary-color);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid #D1FAE5;
    }
    
    .fork-button {
        background: var(--primary-color);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        position: absolute;
        top: 1rem;
        right: 1rem;
    }
    
    .fork-button:hover {
        background: var(--secondary-color);
        transform: translateY(-1px);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 模拟设备数据
@st.cache_data
def get_device_types():
    return {
        1: {"name": "气象站", "icon": "🌤️", "color": "#3B82F6"},
        2: {"name": "土壤墒情", "icon": "🌱", "color": "#10B981"},
        3: {"name": "水质监测", "icon": "💧", "color": "#06B6D4"},
        4: {"name": "视频监控", "icon": "📹", "color": "#8B5CF6"},
        5: {"name": "配电柜", "icon": "⚡", "color": "#F59E0B"},
        6: {"name": "虫情监测", "icon": "🐛", "color": "#EF4444"},
        7: {"name": "孢子仪", "icon": "🦠", "color": "#84CC16"},
        8: {"name": "环境监测", "icon": "🌡️", "color": "#6366F1"},
        9: {"name": "智能灌溉", "icon": "💦", "color": "#14B8A6"},
        10: {"name": "杀虫灯", "icon": "💡", "color": "#F97316"},
        11: {"name": "一体化闸门", "icon": "🚪", "color": "#64748B"},
        12: {"name": "积水传感器", "icon": "🌊", "color": "#0EA5E9"},
        13: {"name": "植物生长记录仪", "icon": "📊", "color": "#22C55E"}
    }

def generate_sample_devices():
    device_types = get_device_types()
    devices = []
    
    for i in range(1, 6):
        device_type = random.choice(list(device_types.keys()))
        device = {
            'id': i,
            'device_id': f'DEV{i:03d}',
            'name': f'{device_types[device_type]["name"]}{i:02d}',
            'type': device_type,
            'type_name': device_types[device_type]["name"],
            'icon': device_types[device_type]["icon"],
            'color': device_types[device_type]["color"],
            'status': random.choice(['online', 'offline']),
            'last_seen': datetime.now() - timedelta(minutes=random.randint(0, 60)),
            'location': {'lat': 39.9 + random.uniform(-0.1, 0.1), 
                        'lng': 116.4 + random.uniform(-0.1, 0.1)}
        }
        devices.append(device)
    
    return devices

def generate_sample_data(device_id, hours=24):
    """生成模拟的传感器数据"""
    now = datetime.now()
    data = []
    
    for i in range(hours * 6):  # 每10分钟一个数据点
        timestamp = now - timedelta(minutes=i*10)
        
        # 模拟不同类型的传感器数据
        if device_id == 'DEV001':  # 气象站
            temp = 20 + 10 * random.random() + 5 * (0.5 - random.random())
            humidity = 40 + 40 * random.random()
            data.append({
                'timestamp': timestamp,
                'temperature': round(temp, 1),
                'humidity': round(humidity, 1),
                'wind_speed': round(random.uniform(0, 15), 1)
            })
        elif device_id == 'DEV002':  # 土壤墒情
            moisture = 30 + 40 * random.random()
            data.append({
                'timestamp': timestamp,
                'soil_moisture': round(moisture, 1),
                'soil_temperature': round(15 + 10 * random.random(), 1),
                'ph_value': round(6.0 + 2 * random.random(), 2)
            })
        else:  # 其他设备
            data.append({
                'timestamp': timestamp,
                'value': round(50 + 50 * random.random(), 1),
                'status': random.choice(['normal', 'warning', 'alarm'])
            })
    
    return list(reversed(data))

def main():
    load_custom_css()
    
    # 页面标题
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1>🌱 农业物联网可视化平台 v2.0</h1>
        <p style="color: #6B7280; font-size: 1.1rem;">Go Gin + Streamlit 现代化IoT数据分析与可视化系统演示</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏导航
    with st.sidebar:
        st.markdown("### 🧭 导航菜单")
        page = st.radio(
            "选择页面",
            ["📊 仪表板", "🏭 设备管理", "🔄 项目管理", "📈 实时数据", "🎯 Fork演示"],
            key="navigation"
        )
        
        st.markdown("---")
        st.markdown("### 🔑 演示信息")
        st.info("""
        **演示账号:**
        - 用户: 18823870097
        - 密码: yaohongming
        
        **系统特性:**
        - ✅ Go Gin高性能后端
        - ✅ Streamlit快速前端
        - ✅ WebSocket实时推送
        - ✅ Fork项目管理
        """)
    
    # 主内容区域
    if page == "📊 仪表板":
        render_dashboard()
    elif page == "🏭 设备管理":
        render_device_management()
    elif page == "🔄 项目管理":
        render_project_management()
    elif page == "📈 实时数据":
        render_realtime_data()
    elif page == "🎯 Fork演示":
        render_fork_demo()

def render_dashboard():
    """渲染仪表板"""
    st.header("📊 系统概览仪表板")
    
    # 顶部统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="data-card">
            <div class="data-value">5</div>
            <div class="data-label">🏭 在线设备</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="data-card" style="background: linear-gradient(135deg, #3B82F6, #1E40AF);">
            <div class="data-value">13</div>
            <div class="data-label">📊 项目总数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="data-card" style="background: linear-gradient(135deg, #F59E0B, #D97706);">
            <div class="data-value">1,247</div>
            <div class="data-label">📈 数据点数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="data-card" style="background: linear-gradient(135deg, #8B5CF6, #7C3AED);">
            <div class="data-value">98.5%</div>
            <div class="data-label">✅ 系统可用性</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 设备状态和实时数据
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🏭 设备状态")
        devices = generate_sample_devices()
        
        for device in devices:
            status_class = "status-online" if device['status'] == 'online' else "status-offline"
            status_text = "在线" if device['status'] == 'online' else "离线"
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <span style="font-size: 1.5rem; margin-right: 0.5rem;">{device['icon']}</span>
                        <strong>{device['name']}</strong>
                        <br>
                        <small style="color: #6B7280;">ID: {device['device_id']}</small>
                    </div>
                    <span class="device-status {status_class}">{status_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("📈 实时数据趋势")
        
        # 生成模拟实时数据
        data = generate_sample_data('DEV001', 24)
        df = pd.DataFrame(data)
        
        if not df.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['temperature'],
                mode='lines+markers',
                name='温度 (°C)',
                line=dict(color='#EF4444', width=2),
                marker=dict(size=4)
            ))
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['humidity'],
                mode='lines+markers',
                name='湿度 (%)',
                line=dict(color='#3B82F6', width=2),
                marker=dict(size=4),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title="气象站实时监控数据",
                xaxis_title="时间",
                yaxis=dict(title="温度 (°C)", side="left"),
                yaxis2=dict(title="湿度 (%)", side="right", overlaying="y"),
                hovermode='x unified',
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)

def render_device_management():
    """渲染设备管理页面"""
    st.header("🏭 设备管理")
    
    tab1, tab2, tab3 = st.tabs(["设备列表", "添加设备", "设备统计"])
    
    with tab1:
        st.subheader("设备列表")
        devices = generate_sample_devices()
        
        # 筛选器
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("状态筛选", ["全部", "在线", "离线"])
        with col2:
            type_filter = st.selectbox("类型筛选", ["全部"] + [f"{v['icon']} {v['name']}" for v in get_device_types().values()])
        with col3:
            st.write("")  # 占位符
        
        # 设备表格
        for device in devices:
            with st.expander(f"{device['icon']} {device['name']} - {device['device_id']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**设备类型:** {device['type_name']}")
                    st.write(f"**设备ID:** {device['device_id']}")
                    status_color = "🟢" if device['status'] == 'online' else "🔴"
                    st.write(f"**状态:** {status_color} {device['status']}")
                
                with col2:
                    st.write(f"**最后通信:** {device['last_seen'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**位置:** {device['location']['lat']:.3f}, {device['location']['lng']:.3f}")
                
                with col3:
                    if st.button(f"查看详情", key=f"detail_{device['id']}"):
                        st.success(f"正在跳转到 {device['name']} 详情页面...")
                    
                    if st.button(f"编辑设备", key=f"edit_{device['id']}"):
                        st.info("编辑功能开发中...")
    
    with tab2:
        st.subheader("添加新设备")
        
        with st.form("add_device_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                device_id = st.text_input("设备ID", placeholder="例：DEV006")
                device_name = st.text_input("设备名称", placeholder="例：温室气象站")
                device_type = st.selectbox("设备类型", options=list(get_device_types().keys()),
                                         format_func=lambda x: f"{get_device_types()[x]['icon']} {get_device_types()[x]['name']}")
            
            with col2:
                location_lat = st.number_input("纬度", value=39.9042)
                location_lng = st.number_input("经度", value=116.4074)
                description = st.text_area("设备描述", placeholder="设备功能和用途描述...")
            
            submitted = st.form_submit_button("添加设备", type="primary")
            
            if submitted:
                st.success(f"✅ 设备 {device_name} ({device_id}) 添加成功！")
                st.balloons()
    
    with tab3:
        st.subheader("设备统计")
        
        device_types = get_device_types()
        devices = generate_sample_devices()
        
        # 按类型统计
        type_counts = {}
        for device in devices:
            type_name = device['type_name']
            if type_name not in type_counts:
                type_counts[type_name] = {'total': 0, 'online': 0}
            type_counts[type_name]['total'] += 1
            if device['status'] == 'online':
                type_counts[type_name]['online'] += 1
        
        # 饼图
        labels = list(type_counts.keys())
        values = [type_counts[label]['total'] for label in labels]
        
        fig = px.pie(values=values, names=labels, title="设备类型分布")
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        
        # 统计表格
        stats_data = []
        for type_name, counts in type_counts.items():
            stats_data.append({
                "设备类型": type_name,
                "总数": counts['total'],
                "在线": counts['online'],
                "离线": counts['total'] - counts['online'],
                "在线率": f"{counts['online']/counts['total']*100:.1f}%"
            })
        
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True)

def render_project_management():
    """渲染项目管理页面"""
    st.header("🔄 项目管理")
    
    tab1, tab2, tab3 = st.tabs(["我的项目", "公开项目", "创建项目"])
    
    with tab1:
        st.subheader("我的项目")
        
        # 模拟项目数据
        my_projects = [
            {
                'id': 1,
                'name': '温室环境监控',
                'description': '监控温室内的温度、湿度、CO2浓度等关键环境参数',
                'tags': ['温室', '环境监控', 'Python'],
                'stars': 12,
                'forks': 3,
                'created_at': '2024-07-15',
                'updated_at': '2024-08-10',
                'public': True
            },
            {
                'id': 2,
                'name': '土壤墒情分析',
                'description': '分析土壤湿度变化趋势，提供灌溉建议',
                'tags': ['土壤', '数据分析', '机器学习'],
                'stars': 8,
                'forks': 1,
                'created_at': '2024-06-20',
                'updated_at': '2024-08-05',
                'public': False
            }
        ]
        
        for project in my_projects:
            st.markdown(f"""
            <div class="project-card">
                <div class="project-title">{project['name']}</div>
                <div class="project-description">{project['description']}</div>
                <div style="margin-bottom: 1rem;">
                    {''.join([f'<span class="project-tag">{tag}</span>' for tag in project['tags']])}
                </div>
                <div class="project-stats">
                    <span>⭐ {project['stars']}</span>
                    <span>🔄 {project['forks']}</span>
                    <span>📅 {project['updated_at']}</span>
                    <span>{'🌍 公开' if project['public'] else '🔒 私有'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("查看", key=f"view_my_{project['id']}"):
                    st.success(f"打开项目: {project['name']}")
            with col2:
                if st.button("编辑", key=f"edit_my_{project['id']}"):
                    st.info("编辑功能开发中...")
            with col3:
                if st.button("分享", key=f"share_my_{project['id']}"):
                    st.success("项目链接已复制到剪贴板")
            with col4:
                if st.button("删除", key=f"delete_my_{project['id']}"):
                    st.warning("确认删除此项目？")
            
            st.markdown("---")
    
    with tab2:
        st.subheader("公开项目")
        
        # 模拟公开项目
        public_projects = [
            {
                'id': 3,
                'name': '智慧农场大数据平台',
                'description': '集成多种传感器数据，提供农场全方位监控和数据分析',
                'author': 'admin',
                'tags': ['大数据', '物联网', '农业'],
                'stars': 45,
                'forks': 12,
                'created_at': '2024-05-01',
                'updated_at': '2024-08-12'
            },
            {
                'id': 4,
                'name': '水质监测预警系统',
                'description': '实时监测水质参数，自动预警异常情况',
                'author': 'water_expert',
                'tags': ['水质', '预警', '自动化'],
                'stars': 23,
                'forks': 8,
                'created_at': '2024-04-15',
                'updated_at': '2024-07-28'
            },
            {
                'id': 5,
                'name': '植物生长监控系统',
                'description': '利用计算机视觉技术监控植物生长状态',
                'author': 'ai_farmer',
                'tags': ['计算机视觉', '植物', 'AI'],
                'stars': 67,
                'forks': 25,
                'created_at': '2024-03-10',
                'updated_at': '2024-08-08'
            }
        ]
        
        for project in public_projects:
            st.markdown(f"""
            <div class="project-card">
                <button class="fork-button">🔄 Fork</button>
                <div class="project-title">{project['name']}</div>
                <div class="project-description">{project['description']}</div>
                <div style="margin-bottom: 1rem;">
                    {''.join([f'<span class="project-tag">{tag}</span>' for tag in project['tags']])}
                </div>
                <div class="project-stats">
                    <span>👤 {project['author']}</span>
                    <span>⭐ {project['stars']}</span>
                    <span>🔄 {project['forks']}</span>
                    <span>📅 {project['updated_at']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("查看详情", key=f"view_public_{project['id']}"):
                    st.success(f"打开项目: {project['name']}")
            with col2:
                if st.button("⭐ 点赞", key=f"star_public_{project['id']}"):
                    st.success("点赞成功！")
            with col3:
                if st.button("🔄 Fork", key=f"fork_public_{project['id']}"):
                    show_fork_dialog(project)
            
            st.markdown("---")
    
    with tab3:
        st.subheader("创建新项目")
        
        with st.form("create_project_form"):
            project_name = st.text_input("项目名称", placeholder="例：我的农场监控系统")
            project_desc = st.text_area("项目描述", placeholder="描述项目的功能和用途...")
            
            col1, col2 = st.columns(2)
            with col1:
                project_tags = st.text_input("项目标签", placeholder="用逗号分隔，例：温度,湿度,监控")
                project_public = st.checkbox("公开项目", help="公开项目可以被其他用户查看和Fork")
            
            with col2:
                template = st.selectbox("选择模板", 
                                      ["空白项目", "基础监控模板", "数据分析模板", "实时预警模板"])
                
            submitted = st.form_submit_button("创建项目", type="primary")
            
            if submitted:
                if project_name:
                    st.success(f"✅ 项目 '{project_name}' 创建成功！")
                    st.balloons()
                    
                    # 显示项目配置界面
                    st.markdown("### 🎨 项目配置")
                    st.info("项目创建成功！您可以开始配置可视化界面了。")
                    
                    # 简单的配置选项
                    config_col1, config_col2 = st.columns(2)
                    
                    with config_col1:
                        chart_type = st.selectbox("主要图表类型", ["折线图", "柱状图", "饼图", "散点图"])
                        data_source = st.selectbox("数据源", ["实时数据", "历史数据", "混合数据"])
                    
                    with config_col2:
                        refresh_interval = st.slider("刷新间隔 (秒)", 1, 60, 5)
                        show_legend = st.checkbox("显示图例", value=True)
                    
                    if st.button("保存配置"):
                        st.success("项目配置已保存！")
                else:
                    st.error("请输入项目名称")

def show_fork_dialog(project):
    """显示Fork对话框"""
    with st.expander(f"🔄 Fork项目: {project['name']}", expanded=True):
        st.markdown(f"**原项目:** {project['name']}")
        st.markdown(f"**作者:** {project['author']}")
        st.markdown(f"**描述:** {project['description']}")
        
        fork_name = st.text_input("Fork项目名称", value=f"{project['name']} (我的Fork)")
        fork_desc = st.text_area("Fork说明", placeholder="描述您的修改计划...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("确认Fork", type="primary", key=f"confirm_fork_{project['id']}"):
                st.success(f"✅ 成功Fork项目 '{fork_name}'！")
                st.balloons()
        with col2:
            if st.button("取消", key=f"cancel_fork_{project['id']}"):
                st.info("已取消Fork操作")

def render_realtime_data():
    """渲染实时数据页面"""
    st.header("📈 实时数据监控")
    
    # 实时数据更新
    placeholder = st.empty()
    
    if st.checkbox("启用实时更新", value=True):
        # 模拟实时数据流
        for i in range(10):
            with placeholder.container():
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🌤️ 气象数据")
                    
                    # 生成随机数据
                    temp = 20 + 10 * random.random()
                    humidity = 40 + 40 * random.random()
                    wind_speed = random.uniform(0, 15)
                    
                    # 显示实时数值
                    col1a, col1b, col1c = st.columns(3)
                    with col1a:
                        st.metric("温度", f"{temp:.1f}°C", f"{random.uniform(-1, 1):.1f}")
                    with col1b:
                        st.metric("湿度", f"{humidity:.1f}%", f"{random.uniform(-5, 5):.1f}")
                    with col1c:
                        st.metric("风速", f"{wind_speed:.1f}m/s", f"{random.uniform(-1, 1):.1f}")
                
                with col2:
                    st.subheader("🌱 土壤数据")
                    
                    # 土壤数据
                    soil_temp = 15 + 10 * random.random()
                    soil_moisture = 30 + 40 * random.random()
                    ph_value = 6.0 + 2 * random.random()
                    
                    col2a, col2b, col2c = st.columns(3)
                    with col2a:
                        st.metric("土壤温度", f"{soil_temp:.1f}°C", f"{random.uniform(-0.5, 0.5):.1f}")
                    with col2b:
                        st.metric("土壤湿度", f"{soil_moisture:.1f}%", f"{random.uniform(-2, 2):.1f}")
                    with col2c:
                        st.metric("pH值", f"{ph_value:.2f}", f"{random.uniform(-0.1, 0.1):.2f}")
                
                # 实时图表
                st.subheader("📊 实时趋势")
                
                # 生成时间序列数据
                times = [datetime.now() - timedelta(minutes=x) for x in range(30, 0, -1)]
                temps = [20 + 5 * random.random() + 2 * random.random() for _ in times]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=times,
                    y=temps,
                    mode='lines+markers',
                    name='温度',
                    line=dict(color='#EF4444', width=3)
                ))
                
                fig.update_layout(
                    title="实时温度变化",
                    xaxis_title="时间",
                    yaxis_title="温度 (°C)",
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 状态信息
                st.info(f"🔄 数据更新时间: {datetime.now().strftime('%H:%M:%S')} | 连接状态: ✅ 正常")
            
            # 等待1秒后更新
            time.sleep(1)
    else:
        st.info("实时更新已暂停。勾选上方复选框以启用实时数据流。")

def render_fork_demo():
    """渲染Fork功能演示"""
    st.header("🎯 Fork功能演示")
    
    st.markdown("""
    ### 🔄 什么是Fork功能？
    
    Fork功能借鉴了Git版本控制的理念，允许用户：
    - **复制项目配置**: 创建他人项目的副本
    - **自定义修改**: 根据自己需求调整配置
    - **版本管理**: 跟踪所有配置变更
    - **协作共享**: 与其他用户分享和合作
    """)
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Fork流程演示", "配置对比", "版本历史"])
    
    with tab1:
        st.subheader("📝 Fork操作流程")
        
        step = st.select_slider(
            "选择演示步骤",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: f"步骤 {x}"
        )
        
        if step == 1:
            st.markdown("#### 步骤1: 发现感兴趣的项目")
            st.success("✅ 浏览公开项目库，找到有用的可视化配置")
            
            st.markdown("""
            <div class="project-card">
                <div class="project-title">🌟 智能温室监控系统</div>
                <div class="project-description">完整的温室环境监控方案，包含温度、湿度、光照等多维度分析</div>
                <div class="project-stats">
                    <span>👤 expert_farmer</span>
                    <span>⭐ 89</span>
                    <span>🔄 23</span>
                    <span>🌍 公开</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif step == 2:
            st.markdown("#### 步骤2: 点击Fork按钮")
            st.success("✅ 创建项目副本到您的账户下")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**原项目**")
                st.code("""
项目名: 智能温室监控系统
作者: expert_farmer  
配置: {
  "charts": ["temperature", "humidity"],
  "refresh": 10,
  "alerts": true
}
                """)
            
            with col2:
                st.markdown("**Fork副本**")
                st.code("""
项目名: 智能温室监控系统 (我的版本)
作者: 您的用户名
配置: {
  "charts": ["temperature", "humidity"],
  "refresh": 10,
  "alerts": true
}
                """)
        
        elif step == 3:
            st.markdown("#### 步骤3: 自定义配置")
            st.success("✅ 根据需求修改可视化配置")
            
            with st.form("config_form"):
                st.markdown("**修改可视化配置:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    charts = st.multiselect("选择图表", 
                                          ["temperature", "humidity", "light", "co2"],
                                          default=["temperature", "humidity", "light"])
                    refresh_rate = st.slider("刷新频率(秒)", 1, 60, 5)
                
                with col2:
                    enable_alerts = st.checkbox("启用告警", value=True)
                    chart_type = st.selectbox("图表类型", ["line", "bar", "area"])
                
                if st.form_submit_button("保存修改"):
                    st.success("配置已保存！系统将记录此次变更。")
        
        elif step == 4:
            st.markdown("#### 步骤4: 版本管理")
            st.success("✅ 系统自动记录所有配置变更")
            
            st.markdown("**变更历史:**")
            history_data = [
                {"时间": "2024-08-14 16:45", "操作": "Fork项目", "用户": "您", "描述": "从expert_farmer的项目创建Fork"},
                {"时间": "2024-08-14 16:47", "操作": "修改配置", "用户": "您", "描述": "添加光照传感器图表"},
                {"时间": "2024-08-14 16:50", "操作": "调整刷新", "用户": "您", "描述": "将刷新频率从10秒改为5秒"},
            ]
            
            st.dataframe(pd.DataFrame(history_data), use_container_width=True)
        
        elif step == 5:
            st.markdown("#### 步骤5: 分享和协作")
            st.success("✅ 分享您的配置或提交合并请求")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**分享您的Fork:**")
                st.code("https://platform.com/projects/your_fork_123")
                if st.button("复制链接"):
                    st.success("链接已复制到剪贴板")
            
            with col2:
                st.markdown("**提交合并请求:**")
                st.text_area("描述您的改进", placeholder="说明您的修改如何改进了原项目...")
                if st.button("提交Pull Request"):
                    st.success("合并请求已提交，等待原作者审核")
    
    with tab2:
        st.subheader("⚖️ 配置对比工具")
        
        st.markdown("比较不同版本的项目配置差异：")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**原始配置**")
            st.json({
                "project_name": "智能温室监控系统",
                "charts": ["temperature", "humidity"],
                "refresh_interval": 10,
                "alert_enabled": True,
                "chart_type": "line",
                "color_scheme": "default"
            })
        
        with col2:
            st.markdown("**修改后配置**")
            st.json({
                "project_name": "智能温室监控系统 (增强版)",
                "charts": ["temperature", "humidity", "light", "co2"],
                "refresh_interval": 5,
                "alert_enabled": True,
                "chart_type": "area",
                "color_scheme": "green"
            })
        
        st.markdown("### 📊 差异摘要")
        diff_data = [
            {"字段": "project_name", "变更类型": "修改", "原值": "智能温室监控系统", "新值": "智能温室监控系统 (增强版)"},
            {"字段": "charts", "变更类型": "添加", "原值": "2个图表", "新值": "4个图表 (+light, +co2)"},
            {"字段": "refresh_interval", "变更类型": "修改", "原值": "10秒", "新值": "5秒"},
            {"字段": "chart_type", "变更类型": "修改", "原值": "line", "新值": "area"},
            {"字段": "color_scheme", "变更类型": "修改", "原值": "default", "新值": "green"}
        ]
        
        st.dataframe(pd.DataFrame(diff_data), use_container_width=True)
    
    with tab3:
        st.subheader("📈 Fork网络图")
        
        st.markdown("""
        可视化项目的Fork关系网络，了解项目的传播和演化情况：
        """)
        
        # 创建一个简单的网络图示意
        fig = go.Figure()
        
        # 原始项目
        fig.add_trace(go.Scatter(
            x=[0], y=[0],
            mode='markers+text',
            marker=dict(size=30, color='#10B981'),
            text=["原始项目"],
            textposition="bottom center",
            name="原始项目"
        ))
        
        # Fork项目们
        fork_positions = [(1, 0.5), (1, -0.5), (-1, 0.5), (-1, -0.5), (0, 1)]
        fork_names = ["Fork A", "Fork B", "Fork C", "Fork D", "Fork E"]
        
        for i, (x, y) in enumerate(fork_positions):
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers+text',
                marker=dict(size=20, color='#3B82F6'),
                text=[fork_names[i]],
                textposition="bottom center",
                name=fork_names[i]
            ))
            
            # 连接线
            fig.add_trace(go.Scatter(
                x=[0, x], y=[0, y],
                mode='lines',
                line=dict(color='#E5E7EB', width=2),
                showlegend=False
            ))
        
        fig.update_layout(
            title="项目Fork关系网络",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📊 Fork统计")
        fork_stats = {
            "总Fork数": 23,
            "活跃Fork": 15,
            "本月新增": 5,
            "平均评分": 4.6
        }
        
        cols = st.columns(len(fork_stats))
        for i, (key, value) in enumerate(fork_stats.items()):
            with cols[i]:
                st.metric(key, value)

if __name__ == "__main__":
    main()