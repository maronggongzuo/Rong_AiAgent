#!/usr/bin/env python3
"""使用示例"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.document.document_generator import DocumentGenerator
from src.skills.notification_skill import NotificationSkill


def example_generate_document():
    """示例：生成项目报告"""
    print("=== 示例：生成项目报告 ===")
    
    generator = DocumentGenerator("templates")
    
    data = {
        "project_name": "Rong_TraeStart Rong_AiAgent",
        "report_date": "2024-01-15",
        "status": "进行中",
        "manager": "张三",
        "progress_summary": "项目已完成基础架构搭建",
        "completed_work": "- 完成项目初始化\n- 创建核心模块结构\n- 实现飞书 API 基础集成",
        "milestones_table": "| 架构设计 | 2024-01-10 | 2024-01-10 | 完成 |\n| 核心开发 | 2024-01-20 | - | 进行中 |",
        "risks_and_issues": "- 暂无重大风险",
        "next_steps": "1. 完成技能模块开发\n2. 集成飞书消息推送",
        "generated_at": "2024-01-15 10:00:00"
    }
    
    content = generator.generate("project_report", data)
    generator.save_document(content, "data/output/project_report.md")
    
    print("✓ 项目报告已生成: data/output/project_report.md")
    print("\n文档预览:")
    print(content[:200] + "...")


def example_notification():
    """示例：发送通知"""
    print("\n=== 示例：发送通知 ===")
    
    settings = Settings()
    notification = NotificationSkill(settings)
    
    # 使用你的飞书用户 ID（之前我们找到的那个）
    user_id = "ou_e47357c17dcbb2d3517f9e5520790f24"
    
    result = notification.send_task_reminder(
        task_name="完成项目架构设计",
        deadline="2024-01-20",
        user_id=user_id,
        progress=80,
        assignee="张三"
    )
    
    print(f"✓ 通知发送结果: {result}")


def main():
    """主函数"""
    print("Rong_AiAgent - 使用示例\n")
    
    example_generate_document()
    example_notification()
    
    print("\n所有示例执行完成！")


if __name__ == "__main__":
    main()
