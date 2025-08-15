#!/usr/bin/env python3
"""
创建系统演示预览
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_system_architecture():
    """创建系统架构图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 设置背景色
    ax.set_facecolor('#f8f9fa')
    
    # 前端层
    frontend_rect = patches.Rectangle((1, 7), 12, 2, linewidth=2, 
                                    edgecolor='#10B981', facecolor='#D1FAE5', alpha=0.7)
    ax.add_patch(frontend_rect)
    ax.text(7, 8, '🌱 Streamlit 前端界面\n数据可视化 | Fork管理 | 实时监控', 
            ha='center', va='center', fontsize=12, weight='bold')
    
    # API层
    api_rect = patches.Rectangle((1, 4.5), 12, 2, linewidth=2, 
                               edgecolor='#3B82F6', facecolor='#DBEAFE', alpha=0.7)
    ax.add_patch(api_rect)
    ax.text(7, 5.5, '⚡ Go Gin API 后端\nRESTful API | JWT认证 | WebSocket实时推送', 
            ha='center', va='center', fontsize=12, weight='bold')
    
    # 数据层
    data_rect = patches.Rectangle((1, 2), 5.5, 2, linewidth=2, 
                                edgecolor='#8B5CF6', facecolor='#EDE9FE', alpha=0.7)
    ax.add_patch(data_rect)
    ax.text(3.75, 3, '🗄️ PostgreSQL\n设备数据 | 用户信息\n项目配置', 
            ha='center', va='center', fontsize=10, weight='bold')
    
    cache_rect = patches.Rectangle((7.5, 2), 5.5, 2, linewidth=2, 
                                 edgecolor='#EF4444', facecolor='#FEE2E2', alpha=0.7)
    ax.add_patch(cache_rect)
    ax.text(10.25, 3, '⚡ Redis 缓存\n实时数据缓存\n会话管理', 
            ha='center', va='center', fontsize=10, weight='bold')
    
    # IoT设备层
    iot_rect = patches.Rectangle((1, 0), 12, 1.5, linewidth=2, 
                               edgecolor='#F59E0B', facecolor='#FEF3C7', alpha=0.7)
    ax.add_patch(iot_rect)
    ax.text(7, 0.75, '🏭 IoT 设备层\n13种农业设备 | 实时数据采集 | 状态监控', 
            ha='center', va='center', fontsize=12, weight='bold')
    
    # 连接线
    # 前端到API
    ax.arrow(7, 7, 0, -0.4, head_width=0.2, head_length=0.1, fc='gray', ec='gray')
    # API到数据库
    ax.arrow(5, 4.5, -1, -0.4, head_width=0.2, head_length=0.1, fc='gray', ec='gray')
    # API到Redis
    ax.arrow(9, 4.5, 1, -0.4, head_width=0.2, head_length=0.1, fc='gray', ec='gray')
    # API到IoT
    ax.arrow(7, 4.5, 0, -2.9, head_width=0.2, head_length=0.1, fc='gray', ec='gray')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(-0.5, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('🌱 农业物联网可视化平台 v2.0 - 系统架构', fontsize=16, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/home/arc/work/ai4s/system_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_feature_comparison():
    """创建功能对比图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 原系统
    ax1.set_title('🏢 原 Java 系统', fontsize=14, weight='bold', color='#6B7280')
    features_old = ['静态仪表板', '轮询更新', 'ECharts图表', '单用户模式', '重型架构']
    scores_old = [6, 5, 7, 6, 5]
    colors_old = ['#DC2626', '#F59E0B', '#10B981', '#F59E0B', '#DC2626']
    
    bars1 = ax1.barh(features_old, scores_old, color=colors_old, alpha=0.7)
    ax1.set_xlim(0, 10)
    ax1.set_xlabel('功能评分', fontsize=10)
    
    for i, (bar, score) in enumerate(zip(bars1, scores_old)):
        ax1.text(score + 0.1, i, f'{score}/10', va='center', fontsize=10, weight='bold')
    
    # 新系统
    ax2.set_title('🚀 新 Go+Streamlit 系统', fontsize=14, weight='bold', color='#10B981')
    features_new = ['动态可视化', 'WebSocket实时', 'Plotly交互', 'Fork协作', '云原生架构']
    scores_new = [9, 10, 9, 10, 9]
    colors_new = ['#10B981', '#10B981', '#10B981', '#10B981', '#10B981']
    
    bars2 = ax2.barh(features_new, scores_new, color=colors_new, alpha=0.7)
    ax2.set_xlim(0, 10)
    ax2.set_xlabel('功能评分', fontsize=10)
    
    for i, (bar, score) in enumerate(zip(bars2, scores_new)):
        ax2.text(score + 0.1, i, f'{score}/10', va='center', fontsize=10, weight='bold')
    
    plt.suptitle('🔄 系统功能对比', fontsize=16, weight='bold')
    plt.tight_layout()
    plt.savefig('/home/arc/work/ai4s/feature_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_fork_workflow():
    """创建Fork工作流程图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 步骤框
    steps = [
        ('1. 发现项目', '浏览公开项目库\n找到有用的配置', (2, 8)),
        ('2. 点击Fork', '创建项目副本\n保留原始配置', (7, 8)),
        ('3. 自定义配置', '修改可视化设置\n适配个人需求', (12, 8)),
        ('4. 版本管理', '记录配置变更\n追踪修改历史', (2, 4)),
        ('5. 分享协作', '公开Fork项目\n提交合并请求', (7, 4)),
        ('6. 持续改进', '社区反馈\n迭代优化', (12, 4))
    ]
    
    colors = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EF4444', '#06B6D4']
    
    for i, (title, desc, (x, y)) in enumerate(steps):
        # 绘制步骤框
        rect = patches.Rectangle((x-1.5, y-1), 3, 2, linewidth=2, 
                               edgecolor=colors[i], facecolor=colors[i], alpha=0.2)
        ax.add_patch(rect)
        
        # 步骤标题
        ax.text(x, y+0.3, title, ha='center', va='center', fontsize=11, 
                weight='bold', color=colors[i])
        
        # 步骤描述
        ax.text(x, y-0.3, desc, ha='center', va='center', fontsize=9)
        
        # 连接箭头
        if i < len(steps) - 1:
            next_x, next_y = steps[i+1][2]
            if y == next_y:  # 同一行
                ax.arrow(x+1.5, y, next_x-x-3, 0, head_width=0.2, head_length=0.3, 
                        fc=colors[i], ec=colors[i], alpha=0.7)
            else:  # 换行
                # 先向下
                ax.arrow(x, y-1, 0, -1.5, head_width=0.2, head_length=0.3, 
                        fc=colors[i], ec=colors[i], alpha=0.7)
    
    # 中央Fork图标
    fork_rect = patches.Circle((7, 6), 1, linewidth=3, 
                             edgecolor='#10B981', facecolor='#D1FAE5', alpha=0.8)
    ax.add_patch(fork_rect)
    ax.text(7, 6, '🔄\nFork', ha='center', va='center', fontsize=16, weight='bold')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(2, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('🔄 Fork 功能工作流程', fontsize=16, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/home/arc/work/ai4s/fork_workflow.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_device_overview():
    """创建设备概览图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # 设备类型数据
    device_types = [
        '🌤️ 气象站', '🌱 土壤墒情', '💧 水质监测', '📹 视频监控',
        '⚡ 配电柜', '🐛 虫情监测', '🦠 孢子仪', '🌡️ 环境监测',
        '💦 智能灌溉', '💡 杀虫灯', '🚪 一体化闸门', '🌊 积水传感器', '📊 植物生长记录仪'
    ]
    
    # 模拟设备数量
    np.random.seed(42)
    counts = np.random.randint(0, 10, len(device_types))
    counts[2] = 1  # 水质监测设备设为1，与演示数据一致
    
    # 创建饼图
    colors = plt.cm.Set3(np.linspace(0, 1, len(device_types)))
    wedges, texts, autotexts = ax.pie(counts, labels=device_types, colors=colors,
                                     autopct=lambda pct: f'{pct:.1f}%' if pct > 0 else '',
                                     startangle=90)
    
    # 设置文本样式
    for text in texts:
        text.set_fontsize(9)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')
        autotext.set_fontsize(8)
    
    ax.set_title('🏭 支持的IoT设备类型分布', fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/home/arc/work/ai4s/device_overview.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("🎨 创建系统演示图片...")
    
    # 创建各种图表
    create_system_architecture()
    print("✅ 系统架构图已生成")
    
    create_feature_comparison()
    print("✅ 功能对比图已生成")
    
    create_fork_workflow()
    print("✅ Fork工作流程图已生成")
    
    create_device_overview()
    print("✅ 设备概览图已生成")
    
    print(f"\n🎉 所有演示图片已生成完成！")
    print("📂 图片保存位置: /home/arc/work/ai4s/")
    print("📋 生成的文件:")
    print("  - system_architecture.png  (系统架构图)")
    print("  - feature_comparison.png   (功能对比图)")
    print("  - fork_workflow.png        (Fork工作流程图)")
    print("  - device_overview.png      (设备概览图)")