#!/usr/bin/env python3
"""测试任务提醒和项目周报功能"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.notification_skill import NotificationSkill

def main():
    print("=" * 60)
    print("📋 测试任务提醒和项目周报功能")
    print("=" * 60)
    
    settings = Settings()
    skill = NotificationSkill(settings)
    
    # 你的用户 ID
    user_id = "ou_e47357c17dcbb2d3517f9e5520790f24"
    
    print("\n" + "=" * 60)
    print("1️⃣  测试任务提醒功能")
    print("=" * 60)
    
    # 测试任务提醒
    result1 = skill.send_task_reminder(
        task_name="完成项目文档",
        deadline="2024-01-31",
        user_id=user_id,
        progress=50,
        assignee="张三"
    )
    
    if result1.get("success"):
        print("✅ 任务提醒发送成功！")
        print(f"   消息 ID: {result1.get('feishu_result', {}).get('data', {}).get('message_id')}")
    else:
        print("❌ 任务提醒发送失败")
        print(f"   错误: {result1.get('feishu_result', {})}")
    
    print("\n" + "=" * 60)
    print("2️⃣  测试项目周报功能")
    print("=" * 60)
    
    # 测试项目周报
    result2 = skill.send_project_summary(
        project_name="Rong_AiAgent",
        user_ids=[user_id],
        completed_tasks=10,
        total_tasks=20,
        milestone="一期开发完成"
    )
    
    if result2.get("success"):
        print("✅ 项目周报发送成功！")
        for r in result2.get("results", []):
            msg_id = r.get("result", {}).get("data", {}).get("message_id")
            print(f"   用户 {r.get('user_id')}: 消息 ID = {msg_id}")
    else:
        print("❌ 项目周报发送失败")
        print(f"   错误: {result2}")
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！请查看飞书机器人消息")
    print("=" * 60)

if __name__ == "__main__":
    main()
