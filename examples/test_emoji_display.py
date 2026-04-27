#!/usr/bin/env python3
"""测试 emoji 显示效果"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.meego_skill import MeegoSkill

print("=" * 80)
print("测试 📅 emoji 显示效果")
print("=" * 80)

settings = Settings()
skill = MeegoSkill(settings)

# 发送通知（不艾特）
print("\n正在发送通知...")
result = skill.send_dual_board_notification(mention_admin=False)

if result.get("success"):
    print("✅ 发送成功！")
    print("\n请查看飞书消息，确认 📅 是否正常显示")
else:
    print(f"❌ 发送失败：{result.get('error')}")
    sys.exit(1)

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
