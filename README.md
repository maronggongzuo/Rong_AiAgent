# Rong_AiAgent

智能Rong_AiAgent，支持飞书消息推送、文档生成、Meego 看板集成、任务调度等功能。

## 项目结构

```
Rong_TraeStart/
├── src/
│   ├── agent/              # Agent 核心模块
│   │   └── project_agent.py    # 主 Agent 类
│   ├── skills/             # 技能模块
│   │   ├── base_skill.py       # 技能基类
│   │   ├── notification_skill.py  # 通知技能
│   │   ├── document_skill.py     # 文档技能
│   │   ├── meego_skill.py        # Meego 看板集成技能
│   │   ├── gantt_skill.py        # 甘特图技能
│   │   └── github_skill.py       # GitHub 集成技能
│   ├── scheduler/          # 调度器模块
│   │   └── task_scheduler.py    # 任务调度器
│   ├── document/           # 文档处理模块
│   │   └── document_generator.py # 文档生成器
│   ├── chatbot/            # 问答机器人模块
│   │   └── qa_bot.py           # 问答机器人
│   ├── integrations/       # 第三方集成
│   │   └── feishu_client.py     # 飞书 API 客户端
│   ├── utils/              # 工具函数
│   └── main.py             # 主入口
├── examples/               # 示例脚本
├── docs/                   # 文档目录
│   ├── feishu_setup_guide.md    # 飞书应用配置指南
│   └── meego_notification_template.md # Meego 通知模板
├── templates/              # 文档模板
├── tests/                  # 测试文件
├── config/                 # 配置文件
├── .env                    # 环境变量
└── README.md               # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置飞书应用

复制 `.env.example` 为 `.env`，并填写飞书应用凭证：

```env
# 飞书配置
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
```

详细配置步骤请参考 [飞书应用配置指南](docs/feishu_setup_guide.md)。

### 3. 配置 Meego（可选）

如果需要使用 Meego 看板集成功能，在 `.env` 中添加：

```env
# Meego 配置（MCP 服务器）
MEEGO_MCP_URL=https://meego.larkoffice.com/mcp_server/v1
MEEGO_MCP_TOKEN=m-xxxxxxxxxxxxx
```

### 4. 运行测试

```bash
# 验证飞书配置
python3 examples/verify_feishu.py

# 发送测试消息
python3 examples/test_multiple_id_types.py

# 测试 Meego 看板通知
python3 examples/test_dual_board_notification.py
```

---

## 飞书交互能力

### 1. 文本消息发送

**使用场景**：发送普通文本通知、提醒、消息

**调用方法**：

```python
from config.settings import Settings
from src.integrations.feishu_client import FeishuClient

settings = Settings()
client = FeishuClient(settings)

# 发送文本消息
result = client.send_text_message(
    user_id="ou_e47357c17dcbb2d3517f9e5520790f24",
    text="你好！这是一条测试消息",
    receive_id_type="open_id"  # 可选: open_id, user_id, union_id
)
```

**示例脚本**：
```bash
python3 examples/test_multiple_id_types.py
python3 examples/interactive_send.py <用户ID>
```

---

### 2. 任务提醒

**使用场景**：项目任务截止提醒、进度更新提醒

**调用方法**：

```python
from config.settings import Settings
from src.skills.notification_skill import NotificationSkill

settings = Settings()
skill = NotificationSkill(settings)

# 发送任务提醒
result = skill.send_task_reminder(
    task_name="完成项目文档",
    deadline="2024-01-31",
    user_id="ou_e47357c17dcbb2d3517f9e5520790f24",
    progress=50,  # 可选：进度百分比
    assignee="张三"  # 可选：负责人
)
```

---

### 3. 项目周报

**使用场景**：定期发送项目进度摘要、周报

**调用方法**：

```python
from config.settings import Settings
from src.skills.notification_skill import NotificationSkill

settings = Settings()
skill = NotificationSkill(settings)

# 发送项目周报
result = skill.send_project_summary(
    project_name="Rong_AiAgent",
    user_ids=["ou_e47357c17dcbb2d3517f9e5520790f24"],
    completed_tasks=10,
    total_tasks=20,
    milestone="一期开发完成"  # 可选：里程碑
)
```

---

### 4. 通用通知

**使用场景**：自定义消息、批量发送通知

**调用方法**：

```python
from config.settings import Settings
from src.skills.notification_skill import NotificationSkill

settings = Settings()
skill = NotificationSkill(settings)

