#!/usr/bin/env python3
"""尝试其他方式获取用户信息"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient

def try_other_apis(email):
    """尝试其他 API"""
    settings = Settings()
    client = FeishuClient(settings)
    
    token = client._get_tenant_access_token()
    if not token:
        print("❌ 无法获取 token")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    # 尝试方法 1：search 用户
    print("=" * 60)
    print("方法 1：尝试搜索用户")
    print("=" * 60)
    url1 = f"{client.BASE_URL}/contact/v3/users/search"
    data1 = {
        "query": email,
        "page_size": 10
    }
    try:
        import requests
        response1 = requests.post(url1, headers=headers, json=data1)
        print(f"状态码: {response1.status_code}")
        print(f"响应: {json.dumps(response1.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("💡 推荐方案：")
    print("=" * 60)
    print("1️⃣  让 tianshouzhi@bytedance.com 在飞书中给机器人发一条消息")
    print("2️⃣  在飞书开放平台的事件日志中就能看到他的 open_id")
    print("3️⃣  用这个 open_id 就可以给他发消息了！")
    print("\n示例 open_id 格式: ou_xxxxxxxxx")
    
    print("\n" + "=" * 60)
    print("📝 或者，试试这个最简单的：")
    print("=" * 60)
    print("直接在飞书客户端中：")
    print("1. 搜索Rong_AiAgent机器人")
    print("2. 把 tianshouzhi@bytedance.com 拉到一个群里")
    print("3. 或者让他主动给机器人发消息")

def main():
    email = "tianshouzhi@bytedance.com"
    try_other_apis(email)

if __name__ == "__main__":
    main()
