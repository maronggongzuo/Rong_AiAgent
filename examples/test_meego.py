#!/usr/bin/env python3
"""测试 Meego 技能"""

import sys
import os
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.meego_skill import MeegoSkill


def test_meego_skill():
    """测试 Meego 技能"""
    print("=" * 60)
    print("📊 测试 Meego 技能")
    print("=" * 60)
    
    settings = Settings()
    skill = MeegoSkill(settings)
    
    print("\n1. 测试获取 Tech Owner...")
    board_url = "https://meego.larkoffice.com/pnsi/board/123"
    owners_result = skill.get_board_tech_owners(board_url)
    print(f"✅ 结果: {owners_result}")
    
    print("\n2. 测试检查风险项...")
    risk_result = skill.check_risk_items(board_url)
    print(f"✅ 结果: {risk_result}")
    
    print("\n3. 测试构建通知模板...")
    test_owners = ["张三", "李四"]
    template = skill._build_default_template(test_owners)
    print("\n📝 通知模板:")
    print(template)
    
    print("\n4. 测试发送通知（模拟）...")
    # 注意：这里需要替换为实际的群聊 ID
    test_chat_id = "oc_1234567890"
    
    try:
        notification_result = skill.send_meego_notification(
            chat_id=test_chat_id,
            board_url=board_url
        )
        print(f"✅ 通知发送结果: {notification_result.get('success')}")
        print(f"📄 发送的消息: {notification_result.get('message')}")
    except Exception as e:
        print(f"❌ 发送通知失败: {e}")
    
    print("\n" + "=" * 60)
    print("💡 测试完成！")
    print("提示：要实际发送通知，请:")
    print("1. 获取实际的群聊 ID")
    print("2. 替换 test_chat_id 的值")
    print("3. 确保飞书应用有群聊消息发送权限")
    print("=" * 60)


def main():
    test_meego_skill()


if __name__ == "__main__":
    main()
