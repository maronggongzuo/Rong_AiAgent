#!/usr/bin/env python3
"""测试所有技能"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.agent.project_agent import ProjectAgent

def test_notification_skill(agent):
    """测试通知技能"""
    print("\n" + "=" * 60)
    print("🔔 测试通知技能")
    print("=" * 60)
    
    result = agent.execute_skill(
        "notification",
        task_name="测试任务提醒",
        deadline="2024-02-01",
        user_id="ou_e47357c17dcbb2d3517f9e5520790f24"
    )
    
    print(f"✓ 结果: {result}")
    return result

def test_document_skill(agent):
    """测试文档技能"""
    print("\n" + "=" * 60)
    print("📄 测试文档技能")
    print("=" * 60)
    
    result = agent.execute_skill(
        "document",
        action="generate",
        template="project_report",
        data={"project_name": "Rong_AiAgent"}
    )
    
    print(f"✓ 结果: {result}")
    return result

def test_github_skill(agent):
    """测试 GitHub 技能"""
    print("\n" + "=" * 60)
    print("🐙 测试 GitHub 技能")
    print("=" * 60)
    
    result = agent.execute_skill(
        "github",
        action="get_repos",
        username="octocat"
    )
    
    print(f"✓ 结果: {result}")
    return result

def test_gantt_skill(agent):
    """测试甘特图技能"""
    print("\n" + "=" * 60)
    print("📊 测试甘特图技能")
    print("=" * 60)
    
    result = agent.execute_skill(
        "gantt",
        action="analyze",
        project_name="Rong_AiAgent",
        tasks=[
            {"name": "完成基础架构", "status": "completed"},
            {"name": "开发通知模块", "status": "in_progress"},
            {"name": "集成飞书", "status": "completed"},
            {"name": "开发文档技能", "status": "delayed"}
        ]
    )
    
    print(f"✓ 结果: {result}")
    
    # 获取延期任务
    result2 = agent.execute_skill(
        "gantt",
        action="get_delayed_tasks",
        tasks=[
            {"name": "任务1", "status": "delayed"},
            {"name": "任务2", "status": "completed"}
        ]
    )
    
    print(f"✓ 延期任务: {result2}")
    
    return result

def main():
    print("=" * 60)
    print("🚀 测试所有技能")
    print("=" * 60)
    
    settings = Settings()
    agent = ProjectAgent(settings)
    
    print(f"\n📦 已加载的技能: {list(agent.skills.keys())}")
    
    # 测试所有技能
    test_notification_skill(agent)
    test_document_skill(agent)
    test_github_skill(agent)
    test_gantt_skill(agent)
    
    print("\n" + "=" * 60)
    print("✅ 所有技能测试完成！")
    print("=" * 60)
    print("\n📚 详细文档请查看: docs/SKILLS_GUIDE.md")

if __name__ == "__main__":
    main()
