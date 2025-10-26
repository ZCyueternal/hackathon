import json
import os
from typing import Dict, List, Any

class DataLoader:
    """数据加载模块，负责加载所有配置文件"""
    
    def __init__(self, assets_path: str = "assets"):
        self.assets_path = assets_path
        self._cache = {}
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """加载JSON文件"""
        if filename in self._cache:
            return self._cache[filename]
        
        filepath = os.path.join(self.assets_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._cache[filename] = data
                return data
        except FileNotFoundError:
            print(f"文件未找到: {filepath}")
            return {}
        except json.JSONDecodeError:
            print(f"JSON解析错误: {filepath}")
            return {}
    
    def get_stages(self) -> List[Dict[str, Any]]:
        """获取所有阶段数据"""
        data = self.load_json("stages.json")
        return data.get("stages", [])
    
    def get_stage_by_id(self, stage_id: int) -> Dict[str, Any]:
        """根据ID获取阶段数据"""
        stages = self.get_stages()
        for stage in stages:
            if stage.get("id") == stage_id:
                return stage
        return {}
    
    def get_topics_by_stage(self, stage_id: int) -> List[Dict[str, Any]]:
        """获取指定阶段的所有课题"""
        data = self.load_json("topics.json")
        topics = data.get("topics", [])
        return [topic for topic in topics if topic.get("stage_id") == stage_id]
    
    def get_checklists_by_topic(self, topic_id: int) -> List[Dict[str, Any]]:
        """获取指定课题的所有清单"""
        data = self.load_json("checklists.json")
        checklists = data.get("checklists", [])
        return [checklist for checklist in checklists if checklist.get("topic_id") == topic_id]
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取界面配置"""
        return self.load_json("ui_config.json")
    
    def get_chat_config(self) -> Dict[str, Any]:
        """获取聊天配置"""
        return self.load_json("chat_config.json")
    
    def get_function_panel_config(self) -> Dict[str, Any]:
        """获取功能面板配置"""
        return self.load_json("function_panel_config.json")

# 创建全局数据加载器实例
data_loader = DataLoader()