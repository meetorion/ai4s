# 🚀 农业物联网平台部署指南

## 📋 部署选项

### 1. 本地开发部署
```bash
# 基础版本
./run_demo.sh          # 端口: 8502

# 增强版本 (推荐)
./run_enhanced_demo.sh  # 端口: 8503
```

### 2. Streamlit Cloud 部署

#### 方法一：使用简化版本 (推荐用于云部署)
1. 在 Streamlit Cloud 中选择主文件为 `app.py`
2. 系统会自动读取 `requirements.txt` 安装依赖
3. 简化版本去除了复杂依赖，更适合云环境

#### 方法二：使用完整增强版本
1. 在 Streamlit Cloud 中选择主文件为 `agricultural_iot_enhanced.py`
2. 确保 `requirements.txt` 包含所有依赖
3. 需要上传 `data/` 目录的数据文件

## 📦 文件说明

### 部署相关文件
- `app.py` - Streamlit Cloud 优化版本
- `agricultural_iot_enhanced.py` - 本地增强版本
- `agricultural_iot_demo.py` - 原始基础版本
- `requirements.txt` - Python依赖文件
- `data_generator.py` - 数据生成器

### 数据文件 (可选)
- `data/devices.json` - 设备信息
- `data/current_data.json` - 实时数据
- `data/historical_data.csv` - 历史数据
- `data/sim_cards.json` - SIM卡信息
- `data/stats.json` - 统计信息

## 🔧 依赖说明

```txt
streamlit>=1.28.0      # Web应用框架
plotly>=5.15.0         # 交互式图表 (增强版需要)
pandas>=2.0.0          # 数据处理
folium>=0.14.0         # 地图组件 (增强版需要)
streamlit-folium>=0.13.0  # Streamlit地图集成 (增强版需要)
numpy>=1.24.0          # 数值计算
```

## 🌐 Streamlit Cloud 部署步骤

1. **连接GitHub仓库**
   - 访问 https://share.streamlit.io/
   - 连接到 GitHub 仓库 `meetorion/ai4s`

2. **配置部署**
   - 选择分支: `master`
   - 主文件路径: `app.py` (云部署推荐)
   - 或者: `agricultural_iot_enhanced.py` (完整功能)

3. **自动部署**
   - Streamlit Cloud 会自动读取 `requirements.txt`
   - 安装所需依赖并启动应用

## 📊 版本功能对比

| 特性 | app.py | agricultural_iot_enhanced.py | agricultural_iot_demo.py |
|------|--------|------------------------------|--------------------------|
| **部署环境** | Streamlit Cloud 优化 | 本地/服务器推荐 | 基础版本 |
| **依赖复杂度** | 简化 (仅pandas) | 完整 (plotly+folium) | 中等 |
| **设备数据** | 42台设备 | 42台设备+历史数据 | 少量模拟数据 |
| **交互式图表** | 简化显示 | Plotly专业图表 | 基础图表 |
| **地图功能** | 无 | Folium GIS地图 | 无 |
| **历史数据** | 无 | 6700+数据点 | 无 |
| **启动速度** | 快 | 中等 | 快 |

## 🎯 推荐部署方案

### 开发和演示环境
```bash
./run_enhanced_demo.sh  # 完整功能，本地8503端口
```

### 生产和云部署
- 使用 `app.py` 作为主文件
- 简化的依赖，更稳定的云部署
- 保持核心功能完整

### 自定义部署
- 可以根据需要修改 `app.py`
- 添加或删除特定功能模块
- 调整UI样式和数据展示

## 🔍 故障排除

### 常见问题

1. **ModuleNotFoundError**
   - 确保 `requirements.txt` 存在
   - 检查依赖版本兼容性
   - 使用 `app.py` 避免复杂依赖

2. **数据文件未找到**
   - 运行 `python data_generator.py` 生成数据
   - 或使用 `app.py` 的内置数据生成

3. **内存不足**
   - 使用简化版本 `app.py`
   - 减少历史数据量
   - 优化数据加载逻辑

## 📞 技术支持

- **GitHub仓库**: https://github.com/meetorion/ai4s
- **本地测试**: `streamlit run app.py`
- **数据重新生成**: `python data_generator.py`

---

🌱 **选择合适的部署方案，享受现代化农业物联网监控体验！**