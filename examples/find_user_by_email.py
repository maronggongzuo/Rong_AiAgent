#!/usr/bin/env python3
"""通过邮箱查找飞书用户"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def find_user_by_email(email):
    """通过邮箱查找用户"""
    settings = Settings()
    client = FeishuClient(settings)
    
    token = client._get_tenant_access_token()
    if not token:
        print("❌ 无法获取 token")
        return None
    
    url = f"{client.BASE_URL}/contact/v3/users/batch_get_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    data = {
        "emails": [email]
    }
    
    try:
        import requests
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get("code") == 0:
            users = result.get("data", {}).get("user_list", [])
            if users:
                user = users[0]
                print(f"✅ 找到用户！")
                print(f"  邮箱: {user.get('email')}")
                print(f"  用户 ID: {user.get('user_id')}")
                print(f"  姓名: {user.get('name')}")
                return user.get('user_id')
            else:
                print(f"❌ 未找到邮箱为 {email} 的用户")
                return None
        else:
            print(f"❌ 查找用户失败")
            print(f"错误码: {result.get('code')}")
            print(f"错误信息: {result.get('msg')}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def main():
    print("=" * 60)
    print("🔍 通过邮箱查找飞书用户")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        print("\n请输入飞书邮箱：")
        email = input("> ").strip()
    
    if not email:
        print("❌ 未输入邮箱")
        return
    
    print(f"\n📤 正在查找用户: {email}")
    user_id = find_user_by_email(email)
    
    if user_id:
        print(f"\n💡 用户 ID: {user_id}")
        print("\n现在可以用这个 ID 发送消息了！")


if __name__ == "__main__":
    main()
