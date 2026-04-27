# Rong_AiAgent

智能项目管理助手，集成 Meego 看板、飞书消息推送、定时调度等功能。

## 核心功能

- **Meego 看板通知**：自动获取看板 Tech Owner、统计需求数量，每周定期发送风险提醒
- **飞书集成**：支持发送消息、@ 用户、创建文档
- **定时调度**：支持配置化的定时任务（每周六 20:50 自动通知）
- **自动化部署**：一键部署脚本，快速在开发机持续运行

## 项目结构

```
Rong_TraeStart/
├── src/
│   ├── skills/             # 核心技能模块
│   │   ├── meego_skill.py        # Meego 看板集成（主要功能）
│   │   ├── document_skill.py     # 文档技能
│   │   └── notification_skill.py # 通知技能
│   ├── scheduler/          # 定时调度
│   │   ├── task_scheduler.py     # 任务调度器
│   │   └── start_scheduler.py    # 调度器启动入口
│   ├── integrations/       # 第三方集成
│   │   └── feishu_client.py     # 飞书 API 客户端
│   └── utils/              # 工具函数
├── scripts/                # 生产脚本
│   └── meego_regular_notification.py # Meego 定期通知
├── docs/                   # 核心文档
│   ├── feishu_setup_guide.md      # 飞书应用配置指南
│   ├── meego_notification_template.md # Meego 通知模板
│   └── scheduler_guide.md         # 调度器配置说明
├── templates/              # 文档模板
├── config/                 # 配置文件
├── deploy.sh               # 一键部署脚本
├── requirements.txt        # 依赖列表
├── .env.example            # 环境变量示例
└── README.md               # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填写配置：

```bash
cp .env.example .env
vim .env
```

配置主要内容：

```env
# 飞书配置
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_ADMIN_USER_ID=ou_xxxxxxxxxxxxx

# Meego 配置（MCP 服务器）
MEEGO_MCP_URL=https://meego.larkoffice.com/mcp_server/v1
MEEGO_MCP_TOKEN=m-xxxxxxxxxxxxx
MEEGO_PROJECT_KEY=5f6330a7796d72a1ca2278c5
MEEGO_TEMPLATE_PATH=docs/meego_notification_template.md
MEEGO_MAX_WORKITEMS=50

# 定时任务配置
MEEGO_NOTIFICATION_ENABLED=true
MEEGO_NOTIFICATION_DAY_OF_WEEK=sat  # 每周六
MEEGO_NOTIFICATION_HOUR=20          # 20 点
MEEGO_NOTIFICATION_MINUTE=50         # 50 分
```

详细飞书应用配置请参考 [飞书配置指南](docs/feishu_setup_guide.md)。

### 3. 手动测试

先运行一次通知测试是否正常：

```bash
python3 scripts/meego_regular_notification.py
```

### 4. 启动定时调度

本地测试定时任务：

```bash
python3 src/scheduler/start_scheduler.py
```

## 部署到 Openclaw 开发机

### 方式一：使用 deploy.sh（推荐）

```bash
# 1. SSH 登录开发机
ssh your-username@10.37.211.108

# 2. 克隆项目
cd /opt
sudo git clone https://github.com/maronggongzuo/Rong_AiAgent.git Rong_TraeStart
cd Rong_TraeStart

# 3. 配置环境变量
sudo cp .env.example .env
sudo vim .env  # 填入真实凭证

# 4. 一键部署！
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

### 方式二：手动部署

```bash
# 1. 创建虚拟环境
cd /opt/Rong_TraeStart
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 创建 systemd 服务
sudo cat > /etc/systemd/system/rong-agent.service << EOF
[Unit]
Description=Rong AI Agent Scheduler
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/Rong_TraeStart
Environment="PATH=/opt/Rong_TraeStart/venv/bin"
ExecStart=/opt/Rong_TraeStart/venv/bin/python /opt/Rong_TraeStart/src/scheduler/start_scheduler.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/rong-agent.log
StandardError=append:/var/log/rong-agent-error.log

[Install]
WantedBy=multi-user.target
EOF

# 3. 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable rong-agent
sudo systemctl start rong-agent
```

## 常用管理命令

```bash
# 查看服务状态
sudo systemctl status rong-agent

# 查看实时日志
sudo journalctl -u rong-agent -f

# 重启服务
sudo systemctl restart rong-agent

# 停止服务
sudo systemctl stop rong-agent

# 更新代码（已部署后）
cd /opt/Rong_TraeStart
sudo git pull
sudo systemctl restart rong-agent
```

## Meego 看板通知

### 通知模板

通知模板在 `docs/meego_notification_template.md` 中，支持以下占位符：

- `{workitems_count_1}` - 第 1 个看板的需求数量
- `{workitems_count_2}` - 第 2 个看板的需求数量
- `{owners_text_1}` - 第 1 个看板的 Tech Owner 列表（自动 @）
- `{owners_text_2}` - 第 2 个看板的 Tech Owner 列表（自动 @）

### 手动发送通知

```bash
python3 scripts/meego_regular_notification.py
```

## 飞书应用权限

在飞书开放平台为应用添加以下权限：

| 权限 | 说明 | 是否必须 |
|------|------|----------|
| `im:message` | 发送消息 | ✅ 必须 |
| `im:message.group_at_msg` | 群组 @ 消息 | ✅ 必须 |
| `contact:user.id:readonly` | 通过邮箱查询用户 ID | ✅ 必须 |
| `contact:user.base:readonly` | 获取用户基础信息 | 推荐 |
| `docx:document:create` | 创建文档 | 可选 |

## 常见问题

### Q: 如何通过邮箱查找飞书用户 ID？

**A**: 使用 `FeishuClient.find_user_by_email()` 方法

### Q: 发送消息失败怎么办？

**A**: 检查：
1. 飞书应用是否已发布
2. 是否添加了 `im:message` 权限
3. 用户 ID 格式是否正确
4. 查看错误码和日志

### Q: Meego 看板获取数据失败？

**A**: 检查：
1. `MEEGO_MCP_URL` 和 `MEEGO_MCP_TOKEN` 是否正确
2. `MEEGO_TEMPLATE_PATH` 模板路径是否正确
3. 看板链接 view_id 是否能被正确识别

## 技术栈

- **语言**: Python 3.9+
- **飞书 API**: 飞书开放平台 OpenAPI
- **Meego 集成**: Meego MCP Server
- **任务调度**: APScheduler
- **HTTP 客户端**: requests

## 许可证

MIT License
