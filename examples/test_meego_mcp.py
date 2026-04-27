#!/usr/bin/env python3
"""测试 Meego MCP 服务器连接和功能"""

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


def test_mcp_connection():
    """测试 MCP 服务器连接"""
    print("=" * 60)
    print("🔗 测试 Meego MCP 服务器连接")
    print("=" * 60)
    
    settings = Settings()
    skill = MeegoSkill(settings)
    
    print(f"\n📋 MCP 配置:")
    print(f"   URL: {settings.MEEGO_MCP_URL}")
    print(f"   Token: {settings.MEEGO_MCP_TOKEN[:20]}..." if settings.MEEGO_MCP_TOKEN else "   Token: (未配置)")
    print()
    
    # 测试连接
    result = skill.test_mcp_connection()
    
    print(f"✅ 连接测试结果:")
    print(f"   成功: {result.get('success')}")
    
    if result.get('success'):
        print(f"   消息: {result.get('message')}")
        print(f"   URL: {result.get('url')}")
        print(f"   状态码: {result.get('status_code')}")
        
        if 'available_tools' in result:
            tools = result.get('available_tools', [])
            print(f"\n🛠️  可用工具 ({len(tools)}):")
            for tool in tools:
                print(f"   - {tool}")
    else:
        print(f"   错误: {result.get('error')}")
        if 'status_code' in result:
            print(f"   状态码: {result.get('status_code')}")
    
    return result.get('success')


def test_basic_functions():
    """测试基本功能"""
    print("\n" + "=" * 60)
    print("📊 测试基本功能")
    print("=" * 60)
    
    settings = Settings()
    skill = MeegoSkill(settings)
    
    # 测试获取 Tech Owner
    board_url = "https://meego.larkoffice.com/pnsi/board/123"
    print(f"\n1. 测试获取 Tech Owner...")
    owners_result = skill.get_board_tech_owners(board_url)
    print(f"   成功: {owners_result.get('success')}")
    print(f"   模拟数据: {owners_result.get('is_mock', False)}")
    
    if owners_result.get('success'):
        tech_owners = owners_result.get('tech_owners', [])
        print(f"   Tech Owner 数量: {len(tech_owners)}")
        for owner in tech_owners:
            print(f"   - {owner.get('name')} ({owner.get('email')})")
    
    # 测试检查风险项
    print(f"\n2. 测试检查风险项...")
    risk_result = skill.check_risk_items(board_url)
    print(f"   成功: {risk_result.get('success')}")
    print(f"   模拟数据: {risk_result.get('is_mock', False)}")
    
    if risk_result.get('success'):
        risk_items = risk_result.get('risk_items', {})
        print(f"   风险项:")
        for key, items in risk_items.items():
            print(f"   - {key}: {items}")


def main():
    print("\n" + "=" * 60)
    print("🚀 Meego MCP 测试开始")
    print("=" * 60)
    
    # 测试 MCP 连接
    connection_success = test_mcp_connection()
    
    # 测试基本功能
    test_basic_functions()
    
    print("\n" + "=" * 60)
    print("🎯 测试完成")
    print("=" * 60)
    
    if not connection_success:
        print("\n💡 提示:")
        print("   - MCP 连接测试失败，但功能仍可用（使用模拟数据）")
        print("   - 要使用真实的 Meego 数据，需要确保：")
        print("     1. 网络可以访问 MCP 服务器")
        print("     2. MCP 服务器 URL 和 Token 配置正确")
        print("     3. MCP 服务器运行正常")


if __name__ == "__main__":
    main()
