#!/usr/bin/env python3
"""启动调度器 - 仅运行定时任务"""

import sys
import time
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 可选导入 dotenv
try:
    from dotenv import load_dotenv
    has_dotenv = True
except ImportError:
    has_dotenv = False

from config.settings import Settings
from src.scheduler.task_scheduler import TaskScheduler


def main():
    """主函数"""
    if has_dotenv:
        load_dotenv()
    
    settings = Settings()
    
    logger.info("=" * 80)
    logger.info(f"🚀 启动 {settings.PROJECT_NAME} - 调度器模式")
    logger.info("=" * 80)
    
    # 打印配置
    logger.info("\n📋 调度器配置:")
    logger.info(f"  时区: {settings.SCHEDULER_TIMEZONE}")
    
    if settings.MEEGO_NOTIFICATION_ENABLED:
        logger.info(f"  Meego 通知: 已启用")
        logger.info(f"    时间: 每周 {settings.MEEGO_NOTIFICATION_DAY_OF_WEEK} {settings.MEEGO_NOTIFICATION_HOUR:02d}:{settings.MEEGO_NOTIFICATION_MINUTE:02d}")
    else:
        logger.info(f"  Meego 通知: 已禁用")
    
    # 初始化调度器
    scheduler = TaskScheduler(settings)
    scheduler.start()
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ 调度器已启动，按 Ctrl+C 停止")
    logger.info("=" * 80)
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n收到中断信号，正在停止...")
    finally:
        scheduler.shutdown()
        logger.info("调度器已关闭")


if __name__ == "__main__":
    main()
