#!/usr/bin/env python3
"""从 Meego 看板 URL 查询所有工作项的业务线信息，按业务线分组显示"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from src.skills.meego_skill import MeegoSkill


def main():
    """主函数"""
    
    # 获取命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python scripts/test_mql_query.py <meego_board_url>")
        print("示例: python scripts/test_mql_query.py \"https://meego.larkoffice.com/pnsi/storyView/IiorbuNvg?scope=workspaces&node=64322503\"")
        return 1
    
    board_url = sys.argv[1]
    
    # 加载配置
    settings = Settings()
    
    # 创建 MeegoSkill 实例
    meego_skill = MeegoSkill(settings)
    
    print("=" * 80)
    print("测试 MQL 查询业务线字段")
    print("=" * 80)
    print(f"看板 URL: {board_url}")
    print()
    
    # 查询业务线信息（按业务线分组）
    result = meego_skill.get_business_lines_from_board(board_url)
    
    # 格式化输出（按业务线分组）
    formatted_text = meego_skill.format_business_lines_result(result, group_by_business=True)
    print(formatted_text)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
