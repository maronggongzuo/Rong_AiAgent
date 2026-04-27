#!/usr/bin/env python3
"""Meego 看板详细 debug 测试"""

import sys
from pathlib import Path
import logging

# 配置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.meego_skill import MeegoSkill


def main():
    """主函数"""
    print("=" * 80)
    print("🔍 Meego 看板详细 Debug 测试")
    print("=" * 80)
    
    settings = Settings()
    skill = MeegoSkill(settings)
    
    # 测试第一个看板
    board_url = "https://meego.larkoffice.com/pnsi/storyView/Ztxhe1ZDR"
    view_id = "Ztxhe1ZDR"
    
    print(f"\n测试看板: {board_url}")
    print(f"view_id: {view_id}")
    print("-" * 80)
    
    result = skill.get_board_tech_owners(
        board_url=board_url,
        view_id=view_id,
        project_key=settings.MEEGO_PROJECT_KEY
    )
    
    if result.get("success"):
        print(f"\n✅ 获取成功！")
        print(f"工作项总数: {result.get('workitem_count')}")
        print(f"已检查: {result.get('checked_count')}")
        print(f"Tech Owner 数: {len(result.get('tech_owners', []))}")
        
        print(f"\n详细 Tech Owner 列表:")
        owner_count = result.get("owner_count", {})
        for i, owner in enumerate(result.get("tech_owners", []), 1):
            name = owner.get("name")
            email = owner.get("email")
            count = owner_count.get(email, 1)
            print(f"  {i}. {name} ({email}) - {count} 次")
    else:
        print(f"\n❌ 获取失败: {result.get('error')}")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("✅ Debug 测试完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
