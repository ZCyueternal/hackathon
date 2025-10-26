import streamlit as st
import requests
import json
import time
from datetime import datetime
import plotly.graph_objects as go
from modules.data_loader import data_loader
from modules.stage_selection import StageSelection

# =============================================================================
# 页面状态常量
# =============================================================================

PAGE_STAGE_SELECTION = 'stage_selection'
PAGE_MAIN_INTERFACE = 'main_interface'

# =============================================================================
# 配置模块
# =============================================================================

def configure_page():
    """
    配置 Streamlit 页面设置
    设置页面标题、图标、布局等基础配置
    """
    ui_config = data_loader.get_ui_config()
    st.set_page_config(
        page_title=ui_config.get("app_title", "ReSocial 科研训练系统"),
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# =============================================================================
# 样式模块
# =============================================================================

def apply_custom_styles():
    """
    应用自定义 CSS 样式
    定义应用程序的整体视觉风格和组件样式
    """
    st.markdown("""
    <style>
        /* 主标题样式 */
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        /* 进度条样式 */
        .progress-container {
            background-color: #f0f0f0;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        
        /* 侧边栏样式 */
        .sidebar-section {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* 功能面板样式 */
        .function-panel {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #1f77b4;
        }
        
        /* 聊天界面样式 */
        .chat-message {
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 15px;
            max-width: 80%;
        }
        .user-message {
            background-color: #007bff;
            color: white;
            margin-left: auto;
        }
        .ai-message {
            background-color: #f1f1f1;
            color: #333;
        }
        
        /* 阶段卡片样式 */
        .stage-card {
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            cursor: pointer;
        }
        .stage-card:hover {
            transform: scale(1.05);
        }
        
        /* 清单项目样式 */
        .checklist-item {
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 5px;
            background-color: #f8f9fa;
            border-left: 3px solid #6c757d;
        }
        .checklist-item.completed {
            background-color: #d4edda;
            border-left-color: #28a745;
            text-decoration: line-through;
        }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# 会话状态管理模块
# =============================================================================

def init_session_state():
    """
    初始化会话状态变量
    管理应用程序的状态，包括当前页面、选择的阶段、课题等
    """
    # 当前页面状态
    if 'current_page' not in st.session_state:
        st.session_state.current_page = PAGE_STAGE_SELECTION
    
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

# =============================================================================
# API 通信模块
# =============================================================================

def call_deepseek_api(messages, api_key):
    """
    调用 DeepSeek API 接口
    发送请求到 DeepSeek API 并获取响应结果
    
    Args:
        messages (list): 消息列表
        api_key (str): DeepSeek API 密钥
    
    Returns:
        str: AI 返回的响应文本，失败时返回 None
    """
    chat_config = data_loader.get_chat_config()
    api_config = chat_config.get("chat_interface", {})
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 构建请求数据
    data = {
        "model": api_config.get("model_name", "deepseek-chat"),
        "messages": messages,
        "temperature": api_config.get("interface_params", {}).get("temperature", 0.7),
        "max_tokens": api_config.get("interface_params", {}).get("max_tokens", 4096)
    }
    
    try:
        # 发送 POST 请求到 DeepSeek API
        response = requests.post(api_config.get("model_url", "https://api.deepseek.com/v1/chat/completions"), 
                               headers=headers, json=data, timeout=30)
        response.raise_for_status()  # 检查 HTTP 状态码
        
        # 解析响应数据
        result = response.json()
        return result['choices'][0]['message']['content']
        
    except requests.exceptions.RequestException as e:
        # 处理网络请求错误
        st.error(f"网络请求失败: {str(e)}")
        return None
    except KeyError as e:
        # 处理响应数据解析错误
        st.error(f"API 响应格式错误: {str(e)}")
        return None
    except Exception as e:
        # 处理其他未知错误
        st.error(f"API 调用失败: {str(e)}")
        return None

def get_ai_response(user_message, api_key, context=None):
    """
    获取 AI 对用户消息的回应
    
    Args:
        user_message (str): 用户输入的消息
        api_key (str): DeepSeek API 密钥
        context (dict): 上下文信息（阶段、课题等）
    
    Returns:
        str: AI 返回的响应文本
    """
    chat_config = data_loader.get_chat_config()
    system_prompt = chat_config.get("chat_interface", {}).get("interface_params", {}).get("system_prompt", "")
    
    # 构建上下文信息
    if context:
        stage_name = context.get("stage_name", "")
        topic_name = context.get("topic_name", "")
        system_prompt += f"\n\n当前阶段：{stage_name}\n当前课题：{topic_name}"
    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    
    # 添加聊天历史
    for msg in st.session_state.chat_history[-10:]:  # 只保留最近10条消息
        messages.append(msg)
    
    # 添加当前用户消息
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    return call_deepseek_api(messages, api_key)

# =============================================================================
# 进度追踪模块
# =============================================================================

def update_progress():
    """
    更新用户进度
    计算当前阶段的完成度和得分
    """
    if not st.session_state.selected_stage:
        return
    
    stage_id = st.session_state.selected_stage.get("id")
    topic_id = st.session_state.selected_topic.get("id") if st.session_state.selected_topic else None
    
    # 获取当前课题的清单
    checklists = data_loader.get_checklists_by_topic(topic_id) if topic_id else []
    
    total_items = 0
    completed_items = 0
    total_score = 0
    
    for checklist in checklists:
        for item in checklist.get("items", []):
            total_items += 1
            item_id = f"{checklist['id']}_{item['id']}"
            if st.session_state.checklist_progress.get(item_id, False):
                completed_items += 1
                total_score += item.get("weight", 0) * 100
    
    # 更新进度
    if total_items > 0:
        progress_percentage = (completed_items / total_items) * 100
        st.session_state.user_progress['stage_progress'][stage_id] = progress_percentage
        st.session_state.user_progress['total_score'] = total_score

def toggle_checklist_item(checklist_id, item_id):
    """
    切换清单项目的完成状态
    
    Args:
        checklist_id (int): 清单ID
        item_id (int): 项目ID
    """
    key = f"{checklist_id}_{item_id}"
    if key in st.session_state.checklist_progress:
        st.session_state.checklist_progress[key] = not st.session_state.checklist_progress[key]
    else:
        st.session_state.checklist_progress[key] = True
    
    update_progress()

# =============================================================================
# 页面渲染模块
# =============================================================================

def show_stage_selection():
    """
    显示阶段选择页面
    """
    stage_selection = StageSelection()
    stage_selection.render()

def show_main_interface():
    """
    显示主界面
    包含进度条、左侧边栏、聊天界面和功能面板
    """
    ui_config = data_loader.get_ui_config()
    main_config = ui_config.get("main_interface", {})
    
    # 页面标题
    st.title(f"{st.session_state.selected_stage.get('icon', '🎓')} {st.session_state.selected_stage.get('name', '')}")
    
    # 顶部进度条
    show_progress_bar()
    
    # 主界面布局（现在只有两列，因为侧边栏使用Streamlit默认侧边栏）
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_chat_interface()
    
    with col2:
        show_function_panel()

def show_progress_bar():
    """
    显示顶部进度条
    """
    stage = st.session_state.selected_stage
    if not stage:
        return
    
    stage_id = stage.get("id")
    progress = st.session_state.user_progress['stage_progress'].get(stage_id, 0)
    
    st.markdown("### 📊 当前阶段进度")
    st.progress(progress / 100)
    st.markdown(f"**完成度: {progress:.1f}%**")
    st.markdown("---")


def show_checklist():
    """
    显示当前课题的任务清单
    """
    topic_id = st.session_state.selected_topic.get("id")
    checklists = data_loader.get_checklists_by_topic(topic_id)
    
    for checklist in checklists:
        st.markdown(f"**{checklist.get('name', '清单')}**")
        
        for item in checklist.get("items", []):
            item_id = f"{checklist['id']}_{item['id']}"
            is_completed = st.session_state.checklist_progress.get(item_id, False)
            
            checkbox_label = f"{item.get('description', '')} (权重: {item.get('weight', 0)})"
            
            if st.checkbox(checkbox_label, value=is_completed, 
                         key=f"check_{item_id}"):
                if not is_completed:
                    toggle_checklist_item(checklist['id'], item['id'])
            else:
                if is_completed:
                    toggle_checklist_item(checklist['id'], item['id'])

def show_chat_interface():
    """
    显示聊天界面
    """
    ui_config = data_loader.get_ui_config()
    chat_config = ui_config.get("main_interface", {}).get("chat_interface", {})
    
    st.markdown(f"### {chat_config.get('title', 'AI科研助手')}")
    
    # 显示聊天历史
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
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
                             key="chat_input", height=100)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        api_key = st.text_input("DeepSeek API Key:", type="password", 
                               placeholder="sk-...", key="api_key_input")
    
    with col2:
        send_col, clear_col = st.columns([1, 1])
        with send_col:
            if st.button(chat_config.get("send_button", "发送"), use_container_width=True):
                if user_input.strip() and api_key.strip():
                    # 添加用户消息到历史
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    # 获取上下文信息
                    context = {
                        "stage_name": st.session_state.selected_stage.get("name"),
                        "topic_name": st.session_state.selected_topic.get("name") if st.session_state.selected_topic else None
                    }
                    
                    # 获取AI响应
                    with st.spinner(chat_config.get("thinking", "思考中...")):
                        ai_response = get_ai_response(user_input, api_key, context)
                        
                        if ai_response:
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": ai_response
                            })
                            st.rerun()
                        else:
                            st.error("获取AI响应失败，请检查API密钥和网络连接")
        
        with clear_col:
            if st.button(chat_config.get("clear_button", "清空对话"), use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

def show_function_panel():
    """
    显示右侧功能面板
    """
    ui_config = data_loader.get_ui_config()
    panel_config = ui_config.get("main_interface", {}).get("function_panel", {})
    
    st.markdown(f"### {panel_config.get('title', '功能面板')}")
    
    # 得分显示
    st.markdown("#### 📈 当前得分")
    st.markdown(f"<div class='function-panel'><h2 style='text-align: center; color: #1f77b4;'>{st.session_state.user_progress['total_score']:.1f}</h2></div>", 
                unsafe_allow_html=True)
    
    # 功能按钮
    function_config = data_loader.get_function_panel_config()
    functions = function_config.get("function_panel", {}).get("functions", [])
    
    for func in functions:
        if st.button(f"{func.get('icon', '📋')} {func.get('button_text', '功能')}", 
                    key=f"func_{func.get('id')}", use_container_width=True):
            # 这里可以添加功能的具体实现
            st.info(f"点击了 {func.get('name')} 功能")
    
    # 当前清单概览
    if st.session_state.selected_topic:
        st.markdown("#### 📋 当前清单")
        topic_id = st.session_state.selected_topic.get("id")
        checklists = data_loader.get_checklists_by_topic(topic_id)
        
        total_items = 0
        completed_items = 0
        
        for checklist in checklists:
            for item in checklist.get("items", []):
                total_items += 1
                item_id = f"{checklist['id']}_{item['id']}"
                if st.session_state.checklist_progress.get(item_id, False):
                    completed_items += 1
        
        if total_items > 0:
            completion_rate = (completed_items / total_items) * 100
            st.metric("完成进度", f"{completion_rate:.1f}%")
            st.metric("已完成项目", f"{completed_items}/{total_items}")

# =============================================================================
# 侧边栏模块
# =============================================================================

def show_sidebar():
    """
    显示Streamlit默认侧边栏
    包含导航、课题选择、任务清单和系统信息
    """
    ui_config = data_loader.get_ui_config()
    sidebar_config = ui_config.get("main_interface", {}).get("sidebar", {})
    
    # 导航按钮
    if st.button("⬅️ 返回阶段选择", use_container_width=True):
        st.session_state.current_page = PAGE_STAGE_SELECTION
        st.rerun()
    
    st.markdown("---")
    
    # 课题选择 - 可折叠
    with st.expander(f"📚 {sidebar_config.get('topic_selection', '课题选择')}", expanded=True):
        stage_id = st.session_state.selected_stage.get("id")
        topics = data_loader.get_topics_by_stage(stage_id)
        
        for topic in topics:
            if st.button(f"{topic.get('name')}", key=f"topic_{topic.get('id')}", use_container_width=True):
                st.session_state.selected_topic = topic
                st.rerun()
    
    st.markdown("---")
    
    # 任务清单 - 可折叠
    if st.session_state.selected_topic:
        with st.expander(f"📋 {sidebar_config.get('checklist', '任务清单')}", expanded=True):
            show_checklist()
    
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
        if st.session_state.user_progress['total_score'] > 0:
            st.metric("总得分", f"{st.session_state.user_progress['total_score']:.1f}")
            completed_stages = len([p for p in st.session_state.user_progress['stage_progress'].values() if p > 0])
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

def render_sidebar():
    """
    渲染Streamlit默认侧边栏
    """
    with st.sidebar:
        if st.session_state.current_page == PAGE_MAIN_INTERFACE:
            show_sidebar()
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
            if st.session_state.user_progress['total_score'] > 0:
                st.metric("总得分", f"{st.session_state.user_progress['total_score']:.1f}")
                completed_stages = len([p for p in st.session_state.user_progress['stage_progress'].values() if p > 0])
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

# =============================================================================
# 主应用模块
# =============================================================================

def main():
    """
    主应用函数
    初始化应用并管理页面路由
    """
    # 初始化配置
    configure_page()
    apply_custom_styles()
    init_session_state()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 主内容路由
    if st.session_state.current_page == PAGE_STAGE_SELECTION:
        show_stage_selection()
    elif st.session_state.current_page == PAGE_MAIN_INTERFACE:
        show_main_interface()

if __name__ == "__main__":
    main()
