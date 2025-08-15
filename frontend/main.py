"""
农业物联网可视化平台 - Streamlit前端
基于Go Gin后端的现代化IoT数据可视化系统
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# 页面配置
st.set_page_config(
    page_title="农业物联网可视化平台",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入自定义模块
from config.settings import Settings
from services.api_client import APIClient
from components.auth import AuthManager
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.devices import render_device_management
from components.projects import render_project_management
from components.realtime import render_realtime_data
from utils.cache import cache_manager
from utils.websocket_client import WebSocketManager

# 初始化设置
settings = Settings()
api_client = APIClient(settings.API_BASE_URL)

# 自定义CSS样式
def load_custom_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
    /* 主题色彩 - 农业绿色主题 */
    :root {
        --primary-color: #10B981;
        --secondary-color: #059669;
        --accent-color: #34D399;
        --background-color: #F0FDF4;
        --text-color: #1F2937;
        --border-color: #E5E7EB;
        --success-color: #10B981;
        --warning-color: #F59E0B;
        --error-color: #EF4444;
        --info-color: #3B82F6;
    }
    
    /* 全局样式 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 卡片样式 */
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
    
    /* 设备状态指示器 */
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
    
    .status-error {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
    }
    
    /* 脉搏动画 */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* 导航标签样式 */
    .nav-tab {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        margin: 0.25rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .nav-tab:hover {
        background: var(--background-color);
        border-color: var(--primary-color);
    }
    
    .nav-tab.active {
        background: var(--primary-color);
        color: white;
        border-color: var(--primary-color);
    }
    
    /* 数据卡片 */
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
    
    /* 项目卡片 */
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
    
    .project-description {
        color: #6B7280;
        font-size: 0.875rem;
        margin-bottom: 1rem;
        line-height: 1.5;
    }
    
    .project-stats {
        display: flex;
        align-items: center;
        gap: 1rem;
        font-size: 0.875rem;
        color: #6B7280;
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
    
    /* Fork按钮样式 */
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
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .metric-card {
            padding: 1rem;
        }
        
        .data-value {
            font-size: 2rem;
        }
        
        .project-card {
            padding: 1rem;
        }
        
        .fork-button {
            position: static;
            margin-top: 1rem;
            width: 100%;
        }
    }
    
    /* Plotly图表样式调整 */
    .js-plotly-plot .plotly .modebar {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 6px;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #F0FDF4 0%, #ECFDF5 100%);
        border-right: 1px solid var(--border-color);
    }
    
    /* 加载动画 */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 0.5rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* 通知样式 */
    .notification {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid;
        position: relative;
    }
    
    .notification-success {
        background: #D1FAE5;
        border-color: #A7F3D0;
        color: #065F46;
    }
    
    .notification-warning {
        background: #FEF3C7;
        border-color: #FDE68A;
        color: #92400E;
    }
    
    .notification-error {
        background: #FEE2E2;
        border-color: #FECACA;
        color: #991B1B;
    }
    
    .notification-info {
        background: #DBEAFE;
        border-color: #BFDBFE;
        color: #1E40AF;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """主函数"""
    # 加载自定义CSS
    load_custom_css()
    
    # 初始化会话状态
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    # 认证检查
    auth_manager = AuthManager(api_client)
    
    if not st.session_state.authenticated:
        # 显示登录页面
        auth_manager.render_login_page()
        return
    
    # 已认证用户界面
    render_authenticated_app()

def render_authenticated_app():
    """渲染已认证用户的应用界面"""
    
    # 渲染侧边栏
    current_page = render_sidebar()
    
    # 主内容区域
    main_container = st.container()
    
    with main_container:
        # 页面标题和用户信息
        render_header()
        
        # 根据选择的页面渲染对应内容
        if current_page == 'dashboard':
            render_dashboard(api_client)
        elif current_page == 'devices':
            render_device_management(api_client)
        elif current_page == 'projects':
            render_project_management(api_client)
        elif current_page == 'realtime':
            render_realtime_data(api_client)
        elif current_page == 'analytics':
            render_analytics_page()
        elif current_page == 'settings':
            render_settings_page()

def render_header():
    """渲染页面头部"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🌱 农业物联网可视化平台")
        st.markdown("*现代化IoT数据分析与可视化系统*")
    
    with col2:
        # 实时时间显示
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"**当前时间:** {current_time}")
    
    with col3:
        # 用户信息和退出按钮
        if st.session_state.user_info:
            user = st.session_state.user_info
            st.markdown(f"**欢迎:** {user.get('username', 'Unknown')}")
            if st.button("退出登录", key="logout_btn"):
                logout()

def logout():
    """用户登出"""
    # 调用后端登出API
    try:
        api_client.logout()
    except Exception as e:
        st.warning(f"登出时发生错误: {e}")
    
    # 清除会话状态
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.success("已成功退出登录")
    time.sleep(1)
    st.rerun()

def render_analytics_page():
    """渲染数据分析页面"""
    st.header("📊 数据分析")
    
    st.info("🚧 数据分析功能正在开发中，敬请期待！")
    
    # 占位符内容
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("预测分析")
        st.write("- 设备性能预测")
        st.write("- 故障预警")
        st.write("- 优化建议")
    
    with col2:
        st.subheader("智能报告")
        st.write("- 自动化报告生成")
        st.write("- 数据洞察")
        st.write("- 趋势分析")

def render_settings_page():
    """渲染设置页面"""
    st.header("⚙️ 系统设置")
    
    tab1, tab2, tab3 = st.tabs(["个人设置", "系统配置", "关于"])
    
    with tab1:
        st.subheader("个人设置")
        
        # 用户信息编辑
        if st.session_state.user_info:
            user = st.session_state.user_info
            
            with st.form("user_settings"):
                st.text_input("用户名", value=user.get('username', ''), disabled=True)
                st.text_input("邮箱", value=user.get('email', ''))
                st.text_input("手机号", value=user.get('phone', ''))
                
                submitted = st.form_submit_button("保存设置")
                if submitted:
                    st.success("设置已保存！")
    
    with tab2:
        st.subheader("系统配置")
        
        # 主题设置
        theme = st.selectbox("界面主题", ["绿色农业", "蓝色科技", "橙色工业"])
        
        # 数据刷新间隔
        refresh_interval = st.slider("数据刷新间隔（秒）", 1, 60, 5)
        
        # 图表设置
        chart_animation = st.checkbox("启用图表动画", value=True)
        
        if st.button("应用设置"):
            st.success("系统设置已更新！")
    
    with tab3:
        st.subheader("关于系统")
        
        st.markdown("""
        **农业物联网可视化平台 v2.0**
        
        基于现代化技术栈构建的IoT数据可视化系统：
        - **后端**: Go Gin + PostgreSQL + Redis
        - **前端**: Streamlit + Plotly + WebSocket
        - **特色功能**: Fork项目管理、实时数据推送、智能分析
        
        **技术特点:**
        - 🚀 高性能实时数据处理
        - 🔄 Git-like项目管理模式
        - 📱 响应式设计
        - 🔐 安全认证体系
        - 📊 丰富的可视化组件
        
        **开发团队**: zhuoying.li
        **更新日期**: 2025-08-14
        """)

if __name__ == "__main__":
    main()