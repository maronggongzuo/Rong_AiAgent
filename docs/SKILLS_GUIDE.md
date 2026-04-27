# Skills 使用指南

本指南介绍Rong_AiAgent中的技能系统，包括：
- 项目中已有的 skills
- 如何使用市场成熟的 skills
- 如何创建新 skill

---

## 📦 项目中已有的 Skills

### 1. NotificationSkill - 通知技能

**文件**：`src/skills/notification_skill.py`

**功能**：
- 发送任务提醒
- 发送项目周报
- 发送自定义通知

**使用示例**：
```python
from config.settings import Settings
from src.skills.notification_skill import NotificationSkill

settings = Settings()
skill = NotificationSkill(settings)

# 发送任务提醒
result = skill.send_task_reminder(
    task_name="完成项目文档",
    deadline="2024-01-31",
    user_id="ou_e47357c17dcbb2d3517f9e5520790f24"
)
```

---

### 2. DocumentSkill - 文档技能

**文件**：`src/skills/document_skill.py`

**功能**：
- 生成文档（按模板）
- 解析文档

**使用示例**：
```python
from config.settings import Settings
from src.skills.document_skill import DocumentSkill

settings = Settings()
skill = DocumentSkill(settings)

# 生成文档
result = skill.execute(
    action="generate",
    template="project_report",
    data={"project_name": "Rong_AiAgent"}
)
```

---

### 3. GithubSkill - GitHub 技能（新）

**文件**：`src/skills/github_skill.py`

**功能**：
- 获取仓库列表
- 获取 Issues
- 创建 Issue

**使用示例**：
```python
from config.settings import Settings
from src.skills.github_skill import GithubSkill

settings = Settings()
skill = GithubSkill(settings)

# 获取仓库
result = skill.execute(action="get_repos", username="your-username")
```

---

### 4. GanttSkill - 甘特图技能（新）

**文件**：`src/skills/gantt_skill.py`

**功能**：
- 分析项目进度
- 获取延期任务
- 生成甘特图报告

**使用示例**：
```python
from config.settings import Settings
from src.skills.gantt_skill import GanttSkill

settings = Settings()
skill = GanttSkill(settings)

# 分析项目
result = skill.execute(
    action="analyze",
    project_name="Rong_AiAgent",
    tasks=[
        {"name": "任务1", "status": "completed"},
        {"name": "任务2", "status": "in_progress"}
    ]
)
```

---

## 🚀 如何使用市场成熟的 Skills

### 方案 1：集成 LangChain

**LangChain** 是目前最流行的 AI 应用开发框架，提供大量现成的工具链。

#### 安装
```bash
pip install langchain langchain-openai
```

#### 集成示例
```python
# src/skills/langchain_skill.py
from .base_skill import BaseSkill
from langchain.agents import Tool
from langchain.agents import initialize_agent
from langchain.llms import OpenAI

class LangChainSkill(BaseSkill):
    """集成 LangChain 的技能"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.name = "langchain"
        self.llm = OpenAI(temperature=0)
        
    def execute(self, **kwargs):
        """执行 LangChain Agent"""
        prompt = kwargs.get("prompt", "")
        
        tools = [
            Tool(
                name="Search",
                func=self._search_web,
                description="搜索网络获取信息"
            )
        ]
        
        agent = initialize_agent(
            tools,
            self.llm,
            agent="zero-shot-react-description"
        )
        
        result = agent.run(prompt)
        return {"success": True, "result": result}
```

---

### 方案 2：集成 Hugging Face Agents

**Hugging Face Agents** 提供大量预训练的 AI 工具。

#### 安装
```bash
pip install transformers
```

#### 集成示例
```python
# src/skills/huggingface_skill.py
from .base_skill import BaseSkill
from transformers import pipeline

class HuggingFaceSkill(BaseSkill):
    """Hugging Face 技能"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.name = "huggingface"
        self.summarizer = pipeline("summarization")
        
    def execute(self, **kwargs):
        """执行摘要"""
        text = kwargs.get("text", "")
        
        summary = self.summarizer(text, max_length=50)
        return {"success": True, "summary": summary}
```

---

### 方案 3：集成 Semantic Kernel（微软）

**Semantic Kernel** 是微软开源的企业级 AI 应用框架。

#### 安装
```bash
pip install semantic-kernel
```

---

## 📝 如何创建新 Skill

### 步骤 1：继承 BaseSkill

```python
from .base_skill import BaseSkill

class MyNewSkill(BaseSkill):
    """我的新技能"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.name = "my_new_skill"
```

### 步骤 2：实现 execute 方法

```python
    def execute(self, **kwargs):
        """执行技能"""
        action = kwargs.get("action", "default")
        
        if action == "something":
            return self._do_something(**kwargs)
        
        return {"success": False, "error": "未知操作"}
```

### 步骤 3：注册到 Agent

在 `src/agent/project_agent.py` 的 `_init_skills` 中添加：

```python
from src.skills.my_new_skill import MyNewSkill

self.skills["my_new_skill"] = MyNewSkill(self.settings)
```

---

## 🎯 推荐的市场成熟 Skills

### 1. 文档处理类
- **LangChain Document Loaders** - 读取各种格式文档
- **Unstructured.io** - 文档解析

### 2. 网络搜索类
- **SerpAPI** - 搜索引擎集成
- **DuckDuckGo** - 免费搜索

### 3. 项目管理类
- **GitHub API** - 代码仓库管理
- **Jira API** - 问题跟踪
- **Trello API** - 看板管理

### 4. 数据分析类
- **Pandas** - 数据处理
- **Matplotlib** - 数据可视化

---

## 🔧 完整使用示例

```python
from config.settings import Settings
from src.agent.project_agent import ProjectAgent

settings = Settings()
agent = ProjectAgent(settings)

# 执行通知技能
result = agent.execute_skill(
    "notification",
    action="send_task_reminder",
    task_name="测试任务",
    deadline="2024-02-01",
    user_id="ou_e47357c17dcbb2d3517f9e5520790f24"
)

# 执行 GitHub 技能
result = agent.execute_skill(
    "github",
    action="get_repos",
    username="octocat"
)

# 执行甘特图技能
result = agent.execute_skill(
    "gantt",
    action="analyze",
    project_name="我的项目",
    tasks=[
        {"name": "任务1", "status": "completed"},
        {"name": "任务2", "status": "delayed"}
    ]
)
```

---

## 📚 更多资源

- **LangChain 文档**：https://python.langchain.com
- **Hugging Face**：https://huggingface.co
- **Semantic Kernel**：https://github.com/microsoft/semantic-kernel
- **飞书开放平台**：https://open.feishu.cn
