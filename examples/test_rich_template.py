#!/usr/bin/env python3
"""测试富文本通知模板"""

import sys
import os
from pathlib import Path
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.meego_skill import MeegoSkill


def test_rich_template():
    """测试富文本通知模板"""
    print("=" * 60)
    print("🔧 测试富文本通知模板")
    print("=" * 60)
    
    settings = Settings()
    skill = MeegoSkill(settings)
    
    # 测试获取 Tech Owner
    board_url = "https://meego.larkoffice.com/pnsi/storyView/Ztxhe1ZDR"
    owners_result = skill.get_board_tech_owners(board_url)
    
    print(f"\n✅ 获取 Tech Owner 结果:")
    print(f"成功: {owners_result.get('success')}")
    print(f"使用模拟数据: {owners_result.get('is_mock')}")
    
    if owners_result.get('success'):
        tech_owners = owners_result.get('tech_owners', [])
        print(f"\n👥 Tech Owner 列表 ({len(tech_owners)}):")
        for i, owner in enumerate(tech_owners, 1):
            print(f"{i}. {owner.get('name')} ({owner.get('email')})")
        
        owner_names = [owner.get('name') for owner in tech_owners]
        
        # 构建富文本通知
        text_message, rich_content = skill._build_default_template(owner_names)
        
        print(f"\n📝 文本消息:")
        print(text_message)
        
        print(f"\n🎨 富文本内容 (JSON):")
        print(json.dumps(rich_content, ensure_ascii=False, indent=2))
        
        print(f"\n📋 富文本内容 (格式化):")
        for i, line_elements in enumerate(rich_content, 1):
            line_parts = []
            for elem in line_elements:
                if elem.get('tag') == 'text':
                    line_parts.append(elem.get('text', ''))
                elif elem.get('tag') == 'a':
                    line_parts.append(f"[{elem.get('text', '')}]({elem.get('href', '')})")
            print(f"{i}. {' '.join(line_parts)}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


def main():
    test_rich_template()


if __name__ == "__main__":
    main()
