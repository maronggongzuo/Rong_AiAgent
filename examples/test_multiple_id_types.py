#!/usr/bin/env python3
"""测试不同类型的用户 ID 发送消息"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def test_send(user_id):
    """测试发送消息"""
    settings = Settings()
    client = FeishuClient(settings)
    
    message = """🎉 恭喜！Rong_AiAgent已成功连接飞书！

📋 可用功能：
• 任务提醒 - 截止日期前自动提醒
• 项目周报 - 定期发送项目进度
• 文档生成 - 按模板生成项目文档
• 智能问答 - 基于项目文档回答问题

💬 这是一条测试消息，说明配置成功！

—— Rong_AiAgent 🤖
"""
    
    # 尝试多种 ID 类型
    id_types = ["open_id", "user_id", "union_id"]
    
    for id_type in id_types:
        print(f"\n{'=' * 60}")
        print(f"尝试使用 {id_type} 发送...")
        print('=' * 60)
        
        result = client.send_text_message(user_id, message, id_type)
        
        print(f"结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get("code") == 0:
            print(f"\n✅ {id_type} 发送成功！")
            return True
        else:
            print(f"\n❌ {id_type} 发送失败")
    
    return False


def main():
    user_id = "ou_e47357c17dcbb2d3517f9e5520790f24"
    
    print("=" * 60)
    print("📤 测试不同用户 ID 类型发送消息")
    print("=" * 60)
    print(f"\n用户 ID: {user_id}")
    
    success = test_send(user_id)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 消息发送成功！请检查飞书")
    else:
        print("❌ 所有方式都失败了")
        print("\n💡 可能需要：")
        print("1. 在飞书开放平台添加权限: im:message")
        print("2. 在飞书开放平台添加权限: contact:user.base:readonly")
        print("3. 确保应用已发布")
    print("=" * 60)


if __name__ == "__main__":
    main()
