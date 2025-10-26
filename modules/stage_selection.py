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
        # 创建可直接点击的大框
        if st.button(
            f"### {stage.get('icon', '📝')} {stage.get('name', '阶段')}\n\n{stage.get('description', '')}",
            key=f"stage_{stage.get('id')}",
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