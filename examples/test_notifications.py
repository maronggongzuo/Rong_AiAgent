#!/usr/bin/env python3
"""通知功能测试脚本"""

import sys
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.notification_skill import NotificationSkill


def test_task_reminder(skill: NotificationSkill):
    """测试任务提醒"""
    print("\n=== 测试 1: 任务提醒 ===")
    
    result = skill.send_task_reminder(
        task_name="完成Rong_AiAgent开发",
        deadline="2024-01-20",
        user_id="test_user_001",
        progress=75,
        assignee="张三"
    )
    
    if result.get("success"):
        print("✓ 任务提醒发送成功")
        print(f"  任务: {result.get('task_name')}")
        print(f"  截止日期: {result.get('deadline')}")
    else:
        print("✗ 任务提醒发送失败")
    
    return result


def test_project_summary(skill: NotificationSkill):
    """测试项目摘要"""
    print("\n=== 测试 2: 项目摘要 ===")
    
    result = skill.send_project_summary(
        project_name="Rong_TraeStart 项目",
        user_ids=["test_user_001", "test_user_002"],
        completed_tasks=15,
        total_tasks=20,
        milestone="Beta 版本发布"
    )
    
    if result.get("success"):
        print("✓ 项目摘要发送成功")
        print(f"  项目: {result.get('project_name')}")
        print(f"  接收人数: {len(result.get('results', []))}")
    else:
        print("✗ 项目摘要发送失败")
    
    return result


def test_generic_notification(skill: NotificationSkill):
    """测试通用通知"""
    print("\n=== 测试 3: 通用通知 ===")
    
    result = skill.execute(
        message="🔔 系统通知：系统将于今晚 22:00-24:00 进行维护，请保存好您的工作！",
        recipients=["test_user_001", "test_user_003"],
        channel="feishu"
    )
    
    if result.get("success"):
        print("✓ 通用通知发送成功")
        print(f"  消息: {result.get('message')[:50]}...")
        print(f"  接收人数: {len(result.get('recipients', []))}")
    else:
        print("✗ 通用通知发送失败")
    
    return result


def main():
    """主函数"""
    print("=" * 60)
    print("通知功能测试")
    print("=" * 60)
    
    print("\n📋 可用通知类型：")
    print("  1. 任务提醒 - 单个任务的截止日期提醒")
    print("  2. 项目摘要 - 项目进度周报")
    print("  3. 通用通知 - 自定义消息")
    print()
    
    settings = Settings()
    skill = NotificationSkill(settings)
    
    try:
        test_task_reminder(skill)
        test_project_summary(skill)
        test_generic_notification(skill)
        
        print("\n" + "=" * 60)
        print("✓ 所有通知测试完成！")
        print("=" * 60)
        
        print("\n💡 提示：")
        print("  - 当前使用模拟模式")
        print("  - 配置飞书凭证后可发送真实消息")
        print("  - 详细配置请查看 docs/feishu_setup_guide.md")
        
    except Exception as e:
        print(f"\n✗ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
