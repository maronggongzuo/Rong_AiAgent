#!/usr/bin/env python3
"""获取飞书用户列表"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def get_user_list(client):
    """获取用户列表（支持分页）"""
    url = f"{client.BASE_URL}/contact/v3/users"
    page_size = 10
    page_token = ""
    all_users = []
    
    token = client._get_tenant_access_token()
    if not token:
        print("❌ 无法获取 token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    try:
        import requests
        has_more = True
        page_count = 0
        
        print("📄 正在获取所有用户...\n")
        
        while has_more:
            page_count += 1
            params = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token
            
            response = requests.get(url, headers=headers, params=params)
            result = response.json()
            
            if result.get("code") == 0:
                data = result.get("data", {})
                users = data.get("items", [])
                has_more = data.get("has_more", False)
                page_token = data.get("page_token", "")
                
                all_users.extend(users)
                print(f"✓ 第 {page_count} 页: 获取到 {len(users)} 个用户")
            else:
                print(f"❌ 获取用户列表失败")
                print(f"错误码: {result.get('code')}")
                print(f"错误信息: {result.get('msg')}")
                return
        
        print(f"\n✅ 共获取到 {len(all_users)} 个用户：\n")
        
        for i, user in enumerate(all_users, 1):
            open_id = user.get("open_id", "")
            union_id = user.get("union_id", "")
            name = user.get("name", "未知")
            en_name = user.get("en_name", "")
            email = user.get("email", "")
            
            print(f"  {i}. 用户")
            if name:
                print(f"     姓名: {name}")
            if en_name:
                print(f"     英文名: {en_name}")
            if email:
                print(f"     邮箱: {email}")
            print(f"     Open ID: {open_id}")
            print(f"     Union ID: {union_id}")
            print()
        
        if all_users:
            print("💡 使用 Open ID 就可以发送消息了！")
                
        else:
            print(f"❌ 获取用户列表失败")
            print(f"错误码: {result.get('code')}")
            print(f"错误信息: {result.get('msg')}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def main():
    print("=" * 60)
    print("👥 获取飞书用户列表")
    print("=" * 60)
    
    settings = Settings()
    client = FeishuClient(settings)
    
    if client.use_mock:
        print("❌ 未检测到飞书凭证")
        return
    
    print("\n📤 正在获取用户列表...\n")
    get_user_list(client)


if __name__ == "__main__":
    main()
