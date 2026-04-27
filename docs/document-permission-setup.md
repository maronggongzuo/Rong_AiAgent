# 飞书文档权限配置指南

## 概述

本项目可以通过API自动创建飞书文档，并自动将管理员设置为文档协作者。

## 功能特性

✅ **创建文档** - 通过API创建飞书Docx文档  
✅ **自动发送链接** - 文档创建后自动发送链接给管理员  
✅ **自动设置权限** - （需要额外配置权限）自动将管理员设置为文档协作者（full_access权限）

## 配置步骤

### 1. 基本配置（已完成）

在 `.env` 文件中配置：

```env
# 项目名称
PROJECT_NAME=Rong_AiAgent

# 飞书应用凭证
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx
FEISHU_ADMIN_USER_ID=ou_xxxxxxxxxxxxx  # 管理员的open_id
```

### 2. 权限配置（可选但推荐）

要使用自动设置文档权限的功能，需要在飞书开放平台申请以下权限之一：

#### 推荐权限
- **`docs:permission.member:create`** - 添加云文档协作者
- **`docs:doc`** - 查看、评论、编辑和管理文档

#### 其他可选权限
- `drive:drive` - 查看、评论、编辑和管理云空间中所有文件
- `drive:file` - 上传、下载文件到云空间
- `sheets:spreadsheet` - 查看、评论、编辑和管理电子表格
- `wiki:wiki` - 查看、编辑和管理知识库
- `bitable:bitable` - 查看、评论、编辑和管理多维表格

#### 申请权限的步骤

1. 打开 [飞书开放平台](https://open.feishu.cn/)
2. 进入你的应用 → **权限管理**
3. 搜索并添加上述权限之一（推荐 `docs:permission.member:create` 或 `docs:doc`）
4. 点击 **申请开通**
5. 进入 **版本管理与发布** → 创建新版本 → 申请发布
6. 发布后，API权限设置功能即可正常工作

## 使用方法

### 基本用法

```python
from config.settings import Settings
from src.integrations.feishu_client import FeishuClient

settings = Settings()
client = FeishuClient(settings)

# 创建文档（默认会自动发送链接并尝试设置权限）
result = client.create_document("我的项目文档", "")
```

### 自定义参数

```python
# 创建文档但不发送通知
result = client.create_document("我的项目文档", "", notify_admin=False)

# 创建文档但不设置权限
result = client.create_document("我的项目文档", "", grant_admin_permission=False)

# 两者都不做
result = client.create_document("我的项目文档", "", notify_admin=False, grant_admin_permission=False)
```

## 测试

运行完整测试：

```bash
python examples/test_feishu.py
```

这会测试：
1. 基础连接
2. 发送文本消息
3. 发送任务提醒
4. 创建文档（含自动发送链接和权限设置）

## 权限配置前后对比

### 配置权限前
- ✅ 可以创建文档
- ✅ 可以发送文档链接
- ⚠️ 权限设置会失败，但代码会自动处理并继续
- 📝 需要在飞书网页中手动设置权限

### 配置权限后
- ✅ 可以创建文档
- ✅ 可以发送文档链接
- ✅ 可以自动设置管理员为文档协作者（full_access权限）
- 🎉 管理员可以直接访问文档，无需手动设置权限

## 代码实现细节

### 新增方法

1. **`create_document`** - 创建文档，可配置是否发送通知和设置权限
2. **`_grant_admin_permission_to_doc`** - 设置文档权限
3. **`_send_doc_link_to_admin`** - 发送文档链接

### 权限设置API

使用飞书API：
- **接口**: `POST /open-apis/drive/v1/permissions/{doc_id}/members`
- **参数**:
  - `member_type`: "openid"
  - `member_id`: 用户的open_id
  - `perm`: "full_access" （可管理权限）

## 常见问题

### Q: 权限设置失败了怎么办？
A: 代码会自动处理失败情况，继续执行其他功能。你仍会收到文档链接，只需在飞书网页中手动设置权限即可。

### Q: 如何测试权限设置功能？
A: 在飞书开放平台配置权限后，再次运行 `python examples/test_feishu.py`，看日志中是否显示"文档权限设置成功"。

### Q: full_access权限有哪些功能？
A: full_access权限允许：
- 查看和编辑文档
- 管理协作者
- 分享文档
- 管理文档权限设置
- 删除文档

### Q: 没有权限配置，功能还能用吗？
A: 完全可以！文档创建和消息发送功能都正常工作，只是需要手动设置文档权限。

## 相关文件

- `src/integrations/feishu_client.py` - 飞书API客户端实现
- `config/settings.py` - 配置管理
- `examples/test_feishu.py` - 飞书功能测试脚本

## 总结

项目已经完全可用！权限配置是可选但推荐的，配置后可以提供更流畅的使用体验。
