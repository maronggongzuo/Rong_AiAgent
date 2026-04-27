# 调度器使用指南

## 快速启动

### 方式 1：使用主程序（推荐）
主程序已经包含调度器功能：
```bash
python3 src/main.py
```

### 方式 2：仅启动调度器
如果只需要定时任务，不需要其他功能：
```bash
python3 scripts/start_scheduler.py
```

## Meego 定时任务配置

在 `.env` 文件中配置：

```env
# 启用/禁用 Meego 定时通知
MEEGO_NOTIFICATION_ENABLED=true

# 星期几: mon, tue, wed, thu, fri, sat, sun
MEEGO_NOTIFICATION_DAY_OF_WEEK=sat

# 小时 (0-23)
MEEGO_NOTIFICATION_HOUR=20

# 分钟 (0-59)
MEEGO_NOTIFICATION_MINUTE=50
```

## 配置说明

### 星期几取值
- `mon` - 周一
- `tue` - 周二
- `wed` - 周三
- `thu` - 周四
- `fri` - 周五
- `sat` - 周六
- `sun` - 周日

### 多个时间点
如果需要多个时间点，可以修改 `src/scheduler/task_scheduler.py` 中的 `_init_default_jobs()` 方法。

## 其他 Meego 配置

```env
# Meego MCP 服务器配置
MEEGO_MCP_URL=https://meego.larkoffice.com/mcp_server/v1
MEEGO_MCP_TOKEN=your_mcp_token
MEEGO_PROJECT_KEY=5f6330a7796d72a1ca2278c5

# 最多检查多少个工作项（提高性能）
MEEGO_MAX_WORKITEMS=10

# 飞书管理员用户 ID（接收通知）
FEISHU_ADMIN_USER_ID=ou_e47357c17dcbb2d3517f9e5520790f24
```

## 手动触发通知

如果想立即测试通知，可以运行：
```bash
python3 scripts/meego_regular_notification.py
```

## 生产部署建议

### 使用 systemd (Linux)
创建 `/etc/systemd/system/meego-scheduler.service`：
```ini
[Unit]
Description=Meego Scheduler
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/Rong_TraeStart
ExecStart=/path/to/venv/bin/python scripts/start_scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable meego-scheduler
sudo systemctl start meego-scheduler
sudo systemctl status meego-scheduler
```

### 使用 nohup
```bash
nohup python3 scripts/start_scheduler.py > scheduler.log 2>&1 &
```

### 使用 PM2
```bash
npm install -g pm2
pm2 start scripts/start_scheduler.py --name meego-scheduler
pm2 save
pm2 startup
```

## 日志查看

调度器运行时会输出详细日志，包含：
- 任务启动信息
- 配置信息
- 任务执行情况
- 错误信息
