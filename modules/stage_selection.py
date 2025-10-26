import streamlit as st
from modules.data_loader import data_loader

class StageSelection:
    """阶段选择页面模块"""
    
    def __init__(self):
        self.data_loader = data_loader
        self.ui_config = self.data_loader.get_ui_config()
    
    def render(self):
        """渲染阶段选择页面"""
        st.set_page_config(
            page_title=self.ui_config.get("app_title", "ReSocial 科研训练系统"),
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
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
        # 卡片样式
        card_style = f"""
        <div style='
            border: 2px solid {stage.get("color", "#e0e0e0")};
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
        '
        onmouseover="this.style.transform='scale(1.05)'"
        onmouseout="this.style.transform='scale(1)'"
        >
            <div style='text-align: center;'>
                <div style='font-size: 2.5em; margin-bottom: 10px;'>{stage.get("icon", "📝")}</div>
                <h3 style='margin: 10px 0; color: {stage.get("color", "#333")};'>{stage.get("name", "阶段")}</h3>
                <p style='color: #666; font-size: 0.9em;'>{stage.get("description", "")}</p>
            </div>
            <div style='text-align: center; margin-top: 10px;'>
                <div style='
                    background-color: {stage.get("color", "#4CAF50")};
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    display: inline-block;
                '>
                    {self.ui_config.get("stage_selection", {}).get("start_button", "开始训练")}
                </div>
            </div>
        </div>
        """
        
        # 渲染卡片
        st.markdown(card_style, unsafe_allow_html=True)
        
        # 添加点击事件
        if st.button(f"选择 {stage.get('name')}", key=f"stage_{stage.get('id')}", 
                    use_container_width=True):
            # 保存选择的阶段到session state
            st.session_state.selected_stage = stage
            st.session_state.current_page = "main_interface"
            st.rerun()
    
    def get_selected_stage(self):
        """获取用户选择的阶段"""
        return st.session_state.get("selected_stage")

def main():
    """主函数，用于测试阶段选择页面"""
    stage_selection = StageSelection()
    stage_selection.render()

if __name__ == "__main__":
    main()