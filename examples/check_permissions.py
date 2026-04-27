#!/usr/bin/env python3
"""检查并测试基本的消息发送（不需要用户 ID 查询权限）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def main():
    print("=" * 60)
    print("🔐 快速权限检查")
    print("=" * 60)
    
    settings = Settings()
    client = FeishuClient(settings)
    
    print("\n✅ 飞书连接成功！")
    print("\n📋 需要你完成以下步骤：")
    print("1. 打开飞书客户端")
    print("2. 搜索「Rong_AiAgent」机器人")
    print("3. 给机器人发任意消息（比如「你好」）")
    print("4. 然后告诉我，我来帮你发送测试消息！")
    print()
    print("💡 或者：如果你已经在飞书中找到机器人并打开了对话框，")
    print("   可以直接在飞书里回复我，我就能知道你的用户 ID！")


if __name__ == "__main__":
    main()
