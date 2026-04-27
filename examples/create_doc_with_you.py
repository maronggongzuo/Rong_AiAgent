#!/usr/bin/env python3
"""创建文档并自动添加你为协作者"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def find_user_by_email(client, email):
    """通过邮箱查找用户"""
    url = f"{client.BASE_URL}/contact/v3/users/batch_get_id"
    
    token = client._get_tenant_access_token()
    if not token:
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "user_id_type": "open_id",
        "emails": [email]
    }
    
    try:
        import requests
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        if result.get("code") == 0:
            users = result.get("data", {}).get("user_list", [])
            if users:
                return users[0].get("user_id")
        return None
    except:
        return None


def main():
    print("=== 创建文档并自动添加协作者 ===\n")
    
    settings = Settings()
    client = FeishuClient(settings)
    
    # 1. 创建文档
    doc_title = "Rong_AiAgent - 我的文档"
    
    print(f"📄 步骤1: 创建文档")
    result = client.create_document(doc_title, "")
    
    if not result.get("success"):
        print(f"✗ 文档创建失败")
        return
    
    doc_url = result.get("document_url")
    doc_id = result.get("document_id")
    
    print(f"✓ 文档创建成功")
    print(f"  文档链接: {doc_url}")
    print(f"  文档 ID: {doc_id}")
    print()
    
    # 2. 通过邮箱查找你的用户 ID
    your_email = "marong.01@bytedance.com"
    print(f"📄 步骤2: 通过邮箱查找你的用户 ID: {your_email}")
    
    your_open_id = find_user_by_email(client, your_email)
    
    if not your_open_id:
        print(f"✗ 未找到用户 ID，尝试其他方法...")
        print()
        print("💡 替代方案:")
        print("  1. 你先给机器人发一条消息")
        print("  2. 然后在飞书开放平台查看事件日志获取你的 open_id")
        print("  3. 然后用下面的脚本手动添加")
        print()
        print("或者直接在飞书中打开文档，然后手动分享给自己！")
        print(f"文档链接: {doc_url}")
        return
    
    print(f"✓ 找到你的用户 ID: {your_open_id}")
    print()
    
    # 3. 添加你为协作者
    print(f"📄 步骤3: 添加你为协作者 (可编辑权限)")
    
    result = client.add_document_collaborator(doc_id, your_open_id, "edit")
    
    if result.get("success"):
        print(f"✓ {result.get('message')}")
        print()
        print(f"🎉 完成！现在你可以打开文档了！")
        print(f"文档链接: {doc_url}")
    else:
        print(f"✗ 添加协作者失败")
        print(f"错误码: {result.get('code')}")
        print(f"错误信息: {result.get('msg')}")
        print()
        print(f"💡 可能需要在飞书开放平台添加权限: 'docx:document:edit'")
        print()
        print(f"不过没关系！你可以直接在飞书中打开文档，然后通过飞书界面手动分享给自己！")
        print(f"文档链接: {doc_url}")


if __name__ == "__main__":
    main()
