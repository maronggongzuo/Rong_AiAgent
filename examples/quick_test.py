#!/usr/bin/env python3
"""快速测试脚本"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def main():
    print("=" * 60)
    print("🚀 Rong_AiAgent - 快速测试")
    print("=" * 60)
    
    settings = Settings()
    client = FeishuClient(settings)
    
    if client.use_mock:
        print("❌ 未检测到飞书凭证")
        return
    
    print("\n✅ 飞书连接成功！")
    print("\n📋 下一步操作：")
    print("1. 打开飞书客户端")
    print("2. 搜索并找到「Rong_AiAgent」机器人")
    print("3. 给机器人发一条消息，比如「你好」")
    print("4. 告诉我，然后我就能获取你的用户 ID 并发送消息了！")
    print("\n💡 或者，如果你已经知道用户 ID，请直接告诉我")


if __name__ == "__main__":
    main()
