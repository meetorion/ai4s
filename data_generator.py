#!/usr/bin/env python3
"""
农业物联网平台 - 数据生成器
生成真实的农业设备数据用于演示
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random
import os

class AgricultureDataGenerator:
    def __init__(self):
        # 13种设备类型及其详细配置
        self.device_types = {
            "气象站": {
                "icon": "🌤️",
                "count": 3,
                "parameters": {
                    "temperature": {"range": [15, 35], "unit": "°C", "name": "温度"},
                    "humidity": {"range": [40, 85], "unit": "%", "name": "湿度"},
                    "wind_speed": {"range": [0, 8], "unit": "m/s", "name": "风速"},
                    "pressure": {"range": [1000, 1030], "unit": "hPa", "name": "气压"},
                    "rainfall": {"range": [0, 15], "unit": "mm", "name": "降雨量"}
                }
            },
            "土壤墒情": {
                "icon": "🌱",
                "count": 5,
                "parameters": {
                    "soil_temp": {"range": [12, 28], "unit": "°C", "name": "土壤温度"},
                    "soil_humidity": {"range": [25, 75], "unit": "%", "name": "土壤湿度"},
                    "soil_ph": {"range": [6.0, 8.0], "unit": "pH", "name": "土壤pH值"},
                    "ec": {"range": [0.8, 2.5], "unit": "mS/cm", "name": "电导率"},
                    "n_content": {"range": [80, 150], "unit": "mg/kg", "name": "氮含量"}
                }
            },
            "水质监测": {
                "icon": "💧",
                "count": 1,
                "device_id": "865989071557605",
                "parameters": {
                    "ph": {"range": [6.8, 7.2], "unit": "pH", "name": "pH值"},
                    "turbidity": {"range": [15, 25], "unit": "NTU", "name": "浊度"},
                    "dissolved_oxygen": {"range": [6.5, 8.5], "unit": "mg/L", "name": "溶解氧"},
                    "water_temp": {"range": [18, 25], "unit": "°C", "name": "水温"},
                    "conductivity": {"range": [180, 220], "unit": "μS/cm", "name": "电导率"}
                }
            },
            "视频监控": {
                "icon": "📹",
                "count": 4,
                "parameters": {
                    "online_status": {"range": [0, 1], "unit": "", "name": "在线状态"},
                    "resolution": {"values": ["1080P", "720P", "4K"], "name": "分辨率"},
                    "storage_usage": {"range": [20, 80], "unit": "%", "name": "存储使用率"}
                }
            },
            "配电柜": {
                "icon": "⚡",
                "count": 2,
                "parameters": {
                    "voltage": {"range": [220, 240], "unit": "V", "name": "电压"},
                    "current": {"range": [8, 25], "unit": "A", "name": "电流"},
                    "power": {"range": [1.5, 6.0], "unit": "kW", "name": "功率"},
                    "frequency": {"range": [49.8, 50.2], "unit": "Hz", "name": "频率"}
                }
            },
            "虫情监测": {
                "icon": "🐛",
                "count": 3,
                "parameters": {
                    "pest_count": {"range": [0, 50], "unit": "只", "name": "害虫数量"},
                    "trap_temp": {"range": [20, 35], "unit": "°C", "name": "诱捕器温度"},
                    "light_intensity": {"range": [0, 100], "unit": "%", "name": "灯光强度"}
                }
            },
            "孢子仪": {
                "icon": "🦠",
                "count": 2,
                "parameters": {
                    "spore_count": {"range": [100, 2000], "unit": "个/m³", "name": "孢子浓度"},
                    "analysis_temp": {"range": [25, 30], "unit": "°C", "name": "分析温度"},
                    "sample_volume": {"range": [10, 100], "unit": "L", "name": "采样体积"}
                }
            },
            "环境监测": {
                "icon": "🌡️",
                "count": 4,
                "parameters": {
                    "ambient_temp": {"range": [18, 32], "unit": "°C", "name": "环境温度"},
                    "ambient_humidity": {"range": [45, 80], "unit": "%", "name": "环境湿度"},
                    "co2": {"range": [400, 800], "unit": "ppm", "name": "CO2浓度"},
                    "light_intensity": {"range": [20000, 80000], "unit": "lux", "name": "光照强度"}
                }
            },
            "智能灌溉": {
                "icon": "💦",
                "count": 6,
                "parameters": {
                    "flow_rate": {"range": [2, 15], "unit": "L/min", "name": "流量"},
                    "pressure": {"range": [0.2, 0.8], "unit": "MPa", "name": "水压"},
                    "valve_status": {"values": ["开启", "关闭"], "name": "阀门状态"},
                    "water_level": {"range": [30, 95], "unit": "%", "name": "水位"}
                }
            },
            "杀虫灯": {
                "icon": "💡",
                "count": 4,
                "parameters": {
                    "power_consumption": {"range": [15, 30], "unit": "W", "name": "功耗"},
                    "working_hours": {"range": [6, 12], "unit": "h", "name": "工作时长"},
                    "killed_insects": {"range": [50, 300], "unit": "只", "name": "灭虫数量"}
                }
            },
            "一体化闸门": {
                "icon": "🚪",
                "count": 2,
                "parameters": {
                    "gate_opening": {"range": [0, 100], "unit": "%", "name": "闸门开度"},
                    "water_flow": {"range": [0, 500], "unit": "m³/h", "name": "过水流量"},
                    "upstream_level": {"range": [2.0, 4.5], "unit": "m", "name": "上游水位"},
                    "downstream_level": {"range": [1.5, 4.0], "unit": "m", "name": "下游水位"}
                }
            },
            "积水传感器": {
                "icon": "🌊",
                "count": 3,
                "parameters": {
                    "water_depth": {"range": [0, 80], "unit": "cm", "name": "积水深度"},
                    "alert_level": {"values": ["正常", "警告", "危险"], "name": "预警等级"},
                    "drain_status": {"values": ["畅通", "堵塞"], "name": "排水状态"}
                }
            },
            "植物生长记录仪": {
                "icon": "📊",
                "count": 3,
                "parameters": {
                    "plant_height": {"range": [15, 120], "unit": "cm", "name": "植株高度"},
                    "leaf_area": {"range": [50, 200], "unit": "cm²", "name": "叶面积"},
                    "growth_rate": {"range": [0.5, 3.0], "unit": "cm/day", "name": "生长速率"},
                    "chlorophyll": {"range": [30, 60], "unit": "SPAD", "name": "叶绿素含量"}
                }
            }
        }
        
        # 地理位置配置 (国科大深圳先进技术研究院)
        self.base_location = {"lat": 22.59163, "lng": 113.972654}  # 深圳大学城
        self.location_spread = 0.01  # 位置散布范围 (约1km半径，适合研究院规模)
        
    def generate_device_list(self):
        """生成所有设备列表"""
        devices = []
        device_id = 1001
        
        for device_type, config in self.device_types.items():
            for i in range(config["count"]):
                # 特殊处理水质监测设备ID
                if device_type == "水质监测":
                    dev_id = config["device_id"]
                else:
                    dev_id = f"{device_id:012d}"
                
                device = {
                    "device_id": dev_id,
                    "device_name": f"{config['icon']} {device_type}-{i+1:02d}",
                    "device_type": device_type,
                    "icon": config["icon"],
                    "location": {
                        "lat": self.base_location["lat"] + random.uniform(-self.location_spread, self.location_spread),
                        "lng": self.base_location["lng"] + random.uniform(-self.location_spread, self.location_spread)
                    },
                    "status": random.choice(["在线", "在线", "在线", "离线"]),  # 80%在线率
                    "install_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
                    "last_update": (datetime.now() - timedelta(minutes=random.randint(1, 30))).isoformat(),
                    "parameters": config["parameters"]
                }
                
                devices.append(device)
                device_id += 1
                
        return devices
    
    def generate_current_data(self, devices):
        """生成当前实时数据"""
        current_data = {}
        
        for device in devices:
            device_id = device["device_id"]
            if device["status"] == "离线":
                continue
                
            data = {"timestamp": datetime.now().isoformat()}
            
            for param, config in device["parameters"].items():
                if "range" in config:
                    # 数值型参数
                    min_val, max_val = config["range"]
                    if device["device_type"] == "水质监测":
                        # 水质数据添加轻微波动
                        base_val = (min_val + max_val) / 2
                        variation = (max_val - min_val) * 0.1
                        value = base_val + random.uniform(-variation, variation)
                    else:
                        value = random.uniform(min_val, max_val)
                    
                    data[param] = round(value, 2)
                elif "values" in config:
                    # 枚举型参数
                    data[param] = random.choice(config["values"])
            
            current_data[device_id] = data
        
        return current_data
    
    def generate_historical_data(self, devices, days=7):
        """生成历史数据"""
        historical_data = []
        
        # 生成时间序列
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # 每小时生成一条数据
        current_time = start_time
        while current_time <= end_time:
            for device in devices:
                if random.random() > 0.95:  # 5%的数据缺失率
                    continue
                    
                record = {
                    "device_id": device["device_id"],
                    "device_type": device["device_type"],
                    "timestamp": current_time.isoformat(),
                }
                
                # 生成参数数据
                for param, config in device["parameters"].items():
                    if "range" in config:
                        min_val, max_val = config["range"]
                        
                        # 添加时间趋势和季节性
                        hour = current_time.hour
                        day_factor = np.sin(2 * np.pi * hour / 24)  # 日周期
                        
                        if param in ["temperature", "ambient_temp", "soil_temp"]:
                            # 温度有明显的日周期
                            base_val = (min_val + max_val) / 2
                            amplitude = (max_val - min_val) * 0.3
                            value = base_val + amplitude * day_factor + random.uniform(-2, 2)
                        elif param in ["humidity", "soil_humidity", "ambient_humidity"]:
                            # 湿度与温度反相关
                            base_val = (min_val + max_val) / 2
                            amplitude = (max_val - min_val) * 0.2
                            value = base_val - amplitude * day_factor + random.uniform(-5, 5)
                        else:
                            # 其他参数正常波动
                            value = random.uniform(min_val, max_val)
                        
                        record[param] = round(max(min_val, min(max_val, value)), 2)
                    elif "values" in config:
                        record[param] = random.choice(config["values"])
                
                historical_data.append(record)
            
            current_time += timedelta(hours=1)
        
        return historical_data
    
    def generate_sim_card_data(self):
        """生成物联网卡数据"""
        operators = ["中国移动", "中国联通", "中国电信"]
        card_data = []
        
        for i in range(25):  # 25张SIM卡
            total_data = random.randint(500, 2000)  # MB
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
            
            card_data.append(card)
        
        return card_data
    
    def save_data(self, output_dir="data"):
        """保存所有生成的数据到文件"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成设备列表
        devices = self.generate_device_list()
        with open(f"{output_dir}/devices.json", "w", encoding="utf-8") as f:
            json.dump(devices, f, ensure_ascii=False, indent=2)
        
        # 生成当前数据
        current_data = self.generate_current_data(devices)
        with open(f"{output_dir}/current_data.json", "w", encoding="utf-8") as f:
            json.dump(current_data, f, ensure_ascii=False, indent=2)
        
        # 生成历史数据
        historical_data = self.generate_historical_data(devices)
        df_historical = pd.DataFrame(historical_data)
        df_historical.to_csv(f"{output_dir}/historical_data.csv", index=False, encoding="utf-8")
        
        # 生成SIM卡数据
        sim_card_data = self.generate_sim_card_data()
        with open(f"{output_dir}/sim_cards.json", "w", encoding="utf-8") as f:
            json.dump(sim_card_data, f, ensure_ascii=False, indent=2)
        
        # 生成统计数据
        stats = {
            "total_devices": len(devices),
            "online_devices": len([d for d in devices if d["status"] == "在线"]),
            "device_types": len(self.device_types),
            "data_points": len(historical_data),
            "sim_cards": len(sim_card_data),
            "last_update": datetime.now().isoformat()
        }
        
        with open(f"{output_dir}/stats.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        return devices, current_data, historical_data, sim_card_data, stats

if __name__ == "__main__":
    print("🌱 生成农业物联网演示数据...")
    
    generator = AgricultureDataGenerator()
    devices, current_data, historical_data, sim_card_data, stats = generator.save_data()
    
    print(f"✅ 数据生成完成！")
    print(f"📊 设备总数: {stats['total_devices']}")
    print(f"🟢 在线设备: {stats['online_devices']}")
    print(f"📈 历史数据点: {stats['data_points']}")
    print(f"📱 SIM卡数量: {stats['sim_cards']}")
    print(f"📂 数据保存至: data/ 目录")