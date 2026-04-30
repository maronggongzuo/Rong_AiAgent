#!/usr/bin/env python3
"""Meego 双看板定期通知"""

import sys
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.meego_skill import MeegoSkill


def main():
    """主函数"""
    print("=" * 80)
    print("🚀 Meego 双看板定期通知")
    print("=" * 80)
    
    settings = Settings()
    skill = MeegoSkill(settings)
    
    # 获取业务线过滤配置
    business_line = settings.MEEGO_NOTIFICATION_BUSINESS_LINE
    if business_line:
        print(f"📋 业务线过滤: {business_line}")
    
    # 发送双看板通知（使用配置的参数，艾特管理员）
    result = skill.send_dual_board_notification(
        mention_admin=True,
        business_line=business_line
    )
    
    if result.get("success"):
        print("\n✅ 通知发送成功！")
        
        # 打印通知内容（验证占位符替换）
        print("\n" + "=" * 80)
        print("📄 通知内容")
        print("=" * 80)
        print(result.get("message_content", ""))
        print("=" * 80)
    else:
        print(f"\n❌ 通知发送失败: {result.get('error')}")
        sys.exit(1)
    
    # 打印详细信息
    print("\n" + "=" * 80)
    print("📊 详细信息")
    print("=" * 80)
    
    link_owners = result.get("link_owners", {})
    for link, data in link_owners.items():
        view_id = data.get("view_id")
        owners_result = data.get("owners_result", {})
        print(f"\n看板: {view_id}")
        print(f"链接: {link}")
        print(f"成功: {owners_result.get('success')}")
        
        if owners_result.get("success"):
            tech_owners = owners_result.get("tech_owners", [])
            print(f"Tech Owner 数量: {len(tech_owners)}")
            for i, owner in enumerate(tech_owners, 1):
                print(f"  {i}. {owner.get('name')} ({owner.get('email')})")
        else:
            print(f"错误: {owners_result.get('error')}")
    
    print("\n" + "=" * 80)
    print("✅ 执行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
