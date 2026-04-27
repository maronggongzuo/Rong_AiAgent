"""甘特图技能 - 项目进度管理示例"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_skill import BaseSkill
from config.settings import Settings

logger = logging.getLogger(__name__)


class GanttSkill(BaseSkill):
    """甘特图技能 - 项目进度管理"""
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.name = "gantt"
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行甘特图相关操作"""
        action = kwargs.get("action", "analyze")
        
        if action == "analyze":
            return self.analyze_project(**kwargs)
        elif action == "get_delayed_tasks":
            return self.get_delayed_tasks(**kwargs)
        elif action == "generate_report":
            return self.generate_gantt_report(**kwargs)
        else:
            return {"success": False, "error": f"未知的操作: {action}"}
    
    def analyze_project(self, **kwargs) -> Dict[str, Any]:
        """分析项目进度"""
        project_name = kwargs.get("project_name", "未命名项目")
        tasks = kwargs.get("tasks", [])
        
        logger.info(f"分析项目 {project_name} 的甘特图")
        
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
        delayed = sum(1 for t in tasks if t.get("status") == "delayed")
        
        return {
            "success": True,
            "project_name": project_name,
            "summary": {
                "total_tasks": len(tasks),
                "completed": completed,
                "in_progress": in_progress,
                "delayed": delayed
            },
            "progress_percentage": int((completed / len(tasks) * 100) if tasks else 0)
        }
    
    def get_delayed_tasks(self, **kwargs) -> Dict[str, Any]:
        """获取延期任务"""
        tasks = kwargs.get("tasks", [])
        
        logger.info("获取延期任务")
        
        delayed_tasks = [t for t in tasks if t.get("status") == "delayed"]
        
        return {
            "success": True,
            "delayed_tasks": delayed_tasks,
            "count": len(delayed_tasks)
        }
    
    def generate_gantt_report(self, **kwargs) -> Dict[str, Any]:
        """生成甘特图报告"""
        project_name = kwargs.get("project_name", "未命名项目")
        
        logger.info(f"生成项目 {project_name} 的甘特图报告")
        
        return {
            "success": True,
            "project_name": project_name,
            "report_url": f"https://example.com/gantt/{project_name}",
            "generated_at": datetime.now().isoformat()
        }
