"""
应用配置管理
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Settings:
    """应用设置类"""
    
    # API配置
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8080")
    API_VERSION: str = "v1"
    WEBSOCKET_URL: str = None
    
    # 前端配置
    PAGE_TITLE: str = "农业物联网可视化平台"
    PAGE_ICON: str = "🌱"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"
    
    # 数据刷新设置
    DEFAULT_REFRESH_INTERVAL: int = 5  # 秒
    MAX_REFRESH_INTERVAL: int = 60     # 秒
    MIN_REFRESH_INTERVAL: int = 1      # 秒
    
    # 缓存设置
    CACHE_TTL: int = 300  # 5分钟
    ENABLE_CACHE: bool = True
    
    # UI设置
    THEME_PRIMARY_COLOR: str = "#10B981"
    THEME_BACKGROUND_COLOR: str = "#F0FDF4"
    ENABLE_ANIMATIONS: bool = True
    
    # 数据限制
    MAX_CHART_POINTS: int = 1000
    MAX_TABLE_ROWS: int = 100
    MAX_HISTORY_DAYS: int = 30
    
    # 地图设置
    DEFAULT_MAP_CENTER: tuple = (39.9042, 116.4074)  # 北京
    DEFAULT_MAP_ZOOM: int = 10
    MAP_STYLE: str = "OpenStreetMap"
    
    # WebSocket设置
    WS_RECONNECT_INTERVAL: int = 5  # 秒
    WS_MAX_RECONNECT_ATTEMPTS: int = 10
    
    # 文件上传设置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = ['.csv', '.json', '.xlsx']
    
    # 分页设置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 调试设置
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    SHOW_DEBUG_INFO: bool = DEBUG
    
    def __post_init__(self):
        """初始化后处理"""
        # 构建WebSocket URL
        if not self.WEBSOCKET_URL:
            ws_protocol = "ws" if self.API_BASE_URL.startswith("http://") else "wss"
            ws_host = self.API_BASE_URL.replace("http://", "").replace("https://", "")
            self.WEBSOCKET_URL = f"{ws_protocol}://{ws_host}/api/{self.API_VERSION}/ws"
        
        # 构建完整的API URL
        if not self.API_BASE_URL.endswith("/"):
            self.API_BASE_URL += "/"
        self.API_URL = f"{self.API_BASE_URL}api/{self.API_VERSION}"
    
    @property
    def api_url(self) -> str:
        """获取API基础URL"""
        return self.API_URL
    
    @property
    def websocket_url(self) -> str:
        """获取WebSocket URL"""
        return self.WEBSOCKET_URL
    
    def get_device_type_names(self) -> dict:
        """获取设备类型名称映射"""
        return {
            1: "气象站",
            2: "土壤墒情",
            3: "水质监测", 
            4: "视频监控",
            5: "配电柜",
            6: "虫情监测",
            7: "孢子仪",
            8: "环境监测",
            9: "智能灌溉",
            10: "杀虫灯",
            11: "一体化闸门",
            12: "积水传感器",
            13: "植物生长记录仪"
        }
    
    def get_device_type_icons(self) -> dict:
        """获取设备类型图标"""
        return {
            1: "🌤️",   # 气象站
            2: "🌱",   # 土壤墒情
            3: "💧",   # 水质监测
            4: "📹",   # 视频监控
            5: "⚡",   # 配电柜
            6: "🐛",   # 虫情监测
            7: "🦠",   # 孢子仪
            8: "🌡️",   # 环境监测
            9: "💦",   # 智能灌溉
            10: "💡",  # 杀虫灯
            11: "🚪",  # 一体化闸门
            12: "🌊",  # 积水传感器
            13: "📊"   # 植物生长记录仪
        }
    
    def get_device_type_colors(self) -> dict:
        """获取设备类型颜色"""
        return {
            1: "#3B82F6",   # 蓝色
            2: "#10B981",   # 绿色
            3: "#06B6D4",   # 青色
            4: "#8B5CF6",   # 紫色
            5: "#F59E0B",   # 橙色
            6: "#EF4444",   # 红色
            7: "#84CC16",   # 浅绿色
            8: "#6366F1",   # 靛色
            9: "#14B8A6",   # 青绿色
            10: "#F97316",  # 深橙色
            11: "#64748B",  # 灰色
            12: "#0EA5E9",  # 天蓝色
            13: "#22C55E"   # 绿色
        }
    
    def get_chart_config(self) -> dict:
        """获取图表默认配置"""
        return {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': [
                'pan2d', 'lasso2d', 'select2d', 'autoScale2d',
                'hoverClosestCartesian', 'hoverCompareCartesian',
                'toggleSpikelines'
            ],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'iot_chart',
                'height': 600,
                'width': 1000,
                'scale': 2
            },
            'responsive': True
        }
    
    def get_map_config(self) -> dict:
        """获取地图默认配置"""
        return {
            'scrollWheelZoom': True,
            'doubleClickZoom': True,
            'dragging': True,
            'zoomControl': True,
            'attributionControl': True
        }
    
    def validate(self) -> bool:
        """验证设置"""
        try:
            # 验证URL格式
            if not self.API_BASE_URL.startswith(('http://', 'https://')):
                raise ValueError("API_BASE_URL must start with http:// or https://")
            
            # 验证数值范围
            if not (self.MIN_REFRESH_INTERVAL <= self.DEFAULT_REFRESH_INTERVAL <= self.MAX_REFRESH_INTERVAL):
                raise ValueError("Invalid refresh interval range")
            
            if self.MAX_CHART_POINTS <= 0:
                raise ValueError("MAX_CHART_POINTS must be positive")
            
            if self.CACHE_TTL <= 0:
                raise ValueError("CACHE_TTL must be positive")
            
            return True
            
        except Exception as e:
            print(f"Settings validation error: {e}")
            return False

# 创建全局设置实例
settings = Settings()

# 验证设置
if not settings.validate():
    raise ValueError("Invalid application settings")

# 导出设置
__all__ = ['Settings', 'settings']