#!/usr/bin/env python3
"""测试艾特管理员功能"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.meego_skill import MeegoSkill

print("=" * 80)
print("测试艾特管理员功能")
print("=" * 80)

settings = Settings()
skill = MeegoSkill(settings)

# 1. 测试不艾特管理员
print("\n1. 测试不艾特管理员...")
result1 = skill.send_dual_board_notification(mention_admin=False)
if result1.get("success"):
    print("✅ 发送成功！（不艾特管理员）")
else:
    print(f"❌ 发送失败：{result1.get('error')}")

# 2. 测试艾特管理员
print("\n2. 测试艾特管理员...")
result2 = skill.send_dual_board_notification(mention_admin=True)
if result2.get("success"):
    print("✅ 发送成功！（艾特管理员）")
else:
    print(f"❌ 发送失败：{result2.get('error')}")

print("\n" + "=" * 80)
print("测试完成！请查看两条飞书消息对比区别。")
print("=" * 80)
