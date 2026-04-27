#!/usr/bin/env python3
"""测试 emoji 发送"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient
import json

settings = Settings()
client = FeishuClient(settings)

print("=" * 80)
print("测试 emoji 发送")
print("=" * 80)

# 测试 1：原始模板
print("\n1. 测试原始模板...")
template_path = Path("docs/meego_notification_template.md")
with open(template_path, "r", encoding="utf-8") as f:
    template = f.read()

# 移除标题
if template.startswith("#"):
    template = "\n".join(template.split("\n")[1:])

template = template.strip()

print(f"模板内容：\n{template}")

# 替换占位符
owners_text_1 = "张三、李四"
owners_text_2 = "王五、赵六"
template = template.replace("{owners_text_1}", owners_text_1)
template = template.replace("{owners_text_2}", owners_text_2)

print(f"\n最终消息：\n{template}")

# 发送
print("\n发送中...")
result = client.send_text_message(
    user_id=settings.FEISHU_ADMIN_USER_ID,
    text=template
)

if result.get("code") == 0:
    print("✅ 发送成功！")
else:
    print(f"❌ 发送失败：{result}")

# 测试 2：替换 emoji
print("\n" + "=" * 80)
print("2. 测试替换 emoji...")

# 把 ⏰ 换成 [闹钟]
template2 = template.replace("⏰", "[闹钟]")
print(f"替换后：\n{template2}")

print("\n发送中...")
result2 = client.send_text_message(
    user_id=settings.FEISHU_ADMIN_USER_ID,
    text=template2
)

if result2.get("code") == 0:
    print("✅ 发送成功！")
else:
    print(f"❌ 发送失败：{result2}")
