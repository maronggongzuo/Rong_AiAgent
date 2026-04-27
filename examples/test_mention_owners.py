#!/usr/bin/env python3
"""测试艾特 Tech Owner"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.meego_skill import MeegoSkill

print("=" * 80)
print("测试艾特 Tech Owner 功能")
print("=" * 80)

settings = Settings()
skill = MeegoSkill(settings)

# 发送通知（不艾特管理员）
print("\n正在发送通知...")
result = skill.send_dual_board_notification(mention_admin=False)

if result.get("success"):
    print("✅ 发送成功！")
    print("\n请查看飞书消息，确认人名是否被艾特！")
else:
    print(f"❌ 发送失败：{result.get('error')}")
    sys.exit(1)

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
