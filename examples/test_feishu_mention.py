#!/usr/bin/env python3
"""测试飞书艾特消息"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

# 可选导入 dotenv
try:
    from dotenv import load_dotenv
    has_dotenv = True
except ImportError:
    has_dotenv = False

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def send_text_with_mention(client: FeishuClient, user_id: str, text: str, mention_user_id: str, mention_name: str = "管理员"):
    """发送带艾特的文本消息"""
    content = {
        "text": f"{text} <at user_id=\"{mention_user_id}\">{mention_name}</at>"
    }
    return client.send_message(user_id, "text", content)


def send_rich_text_with_mention(client: FeishuClient, user_id: str, title: str, mention_user_id: str, mention_name: str = "管理员"):
    """发送带艾特的富文本消息"""
    content = {
        "title": title,
        "content": [
            [
                {
                    "tag": "text",
                    "text": "👋 你好 "
                },
                {
                    "tag": "at",
                    "user_id": mention_user_id,
                    "user_name": mention_name
                },
                {
                    "tag": "text",
                    "text": "！\n"
                }
            ],
            [
                {
                    "tag": "text",
                    "text": "这是一条测试消息，用于验证艾特功能是否正常工作。\n"
                }
            ],
            [
                {
                    "tag": "text",
                    "text": "📅 发送时间: "
                },
                {
                    "tag": "text",
                    "text": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
        ]
    }
    return client.send_message(user_id, "post", content)


def main():
    """主函数"""
    if has_dotenv:
        load_dotenv()
    
    settings = Settings()
    client = FeishuClient(settings)
    
    admin_user_id = settings.FEISHU_ADMIN_USER_ID
    
    if not admin_user_id:
        logger.error("❌ 未配置 FEISHU_ADMIN_USER_ID")
        return
    
    logger.info("=" * 80)
    logger.info("🚀 测试飞书艾特消息")
    logger.info("=" * 80)
    logger.info(f"  管理员用户 ID: {admin_user_id}")
    
    # 测试 1: 发送带艾特的文本消息
    logger.info("\n" + "=" * 80)
    logger.info("📝 测试 1: 发送带艾特的文本消息")
    logger.info("=" * 80)
    
    result1 = send_text_with_mention(
        client,
        admin_user_id,
        "这是一条测试消息，艾特",
        admin_user_id,
        "管理员"
    )
    
    if result1.get("code") == 0 or result1.get("mock"):
        logger.info("✅ 文本消息发送成功")
        logger.info(f"   结果: {result1}")
    else:
        logger.error(f"❌ 文本消息发送失败: {result1}")
    
    # 测试 2: 发送带艾特的富文本消息
    logger.info("\n" + "=" * 80)
    logger.info("🎨 测试 2: 发送带艾特的富文本消息")
    logger.info("=" * 80)
    
    result2 = send_rich_text_with_mention(
        client,
        admin_user_id,
        "测试艾特功能",
        admin_user_id,
        "管理员"
    )
    
    if result2.get("code") == 0 or result2.get("mock"):
        logger.info("✅ 富文本消息发送成功")
        logger.info(f"   结果: {result2}")
    else:
        logger.error(f"❌ 富文本消息发送失败: {result2}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ 测试完成")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
