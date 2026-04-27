#!/usr/bin/env python3
"""项目管理助手主入口"""

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
from src.agent.project_agent import ProjectAgent
from src.scheduler.task_scheduler import TaskScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    if has_dotenv:
        load_dotenv()
    
    settings = Settings()
    
    logger.info(f"启动 {settings.PROJECT_NAME}")
    
    agent = ProjectAgent(settings)
    scheduler = TaskScheduler(settings)
    
    scheduler.start()
    
    try:
        agent.run()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止...")
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    main()
