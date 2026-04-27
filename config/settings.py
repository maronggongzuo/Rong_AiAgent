"""配置管理"""

import os
from pathlib import Path
from typing import Optional


def _load_dotenv():
    """加载 .env 文件（不依赖 python-dotenv）"""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                # 移除引号（如果有）
                if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                    value = value[1:-1]
                
                os.environ[key] = value


class Settings:
    """应用配置"""
    
    def __init__(self):
        _load_dotenv()
        
        self.PROJECT_NAME = os.getenv("PROJECT_NAME", "Rong_AiAgent")
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        
        self.FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
        self.FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
        self.FEISHU_BOT_TOKEN = os.getenv("FEISHU_BOT_TOKEN")
        self.FEISHU_ADMIN_USER_ID = os.getenv("FEISHU_ADMIN_USER_ID", "ou_e47357c17dcbb2d3517f9e5520790f24")
        
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        self.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        
        self.SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "Asia/Shanghai")
        
        # Meego 配置（MCP 服务器）
        self.MEEGO_MCP_URL = os.getenv("MEEGO_MCP_URL", "https://meego.larkoffice.com/mcp_server/v1")
        self.MEEGO_MCP_TOKEN = os.getenv("MEEGO_MCP_TOKEN")
        
        # Meego 看板通知配置
        self.MEEGO_PROJECT_KEY = os.getenv("MEEGO_PROJECT_KEY", "5f6330a7796d72a1ca2278c5")
        self.MEEGO_TEMPLATE_PATH = os.getenv("MEEGO_TEMPLATE_PATH")
        self.MEEGO_MAX_WORKITEMS = int(os.getenv("MEEGO_MAX_WORKITEMS", "200"))
        
        # Meego 定时任务配置
        self.MEEGO_NOTIFICATION_ENABLED = os.getenv("MEEGO_NOTIFICATION_ENABLED", "true").lower() == "true"
        self.MEEGO_NOTIFICATION_DAY_OF_WEEK = os.getenv("MEEGO_NOTIFICATION_DAY_OF_WEEK", "sat")  # 周六
        self.MEEGO_NOTIFICATION_HOUR = int(os.getenv("MEEGO_NOTIFICATION_HOUR", "20"))  # 20点
        self.MEEGO_NOTIFICATION_MINUTE = int(os.getenv("MEEGO_NOTIFICATION_MINUTE", "50"))  # 50分

