# 农业物联网可视化系统架构设计
## Go Gin + Streamlit 现代化重构方案

**Author:** zhuoying.li  
**Date:** 2025-08-14  
**Version:** 1.0  

## 1. 系统架构总览

### 1.1 技术栈选型对比

| 组件 | 原系统 | 新系统 | 优势 |
|------|--------|--------|------|
| 后端 | Java Web | Go Gin | 高并发、低资源占用、云原生 |
| 前端 | Bootstrap+jQuery | Streamlit | 数据科学友好、快速原型、Python生态 |
| 数据库 | 关系型DB | PostgreSQL+Redis | 性能优化、缓存支持 |
| 实时通信 | 轮询 | WebSocket | 真正的实时数据推送 |
| 地图服务 | 高德地图 | Folium+OpenStreetMap | 开源、可定制性强 |
| 部署 | 传统部署 | 容器化 | DevOps友好、弹性扩展 |

### 1.2 系统架构图

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    Go Gin API    │    │   PostgreSQL    │
│   前端界面      │◄──►│    后端服务      │◄──►│    主数据库     │
│                 │    │                  │    │                 │
│ • 数据可视化    │    │ • RESTful API    │    │ • 设备数据      │
│ • 用户交互      │    │ • WebSocket      │    │ • 用户信息      │
│ • Fork管理      │    │ • 实时推送       │    │ • Fork配置      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────WebSocket────┘                       │
                                │                        │
                      ┌─────────▼────────┐    ┌─────────▼─────────┐
                      │      Redis       │    │   IoT Devices    │
                      │   缓存+消息队列  │    │   物联网设备     │
                      └──────────────────┘    └───────────────────┘
```

## 2. 核心功能模块设计

### 2.1 设备管理模块
**原系统痛点：** 静态列表、刷新缓慢、交互复杂
**新系统优化：**
- 实时设备状态更新（WebSocket推送）
- 可视化设备拓扑图
- 智能设备分组和筛选
- 设备配置的版本管理（Fork功能）

### 2.2 数据可视化模块
**原系统痛点：** ECharts配置复杂、图表类型有限
**新系统优化：**
- Plotly交互式图表（缩放、选择、hover）
- 多维数据分析（时间序列、相关性、预测）
- 自定义图表模板系统
- 实时数据流图表

### 2.3 地理信息模块
**原系统痛点：** 高德地图API限制、定制性差
**新系统优化：**
- Folium开源地图，无API限制
- 热力图、聚类图、路径规划
- 地理围栏和报警区域设置
- 三维地形可视化

## 3. Fork功能深度设计

### 3.1 Fork功能概念
Fork功能借鉴Git版本控制理念，允许用户：
- **复制项目配置**：创建个人数据看板副本
- **自定义修改**：调整图表、布局、筛选条件
- **版本管理**：跟踪配置变更历史
- **协作共享**：分享配置或提交合并请求

### 3.2 技术实现方案

#### 数据模型设计
```go
// 项目配置表
type Project struct {
    ID          uint      `json:"id" gorm:"primarykey"`
    Name        string    `json:"name"`
    Description string    `json:"description"`
    OwnerID     uint      `json:"owner_id"`
    ParentID    *uint     `json:"parent_id"`      // Fork来源
    Config      JSONB     `json:"config"`         // 配置JSON
    Public      bool      `json:"public"`
    Tags        pq.StringArray `gorm:"type:text[]"` // 标签
    StarCount   int       `json:"star_count"`
    ForkCount   int       `json:"fork_count"`
    CreatedAt   time.Time `json:"created_at"`
    UpdatedAt   time.Time `json:"updated_at"`
}

// Fork历史记录
type ForkHistory struct {
    ID          uint      `json:"id" gorm:"primarykey"`
    ProjectID   uint      `json:"project_id"`
    UserID      uint      `json:"user_id"`
    Action      string    `json:"action"` // create, update, merge
    ConfigDiff  JSONB     `json:"config_diff"`
    Message     string    `json:"message"`
    CreatedAt   time.Time `json:"created_at"`
}
```

#### Fork操作流程
1. **创建Fork**: `POST /api/projects/{id}/fork`
2. **更新配置**: `PUT /api/projects/{id}/config`
3. **查看历史**: `GET /api/projects/{id}/history`
4. **合并请求**: `POST /api/projects/{id}/pull-request`

### 3.3 Fork功能界面设计

#### Streamlit界面组织
```python
# 主导航
with st.sidebar:
    page = option_menu("主菜单", 
        ["仪表板", "我的项目", "公共项目", "Fork管理"])

