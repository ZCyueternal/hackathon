import streamlit as st
import requests
import os
from dotenv import load_dotenv
from modules.data_loader import data_loader
from modules.session_manager import session_manager

# 加载环境变量
load_dotenv()

class APIClient:
    """API 通信管理类，负责与 DeepSeek API 的交互"""
    
    def __init__(self):
        self.data_loader = data_loader
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
    
    def call_deepseek_api(self, messages):
        """
        调用 DeepSeek API 接口
        发送请求到 DeepSeek API 并获取响应结果
        
        Args:
            messages (list): 消息列表
        
        Returns:
            str: AI 返回的响应文本，失败时返回 None
        """
        if not self.api_key:
            st.error("DeepSeek API密钥未配置，请在.env文件中设置DEEPSEEK_API_KEY")
            return None
            
        chat_config = self.data_loader.get_chat_config()
        api_config = chat_config.get("chat_interface", {})
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
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
    
    def get_ai_response(self, user_message, context=None, stage_id=None):
        """
        获取 AI 对用户消息的回应
        
        Args:
            user_message (str): 用户输入的消息
            context (dict): 上下文信息（阶段、课题等）
            stage_id (int): 阶段ID，用于获取特定阶段的聊天历史
        
        Returns:
            str: AI 返回的响应文本
        """
        chat_config = self.data_loader.get_chat_config()
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
        
        # 添加聊天历史（使用阶段特定的历史或全局历史）
        chat_history = session_manager.get_chat_history(stage_id)
        for msg in chat_history[-10:]:  # 只保留最近10条消息
            messages.append(msg)
        
        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return self.call_deepseek_api(messages)
    
    def send_message(self, user_message, stage_id=None, topic_id=None):
        """
        发送消息到 AI 并处理响应
        
        Args:
            user_message (str): 用户消息
            stage_id (int): 阶段ID
            topic_id (int): 课题ID
        
        Returns:
            tuple: (success, response_message)
        """
        if not user_message.strip():
            return False, "消息不能为空"
        
        if not self.api_key:
            return False, "DeepSeek API密钥未配置，请在.env文件中设置DEEPSEEK_API_KEY"
        
        # 构建上下文
        context = {}
        selected_stage = session_manager.get_selected_stage()
        selected_topic = session_manager.get_selected_topic()
        
        if selected_stage:
            context["stage_name"] = selected_stage.get("name", "")
        if selected_topic:
            context["topic_name"] = selected_topic.get("name", "")
        
        # 添加用户消息到历史
        session_manager.add_chat_message("user", user_message, stage_id)
        
        # 获取AI响应
        ai_response = self.get_ai_response(user_message, context, stage_id)
        
        if ai_response:
            # 添加AI响应到历史
            session_manager.add_chat_message("assistant", ai_response, stage_id)
            return True, ai_response
        else:
            return False, "获取AI响应失败，请检查API密钥和网络连接"
    
    def clear_chat_history(self, stage_id=None):
        """
        清空聊天历史
        
        Args:
            stage_id (int): 阶段ID，如果提供则清空特定阶段的聊天历史
        """
        session_manager.set_chat_history([], stage_id)

# 创建全局 API 客户端实例
api_client = APIClient()