# 飞书应用创建指南

## 步骤 1：创建飞书企业自建应用

1. 访问 [飞书开放平台](https://open.feishu.cn)
2. 登录你的飞书账号
3. 进入 **开发者后台** → **应用管理**
4. 点击 **创建应用** → **企业自建应用**
5. 填写应用信息：
   - 应用名称：Rong_AiAgent
   - 应用描述：智能Rong_AiAgent
6. 点击 **确定创建**

## 步骤 2：获取凭证

在应用详情页的 **凭证与基础信息** 中，你可以获取到：
- **App ID**（应用 ID）
- **App Secret**（应用密钥）

## 步骤 3：添加应用能力

1. 进入 **添加应用能力**
2. 添加 **机器人** 能力
3. 开启机器人功能

## 步骤 4：配置权限

在 **权限管理** 中，添加以下权限：
- `im:message` - 发送消息
- `im:message.group_at_msg` - 群组 @ 消息
- `docs:document` - 文档操作（可选）

## 步骤 5：发布应用

1. 进入 **版本管理与发布**
2. 创建一个版本
3. 申请发布（如果是企业内部使用，可直接发布）

## 步骤 6：获取用户 ID

1. 在飞书中打开用户的个人信息页
2. 或者通过 API 获取用户 ID

## 配置到项目

将获取到的凭证填写到 `.env` 文件中：

```env
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_BOT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
```

## 测试消息推送

配置完成后，运行飞书测试脚本。
