"""工具函数"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def load_json(file_path: str) -> Dict[str, Any]:
    """加载 JSON 文件"""
    path = Path(file_path)
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: str):
    """保存 JSON 文件"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_current_time_str() -> str:
    """获取当前时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_date(date_obj: datetime) -> str:
    """格式化日期"""
    return date_obj.strftime("%Y-%m-%d")
