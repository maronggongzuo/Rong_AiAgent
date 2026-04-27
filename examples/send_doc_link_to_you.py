#!/usr/bin/env python3
"""创建文档并把链接发给你"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def main():
    print("=== 创建文档并发送链接给你 ===\n")
    
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
    
    # 2. 发送文档链接给你
    your_open_id = "ou_e47357c17dcbb2d3517f9e5520790f24"
    
    print(f"📄 步骤2: 发送文档链接给你")
    
    message = f"""
📄 新文档已创建！

**标题**: {doc_title}
**链接**: {doc_url}

💡 下一步:
1. 点击上面的链接打开文档
2. 在飞书中点击右上角的「分享」按钮
3. 添加你需要的协作者或设置文档公开
4. 完成！
    """.strip()
    
    result = client.send_text_message(your_open_id, message)
    
    if result.get("code") == 0:
        print(f"✓ 消息发送成功！去飞书中查看吧～")
        print(f"\n🎉 或者直接点击这个链接打开文档:")
        print(f"   {doc_url}")
    else:
        print(f"✗ 消息发送失败")
        print(f"\n但没关系！你还是可以直接打开文档:")
        print(f"   {doc_url}")
        print(f"\n在飞书中打开后，点击右上角的「分享」来设置权限即可！")


if __name__ == "__main__":
    main()
