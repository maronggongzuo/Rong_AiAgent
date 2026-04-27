"""技能基类"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from config.settings import Settings


class BaseSkill(ABC):
    """技能基类"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.name = self.__class__.__name__
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行技能"""
        pass
    
    def get_name(self) -> str:
        """获取技能名称"""
        return self.name
