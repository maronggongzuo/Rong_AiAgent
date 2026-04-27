#!/usr/bin/env python3
"""获取机器人最近收到的消息"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def get_recent_messages(client):
    """获取最近消息"""
    token = client._get_tenant_access_token()
    if not token:
        print("❌ 无法获取 token")
        return None
    
    # 先获取机器人所在的群聊列表，获取第一个群聊的 ID
    print("🔍 正在获取群聊列表...")
    
    url_chat = f"{client.BASE_URL}/im/v1/chats"
    params_chat = {"page_size": 20}
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        import requests
        response_chat = requests.get(url_chat, headers=headers, params=params_chat)
        result_chat = response_chat.json()
        
        if result_chat.get("code") != 0:
            print(f"❌ 获取群聊列表失败: {result_chat.get('msg')}")
            return None
        
        chats = result_chat.get("data", {}).get("items", [])
        if not chats:
            print("📭 机器人还没有加入任何群聊")
            print("💡 请先把机器人拉到一个群里！")
            return None
        
        # 使用第一个群聊的 ID
        container_id = chats[0].get("chat_id")
        print(f"✅ 找到群聊: {chats[0].get('name')} (ID: {container_id})")
        
    except Exception as e:
        print(f"❌ 获取群聊失败: {e}")
        return None
    
    # 然后获取该群聊的消息
    url = f"{client.BASE_URL}/im/v1/messages"
    params = {
        "container_id": container_id,  # 必需参数
        "container_id_type": "chat",
        "page_size": 20,
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        result = response.json()
        
        if result.get("code") == 0:
            messages = result.get("data", {}).get("items", [])
            if messages:
                print(f"✅ 获取到 {len(messages)} 条消息：\n")
                
                user_ids = set()
                for i, msg in enumerate(messages, 1):
                    sender = msg.get("sender", {})
                    sender_id = sender.get("sender_id", {}).get("union_id", sender.get("id", ""))
                    sender_type = sender.get("sender_type", "")
                    msg_type = msg.get("msg_type", "")
                    body = msg.get("body", {})
                    content = body.get("content", "")
                    
                    try:
                        import json
                        content_obj = json.loads(content)
                        if msg_type == "text":
                            content = content_obj.get("text", "")
                    except:
                        pass
                    
                    print(f"  {i}. 发送者: {sender_id} ({sender_type})")
                    print(f"     消息类型: {msg_type}")
                    print(f"     内容: {content[:50]}...")
                    print()
                    
                    if sender_id and sender_type == "user":
                        user_ids.add(sender_id)
                
                if user_ids:
                    print("\n💡 找到的用户 ID：")
                    for uid in user_ids:
                        print(f"  • {uid}")
                    print()
                    return list(user_ids)
                
            else:
                print(f"📭 暂未收到消息")
                
        else:
            print(f"❌ 获取消息失败")
            print(f"错误码: {result.get('code')}")
            print(f"错误信息: {result.get('msg')}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return None


def main():
    print("=" * 60)
    print("📨 获取机器人最近消息")
    print("=" * 60)
    
    settings = Settings()
    client = FeishuClient(settings)
    
    print("\n📤 正在获取消息...\n")
    user_ids = get_recent_messages(client)
    
    if user_ids:
        print("\n现在可以选择一个用户 ID 发送测试消息！")


if __name__ == "__main__":
    main()
