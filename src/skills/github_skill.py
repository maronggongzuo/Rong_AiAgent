"""GitHub 技能 - 集成外部服务的示例"""

import logging
from typing import Dict, Any, Optional
from .base_skill import BaseSkill
from config.settings import Settings

logger = logging.getLogger(__name__)


class GithubSkill(BaseSkill):
    """GitHub 技能 - 展示如何集成外部服务"""
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.name = "github"
        self.github_token = settings.GITHUB_TOKEN
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行 GitHub 相关操作"""
        action = kwargs.get("action", "get_repos")
        
        if action == "get_repos":
            return self.get_repositories(**kwargs)
        elif action == "get_issues":
            return self.get_issues(**kwargs)
        elif action == "create_issue":
            return self.create_issue(**kwargs)
        else:
            return {"success": False, "error": f"未知的操作: {action}"}
    
    def get_repositories(self, **kwargs) -> Dict[str, Any]:
        """获取仓库列表（模拟实现）"""
        username = kwargs.get("username", "example")
        
        logger.info(f"获取 {username} 的 GitHub 仓库")
        
        # 真实场景中，这里会调用 GitHub API
        return {
            "success": True,
            "username": username,
            "repositories": [
                {"name": "project-1", "stars": 100},
                {"name": "project-2", "stars": 50}
            ]
        }
    
    def get_issues(self, **kwargs) -> Dict[str, Any]:
        """获取 Issues（模拟实现）"""
        repo = kwargs.get("repo", "project-1")
        
        logger.info(f"获取仓库 {repo} 的 Issues")
        
        return {
            "success": True,
            "repo": repo,
            "issues": [
                {"title": "Bug 1", "state": "open"},
                {"title": "Feature request", "state": "open"}
            ]
        }
    
    def create_issue(self, **kwargs) -> Dict[str, Any]:
        """创建 Issue（模拟实现）"""
        repo = kwargs.get("repo", "project-1")
        title = kwargs.get("title", "New Issue")
        body = kwargs.get("body", "")
        
        logger.info(f"在 {repo} 中创建 Issue: {title}")
        
        return {
            "success": True,
            "repo": repo,
            "issue_number": 123,
            "title": title
        }
