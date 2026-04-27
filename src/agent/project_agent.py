"""项目管理 Agent 核心"""

import logging
from typing import Dict, Any, List
from config.settings import Settings

logger = logging.getLogger(__name__)


class ProjectAgent:
    """Rong_AiAgent"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.skills = {}
        self._init_skills()
    
    def _init_skills(self):
        """初始化可用技能"""
        logger.info("初始化技能模块...")
        
        from src.skills.notification_skill import NotificationSkill
        from src.skills.document_skill import DocumentSkill
        from src.skills.github_skill import GithubSkill
        from src.skills.gantt_skill import GanttSkill
        
        self.skills["notification"] = NotificationSkill(self.settings)
        self.skills["document"] = DocumentSkill(self.settings)
        self.skills["github"] = GithubSkill(self.settings)
        self.skills["gantt"] = GanttSkill(self.settings)
        
        logger.info(f"已加载 {len(self.skills)} 个技能")
    
    def execute_skill(self, skill_name: str, **kwargs) -> Dict[str, Any]:
        """执行指定技能"""
        if skill_name not in self.skills:
            raise ValueError(f"未知的技能: {skill_name}")
        
        skill = self.skills[skill_name]
        return skill.execute(**kwargs)
    
    def run(self):
        """运行 Agent"""
        logger.info("Rong_AiAgent 已启动")
        logger.info("可用技能: %s", list(self.skills.keys()))
        
        print("\nRong_AiAgent 已就绪！")
        print("输入 'exit' 或 'quit' 退出\n")
        
        while True:
            try:
                user_input = input("> " ).strip()
                if user_input.lower() in ['exit', 'quit']:
                    break
                if not user_input:
                    continue
                
                self._handle_input(user_input)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"处理输入时出错: {e}")
    
    def _handle_input(self, user_input: str):
        """处理用户输入"""
        print(f"收到输入: {user_input}")
        print("（功能开发中...）\n")
