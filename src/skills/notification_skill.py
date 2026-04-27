"""通知技能"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from .base_skill import BaseSkill
from config.settings import Settings
from src.integrations.feishu_client import FeishuClient

logger = logging.getLogger(__name__)


class NotificationSkill(BaseSkill):
    """通知技能"""
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.name = "notification"
        self.feishu_client = FeishuClient(settings)
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """发送通知"""
        message = kwargs.get("message", "")
        recipients = kwargs.get("recipients", [])
        channel = kwargs.get("channel", "feishu")
        
        logger.info(f"发送通知: {message} 给 {recipients} 通过 {channel}")
        
        results = []
        for recipient in recipients:
            if channel == "feishu":
                result = self.feishu_client.send_text_message(recipient, message)
                results.append({"recipient": recipient, "result": result})
        
        return {
            "success": True,
            "message": message,
            "recipients": recipients,
            "channel": channel,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def send_task_reminder(
        self,
        task_name: str,
        deadline: str,
        user_id: str,
        progress: Optional[int] = None,
        assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送任务提醒"""
        
        progress_text = f"\n📊 进度: {progress}%" if progress is not None else ""
        assignee_text = f"\n👤 负责人: {assignee}" if assignee else ""
        
        message = f"""
⚠️ 任务提醒

📋 任务: {task_name}
📅 截止日期: {deadline}{progress_text}{assignee_text}

请及时处理！
        """.strip()
        
        result = self.feishu_client.send_text_message(user_id, message)
        
        return {
            "success": result.get("code") == 0,
            "task_name": task_name,
            "deadline": deadline,
            "user_id": user_id,
            "feishu_result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def send_project_summary(
        self,
        project_name: str,
        user_ids: List[str],
        completed_tasks: int = 0,
        total_tasks: int = 0,
        milestone: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送项目摘要"""
        
        progress = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
        
        message = f"""
📊 项目周报 - {project_name}

📈 整体进度: {progress}%
✅ 已完成任务: {completed_tasks}/{total_tasks}
"""
        
        if milestone:
            message += f"🏁 里程碑: {milestone}\n"
        
        message += """
⏰ 提醒：请及时更新任务状态！
        """.strip()
        
        results = []
        for user_id in user_ids:
            result = self.feishu_client.send_text_message(user_id, message)
            results.append({"user_id": user_id, "result": result})
        
        return {
            "success": all(r.get("result", {}).get("code") == 0 for r in results),
            "project_name": project_name,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

