import streamlit as st
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ResearchEvaluator:
    """研究生论文进度评估类，使用千问API分析研究进度"""
    
    def __init__(self):
        # 初始化千问客户端
        self.client = OpenAI(
            api_key=os.getenv("QWEN_API_KEY", "sk-90224d784fa94a06a5acedd7e152848d"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 阶段定义JSON
        self.stages_json = """{
          "stages": [
            {
              "stage": "开题阶段",
              "purpose": "判断是否已经完成选题、立题与研究方案设计，可正式进入研究阶段",
              "checklist": {
                "选题阶段（Topic Selection）": [
                  "已在专业/导师方向范围内确定选题领域（例如机器人、AI、控制等）",
                  "能说明选题的现实背景或科学意义（why this topic matters）",
                  "已阅读至少10篇核心文献，了解主流方向与最新成果",
                  "能明确当前研究空缺或痛点（what's missing）",
                  "选题难度、创新性、资源需求均在可承受范围内（not too easy / not too ambitious）",
                  "导师认可该题目具备研究/应用价值（达到'可以写开题报告'标准）"
                ],
                "立题与问题定义（Problem Definition）": [
                  "能用1-2句话清晰表述研究问题（research question / hypothesis）",
                  "研究目标明确且可量化（例如'提升x性能''降低y误差''验证z假设'）",
                  "知道研究要解决的问题类型（理论、算法、实验、工程应用等）",
                  "能解释'为什么是你来做'（已有基础、资源或兴趣匹配）"
                ],
                "研究方案设计（Method Design）": [
                  "已确定主要研究方法（实验/建模/仿真/数据分析/系统实现等）",
                  "已识别关键变量、控制因素与评估指标（metrics）",
                  "初步确定数据来源 / 硬件设备 / 软件工具 / 算力平台等",
                  "形成初步研究路线图（包含模块划分或任务分解）",
                  "明确预期成果形式（论文、系统、算法、专利、调研报告等）"
                ],
                "可行性与时间规划（Feasibility & Schedule）": [
                  "已制定阶段性时间表（含关键里程碑和交付物）",
                  "已评估风险点（如实验失败、数据不足、计算资源问题等）并提出应对方案",
                  "导师对计划认可且建议方向可行",
                  "准备了开题报告初稿和汇报材料（含研究背景、意义、方法、计划）"
                ]
              }
            },
            {
              "stage": "中期阶段",
              "purpose": "判断是否核心研究工作已经实质推进，有中期成果",
              "checklist": {
                "研究进展": [
                  "核心算法/系统/实验平台已搭建完毕并能正常运行",
                  "已有第一批实验结果或系统功能可展示",
                  "遇到的主要问题已被识别（数据、参数、收敛、硬件等）"
                ],
                "路径与节奏": [
                  "明确后续优化方向（例如模型调优、特征改进、方法对比）",
                  "能展示阶段性成果图表/视频/结果",
                  "保持每周或双周例会更新进展"
                ],
                "风险与调整": [
                  "已评估当前计划能否如期完成，如有必要已调整方向或目标",
                  "导师对当前进度总体满意，未出现长期停滞"
                ]
              }
            },
            {
              "stage": "结题阶段",
              "purpose": "判断是否进入收尾与论文写作阶段",
              "checklist": {
                "研究结果完善": [
                  "核心实验完成 ≥80%，主要数据和对比实验齐全",
                  "研究结果可复现并支持主要结论",
                  "研究贡献点已形成闭环（从问题→方法→结果→验证）"
                ],
                "论文撰写": [
                  "论文大纲已确定，introduction 与 method 部分初稿完成",
                  "已有主要图表与实验对比结果",
                  "已梳理related work并明确自己相对他人的创新点"
                ],
                "收尾准备": [
                  "准备结题报告、成果展示或演示视频",
                  "导师已审阅论文初稿并反馈修改意见",
                  "准备论文查重、投稿或归档材料"
                ]
              }
            },
            {
              "stage": "答辩阶段",
              "purpose": "判断是否具备自信展示与答辩的准备度",
              "checklist": {
                "展示准备": [
                  "答辩PPT已完成（结构清晰：背景→问题→方法→结果→贡献）",
                  "已进行至少一次模拟答辩，熟悉时间控制与节奏",
                  "能清晰讲述研究动机、方法逻辑、结果意义"
                ],
                "问答应对": [
                  "准备了常见答辩问题：创新点、方法细节、局限性、未来方向",
                  "能冷静应对质疑和延伸性问题",
                  "能把技术内容讲给非本领域听众理解"
                ],
                "后续收尾": [
                  "根据评委意见完成论文最终修改",
                  "归档所有成果：论文、代码、实验记录、PPT、视频等",
                  "准备成果展示或申报（例如优秀毕业论文、竞赛、专利等）"
                ]
              }
            }
          ]
        }"""
    
    def evaluate_research_progress(self, user_text, image_url=None, enable_thinking=True):
        """
        调用千问 qwen3-vl-plus，分析研究生论文阶段、任务进度、建议、导师意图。
        返回 JSON dict: current_stage, tasks_progress, advice, mentor_insights
        """
        system_prompt = f"""
你是一个研究生学术指导助手，专门帮助学生评估论文进度、理解导师意图，并提供改进和沟通建议。
请严格遵循以下规则：

1. 根据学生提供的文本信息和图片（导师沟通记录）判断当前论文阶段：
   - 开题阶段
   - 中期阶段
   - 结题阶段
   - 答辩阶段

2. 对当前阶段的各子任务（checklist）进行量化评估，用 0~1 的数字表示完成程度。
   - 数字越接近1表示该子任务已完成得越充分，0表示尚未开始。
   - 仅对当前阶段的 checklist 进行量化。

3. 根据阶段和子任务进度，生成具体可操作的建议，帮助学生推进论文。

4. 理解导师意思：
   - 分析导师沟通记录或图片内容，提炼核心关注点和建议。
   - 给出学生可执行的沟通策略。

5. 输出必须严格按照 JSON 结构：
{{
  "current_stage": "开题阶段/中期阶段/结题阶段/答辩阶段",
  "tasks_progress": {{
    "子任务名称": 完成度(0~1),
    ...
  }},
  "advice": "可操作建议文本",
  "mentor_insights": "导师意见解读及沟通建议"
}}

6. 理解阶段及子任务信息如下：
{self.stages_json}
"""

        messages = [{"role": "system", "content": system_prompt}]

        user_content = [{"type": "text", "text": user_text}]
        if image_url:
            user_content.insert(0, {"type": "image_url", "image_url": {"url": image_url}})

        messages.append({"role": "user", "content": user_content})

        try:
            completion = self.client.chat.completions.create(
                model="qwen3-vl-plus",
                messages=messages,
                stream=False,
                extra_body={"enable_thinking": enable_thinking, "thinking_budget": 81920}
            )

            content = completion.choices[0].message.content
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = {"raw_output": content, "error": "JSON解析失败"}
                
        except Exception as e:
            result = {"error": f"API调用失败: {str(e)}"}
        
        return result
    
    def show_evaluation_interface(self):
        """
        显示研究进度评估界面
        """
        st.markdown("### 📊 研究进度智能评估")
        
        # 用户输入区域
        user_text = st.text_area(
            "描述您的研究进度和遇到的问题：",
            placeholder="例如：我已经完成开题文献阅读和实验方案初步设计，但模拟实验还未完成...",
            height=150
        )
        
        # 图片上传（可选）
        uploaded_file = st.file_uploader(
            "上传导师沟通记录截图（可选）", 
            type=['png', 'jpg', 'jpeg'],
            help="可以上传与导师的聊天记录、邮件截图等"
        )
        
        image_url = None
        if uploaded_file is not None:
            # 在实际应用中，这里需要将文件上传到图床并获取URL
            # 目前先显示预览
            st.image(uploaded_file, caption="上传的图片", use_column_width=True)
            st.info("图片上传功能需要配置图床服务，目前仅作预览")
        
        # 评估按钮
        if st.button("🔍 智能评估研究进度", use_container_width=True):
            if not user_text.strip():
                st.error("请输入您的研究进度描述")
                return
            
            with st.spinner("正在分析您的研究进度..."):
                result = self.evaluate_research_progress(user_text, image_url)
            
            # 显示评估结果
            self._display_evaluation_result(result)
    
    def _display_evaluation_result(self, result):
        """
        显示评估结果
        """
        if "error" in result:
            st.error(f"评估失败: {result['error']}")
            if "raw_output" in result:
                st.text_area("原始输出", result["raw_output"], height=200)
            return
        
        # 显示当前阶段
        current_stage = result.get("current_stage", "未知阶段")
        st.markdown(f"#### 📍 当前阶段: **{current_stage}**")
        
        # 显示任务进度
        tasks_progress = result.get("tasks_progress", {})
        if tasks_progress:
            st.markdown("#### 📈 任务完成度")
            
            for task_name, progress in tasks_progress.items():
                progress_percent = int(progress * 100)
                st.markdown(f"**{task_name}**")
                st.progress(progress, text=f"{progress_percent}%")
        
        # 显示建议
        advice = result.get("advice", "")
        if advice:
            st.markdown("#### 💡 改进建议")
            st.info(advice)
        
        # 显示导师洞察
        mentor_insights = result.get("mentor_insights", "")
        if mentor_insights:
            st.markdown("#### 👨‍🏫 导师意图解读")
            st.warning(mentor_insights)
        
        # 显示原始JSON（调试用）
        with st.expander("📋 查看详细数据"):
            st.json(result)

# 创建全局评估器实例
research_evaluator = ResearchEvaluator()