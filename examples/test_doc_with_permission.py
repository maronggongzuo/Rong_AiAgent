#!/usr/bin/env python3
"""测试创建文档并添加权限"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def main():
    print("=== 测试创建文档并添加权限 ===\n")
    
    settings = Settings()
    client = FeishuClient(settings)
    
    # 1. 创建文档
    doc_title = "Rong_AiAgent - 权限测试文档"
    
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
    
    # 2. 查找用户
    print(f"📄 步骤2: 查找用户")
    # 使用之前获取的用户 open_id
    # 你可以通过 get_users.py 获取用户 open_id
    
    # 这里假设你已经有用户的 open_id 了
    # 如果没有，可以先运行 get_users.py 获取
    
    # 示例:
    # user_open_id = "ou_xxx..."
    
    print("💡 提示:")
    print("  要给文档添加协作者，你需要:")
    print("  1. 先获取用户的 open_id (用 get_users.py)")
    print("  2. 然后添加权限: docx:document:edit")
    print()
    
    # 3. 询问是否添加协作者
    add_collab = input("是否要添加协作者？(y/n): ").strip().lower()
    
    if add_collab == 'y':
        user_id = input("请输入用户的 open_id: ").strip()
        
        role = input("请输入权限 (edit/view/comment, 默认 edit): ").strip()
        if not role:
            role = "edit"
        
        print(f"\n📄 步骤3: 添加协作者 {user_id} ({role})")
        
        result = client.add_document_collaborator(doc_id, user_id, role)
        
        if result.get("success"):
            print(f"✓ {result.get('message')}")
            print(f"现在用户可以访问文档了: {doc_url}")
        else:
            print(f"✗ 添加协作者失败")
            print(f"错误码: {result.get('code')}")
            print(f"错误信息: {result.get('msg')}")
            
            if result.get("code"):
                print(f"\n💡 提示: 可能需要添加权限 'docx:document:edit'")
    
    print("\n📝 其他解决方案:")
    print("  方法1: 通过飞书开放平台手动给应用添加权限")
    print("  方法2: 让用户先给机器人发消息，然后在飞书中分享给用户")
    print("  方法3: 使用飞书的文件夹，将文档放到文件夹中")


if __name__ == "__main__":
    main()
