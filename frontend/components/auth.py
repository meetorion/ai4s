"""
认证组件 - 处理用户登录、注册等认证功能
"""

import streamlit as st
import time
from typing import Optional, Dict, Any
from services.api_client import APIClient

class AuthManager:
    """认证管理器"""
    
    def __init__(self, api_client: APIClient):
        """初始化认证管理器"""
        self.api_client = api_client
    
    def render_login_page(self):
        """渲染登录页面"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1>🌱 农业物联网可视化平台</h1>
            <p style="color: #6B7280; font-size: 1.1rem;">现代化IoT数据分析与可视化系统</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 创建居中的登录表单
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            self._render_login_form()
    
    def _render_login_form(self):
        """渲染登录表单"""
        # 创建选项卡
        tab1, tab2 = st.tabs(["登录", "注册"])
        
        with tab1:
            self._render_login_tab()
        
        with tab2:
            self._render_register_tab()
    
    def _render_login_tab(self):
        """渲染登录标签页"""
        st.markdown("### 用户登录")
        
        with st.form("login_form", clear_on_submit=False):
            # 用户名/邮箱/手机号
            username = st.text_input(
                "用户名/邮箱/手机号",
                placeholder="请输入用户名、邮箱或手机号",
                help="支持使用用户名、邮箱或手机号登录"
            )
            
            # 密码
            password = st.text_input(
                "密码",
                type="password",
                placeholder="请输入密码"
            )
            
            # 记住我
            remember_me = st.checkbox("记住登录状态", value=True)
            
            # 登录按钮
            col1, col2 = st.columns([1, 1])
            
            with col1:
                login_clicked = st.form_submit_button(
                    "登录",
                    use_container_width=True,
                    type="primary"
                )
            
            with col2:
                demo_clicked = st.form_submit_button(
                    "演示账号登录",
                    use_container_width=True
                )
        
        # 处理登录
        if login_clicked or demo_clicked:
            if demo_clicked:
                # 使用演示账号
                username = "18823870097"
                password = "yaohongming"
            
            self._handle_login(username, password, remember_me)
        
        # 显示提示信息
        st.markdown("""
        <div style="margin-top: 2rem; padding: 1rem; background: #F0FDF4; border: 1px solid #D1FAE5; border-radius: 8px;">
            <h4 style="color: #065F46; margin-bottom: 0.5rem;">演示账号</h4>
            <p style="color: #047857; margin: 0;">
                用户名：<code>18823870097</code><br>
                密码：<code>yaohongming</code>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_register_tab(self):
        """渲染注册标签页"""
        st.markdown("### 用户注册")
        
        with st.form("register_form", clear_on_submit=False):
            # 用户名
            username = st.text_input(
                "用户名 *",
                placeholder="请输入用户名（3-50个字符）",
                help="用户名将用于登录，支持字母、数字、下划线"
            )
            
            # 邮箱
            email = st.text_input(
                "邮箱",
                placeholder="请输入邮箱地址（可选）",
                help="用于找回密码和接收通知"
            )
            
            # 手机号
            phone = st.text_input(
                "手机号",
                placeholder="请输入手机号（可选）",
                help="用于登录和接收短信通知"
            )
            
            # 密码
            password = st.text_input(
                "密码 *",
                type="password",
                placeholder="请输入密码（至少6个字符）",
                help="密码长度至少6个字符，建议包含字母和数字"
            )
            
            # 确认密码
            confirm_password = st.text_input(
                "确认密码 *",
                type="password",
                placeholder="请再次输入密码"
            )
            
            # 同意条款
            agree_terms = st.checkbox(
                "我已阅读并同意《用户协议》和《隐私政策》",
                help="注册即表示同意相关条款"
            )
            
            # 注册按钮
            register_clicked = st.form_submit_button(
                "注册",
                use_container_width=True,
                type="primary"
            )
        
        # 处理注册
        if register_clicked:
            self._handle_register(username, email, phone, password, confirm_password, agree_terms)
    
    def _handle_login(self, username: str, password: str, remember_me: bool = True):
        """处理用户登录"""
        # 验证输入
        if not username or not password:
            st.error("请输入用户名和密码")
            return
        
        try:
            with st.spinner("正在登录..."):
                # 调用登录API
                response = self.api_client.login(username, password)
                
                if response.get('status') == 1:
                    # 登录成功
                    user_data = response['data']
                    
                    # 保存用户信息到会话状态
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_data['user']
                    st.session_state.access_token = user_data['access_token']
                    
                    # 显示成功消息
                    st.success(f"欢迎回来，{user_data['user']['username']}！")
                    
                    # 记住登录状态
                    if remember_me:
                        # 这里可以实现持久化存储
                        pass
                    
                    # 延迟后刷新页面
                    time.sleep(1)
                    st.rerun()
                    
                else:
                    # 登录失败
                    error_msg = response.get('error', '登录失败')
                    st.error(f"登录失败：{error_msg}")
                    
        except Exception as e:
            st.error(f"登录时发生错误：{str(e)}")
    
    def _handle_register(self, username: str, email: str, phone: str, 
                        password: str, confirm_password: str, agree_terms: bool):
        """处理用户注册"""
        # 验证输入
        if not self._validate_register_input(username, email, phone, password, confirm_password, agree_terms):
            return
        
        try:
            with st.spinner("正在注册..."):
                # 准备注册数据
                register_data = {
                    'username': username,
                    'password': password
                }
                
                if email:
                    register_data['email'] = email
                if phone:
                    register_data['phone'] = phone
                
                # 调用注册API
                response = self.api_client.post('auth/register', register_data)
                
                if response.get('status') == 1:
                    # 注册成功
                    st.success("注册成功！请使用新账号登录。")
                    
                    # 切换到登录标签页（这里可以通过session state实现）
                    time.sleep(2)
                    st.rerun()
                    
                else:
                    # 注册失败
                    error_msg = response.get('error', '注册失败')
                    st.error(f"注册失败：{error_msg}")
                    
        except Exception as e:
            st.error(f"注册时发生错误：{str(e)}")
    
    def _validate_register_input(self, username: str, email: str, phone: str,
                                password: str, confirm_password: str, agree_terms: bool) -> bool:
        """验证注册输入"""
        # 检查必填字段
        if not username:
            st.error("请输入用户名")
            return False
        
        if not password:
            st.error("请输入密码")
            return False
        
        if not agree_terms:
            st.error("请同意用户协议和隐私政策")
            return False
        
        # 检查用户名长度
        if len(username) < 3 or len(username) > 50:
            st.error("用户名长度应为3-50个字符")
            return False
        
        # 检查密码长度
        if len(password) < 6:
            st.error("密码长度至少为6个字符")
            return False
        
        # 检查密码确认
        if password != confirm_password:
            st.error("两次输入的密码不一致")
            return False
        
        # 检查邮箱格式
        if email and '@' not in email:
            st.error("邮箱格式不正确")
            return False
        
        # 检查手机号格式（简单验证）
        if phone and (not phone.isdigit() or len(phone) != 11):
            st.error("手机号格式不正确")
            return False
        
        return True
    
    def check_authentication(self) -> bool:
        """检查用户是否已认证"""
        if not st.session_state.get('authenticated', False):
            return False
        
        # 检查token是否存在
        token = st.session_state.get('access_token')
        if not token:
            return False
        
        # 设置API客户端的token
        self.api_client.set_auth_token(token)
        
        # 可以在这里添加token有效性检查
        try:
            user_info = self.api_client.get_user_info()
            if user_info.get('status') == 1:
                # 更新用户信息
                st.session_state.user_info = user_info['data']
                return True
            else:
                # Token无效，清除认证状态
                self.logout()
                return False
        except:
            # API调用失败，可能是网络问题，暂时保持认证状态
            return True
    
    def logout(self):
        """用户登出"""
        try:
            # 调用后端登出API
            self.api_client.logout()
        except:
            pass  # 即使后端登出失败也要清除本地状态
        
        # 清除会话状态
        keys_to_clear = [
            'authenticated', 'user_info', 'access_token',
            'current_page', 'selected_devices'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        return st.session_state.get('user_info')
    
    def is_admin(self) -> bool:
        """检查当前用户是否为管理员"""
        user_info = self.get_current_user()
        return user_info and user_info.get('role') == 'admin'