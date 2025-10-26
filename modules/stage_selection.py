import streamlit as st
from modules.data_loader import data_loader
from modules.session_manager import session_manager
from modules.config import PAGE_MAIN_INTERFACE

class StageSelection:
    """阶段选择页面模块"""
    
    def __init__(self):
        self.data_loader = data_loader
        self.ui_config = self.data_loader.get_ui_config()
    
    def render(self):
        """渲染阶段选择页面"""
        # 页面标题和描述
        st.title(self.ui_config.get("stage_selection", {}).get("title", "选择科研阶段"))
        st.markdown(f"**{self.ui_config.get('stage_selection', {}).get('description', '请选择您当前所处的科研阶段')}**")
        st.markdown("---")
        
        # 获取阶段数据
        stages = self.data_loader.get_stages()
        
        # 创建4列的布局
        cols = st.columns(4)
        
        for idx, stage in enumerate(stages):
            with cols[idx]:
                self._render_stage_card(stage)
    
    def _render_stage_card(self, stage: dict):
        """渲染单个阶段卡片"""
        # 获取阶段颜色，如果没有则使用默认颜色
        stage_color = stage.get('color', '#6C757D')
        stage_id = stage.get('id')
        
        # 创建自定义按钮样式 - 为每个阶段创建唯一的CSS类
        button_style = f"""
        <style>
        .stage-button-{stage_id} {{
            background-color: {stage_color}20 !important;
            border: 2px solid {stage_color} !important;
            border-radius: 12px !important;
            padding: 25px !important;
            margin: 10px 0 !important;
            text-align: center !important;
            min-height: 180px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            color: {stage_color} !important;
            font-weight: bold !important;
            width: 100% !important;
            white-space: pre-line !important;
        }}
        .stage-button-{stage_id}:hover {{
            background-color: {stage_color}30 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            border-color: {stage_color} !important;
        }}
        </style>
        """
        
        # 渲染按钮样式
        st.markdown(button_style, unsafe_allow_html=True)
        
        # 创建按钮内容 - 使用纯文本格式
        button_label = f"{stage.get('icon', '📝')}\n\n{stage.get('name', '阶段')}\n\n{stage.get('description', '')}"
        
        # 创建可直接点击的大框
        if st.button(
            button_label,
            key=f"stage_{stage_id}",
            use_container_width=True,
            help=f"点击进入 {stage.get('name')} 阶段"
        ):
            # 保存选择的阶段到session state
            session_manager.set_selected_stage(stage)
            session_manager.set_current_page(PAGE_MAIN_INTERFACE)
            st.rerun()
    
    def get_selected_stage(self):
        """获取用户选择的阶段"""
        return session_manager.get_selected_stage()

def main():
    """主函数，用于测试阶段选择页面"""
    stage_selection = StageSelection()
    stage_selection.render()

if __name__ == "__main__":
    main()
