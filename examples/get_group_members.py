#!/usr/bin/env python3
"""获取飞书群聊成员"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient

def get_group_members(client):
    """获取群聊成员"""
    token = client._get_tenant_access_token()
    if not token:
        print("❌ 无法获取 token")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    print("=" * 60)
    print("📋 步骤 1：先获取机器人所在的群聊列表")
    print("=" * 60)
    
    # 先获取机器人所在的群聊
    url1 = f"{client.BASE_URL}/im/v1/chats"
    params1 = {"page_size": 20}
    
    try:
        import requests
        response1 = requests.get(url1, headers=headers, params=params1)
        result1 = response1.json()
        
        print(f"状态码: {response1.status_code}")
        print(f"完整响应: {json.dumps(result1, ensure_ascii=False, indent=2)}")
        
        if result1.get("code") == 0:
            chats = result1.get("data", {}).get("items", [])
            if chats:
                print(f"\n✅ 找到 {len(chats)} 个群聊：")
                for i, chat in enumerate(chats, 1):
                    print(f"\n  {i}. 群聊:")
                    print(f"     群聊 ID: {chat.get('chat_id')}")
                    print(f"     群聊名称: {chat.get('name')}")
                    print(f"     群聊描述: {chat.get('description')}")
                
                # 尝试获取第一个群聊的成员
                if chats:
                    first_chat_id = chats[0].get("chat_id")
                    print(f"\n" + "=" * 60)
                    print(f"📋 步骤 2：尝试获取群聊 {first_chat_id} 的成员")
                    print("=" * 60)
                    
                    url2 = f"{client.BASE_URL}/im/v1/chats/{first_chat_id}/members"
                    params2 = {"page_size": 50}
                    
                    response2 = requests.get(url2, headers=headers, params=params2)
                    result2 = response2.json()
                    
                    print(f"状态码: {response2.status_code}")
                    print(f"完整响应: {json.dumps(result2, ensure_ascii=False, indent=2)}")
                    
                    if result2.get("code") == 0:
                        members = result2.get("data", {}).get("items", [])
                        print(f"\n✅ 找到 {len(members)} 个群成员：")
                        
                        for i, member in enumerate(members, 1):
                            print(f"\n  {i}. 成员:")
                            for key, value in member.items():
                                print(f"     {key}: {value}")
                    else:
                        print(f"\n❌ 获取群成员失败: {result2.get('msg')}")
            else:
                print(f"\n📭 机器人还没有加入任何群聊")
                print("💡 请先把机器人拉到一个群里！")
        else:
            print(f"\n❌ 获取群聊列表失败: {result1.get('msg')}")
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("=" * 60)
    print("👥 获取飞书群聊成员")
    print("=" * 60)
    print("\n💡 使用前请先：")
    print("1. 在飞书客户端中把「Rong_AiAgent」机器人拉到一个群里")
    print("2. 在群里发一条消息让机器人初始化")
    
    settings = Settings()
    client = FeishuClient(settings)
    
    if client.use_mock:
        print("\n❌ 未检测到飞书凭证")
        return
    
    print("\n" + "=" * 60)
    print("🚀 开始查询...")
    print("=" * 60)
    get_group_members(client)

if __name__ == "__main__":
    main()
