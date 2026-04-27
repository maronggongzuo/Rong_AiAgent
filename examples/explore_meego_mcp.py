#!/usr/bin/env python3
"""探索 Meego MCP 工具，获取项目信息和看板 Tech Owner"""

import sys
import os
from pathlib import Path
import logging
import requests
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.skills.meego_skill import MeegoSkill


def call_mcp_tool(skill: MeegoSkill, tool_name: str, arguments: dict) -> dict:
    """调用 MCP 工具"""
    logger.info(f"调用工具: {tool_name}")
    
    try:
        headers = {
            "X-Mcp-Token": skill.mcp_token,
            "Content-Type": "application/json"
        }
        
        # MCP 协议：调用工具的请求
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = requests.post(
            skill.mcp_url,
            headers=headers,
            json=request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result:
                return result['result']
            return result
        else:
            logger.error(f"工具调用失败，状态码: {response.status_code}")
            return {"error": f"状态码: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"调用工具时发生错误: {e}")
        return {"error": str(e)}


def extract_content(result: dict) -> dict:
    """从结果中提取内容"""
    if 'content' in result and len(result['content']) > 0:
        content_text = result['content'][0].get('text', '')
        try:
            return json.loads(content_text)
        except:
            return content_text
    return result


def explore_workitem_detail(skill: MeegoSkill, project_key: str, workitem_id: str):
    """探索工作项详情"""
    print("\n" + "=" * 60)
    print(f"🔍 探索工作项详情: {workitem_id}")
    print("=" * 60)
    
    # 尝试获取工作项概要
    print("\n1. 尝试获取工作项概要...")
    brief_result = call_mcp_tool(skill, "get_workitem_brief", {
        "project_key": project_key,
        "work_item_id": workitem_id
    })
    brief_content = extract_content(brief_result)
    print(f"结果: {brief_content}")
    
    # 尝试获取工作项字段配置
    print("\n2. 尝试获取工作项字段配置...")
    field_config_result = call_mcp_tool(skill, "list_workitem_field_config", {
        "project_key": project_key,
        "work_item_type_key": "story"
    })
    field_config_content = extract_content(field_config_result)
    print(f"结果: {json.dumps(field_config_content, ensure_ascii=False, indent=2)}")
    
    # 尝试获取工作项角色配置
    print("\n3. 尝试获取工作项角色配置...")
    role_config_result = call_mcp_tool(skill, "list_workitem_role_config", {
        "project_key": project_key,
        "work_item_type_key": "story"
    })
    role_config_content = extract_content(role_config_result)
    print(f"结果: {json.dumps(role_config_content, ensure_ascii=False, indent=2)}")


def main():
    print("=" * 60)
    print("🔧 探索 Meego MCP 工具")
    print("=" * 60)
    
    settings = Settings()
    skill = MeegoSkill(settings)
    
    # 使用我们找到的项目键
    project_key = "5f6330a7796d72a1ca2278c5"
    # 使用第一个工作项 ID
    workitem_id = "6787296030"
    
    # 探索工作项详情
    explore_workitem_detail(skill, project_key, workitem_id)
    
    print("\n" + "=" * 60)
    print("✅ 探索完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
