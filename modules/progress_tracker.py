import streamlit as st
from modules.data_loader import data_loader
from modules.session_manager import session_manager

class ProgressTracker:
    """进度追踪管理类，负责计算和更新用户进度"""
    
    def __init__(self):
        self.data_loader = data_loader
    
    def update_progress(self):
        """
        更新用户进度
        计算当前阶段的完成度和得分
        """
        selected_stage = session_manager.get_selected_stage()
        selected_topic = session_manager.get_selected_topic()
        
        if not selected_stage:
            return
        
        stage_id = selected_stage.get("id")
        topic_id = selected_topic.get("id") if selected_topic else None
        
        # 获取当前课题的清单
        checklists = self.data_loader.get_checklists_by_topic(topic_id) if topic_id else []
        
        total_items = 0
        completed_items = 0
        total_score = 0
        
        for checklist in checklists:
            for item in checklist.get("items", []):
                total_items += 1
                item_id = f"{checklist['id']}_{item['id']}"
                if session_manager.get_checklist_progress().get(item_id, False):
                    completed_items += 1
                    total_score += item.get("weight", 0) * 100
        
        # 更新进度
        if total_items > 0:
            progress_percentage = (completed_items / total_items) * 100
            session_manager.update_stage_progress(stage_id, progress_percentage)
            session_manager.update_total_score(total_score)
    
    def toggle_checklist_item(self, checklist_id, item_id):
        """
        切换清单项目的完成状态
        
        Args:
            checklist_id (int): 清单ID
            item_id (int): 项目ID
        """
        key = f"{checklist_id}_{item_id}"
        current_progress = session_manager.get_checklist_progress()
        current_state = current_progress.get(key, False)
        
        # 切换状态
        session_manager.update_checklist_item(checklist_id, item_id, not current_state)
        
        # 更新整体进度
        self.update_progress()
    
    def get_current_progress_stats(self):
        """
        获取当前进度统计
        
        Returns:
            dict: 包含进度统计信息的字典
        """
        selected_topic = session_manager.get_selected_topic()
        if not selected_topic:
            return {
                'total_items': 0,
                'completed_items': 0,
                'completion_rate': 0,
                'total_score': 0
            }
        
        topic_id = selected_topic.get("id")
        checklists = self.data_loader.get_checklists_by_topic(topic_id)
        
        total_items = 0
        completed_items = 0
        total_score = 0
        
        for checklist in checklists:
            for item in checklist.get("items", []):
                total_items += 1
                item_id = f"{checklist['id']}_{item['id']}"
                if session_manager.get_checklist_progress().get(item_id, False):
                    completed_items += 1
                    total_score += item.get("weight", 0) * 100
        
        completion_rate = (completed_items / total_items * 100) if total_items > 0 else 0
        
        return {
            'total_items': total_items,
            'completed_items': completed_items,
            'completion_rate': completion_rate,
            'total_score': total_score
        }
    
    def get_stage_progress(self, stage_id):
        """
        获取特定阶段的进度
        
        Args:
            stage_id (int): 阶段ID
        
        Returns:
            float: 进度百分比 (0-100)
        """
        user_progress = session_manager.get_user_progress()
        return user_progress.get('stage_progress', {}).get(stage_id, 0)
    
    def get_overall_progress(self):
        """
        获取整体进度（所有阶段的平均进度）
        
        Returns:
            float: 整体进度百分比 (0-100)
        """
        user_progress = session_manager.get_user_progress()
        stage_progress = user_progress.get('stage_progress', {})
        
        if not stage_progress:
            return 0
        
        total_progress = sum(stage_progress.values())
        return total_progress / len(stage_progress)
    
    def reset_progress(self, stage_id=None, topic_id=None):
        """
        重置进度
        
        Args:
            stage_id (int): 阶段ID，如果为None则重置所有进度
            topic_id (int): 课题ID，如果为None则重置阶段的所有课题
        """
        if stage_id is None:
            # 重置所有进度
            session_manager.set_checklist_progress({})
            session_manager.set_user_progress({
                'current_stage': None,
                'stage_progress': {},
                'completed_topics': [],
                'total_score': 0
            })
        elif topic_id is None:
            # 重置特定阶段的所有进度
            current_progress = session_manager.get_checklist_progress()
            new_progress = {}
            
            for key, value in current_progress.items():
                # 只保留不属于该阶段的进度
                checklist_id = int(key.split('_')[0])
                checklist = self._get_checklist_by_id(checklist_id)
                if checklist and checklist.get('topic_id') != topic_id:
                    new_progress[key] = value
            
            session_manager.set_checklist_progress(new_progress)
            self.update_progress()
        else:
            # 重置特定课题的进度
            current_progress = session_manager.get_checklist_progress()
            new_progress = {}
            
            for key, value in current_progress.items():
                checklist_id = int(key.split('_')[0])
                checklist = self._get_checklist_by_id(checklist_id)
                if checklist and checklist.get('topic_id') != topic_id:
                    new_progress[key] = value
            
            session_manager.set_checklist_progress(new_progress)
            self.update_progress()
    
    def _get_checklist_by_id(self, checklist_id):
        """根据ID获取清单"""
        all_checklists = self.data_loader.load_json("checklists.json").get("checklists", [])
        for checklist in all_checklists:
            if checklist.get("id") == checklist_id:
                return checklist
        return None
    
    def export_progress(self):
        """
        导出进度数据
        
        Returns:
            dict: 包含所有进度数据的字典
        """
        return {
            'checklist_progress': session_manager.get_checklist_progress(),
            'user_progress': session_manager.get_user_progress(),
            'timestamp': st.session_state.get('_last_update', '')
        }
    
    def import_progress(self, progress_data):
        """
        导入进度数据
        
        Args:
            progress_data (dict): 进度数据字典
        """
        if 'checklist_progress' in progress_data:
            session_manager.set_checklist_progress(progress_data['checklist_progress'])
        
        if 'user_progress' in progress_data:
            session_manager.set_user_progress(progress_data['user_progress'])
        
        self.update_progress()

# 创建全局进度追踪器实例
progress_tracker = ProgressTracker()