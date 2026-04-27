#!/usr/bin/env python3
"""飞书 API 测试脚本"""

import sys
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def test_basic_connection():
    """测试基础连接"""
    print("=== 测试 1: 基础连接 ===")
    
    settings = Settings()
    client = FeishuClient(settings)
    
    if client.use_mock:
        print("✓ 使用模拟模式（未配置飞书凭证）")
    else:
        print("✓ 使用真实 API 模式")
        token = client._get_tenant_access_token()
        if token:
            print("✓ Token 获取成功")
        else:
            print("✗ Token 获取失败")
    
    return client, settings


def test_send_text_message(client: FeishuClient, admin_user_id: str):
    """测试发送文本消息"""
    print("\n=== 测试 2: 发送文本消息 ===")
    
    test_message = "👋 你好！这是来自Rong_AiAgent的测试消息。\n\n📅 项目进度：50%\n✅ 已完成任务：10 个\n⏳ 待完成任务：5 个"
    
    result = client.send_text_message(admin_user_id, test_message)
    
    if result.get("code") == 0:
        print("✓ 文本消息发送成功")
        if result.get("data", {}).get("mock"):
            print("  (模拟模式，消息未真实发送)")
        else:
            print(f"  消息 ID: {result.get('data', {}).get('message_id')}")
            print("  消息已发送到你的飞书中！")
    else:
        print(f"✗ 消息发送失败: {result.get('msg')}")
    
    return result


def test_send_task_reminder(client: FeishuClient, admin_user_id: str):
    """测试发送任务提醒"""
    print("\n=== 测试 3: 发送任务提醒 ===")
    
    reminder_message = """
⚠️ 任务提醒

📋 任务：完成Rong_AiAgent开发
📅 截止日期：2024-01-20
⏰ 剩余时间：5 天

当前进度：
✅ 项目架构 - 已完成
✅ 文档生成 - 已完成
⏳ 飞书集成 - 进行中
⏳ 任务调度 - 待开始

请抓紧时间！🚀
    """.strip()
    
    result = client.send_text_message(admin_user_id, reminder_message)
    
    if result.get("code") == 0:
        print("✓ 任务提醒发送成功")
        print("  提醒已发送到你的飞书中！")
    else:
        print(f"✗ 任务提醒发送失败: {result.get('msg')}")
    
    return result


def test_create_document(client: FeishuClient):
    """测试创建飞书文档"""
    print("\n=== 测试 4: 创建飞书文档 ===")
    
    doc_title = "Rong_AiAgent - 测试文档"
    doc_content = ""
    
    result = client.create_document(doc_title, doc_content)
    
    if result.get("success"):
        print("✓ 文档创建成功")
        print(f"  文档标题: {result.get('title')}")
        print(f"  文档链接: {result.get('document_url')}")
        print(f"  文档 ID: {result.get('document_id')}")
        if result.get("mock"):
            print("  (模拟模式)")
    else:
        print("✗ 文档创建失败")
        print(f"  错误: {result.get('msg')}")
    
    return result


def main():
    """主函数"""
    print("=" * 50)
    print("飞书 API 测试")
    print("=" * 50)
    
    print("\n📖 提示：")
    print("  - 如果未配置飞书凭证，将使用模拟模式")
    print("  - 如需真实测试，请在 .env 文件中配置：")
    print("    FEISHU_APP_ID=your_app_id")
    print("    FEISHU_APP_SECRET=your_app_secret")
    print("  - 详细创建指南请查看 docs/feishu_setup_guide.md")
    print()
    
    try:
        client, settings = test_basic_connection()
        admin_user_id = settings.FEISHU_ADMIN_USER_ID
        
        test_send_text_message(client, admin_user_id)
        test_send_task_reminder(client, admin_user_id)
        test_create_document(client)
        
        print("\n" + "=" * 50)
        print("✓ 所有测试完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