if page == "我的项目":
    # 项目列表
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("我的项目")
    with col2:
        if st.button("新建项目"):
            create_project()
    
    # 项目卡片展示
    for project in get_my_projects():
        with st.expander(f"📊 {project.name}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(project.description)
            with col2:
                if st.button("编辑", key=f"edit_{project.id}"):
                    edit_project(project.id)
            with col3:
                if st.button("Fork", key=f"fork_{project.id}"):
                    fork_project(project.id)
```

## 4. UI设计优化方案

### 4.1 现代化设计原则
- **信息层次化**：清晰的信息架构和视觉层次
- **渐进式披露**：按需展示复杂信息
- **响应式适配**：优秀的移动端体验
- **可访问性**：符合WCAG 2.1标准

### 4.2 Streamlit UI增强

#### 自定义CSS主题
```python
# 自定义主题配置
def load_custom_css():
    st.markdown("""
    <style>
    /* 主色调：绿色农业主题 */
    :root {
        --primary-color: #10B981;
        --secondary-color: #059669;
        --accent-color: #34D399;
        --background-color: #F0FDF4;
        --text-color: #1F2937;
    }
    
    /* 卡片样式 */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #E5E7EB;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* 设备状态指示器 */
    .device-status-online {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #10B981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)
```

#### 响应式组件设计
```python
# 响应式设备卡片组件
def device_card(device_data):
    """渲染设备状态卡片"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # 设备类型图标
        icon = get_device_icon(device_data['type'])
        st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{icon}</div>", 
                   unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**{device_data['name']}**")
        st.markdown(f"ID: `{device_data['device_id']}`")
        
        # 状态指示器
        status_color = "#10B981" if device_data['online'] else "#EF4444"
        status_text = "在线" if device_data['online'] else "离线"
        st.markdown(f"""
            <span style="color: {status_color};">● {status_text}</span>
        """, unsafe_allow_html=True)
    
    with col3:
        # 操作按钮
        if st.button("详情", key=f"detail_{device_data['id']}"):
            show_device_detail(device_data['id'])
```

## 5. 实时数据处理架构

### 5.1 WebSocket实时推送
```go
// WebSocket管理器
type WSManager struct {
    clients    map[string]*websocket.Conn
    broadcast  chan []byte
    register   chan *WSClient
    unregister chan *WSClient
    mu         sync.RWMutex
}

type WSClient struct {
    conn     *websocket.Conn
    userID   string
    deviceIDs []string // 用户关注的设备
}

// 实时数据推送
func (manager *WSManager) handleDeviceData(data DeviceData) {
    message := map[string]interface{}{
        "type":      "device_data",
        "device_id": data.DeviceID,
        "timestamp": data.Timestamp,
        "data":      data.SensorData,
    }
    
    jsonData, _ := json.Marshal(message)
    manager.broadcast <- jsonData
}
```

### 5.2 Streamlit实时数据接收
```python
# 实时数据流组件
def realtime_data_stream():
    """实时数据流展示"""
    # 创建空白图表
    chart_placeholder = st.empty()
    metric_placeholder = st.empty()
    
    # WebSocket连接
    ws_client = WebSocketClient(WEBSOCKET_URL)
    
    # 数据缓存
    if 'realtime_buffer' not in st.session_state:
        st.session_state.realtime_buffer = deque(maxlen=100)
    
    # 实时更新循环
    while True:
        try:
            # 接收WebSocket数据
            data = ws_client.receive()
            st.session_state.realtime_buffer.append(data)
            
            # 更新图表
            df = pd.DataFrame(list(st.session_state.realtime_buffer))
            
            with chart_placeholder.container():
                fig = px.line(df, x='timestamp', y='value', 
                             title='实时数据监控')
                st.plotly_chart(fig, use_container_width=True)
            
            # 更新指标
            with metric_placeholder.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("当前值", f"{data['value']:.2f}", 
                             f"{data['change']:+.2f}")
                with col2:
                    st.metric("平均值", f"{df['value'].mean():.2f}")
                with col3:
                    st.metric("最大值", f"{df['value'].max():.2f}")
            
            time.sleep(1)
            
        except Exception as e:
            st.error(f"连接错误: {e}")
            time.sleep(5)
```

## 6. 性能优化策略

### 6.1 后端性能优化
- **连接池管理**：数据库连接池优化
- **缓存策略**：Redis多层缓存
- **异步处理**：耗时操作异步化
- **负载均衡**：支持水平扩展

### 6.2 前端性能优化
- **数据缓存**：Streamlit session state缓存
- **懒加载**：大数据集分页加载
- **图表优化**：Plotly性能调优
- **组件复用**：可复用组件设计

## 7. 部署和运维

### 7.1 容器化部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://backend:8080
    depends_on:
      - backend
  
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: iot_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 7.2 监控和日志
- **Prometheus + Grafana**：系统监控
- **ELK Stack**：日志聚合分析
- **健康检查**：服务可用性监控
- **告警机制**：故障自动通知

## 8. 开发路线图

### Phase 1: 基础架构 (4周)
- [x] Go Gin API框架搭建
- [x] PostgreSQL数据模型设计  
- [x] Streamlit基础界面
- [x] 用户认证系统

### Phase 2: 核心功能 (4周)
- [ ] 设备管理界面
- [ ] 实时数据展示
- [ ] 基础可视化图表
- [ ] 简单Fork功能

### Phase 3: 高级功能 (4周)
- [ ] 地图集成
- [ ] 高级图表类型
- [ ] 完整Fork功能
- [ ] 用户权限系统

### Phase 4: 优化部署 (4周)
- [ ] 性能优化
- [ ] UI/UX精细化
- [ ] 容器化部署
- [ ] 监控和日志

这个架构设计实现了从传统Web应用到现代数据科学平台的**根本性转变**，不仅提升了技术先进性，更重要的是提供了更好的用户体验和更强的扩展能力。