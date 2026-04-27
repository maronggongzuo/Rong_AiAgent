#!/usr/bin/env python3
"""测试 Meego 技能 - 使用真实 MCP 工具"""

import sys
import os
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.meego_skill import MeegoSkill


def test_real_meego_skill():
    """测试真实的 Meego 技能"""
    print("=" * 60)
    print("🔧 测试真实的 Meego 技能")
    print("=" * 60)
    
    settings = Settings()
    skill = MeegoSkill(settings)
    
    # 测试获取 Tech Owner
    board_url = "https://meego.larkoffice.com/pnsi/storyView/Ztxhe1ZDR?scope=workspaces&node=63637046&quickFilterId=HvV1nDSD-9RRQ-KIIr-d42J-gcSHcxHsJYd8"
    
    print(f"\n📋 看板 URL: {board_url}")
    
    owners_result = skill.get_board_tech_owners(board_url)
    
    print(f"\n✅ 获取 Tech Owner 结果:")
    print(f"成功: {owners_result.get('success')}")
    print(f"使用模拟数据: {owners_result.get('is_mock')}")
    
    if owners_result.get('success'):
        tech_owners = owners_result.get('tech_owners', [])
        print(f"\n👥 Tech Owner 列表 ({len(tech_owners)}):")
        for i, owner in enumerate(tech_owners, 1):
            print(f"{i}. {owner.get('name')} ({owner.get('email')})")
    
    # 测试构建通知模板
    if owners_result.get('success'):
        tech_owners = owners_result.get('tech_owners', [])
        owner_names = [owner.get('name') for owner in tech_owners]
        
        print(f"\n📝 通知模板:")
        message = skill._build_default_template(owner_names)
        print(message)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


def main():
    test_real_meego_skill()


if __name__ == "__main__":
    main()
