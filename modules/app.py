import streamlit as st
from modules.config import app_config, PAGE_STAGE_SELECTION, PAGE_MAIN_INTERFACE
from modules.session_manager import session_manager
from modules.ui_components import ui_components
from modules.stage_selection import StageSelection

class ReSocialApp:
    """主应用程序类，负责协调所有模块和页面路由"""
    
    def __init__(self):
        self.stage_selection = StageSelection()
    
    def initialize_app(self):
        """
        初始化应用程序
        配置页面、样式和会话状态
        """
        # 初始化配置
        app_config.configure_page()
        app_config.apply_custom_styles()
        session_manager.init_session_state()
    
    def render_sidebar(self):
        """
        渲染侧边栏
        """
        ui_components.render_sidebar()
    
    def route_pages(self):
        """
        页面路由管理
        根据当前页面状态显示相应的页面
        """
        current_page = session_manager.get_current_page()
        
        if current_page == PAGE_STAGE_SELECTION:
            self.show_stage_selection()
        elif current_page == PAGE_MAIN_INTERFACE:
            self.show_main_interface()
        else:
            # 默认显示阶段选择页面
            session_manager.set_current_page(PAGE_STAGE_SELECTION)
            self.show_stage_selection()
    
    def show_stage_selection(self):
        """
        显示阶段选择页面
        """
        self.stage_selection.render()
    
    def show_main_interface(self):
        """
        显示主界面
        """
        ui_components.show_main_interface()
    
    def run(self):
        """
        运行应用程序
        这是主要的应用程序入口点
        """
        # 初始化应用
        self.initialize_app()
        
        # 渲染侧边栏
        self.render_sidebar()
        
        # 路由页面
        self.route_pages()

def main():
    """
    主函数 - 应用程序入口点
    """
    app = ReSocialApp()
    app.run()

if __name__ == "__main__":
    main()