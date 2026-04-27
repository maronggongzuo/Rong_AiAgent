"""文档生成器"""

import logging
from typing import Dict, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class DocumentGenerator:
    """文档生成器"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
    
    def load_template(self, template_name: str) -> str:
        """加载文档模板"""
        template_path = self.templates_dir / f"{template_name}.md"
        
        if template_path.exists():
            return template_path.read_text(encoding="utf-8")
        else:
            return self._get_default_template(template_name)
    
    def _get_default_template(self, template_name: str) -> str:
        """获取默认模板"""
        templates = {
            "project_report": """# {project_name} 项目报告

## 项目概况
- 项目名称: {project_name}
- 报告日期: {report_date}
- 项目状态: {status}

## 进度摘要
{progress_summary}

## 里程碑
{milestones}

## 风险与问题
{risks}
""",
            "meeting_minutes": """# {meeting_title} 会议纪要

## 会议信息
- 时间: {meeting_time}
- 参会人: {attendees}
- 主持人: {host}

## 议题
{agenda}

## 决议
{decisions}

## 行动项
{action_items}
"""
        }
        return templates.get(template_name, "# 文档\n\n请提供模板内容。")
    
    def generate(self, template_name: str, data: Dict[str, Any]) -> str:
        """生成文档"""
        template = self.load_template(template_name)
        
        try:
            content = template.format(**data)
            return content
        except KeyError as e:
            logger.warning(f"模板缺少变量: {e}")
            return template
    
    def save_document(self, content: str, output_path: str):
        """保存文档"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8")
        logger.info(f"文档已保存: {output_path}")
