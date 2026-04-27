#!/usr/bin/env python3
"""验证飞书凭证并获取 tenant_access_token"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.integrations.feishu_client import FeishuClient


def test_token():
    """测试获取 token"""
    print("=" * 60)
    print("🔐 飞书凭证验证")
    print("=" * 60)
    
    settings = Settings()
    
    # 检查配置
    has_app_id = bool(settings.FEISHU_APP_ID)
    has_app_secret = bool(settings.FEISHU_APP_SECRET)
    
    print(f"\n📱 App ID: {settings.FEISHU_APP_ID or '未配置'}")
    if settings.FEISHU_APP_SECRET:
        print(f"🔑 App Secret: {settings.FEISHU_APP_SECRET[:10]}...")
    else:
        print(f"🔑 App Secret: 未配置")
    
    if not has_app_id or not has_app_secret:
        print("\n❌ 请在 .env 文件中配置 FEISHU_APP_ID 和 FEISHU_APP_SECRET")
        return False
    
    client = FeishuClient(settings)
    
    print("\n📤 正在获取 tenant_access_token...")
    
    # 测试获取 token
    token = client._get_tenant_access_token()
    
    if token:
        print(f"✅ Token 获取成功！")
        print(f"🔐 Token: {token[:20]}...")
        return True
    else:
        print("❌ Token 获取失败")
        return False


if __name__ == "__main__":
    test_token()
