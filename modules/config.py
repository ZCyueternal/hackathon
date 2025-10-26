import streamlit as st
from modules.data_loader import data_loader

# =============================================================================
# 页面状态常量
# =============================================================================

PAGE_STAGE_SELECTION = 'stage_selection'
PAGE_MAIN_INTERFACE = 'main_interface'

class AppConfig:
    """应用程序配置和样式管理类"""
    
    def __init__(self):
        self.data_loader = data_loader
    
    def configure_page(self):
        """
        配置 Streamlit 页面设置
        设置页面标题、图标、布局等基础配置
        """
        ui_config = self.data_loader.get_ui_config()
        st.set_page_config(
            page_title=ui_config.get("app_title", "PaperBuddy 论文搭子"),
            page_icon="🎓",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def apply_custom_styles(self):
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
    
    def get_page_constants(self):
        """获取页面常量"""
        return {
            'PAGE_STAGE_SELECTION': PAGE_STAGE_SELECTION,
            'PAGE_MAIN_INTERFACE': PAGE_MAIN_INTERFACE
        }

# 创建全局配置实例
app_config = AppConfig()