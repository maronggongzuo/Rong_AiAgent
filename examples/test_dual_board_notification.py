#!/usr/bin/env python3
"""测试双看板通知 - 识别两个看板链接，获取各自的 Tech Owner，分别填入对应位置，发送飞书通知"""

import sys
import os
from pathlib import Path
import logging
import re
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.meego_skill import MeegoSkill


def extract_meego_links_with_order(template_path: Path) -> list:
    """从模板文件中提取 Meego 看板链接（按出现顺序）"""
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 提取 Markdown 链接格式 [text](url) 中的 URL，保持顺序
    link_pattern = r'\[.*?\]\((https://meego\.larkoffice\.com[^\)]+)\)'
    links = re.findall(link_pattern, template_content)
    
    logger.info(f"从模板中提取到 {len(links)} 个看板链接:")
    for i, link in enumerate(links, 1):
        logger.info(f"  {i}. {link}")
    
    return links


def parse_view_id_from_url(url: str) -> str:
    """从 Meego URL 中解析 view_id"""
    # URL 格式类似: https://meego.larkoffice.com/pnsi/storyView/Ztxhe1ZDR
    # 或者: https://meego.larkoffice.com/pnsi/storyView/2FwTFmZDR?scope=workspaces&node=63579615
    
    # 查找 storyView 后面的 ID
    match = re.search(r'storyView/([^/?]+)', url)
    if match:
        return match.group(1)
    return None


def get_tech_owners_for_links(skill: MeegoSkill, links: list) -> dict:
    """为每个链接获取 Tech Owner 信息"""
    result = {}
    
    for link in links:
        view_id = parse_view_id_from_url(link)
        if not view_id:
            logger.warning(f"无法从链接解析 view_id: {link}")
            continue
        
        logger.info(f"获取看板 Tech Owner: {view_id}")
        
        owners_result = skill.get_board_tech_owners(
            board_url=link,
            view_id=view_id
        )
        
        result[link] = {
            "view_id": view_id,
            "owners_result": owners_result
        }
        
        if owners_result.get("success"):
            tech_owners = owners_result.get("tech_owners", [])
            owner_names = [o.get("name") for o in tech_owners]
            logger.info(f"看板 {view_id} 的 Tech Owner: {', '.join(owner_names)}")
        else:
            logger.error(f"获取看板 {view_id} 的 Tech Owner 失败: {owners_result.get('error')}")
    
    return result


def build_owners_text_for_link(link_owners: dict, link: str) -> str:
    """构建某个链接的 Tech Owner 文本"""
    data = link_owners.get(link, {})
    owners_result = data.get("owners_result", {})
    
    if owners_result.get("success"):
        tech_owners = owners_result.get("tech_owners", [])
        owner_names = [o.get("name") for o in tech_owners]
        if owner_names:
            return "、".join(owner_names)
    
    return "相关同学"


def build_notification_from_template(template_path: Path, link_owners: dict) -> str:
    """从模板构建通知，分别替换两个占位符"""
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 提取链接（按顺序）
    links = extract_meego_links_with_order(template_path)
    
    if len(links) >= 1:
        # 第一个链接对应 {owners_text_1}
        owners_text_1 = build_owners_text_for_link(link_owners, links[0])
        template_content = template_content.replace("{owners_text_1}", owners_text_1)
        logger.info(f"第一个看板的 Tech Owner: {owners_text_1}")
    
    if len(links) >= 2:
        # 第二个链接对应 {owners_text_2}
        owners_text_2 = build_owners_text_for_link(link_owners, links[1])
        template_content = template_content.replace("{owners_text_2}", owners_text_2)
        logger.info(f"第二个看板的 Tech Owner: {owners_text_2}")
    
    # 移除 Markdown 标题
    if template_content.startswith("# "):
        lines = template_content.split("\n")
        template_content = "\n".join(lines[1:])
    
    return template_content.strip()


def main():
    """主函数"""
    print("=" * 80)
    print("🚀 测试双看板通知功能（分别替换）")
    print("=" * 80)
    
    settings = Settings()
    skill = MeegoSkill(settings)
    
    template_path = Path(__file__).parent.parent / "docs" / "meego_notification_template.md"
    
    # 1. 从模板中提取看板链接（按顺序）
    print("\n📋 步骤 1: 从模板中提取看板链接")
    meego_links = extract_meego_links_with_order(template_path)
    
    if not meego_links:
        print("❌ 未找到任何看板链接，退出")
        return
    
    # 2. 为每个链接获取 Tech Owner
    print("\n👥 步骤 2: 为每个看板获取 Tech Owner")
    link_owners = get_tech_owners_for_links(skill, meego_links)
    
    # 3. 构建通知（分别替换两个占位符）
    print("\n📝 步骤 3: 构建通知")
    text_message = build_notification_from_template(template_path, link_owners)
    
    print("\n📋 通知内容:")
    print(text_message)
    
    # 4. 发送飞书通知给管理员
    print("\n📤 步骤 4: 发送飞书通知给管理员")
    
    admin_open_id = settings.FEISHU_ADMIN_USER_ID
    if admin_open_id:
        print(f"📨 发送通知给管理员: {admin_open_id}")
        try:
            result = skill.feishu_client.send_text_message(
                user_id=admin_open_id,
                text=text_message,
                receive_id_type="open_id"
            )
            
            if result.get("code") == 0:
                print("✅ 通知发送成功！请查看飞书消息")
            else:
                print(f"❌ 通知发送失败: {result}")
                
        except Exception as e:
            print(f"❌ 发送通知时发生错误: {e}")
    else:
        print("⚠️ 未配置 FEISHU_ADMIN_USER_ID，跳过发送通知")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)
    
    # 打印详细信息
    print("\n📊 详细信息:")
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


if __name__ == "__main__":
    main()