# 发送通用通知
result = skill.execute(
    message="系统维护通知：今晚 19:00-21:00 系统维护",
    recipients=["ou_e47357c17dcbb2d3517f9e5520790f24"],
    channel="feishu"
)
```

---

### 5. 通过邮箱查找用户 ID

**使用场景**：通过员工邮箱查找飞书用户 ID

**调用方法**：

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient

settings = Settings()
client = FeishuClient(settings)

# 查找用户 ID
token = client._get_tenant_access_token()
if token:
    import requests
    url = f"{client.BASE_URL}/contact/v3/users/batch_get_id"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"emails": ["marong.01@bytedance.com"]}
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if result.get("code") == 0:
        user_list = result.get("data", {}).get("user_list", [])
        for user in user_list:
            print(f"邮箱: {user['email']}, 用户ID: {user['user_id']}")
```

**示例脚本**：
```bash
python3 examples/find_user_by_email.py <邮箱>
python3 examples/debug_email_search.py
```

---

### 6. 文档生成

**使用场景**：根据模板生成项目报告、会议纪要

**调用方法**：

```python
from src.document.document_generator import DocumentGenerator

# 创建文档生成器
generator = DocumentGenerator(templates_dir="templates")

# 准备数据
data = {
    "project_name": "Rong_AiAgent",
    "report_date": "2024-01-20",
    "status": "进行中",
    "progress_summary": "项目已完成基础架构搭建",
    "milestones": "- 架构设计: 完成\n- 核心开发: 进行中",
    "risks": "- 暂无"
}

# 生成文档
content = generator.generate("project_report", data)

# 保存文档
generator.save_document(content, "data/output/project_report.md")
```

**示例脚本**：
```bash
python3 examples/example_usage.py
```

---

### 7. 富文本消息

**使用场景**：发送格式化的富文本消息

**调用方法**：

```python
from config.settings import Settings
from src.integrations.feishu_client import FeishuClient

settings = Settings()
client = FeishuClient(settings)

# 富文本内容
elements = [
    [
        {"tag": "text", "text": "这是一段富文本消息"},
        {"tag": "a", "text": "点击链接", "href": "https://feishu.cn"}
    ]
]

result = client.send_rich_text(
    user_id="ou_e47357c17dcbb2d3517f9e5520790f24",
    title="富文本消息",
    elements=elements
)
```

---

### 8. 卡片消息

**使用场景**：发送交互式卡片消息

**调用方法**：

```python
from config.settings import Settings
from src.integrations.feishu_client import FeishuClient

settings = Settings()
client = FeishuClient(settings)

# 卡片内容
card = {
    "header": {
        "title": {
            "content": "项目进度更新",
            "tag": "plain_text"
        }
    },
    "elements": [
        {
            "tag": "div",
            "text": {
                "content": "整体进度: 50%",
                "tag": "lark_md"
            }
        }
    ]
}

result = client.send_card_message(
    user_id="ou_e47357c17dcbb2d3517f9e5520790f24",
    card=card
)
```

---

### 9. 飞书文档创建

**使用场景**：在飞书中自动创建文档并设置权限

**调用方法**：

```python
from config.settings import Settings
from src.skills.document_skill import DocumentSkill

settings = Settings()
skill = DocumentSkill(settings)

# 创建文档
result = skill.create_document(
    title="项目周报",
    content="这是文档内容...",
    folder_token=None  # 可选：指定文件夹
)

# 转移文档所有权
if settings.FEISHU_ADMIN_USER_ID:
    skill.transfer_owner(
        document_token=result["document_token"],
        owner_user_id=settings.FEISHU_ADMIN_USER_ID
    )
```

**示例脚本**：
```bash
python3 examples/test_doc_create.py
python3 examples/test_doc_with_permission.py
```

---

## Meego 看板集成

### 1. 获取看板 Tech Owner

**使用场景**：从 Meego 看板中自动获取工作项的 Tech Owner 信息

**调用方法**：

```python
from config.settings import Settings
from src.skills.meego_skill import MeegoSkill

settings = Settings()
skill = MeegoSkill(settings)

# 获取单个看板的 Tech Owner
result = skill.get_board_tech_owners(
    board_url="https://meego.larkoffice.com/pnsi/storyView/Ztxhe1ZDR",
    view_id="Ztxhe1ZDR",
    project_key="5f6330a7796d72a1ca2278c5"
)

if result["success"]:
    tech_owners = result["tech_owners"]
    owner_names = [owner["name"] for owner in tech_owners]
    print(f"Tech Owner: {', '.join(owner_names)}")
```

---

### 2. 双看板通知

**使用场景**：从通知模板中识别多个看板链接，获取各自的 Tech Owner，分别填入对应位置并发送通知

**调用方法**：

```python
from config.settings import Settings
from src.skills.meego_skill import MeegoSkill
from pathlib import Path

settings = Settings()
skill = MeegoSkill(settings)

template_path = Path(__file__).parent.parent / "docs" / "meego_notification_template.md"

# 查看完整示例：examples/test_dual_board_notification.py
```

**示例脚本**：
```bash
python3 examples/test_dual_board_notification.py
```

