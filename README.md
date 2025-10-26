# ReSocial 科研训练系统

一个基于 Streamlit 的科研训练平台，通过模块化设计提供系统化的科研阶段训练、AI导师指导和进度跟踪功能。

## 项目概述

ReSocial 科研训练系统旨在帮助研究人员系统化地完成科研各阶段，通过AI导师提供专业指导，并实时跟踪研究进度和成果。系统采用模块化架构设计，具有良好的可维护性和扩展性。

## 功能特性

### 核心功能
- **四阶段科研训练**：涵盖选题、文献综述、实验设计和论文写作四个核心科研阶段
- **AI导师指导**：集成 DeepSeek API 提供专业科研指导
- **进度跟踪**：实时追踪任务完成情况和得分
- **任务清单**：每个课题配备详细的任务清单和权重分配
- **多课题支持**：每个阶段支持多个具体训练课题

### 用户界面
- 响应式布局设计
- 阶段选择卡片界面
- 多标签页主界面
- 实时聊天交互
- 功能面板和侧边栏导航

## 项目结构

```
hackathon/
├── app.py                          # 主应用入口
├── requirements.txt               # Python依赖包
├── README.md                      # 项目文档
├── .env.example                   # 环境变量示例
├── 系统设计文档.md                 # 系统设计文档
│
├── assets/                        # 配置文件目录
│   ├── stages.json               # 阶段配置
│   ├── topics.json               # 课题配置
│   ├── checklists.json           # 任务清单配置
│   ├── ui_config.json            # 界面配置
│   ├── chat_config.json          # 聊天配置
│   └── function_panel_config.json # 功能面板配置
│
└── modules/                       # 模块化代码目录
    ├── app.py                    # 主应用类
    ├── config.py                 # 配置和样式管理
    ├── session_manager.py        # 会话状态管理
    ├── api_client.py             # API通信管理
    ├── progress_tracker.py       # 进度追踪管理
    ├── ui_components.py          # UI组件管理
    ├── data_loader.py            # 数据加载模块
    └── stage_selection.py        # 阶段选择模块
```

## 模块说明

### 核心模块

#### app.py
主应用入口点，负责初始化应用程序并协调各模块工作。

#### modules/app.py
主应用类，实现页面路由和模块协调。

#### modules/config.py
- 页面配置管理
- 自定义样式应用
- 页面状态常量定义

#### modules/session_manager.py
- 会话状态初始化和管理
- 用户进度数据持久化
- 聊天历史管理

#### modules/api_client.py
- DeepSeek API 通信
- 消息发送和响应处理
- 错误处理和重试机制

#### modules/progress_tracker.py
- 用户进度计算和更新
- 任务清单状态管理
- 得分统计和进度报告

#### modules/ui_components.py
- 所有UI组件的渲染
- 侧边栏管理
- 聊天界面和功能面板

#### modules/data_loader.py
- 配置文件加载和缓存
- 数据访问接口
- 错误处理和默认值提供

#### modules/stage_selection.py
- 阶段选择页面渲染
- 阶段卡片设计和交互

## 安装和运行

### 环境要求
- Python 3.8+
- Streamlit 1.28+
- 有效的 DeepSeek API 密钥

### 安装步骤

1. 克隆项目到本地
```bash
git clone <repository-url>
cd hackathon
```

2. 安装依赖包
```bash
pip install -r requirements.txt
```

3. 配置环境变量（可选）
```bash
cp .env.example .env
# 编辑 .env 文件，添加你的 DeepSeek API 密钥
```

4. 运行应用程序
```bash
streamlit run app.py
```

### 依赖包

主要依赖包列表：
- streamlit：Web应用框架
- requests：HTTP请求库
- plotly：数据可视化

完整依赖见 `requirements.txt` 文件。

## 配置说明

### 阶段配置 (stages.json)
定义四个科研阶段的基本信息：
- 阶段ID和名称
- 图标和颜色
- 描述信息

### 课题配置 (topics.json)
定义每个阶段的具体训练课题：
- 课题ID和名称
- 所属阶段ID
- 详细描述

### 任务清单配置 (checklists.json)
定义每个课题的任务清单：
- 清单ID和名称
- 所属课题ID
- 任务项列表（含权重）

### 界面配置 (ui_config.json)
应用程序界面配置：
- 应用标题和主题
- 各页面标题和描述
- 按钮文本和提示信息

### 聊天配置 (chat_config.json)
AI聊天功能配置：
- API端点配置
- 模型参数设置
- 系统提示词

## 使用指南

### 开始使用

1. **选择科研阶段**
   - 在首页选择当前所处的科研阶段
   - 系统提供四个核心阶段：选题、文献综述、实验设计、论文写作

2. **选择训练课题**
   - 在侧边栏选择具体的训练课题
   - 每个阶段包含多个针对性课题

3. **与AI导师交流**
   - 在主界面与AI导师进行实时对话
   - 提供DeepSeek API密钥以启用AI功能

4. **完成任务清单**
   - 在侧边栏查看和完成课题任务
   - 系统自动跟踪完成进度和得分

5. **查看进度报告**
   - 在功能面板查看当前得分和完成率
   - 在系统信息区域查看整体进度

### API配置

要使用AI导师功能，需要配置 DeepSeek API：

1. 获取 DeepSeek API 密钥
2. 在聊天界面输入API密钥
3. 开始与AI导师对话

## 开发说明

### 模块化设计原则

系统采用单一职责原则，每个模块负责特定的功能领域：

- **数据层**：`data_loader.py` 负责所有数据访问
- **业务逻辑层**：各功能模块处理具体业务逻辑
- **表示层**：`ui_components.py` 负责界面渲染

### 扩展开发

添加新功能的建议步骤：

1. 在相应模块中添加新功能方法
2. 更新配置文件以支持新功能
3. 在UI组件中集成新功能界面
4. 更新会话状态管理（如需要）

### 自定义配置

可以通过修改JSON配置文件来自定义：

- 添加新的科研阶段
- 创建新的训练课题
- 调整任务清单和权重
- 修改界面文本和样式

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 验证API配额和限制

2. **界面显示异常**
   - 清除浏览器缓存
   - 检查配置文件格式
   - 验证依赖包版本

3. **进度数据丢失**
   - Streamlit会话状态在页面刷新时会重置
   - 重要进度建议定期导出备份

### 日志和调试

启用Streamlit调试模式：
```bash
streamlit run app.py --logger.level=debug
```

## 技术架构

### 前端技术
- Streamlit Web框架
- 自定义CSS样式
- Plotly数据可视化

### 后端技术
- Python 3.8+
- 模块化架构设计
- 会话状态管理

### 数据存储
- JSON配置文件
- Streamlit会话状态
- 本地文件缓存

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v1.0.0
- 初始版本发布
- 模块化架构重构
- 四阶段科研训练系统
- AI导师集成
- 进度跟踪功能