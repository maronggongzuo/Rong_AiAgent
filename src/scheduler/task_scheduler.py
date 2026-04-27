"""任务调度器"""

import logging
from typing import Callable, Optional, Dict, Any
from datetime import datetime, timedelta
from config.settings import Settings
from src.skills.meego_skill import MeegoSkill

logger = logging.getLogger(__name__)

# 尝试导入 apscheduler，失败则使用模拟模式
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.date import DateTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    has_apscheduler = True
except ImportError:
    has_apscheduler = False
    logger.warning("apscheduler 未安装，将使用模拟调度器")


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.use_mock = not has_apscheduler
        
        if self.use_mock:
            self.jobs: Dict[str, Dict[str, Any]] = {}
            logger.info("使用模拟调度器")
        else:
            self.scheduler = BackgroundScheduler(timezone=settings.SCHEDULER_TIMEZONE)
        
        self._init_default_jobs()
    
    def _init_default_jobs(self):
        """初始化默认任务"""
        logger.info("初始化调度器任务...")
        
        # 1. 添加每日检查任务
        if not self.use_mock:
            self.add_cron_job(
                self._daily_check,
                hour=9,
                minute=0,
                job_id="daily_project_check"
            )
        else:
            self.jobs["daily_project_check"] = {
                "func": self._daily_check,
                "type": "cron",
                "hour": 9,
                "minute": 0
            }
            logger.info("已添加模拟 Cron 任务: daily_project_check")
        
        # 2. 添加 Meego 双看板通知任务（如果启用）
        if self.settings.MEEGO_NOTIFICATION_ENABLED:
            logger.info(f"Meego 定时任务已启用")
            if not self.use_mock:
                self.add_cron_job(
                    self._send_meego_notification,
                    day_of_week=self.settings.MEEGO_NOTIFICATION_DAY_OF_WEEK,
                    hour=self.settings.MEEGO_NOTIFICATION_HOUR,
                    minute=self.settings.MEEGO_NOTIFICATION_MINUTE,
                    job_id="meego_dual_board_notification"
                )
            else:
                self.jobs["meego_dual_board_notification"] = {
                    "func": self._send_meego_notification,
                    "type": "cron",
                    "day_of_week": self.settings.MEEGO_NOTIFICATION_DAY_OF_WEEK,
                    "hour": self.settings.MEEGO_NOTIFICATION_HOUR,
                    "minute": self.settings.MEEGO_NOTIFICATION_MINUTE
                }
                logger.info(f"已添加模拟 Meego 通知任务")
        else:
            logger.info("Meego 定时任务未启用")
    
    def start(self):
        """启动调度器"""
        if self.use_mock:
            logger.info("模拟调度器已启动")
        elif not self.scheduler.running:
            self.scheduler.start()
            logger.info("调度器已启动")
    
    def shutdown(self):
        """关闭调度器"""
        if self.use_mock:
            logger.info("模拟调度器已关闭")
        elif self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("调度器已关闭")
    
    def add_cron_job(self, func: Callable, job_id: Optional[str] = None, **cron_kwargs):
        """添加 Cron 任务"""
        job_id = job_id or func.__name__
        
        if self.use_mock:
            self.jobs[job_id] = {
                "func": func,
                "type": "cron",
                **cron_kwargs
            }
            logger.info(f"已添加模拟 Cron 任务: {job_id}")
            return None
        else:
            job = self.scheduler.add_job(
                func,
                trigger=CronTrigger(**cron_kwargs),
                id=job_id,
                replace_existing=True
            )
            logger.info(f"已添加 Cron 任务: {job_id}")
            return job
    
    def add_interval_job(self, func: Callable, interval: timedelta, job_id: Optional[str] = None):
        """添加间隔任务"""
        job_id = job_id or func.__name__
        
        if self.use_mock:
            self.jobs[job_id] = {
                "func": func,
                "type": "interval",
                "interval_seconds": interval.total_seconds()
            }
            logger.info(f"已添加模拟间隔任务: {job_id}")
            return None
        else:
            job = self.scheduler.add_job(
                func,
                trigger=IntervalTrigger(seconds=interval.total_seconds()),
                id=job_id,
                replace_existing=True
            )
            logger.info(f"已添加间隔任务: {job_id}")
            return job
    
    def add_date_job(self, func: Callable, run_date: datetime, job_id: Optional[str] = None):
        """添加一次性任务"""
        job_id = job_id or func.__name__
        
        if self.use_mock:
            self.jobs[job_id] = {
                "func": func,
                "type": "date",
                "run_date": run_date
            }
            logger.info(f"已添加模拟定时任务: {job_id} at {run_date}")
            return None
        else:
            job = self.scheduler.add_job(
                func,
                trigger=DateTrigger(run_date=run_date),
                id=job_id,
                replace_existing=True
            )
            logger.info(f"已添加定时任务: {job_id} at {run_date}")
            return job
    
    def remove_job(self, job_id: str):
        """移除任务"""
        if self.use_mock:
            if job_id in self.jobs:
                del self.jobs[job_id]
                logger.info(f"已移除模拟任务: {job_id}")
        else:
            try:
                self.scheduler.remove_job(job_id)
                logger.info(f"已移除任务: {job_id}")
            except Exception as e:
                logger.warning(f"移除任务失败: {e}")
    
    def _daily_check(self):
        """每日检查任务"""
        logger.info("执行每日项目检查...")
        logger.info("检查任务进度、发送提醒等")
    
    def _send_meego_notification(self):
        """发送 Meego 双看板通知"""
        logger.info("=" * 60)
        logger.info("🚀 执行 Meego 双看板定时通知")
        logger.info("=" * 60)
        
        try:
            skill = MeegoSkill(self.settings)
            result = skill.send_dual_board_notification()
            
            if result.get("success"):
                logger.info("✅ Meego 通知发送成功")
                
                # 打印详细信息
                link_owners = result.get("link_owners", {})
                for link, data in link_owners.items():
                    view_id = data.get("view_id")
                    owners_result = data.get("owners_result", {})
                    if owners_result.get("success"):
                        tech_owners = owners_result.get("tech_owners", [])
                        owner_names = [owner.get("name") for owner in tech_owners]
                        logger.info(f"看板 {view_id}: {len(owner_names)} 人 - {', '.join(owner_names)}")
                    else:
                        logger.warning(f"看板 {view_id}: 获取失败 - {owners_result.get('error')}")
            else:
                logger.error(f"❌ Meego 通知发送失败: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ 执行 Meego 通知时发生错误: {e}", exc_info=True)

