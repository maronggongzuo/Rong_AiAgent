#!/usr/bin/env python3
"""交互式发送消息"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def send_test_message(user_id):
    """发送测试消息"""
    settings = Settings()
    client = FeishuClient(settings)
    
    message = """🎉 恭喜！Rong_AiAgent已成功连接飞书！

📋 可用功能：
• 任务提醒 - 截止日期前自动提醒
• 项目周报 - 定期发送项目进度
• 文档生成 - 按模板生成项目文档
• 智能问答 - 基于项目文档回答问题

💬 这是一条测试消息，说明配置成功！

—— Rong_AiAgent 🤖
"""
    
    print(f"\n📤 正在发送消息给用户: {user_id}")
    result = client.send_text_message(user_id, message)
    
    return result


def main():
    print("=" * 60)
    print("📤 发送飞书测试消息")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        print("\n请输入飞书用户 ID：")
        user_id = input("> ").strip()
    
    if not user_id:
        print("❌ 未输入用户 ID")
        return
    
    result = send_test_message(user_id)
    
    print("\n" + "=" * 60)
    if result.get("code") == 0:
        print("✅ 消息发送成功！")
        print(f"📨 消息 ID: {result.get('data', {}).get('message_id')}")
    else:
        print("❌ 消息发送失败")
        print(f"错误码: {result.get('code')}")
        print(f"错误信息: {result.get('msg')}")
        
        if result.get("code") == 10013:
            print("\n💡 提示：用户不存在或未开通机器人权限")
        elif result.get("code") == 99991663:
            print("\n💡 提示：机器人未获取到用户授权")
    print("=" * 60)


if __name__ == "__main__":
    main()