**通知模板格式**（`docs/meego_notification_template.md`）：
```markdown
各位同学好，本周 Meego 相关指标风险看板已更新，请大家关注并及时调整：

本周上线延期风险需求列表： [看板1](https://meego.larkoffice.com/pnsi/storyView/Ztxhe1ZDR)
请相关同学 {owners_text_1} ，参照：Data Protection -- Meego指标说明 & 操作手册 操作、调整。

本周大颗粒度/长周期需求列表： [看板2](https://meego.larkoffice.com/pnsi/storyView/2FwTFmZDR)
请相关同学 {owners_text_2} ，参照：Data Protection -- Meego指标说明 & 操作手册 操作、调整。
```

---

### 3. Meego 看板通知

**使用场景**：发送单个 Meego 看板的更新通知

**调用方法**：

```python
from config.settings import Settings
from src.skills.meego_skill import MeegoSkill

settings = Settings()
skill = MeegoSkill(settings)

# 发送看板通知
result = skill.send_meego_notification(
    chat_id="oc_cd69241da2c4b87b",  # 群聊 ID
    board_url="https://meego.larkoffice.com/pnsi/storyView/Ztxhe1ZDR",
    template="default",
    recipients=["ou_e47357c17dcbb2d3517f9e5520790f24"]  # 可选：额外通知的用户
)
```

**示例脚本**：
```bash
python3 examples/test_meego_real.py
```

---

## 完整示例

### 示例 1：端到端测试

```bash
python3 examples/example_usage.py
```

### 示例 2：飞书功能完整测试

```bash
python3 examples/test_notifications.py
```

### 示例 3：通过邮箱查找并发送消息

```bash
python3 examples/find_user_by_email.py marong.01@bytedance.com
# 然后使用找到的用户 ID 发送消息
python3 examples/interactive_send.py <找到的用户ID>
```

### 示例 4：Meego 双看板通知

```bash
python3 examples/test_dual_board_notification.py
```

---

## 权限配置

### 飞书应用权限

在飞书开放平台为应用添加以下权限：

| 权限 | 说明 | 是否必须 |
|------|------|----------|
| `im:message` | 发送消息 | ✅ 必须 |
| `contact:user.id:readonly` | 通过邮箱查询用户 ID | ✅ 推荐 |
| `contact:user.base:readonly` | 获取用户基础信息 | 可选 |
| `docx:document:create` | 创建文档 | 可选 |
| `docx:document:manage` | 管理文档权限 | 可选 |

### Meego MCP 配置

需要配置 Meego MCP 服务器连接信息：
- `MEEGO_MCP_URL`：Meego MCP 服务器地址
- `MEEGO_MCP_TOKEN`：Meego MCP 访问令牌

---

## 常见问题

### Q: 如何获取用户 ID？

**A**: 
1. 通过邮箱查找：使用 `examples/find_user_by_email.py`
2. 在飞书开放平台的事件日志中查看
3. 在飞书中给机器人发送消息，然后从回调中获取

### Q: 发送消息失败怎么办？

**A**: 检查以下几点：
1. 确保应用已发布
2. 确保已添加 `im:message` 权限
3. 检查用户 ID 格式是否正确（尝试 open_id, user_id, union_id）
4. 查看错误码和错误信息

### Q: 支持哪些用户 ID 类型？

**A**: 支持三种：
- `open_id`：应用内用户唯一标识（推荐）
- `user_id`：租户内用户唯一标识
- `union_id`：跨应用用户唯一标识

### Q: 如何获取群聊 ID？

**A**: 
1. 将机器人添加到目标群聊
2. 在群聊中发送消息并 @ 机器人
3. 通过飞书开放平台的事件回调获取群聊 ID

### Q: Meego 看板获取 Tech Owner 失败？

**A**: 
1. 检查 `MEEGO_MCP_URL` 和 `MEEGO_MCP_TOKEN` 是否正确配置
2. 确认 view_id 和 project_key 是否正确
3. 查看日志中的详细错误信息

---

## 下一步开发

- [ ] GitHub 集成 - 自动获取代码提交和 PR 状态
- [x] Meego 看板集成 - 获取 Tech Owner、发送通知
- [ ] 甘特图分析 - 自动解析项目进度并发送提醒
- [ ] 更多消息类型 - 图片、文件、投票等
- [ ] 飞书机器人回调 - 接收并响应用户消息
- [ ] 飞书文档集成 - 直接在飞书中创建和编辑文档
- [ ] 数据持久化 - 保存项目和任务数据

---

## 技术栈

- **语言**: Python 3.9+
- **飞书 API**: 飞书开放平台 OpenAPI
- **Meego 集成**: Meego MCP Server
- **任务调度**: APScheduler (可选)
- **HTTP 客户端**: requests

---

## 许可证

MIT License
