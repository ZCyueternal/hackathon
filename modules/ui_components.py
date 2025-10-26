import streamlit as st
import os
from dotenv import load_dotenv
from modules.data_loader import data_loader
from modules.session_manager import session_manager
from modules.progress_tracker import progress_tracker
from modules.api_client import api_client

# 加载环境变量
load_dotenv()

class UIComponents:
    """UI 组件管理类，负责渲染各种用户界面组件"""
    
    def __init__(self):
        self.data_loader = data_loader
        self.ui_config = self.data_loader.get_ui_config()
    
    def show_checklist(self):
        """
        显示当前课题的任务清单
        """
        selected_topic = session_manager.get_selected_topic()
        if not selected_topic:
            st.info("请先选择一个课题")
            return
        
        topic_id = selected_topic.get("id")
        checklists = self.data_loader.get_checklists_by_topic(topic_id)
        
        for checklist in checklists:
            st.markdown(f"**{checklist.get('name', '清单')}**")
            
            for item in checklist.get("items", []):
                item_id = f"{checklist['id']}_{item['id']}"
                is_completed = session_manager.get_checklist_progress().get(item_id, False)
                
                checkbox_label = f"{item.get('description', '')} (权重: {item.get('weight', 0)})"
                
                if st.checkbox(checkbox_label, value=is_completed, 
                             key=f"check_{item_id}"):
                    if not is_completed:
                        progress_tracker.toggle_checklist_item(checklist['id'], item['id'])
                else:
                    if is_completed:
                        progress_tracker.toggle_checklist_item(checklist['id'], item['id'])
    
    def show_chat_interface(self, stage_id=None):
        """
        显示聊天界面
        
        Args:
            stage_id (int): 阶段ID，用于区分不同阶段的聊天
        """
        ui_config = self.data_loader.get_ui_config()
        chat_config = ui_config.get("main_interface", {}).get("chat_interface", {})
        
        # 使用阶段ID创建唯一的键
        stage_suffix = f"_{stage_id}" if stage_id else ""
        
        st.markdown(f"### {chat_config.get('title', 'AI科研助手')}")
        
        # 检查API密钥是否配置
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key or api_key == 'your_deepseek_api_key_here':
            st.warning("⚠️ DeepSeek API密钥未配置，请在.env文件中设置DEEPSEEK_API_KEY")
            return
        
        # 显示聊天历史
        chat_container = st.container()
        with chat_container:
            chat_history = session_manager.get_chat_history(stage_id)
            
            for message in chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>你:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message ai-message">
                        <strong>AI助手:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # 输入区域
        st.markdown("---")
        user_input = st.text_area(chat_config.get("placeholder", "请输入您的问题或描述您的情况..."),
                                key=f"chat_input{stage_suffix}", height=100)
        
        # 发送和清空按钮
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(chat_config.get("send_button", "发送"), use_container_width=True, key=f"send_btn{stage_suffix}"):
                if user_input.strip():
                    success, response = api_client.send_message(user_input, stage_id)
                    if success:
                        st.rerun()
                    else:
                        st.error(response)
                else:
                    st.error("请输入消息内容")
        
        with col2:
            if st.button(chat_config.get("clear_button", "清空对话"), use_container_width=True, key=f"clear_btn{stage_suffix}"):
                api_client.clear_chat_history(stage_id)
                st.rerun()
    
    def show_function_panel(self, stage_id=None):
        """
        显示右侧功能面板
        
        Args:
            stage_id (int): 阶段ID
        """
        ui_config = self.data_loader.get_ui_config()
        panel_config = ui_config.get("main_interface", {}).get("function_panel", {})
        
        # 使用阶段ID创建唯一的键
        stage_suffix = f"_{stage_id}" if stage_id else ""
        
        st.markdown(f"### {panel_config.get('title', '功能面板')}")
        
        # 得分显示
        st.markdown("#### 📈 当前得分")
        user_progress = session_manager.get_user_progress()
        st.markdown(f"<div class='function-panel'><h2 style='text-align: center; color: #1f77b4;'>{user_progress['total_score']:.1f}</h2></div>",
                    unsafe_allow_html=True)
        
        # 功能按钮
        function_config = self.data_loader.get_function_panel_config()
        functions = function_config.get("function_panel", {}).get("functions", [])
        
        for func in functions:
            if st.button(f"{func.get('icon', '📋')} {func.get('button_text', '功能')}",
                        key=f"func_{func.get('id')}{stage_suffix}", use_container_width=True):
                # 这里可以添加功能的具体实现
                st.info(f"点击了 {func.get('name')} 功能")
        
        # 当前清单概览
        if session_manager.get_selected_topic():
            st.markdown("#### 📋 当前清单")
            stats = progress_tracker.get_current_progress_stats()
            
            if stats['total_items'] > 0:
                st.metric("完成进度", f"{stats['completion_rate']:.1f}%")
                st.metric("已完成项目", f"{stats['completed_items']}/{stats['total_items']}")
    
    def show_sidebar(self):
        """
        显示Streamlit默认侧边栏
        包含导航、课题选择、任务清单和系统信息
        """
        ui_config = self.data_loader.get_ui_config()
        sidebar_config = ui_config.get("main_interface", {}).get("sidebar", {})
        
        # 导航按钮
        if st.button("⬅️ 返回阶段选择", use_container_width=True):
            session_manager.set_current_page('stage_selection')
            st.rerun()
        
        st.markdown("---")
        
        # 课题选择 - 可折叠
        with st.expander(f"📚 {sidebar_config.get('topic_selection', '课题选择')}", expanded=True):
            selected_stage = session_manager.get_selected_stage()
            if selected_stage:
                stage_id = selected_stage.get("id")
                topics = self.data_loader.get_topics_by_stage(stage_id)
                
                for topic in topics:
                    if st.button(f"{topic.get('name')}", key=f"topic_{topic.get('id')}", use_container_width=True):
                        session_manager.set_selected_topic(topic)
                        st.rerun()
        
        st.markdown("---")
        
        # 任务清单 - 可折叠
        if session_manager.get_selected_topic():
            with st.expander(f"📋 {sidebar_config.get('checklist', '任务清单')}", expanded=True):
                self.show_checklist()
        
        st.markdown("---")
        
        # 系统信息和帮助 - 可折叠
        with st.expander("ℹ️ 系统信息", expanded=False):
            st.info("""
            **ReSocial 科研训练系统** 帮助您：
            - 系统化完成科研各阶段
            - 获得AI导师专业指导
            - 跟踪研究进度和成果
            """)
            
            st.markdown("### 📊 你的进度")
            user_progress = session_manager.get_user_progress()
            if user_progress['total_score'] > 0:
                st.metric("总得分", f"{user_progress['total_score']:.1f}")
                completed_stages = len([p for p in user_progress['stage_progress'].values() if p > 0])
                st.metric("进行中阶段", completed_stages)
            else:
                st.info("尚未开始训练")
            
            st.markdown("### 🆘 使用帮助")
            st.write("""
            1. 选择您当前的科研阶段
            2. 选择具体的训练课题
            3. 与AI导师交流获取指导
            4. 完成清单任务跟踪进度
            5. 查看功能面板了解详情
            """)
    
    def render_sidebar(self):
        """
        渲染Streamlit默认侧边栏
        """
        with st.sidebar:
            if session_manager.get_current_page() == 'main_interface':
                self.show_sidebar()
            else:
                # 在阶段选择页面显示简化的侧边栏
                st.markdown("## 🎓 系统信息")
                st.info("""
                **ReSocial 科研训练系统** 帮助您：
                - 系统化完成科研各阶段
                - 获得AI导师专业指导
                - 跟踪研究进度和成果
                """)
                
                st.markdown("## 📊 你的进度")
                user_progress = session_manager.get_user_progress()
                if user_progress['total_score'] > 0:
                    st.metric("总得分", f"{user_progress['total_score']:.1f}")
                    completed_stages = len([p for p in user_progress['stage_progress'].values() if p > 0])
                    st.metric("进行中阶段", completed_stages)
                else:
                    st.info("尚未开始训练")
                
                st.markdown("### 🆘 使用帮助")
                st.write("""
                1. 选择您当前的科研阶段
                2. 选择具体的训练课题
                3. 与AI导师交流获取指导
                4. 完成清单任务跟踪进度
                5. 查看功能面板了解详情
                """)
    
    def show_main_interface(self):
        """
        显示主界面
        包含四个阶段的标签页
        """
        ui_config = self.data_loader.get_ui_config()
        main_config = ui_config.get("main_interface", {})
        
        # 创建四个阶段的标签页
        stages = self.data_loader.get_stages()
        tab_names = [f"{stage.get('icon', '🎓')} {stage.get('name', '')}" for stage in stages]
        
        tabs = st.tabs(tab_names)
        
        for i, tab in enumerate(tabs):
            with tab:
                # 设置当前阶段
                current_stage = stages[i]
                session_manager.set_selected_stage(current_stage)
                
                # 显示该阶段的界面
                st.title(f"{current_stage.get('icon', '🎓')} {current_stage.get('name', '')}")
                
                # 显示阶段描述
                st.info(current_stage.get('description', ''))
                
                # 主界面布局
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    self.show_chat_interface(stage_id=current_stage.get("id"))
                
                with col2:
                    self.show_function_panel(stage_id=current_stage.get("id"))

# 创建全局 UI 组件实例
ui_components = UIComponents()