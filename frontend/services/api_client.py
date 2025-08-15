"""
API客户端 - 处理与后端Go Gin API的通信
"""

import requests
import streamlit as st
from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime, timedelta
import time

class APIClient:
    """API客户端类"""
    
    def __init__(self, base_url: str):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"
        self.session = requests.Session()
        self.timeout = 30
        
        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def set_auth_token(self, token: str):
        """设置认证令牌"""
        if token:
            self.session.headers['Authorization'] = f'Bearer {token}'
        else:
            self.session.headers.pop('Authorization', None)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发送HTTP请求的通用方法
        
        Args:
            method: HTTP方法
            endpoint: API端点
            **kwargs: 其他请求参数
            
        Returns:
            API响应数据
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # 检查响应状态
            if response.status_code == 401:
                # 认证失败，清除token
                self.set_auth_token(None)
                if 'authenticated' in st.session_state:
                    st.session_state.authenticated = False
                raise requests.exceptions.HTTPError("认证失败，请重新登录")
            
            response.raise_for_status()
            
            # 解析JSON响应
            try:
                return response.json()
            except json.JSONDecodeError:
                return {'status': 1, 'data': response.text}
                
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError("无法连接到服务器，请检查网络连接")
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout("请求超时，请稍后重试")
        except requests.exceptions.HTTPError as e:
            # 尝试解析错误响应
            try:
                error_data = response.json()
                error_msg = error_data.get('error', str(e))
            except:
                error_msg = str(e)
            raise requests.exceptions.HTTPError(f"HTTP错误 ({response.status_code}): {error_msg}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET请求"""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST请求"""
        return self._make_request('POST', endpoint, json=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT请求"""
        return self._make_request('PUT', endpoint, json=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE请求"""
        return self._make_request('DELETE', endpoint)
    
    # 认证相关API
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        data = {
            'username': username,
            'password': password
        }
        
        response = self.post('auth/login', data)
        
        # 登录成功后设置token
        if response.get('status') == 1 and 'data' in response:
            token = response['data'].get('access_token')
            if token:
                self.set_auth_token(token)
        
        return response
    
    def logout(self) -> Dict[str, Any]:
        """用户登出"""
        try:
            response = self.post('auth/logout')
        except:
            # 即使后端登出失败，也要清除本地token
            response = {'status': 1, 'msg': '已退出登录'}
        
        # 清除token
        self.set_auth_token(None)
        return response
    
    def get_user_info(self) -> Dict[str, Any]:
        """获取当前用户信息"""
        return self.get('auth/me')
    
    def change_password(self, current_password: str, new_password: str) -> Dict[str, Any]:
        """修改密码"""
        data = {
            'current_password': current_password,
            'new_password': new_password
        }
        return self.put('auth/password', data)
    
    # 设备相关API
    def get_devices(self, page: int = 1, limit: int = 20, **filters) -> Dict[str, Any]:
        """获取设备列表"""
        params = {
            'page': page,
            'limit': limit,
            **filters
        }
        return self.get('devices', params)
    
    def get_device(self, device_id: int) -> Dict[str, Any]:
        """获取设备详情"""
        return self.get(f'devices/{device_id}')
    
    def create_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建设备"""
        return self.post('devices', device_data)
    
    def update_device(self, device_id: int, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新设备"""
        return self.put(f'devices/{device_id}', device_data)
    
    def delete_device(self, device_id: int) -> Dict[str, Any]:
        """删除设备"""
        return self.delete(f'devices/{device_id}')
    
    def get_device_types(self) -> Dict[str, Any]:
        """获取设备类型列表"""
        return self.get('devices/types')
    
    def get_device_stats(self) -> Dict[str, Any]:
        """获取设备统计信息"""
        return self.get('devices/stats')
    
    def get_device_data(self, device_id: str) -> Dict[str, Any]:
        """获取设备实时数据"""
        return self.get(f'devices/{device_id}/data')
    
    def get_device_history(self, device_id: str, start_time: Optional[str] = None, 
                          end_time: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """获取设备历史数据"""
        params = {'limit': limit}
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        
        return self.get(f'devices/{device_id}/history', params)
    
    # 项目相关API
    def get_projects(self, page: int = 1, limit: int = 20, **filters) -> Dict[str, Any]:
        """获取项目列表"""
        params = {
            'page': page,
            'limit': limit,
            **filters
        }
        return self.get('projects', params)
    
    def get_project(self, project_id: int) -> Dict[str, Any]:
        """获取项目详情"""
        return self.get(f'projects/{project_id}')
    
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建项目"""
        return self.post('projects', project_data)
    
    def update_project(self, project_id: int, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新项目"""
        return self.put(f'projects/{project_id}', project_data)
    
    def delete_project(self, project_id: int) -> Dict[str, Any]:
        """删除项目"""
        return self.delete(f'projects/{project_id}')
    
    def fork_project(self, project_id: int, fork_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fork项目"""
        return self.post(f'projects/{project_id}/fork', fork_data)
    
    def star_project(self, project_id: int) -> Dict[str, Any]:
        """给项目点赞/取消点赞"""
        return self.post(f'projects/{project_id}/star')
    
    def get_project_history(self, project_id: int) -> Dict[str, Any]:
        """获取项目历史记录"""
        return self.get(f'projects/{project_id}/history')
    
    # 公开API
    def get_public_projects(self) -> Dict[str, Any]:
        """获取公开项目列表"""
        return self.get('public/projects')
    
    def get_public_stats(self) -> Dict[str, Any]:
        """获取公开统计信息"""
        return self.get('public/stats')
    
    # 健康检查
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    # 数据处理辅助方法
    def get_device_realtime_data(self, device_ids: List[str], max_points: int = 100) -> Dict[str, Any]:
        """获取多个设备的实时数据"""
        data = {}
        
        for device_id in device_ids:
            try:
                response = self.get_device_data(device_id)
                if response.get('status') == 1 and response.get('data'):
                    data[device_id] = response['data']
            except Exception as e:
                st.warning(f"获取设备 {device_id} 数据失败: {e}")
                continue
        
        return data
    
    def get_device_history_range(self, device_id: str, days: int = 7) -> Dict[str, Any]:
        """获取设备指定天数的历史数据"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        return self.get_device_history(
            device_id=device_id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            limit=1000
        )
    
    def batch_get_device_stats(self, device_ids: List[str]) -> Dict[str, Any]:
        """批量获取设备统计信息"""
        stats = {}
        
        for device_id in device_ids:
            try:
                # 获取设备基本信息
                device_info = self.get_device(device_id)
                if device_info.get('status') == 1:
                    device_data = device_info['data']
                    
                    # 获取最新数据
                    latest_data = self.get_device_data(device_data['device_id'])
                    
                    stats[device_id] = {
                        'device': device_data,
                        'latest_data': latest_data.get('data') if latest_data.get('status') == 1 else None,
                        'status': device_data.get('status', 'unknown'),
                        'last_seen': device_data.get('last_seen')
                    }
            except Exception as e:
                st.error(f"获取设备 {device_id} 统计信息失败: {e}")
                continue
        
        return stats

# 创建全局API客户端实例（用于缓存）
@st.cache_resource
def get_api_client(base_url: str) -> APIClient:
    """获取API客户端实例（缓存）"""
    return APIClient(base_url)