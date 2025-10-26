import streamlit as st
from modules.config import PAGE_STAGE_SELECTION

class SessionManager:
    """会话状态管理类，负责管理应用程序的状态"""
    
    def __init__(self):
        self.page_constants = {
            'PAGE_STAGE_SELECTION': PAGE_STAGE_SELECTION,
            'PAGE_MAIN_INTERFACE': 'main_interface'
        }
    
    def init_session_state(self):
        """
        初始化会话状态变量
        管理应用程序的状态，包括当前页面、选择的阶段、课题等
        """
        # 当前页面状态
        if 'current_page' not in st.session_state:
            st.session_state.current_page = self.page_constants['PAGE_STAGE_SELECTION']
        
        # 选择的阶段信息
        if 'selected_stage' not in st.session_state:
            st.session_state.selected_stage = None
        
        # 选择的课题信息
        if 'selected_topic' not in st.session_state:
            st.session_state.selected_topic = None
        
        # 聊天历史
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # 清单完成状态
        if 'checklist_progress' not in st.session_state:
            st.session_state.checklist_progress = {}
        
        # 用户进度追踪
        if 'user_progress' not in st.session_state:
            st.session_state.user_progress = {
                'current_stage': None,
                'stage_progress': {},  # 各阶段进度
                'completed_topics': [],  # 完成的课题
                'total_score': 0  # 总得分
            }
    
    def get_current_page(self):
        """获取当前页面"""
        return st.session_state.get('current_page', self.page_constants['PAGE_STAGE_SELECTION'])
    
    def set_current_page(self, page):
        """设置当前页面"""
        st.session_state.current_page = page
    
    def get_selected_stage(self):
        """获取选择的阶段"""
        return st.session_state.get('selected_stage')
    
    def set_selected_stage(self, stage):
        """设置选择的阶段"""
        st.session_state.selected_stage = stage
    
    def get_selected_topic(self):
        """获取选择的课题"""
        return st.session_state.get('selected_topic')
    
    def set_selected_topic(self, topic):
        """设置选择的课题"""
        st.session_state.selected_topic = topic
    
    def get_chat_history(self, stage_id=None):
        """获取聊天历史"""
        if stage_id:
            chat_history_key = f"chat_history_{stage_id}"
            return st.session_state.get(chat_history_key, [])
        return st.session_state.get('chat_history', [])
    
    def set_chat_history(self, history, stage_id=None):
        """设置聊天历史"""
        if stage_id:
            chat_history_key = f"chat_history_{stage_id}"
            st.session_state[chat_history_key] = history
        else:
            st.session_state.chat_history = history
    
    def add_chat_message(self, role, content, stage_id=None):
        """添加聊天消息"""
        if stage_id:
            chat_history_key = f"chat_history_{stage_id}"
            if chat_history_key not in st.session_state:
                st.session_state[chat_history_key] = []
            st.session_state[chat_history_key].append({"role": role, "content": content})
        else:
            st.session_state.chat_history.append({"role": role, "content": content})
    
    def get_checklist_progress(self):
        """获取清单进度"""
        return st.session_state.get('checklist_progress', {})
    
    def set_checklist_progress(self, progress):
        """设置清单进度"""
        st.session_state.checklist_progress = progress
    
    def update_checklist_item(self, checklist_id, item_id, completed):
        """更新清单项目状态"""
        key = f"{checklist_id}_{item_id}"
        st.session_state.checklist_progress[key] = completed
    
    def get_user_progress(self):
        """获取用户进度"""
        return st.session_state.get('user_progress', {
            'current_stage': None,
            'stage_progress': {},
            'completed_topics': [],
            'total_score': 0
        })
    
    def set_user_progress(self, progress):
        """设置用户进度"""
        st.session_state.user_progress = progress
    
    def update_stage_progress(self, stage_id, progress_percentage):
        """更新阶段进度"""
        if 'stage_progress' not in st.session_state.user_progress:
            st.session_state.user_progress['stage_progress'] = {}
        st.session_state.user_progress['stage_progress'][stage_id] = progress_percentage
    
    def update_total_score(self, score):
        """更新总得分"""
        st.session_state.user_progress['total_score'] = score
    
    def clear_session(self):
        """清空会话状态（重置应用）"""
        keys_to_clear = [
            'current_page', 'selected_stage', 'selected_topic', 
            'chat_history', 'checklist_progress', 'user_progress'
        ]
        
        # 清除所有聊天历史（包括按阶段的）
        for key in list(st.session_state.keys()):
            if key.startswith('chat_history_'):
                del st.session_state[key]
        
        # 清除主要状态
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # 重新初始化
        self.init_session_state()

# 创建全局会话管理器实例
session_manager = SessionManager()