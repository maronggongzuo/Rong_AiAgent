#!/usr/bin/env python3
"""测试文档所有者转移功能"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def main():
    print("=" * 60)
    print("📄 测试文档所有者转移功能")
    print("=" * 60)
    
    settings = Settings()
    client = FeishuClient(settings)
    
    print("\n📝 创建测试文档...")
    
    # 创建一个测试文档
    test_content = "这是一个测试文档，用于测试所有者转移功能。"
    result = client.create_document(
        "测试文档 - 所有者转移",
        test_content,
        transfer_owner=True  # 自动转移所有者
    )
    
    if not result.get("success"):
        print("❌ 创建文档失败")
        print(f"错误: {result.get('msg')}")
        return
    
    doc_url = result.get("document_url")
    doc_id = result.get("document_id")
    
    print(f"✅ 文档创建成功!")
    print(f"📄 文档链接: {doc_url}")
    print(f"📄 文档ID: {doc_id}")
    
    print("\n" + "=" * 60)
    print("💡 检查结果:")
    print("1. 打开飞书，检查文档是否已创建")
    print("2. 查看文档的所有者是否已经是你")
    print("3. 确认你有完整的编辑和管理权限")
    print("=" * 60)


if __name__ == "__main__":
    main()
