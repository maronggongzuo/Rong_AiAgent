#!/usr/bin/env python3
"""测试飞书文档创建功能"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def main():
    print("=== 测试飞书文档创建 ===\n")
    
    settings = Settings()
    client = FeishuClient(settings)
    
    # 创建一个简单的文档
    doc_title = "Rong_AiAgent - 测试文档"
    
    # 文档内容
    content_blocks = [
        "# 这是测试文档",
        "",
        "这是由 Rong_AiAgent 自动创建的文档。",
        "",
        "## 功能介绍",
        "",
        "- 自动发送消息",
        "- 自动创建文档",
        "- 任务提醒",
    ]
    
    content = client.create_docx_content(content_blocks)
    
    print(f"📄 创建文档: {doc_title}")
    result = client.create_document(doc_title, content)
    
    if result.get("success"):
        print(f"✓ 文档创建成功")
        print(f"  文档标题: {result.get('title')}")
        print(f"  文档链接: {result.get('document_url')}")
        print(f"  文档 ID: {result.get('document_id')}")
        print(f"  修订版本: {result.get('revision_id')}")
        
        if result.get("mock"):
            print(f"\n⚠️  注意: 这是模拟模式，文档未实际创建")
    else:
        print(f"✗ 文档创建失败")
        print(f"  错误码: {result.get('code')}")
        print(f"  错误信息: {result.get('msg')}")
        
        if result.get("code"):
            print(f"\n💡 提示: 可能需要在飞书开放平台添加权限 'docx:document:create'")


if __name__ == "__main__":
    main()
