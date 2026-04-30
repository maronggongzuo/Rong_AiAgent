"""Meego 技能 - 用于 Meego 看板通知"""

import logging
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from .base_skill import BaseSkill
from config.settings import Settings
from src.integrations.feishu_client import FeishuClient

logger = logging.getLogger(__name__)


class MeegoSkill(BaseSkill):
    """Meego 技能"""
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.name = "meego"
        self.feishu_client = FeishuClient(settings)
        self.mcp_url = settings.MEEGO_MCP_URL
        self.mcp_token = settings.MEEGO_MCP_TOKEN
        self.project_key = settings.MEEGO_PROJECT_KEY
        self.max_workitems = settings.MEEGO_MAX_WORKITEMS
        
        # 模板路径配置
        if settings.MEEGO_TEMPLATE_PATH:
            self.template_path = Path(settings.MEEGO_TEMPLATE_PATH)
        else:
            self.template_path = Path(__file__).parent.parent.parent / "docs" / "meego_notification_template.md"
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行 Meego 相关操作"""
        action = kwargs.get("action", "send_notification")
        
        if action == "send_notification":
            return self.send_meego_notification(**kwargs)
        elif action == "get_board_owners":
            return self.get_board_tech_owners(**kwargs)
        elif action == "test_connection":
            return self.test_mcp_connection(**kwargs)
        elif action == "get_business_lines":
            board_url = kwargs.get("board_url", "")
            work_item_type = kwargs.get("work_item_type", "story")
            format_output = kwargs.get("format_output", True)
            result = self.get_business_lines_from_board(board_url, work_item_type)
            if format_output and result.get("success"):
                result["formatted_text"] = self.format_business_lines_result(result)
            return result
        else:
            return {"success": False, "error": f"未知的操作: {action}"}
    
    def test_mcp_connection(self) -> Dict[str, Any]:
        """测试 MCP 服务器连接"""
        logger.info(f"测试 MCP 服务器连接: {self.mcp_url}")
        
        if not self.mcp_url or not self.mcp_token:
            return {
                "success": False,
                "error": "MCP 配置不完整，请检查 MEEGO_MCP_URL 和 MEEGO_MCP_TOKEN"
            }
        
        try:
            # 构建 MCP 请求
            headers = {
                "X-Mcp-Token": self.mcp_token,
                "Content-Type": "application/json"
            }
            
            # 尝试获取工具列表或调用简单的工具
            # 首先尝试访问根路径
            response = requests.get(
                self.mcp_url,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "MCP 服务器连接成功",
                    "url": self.mcp_url,
                    "status_code": response.status_code
                }
            elif response.status_code == 404:
                # 404 可能是因为需要特定的端点，尝试调用工具
                logger.info("根路径返回 404，尝试调用工具")
                return self._try_list_tools(headers)
            else:
                return {
                    "success": False,
                    "error": f"服务器返回错误状态码: {response.status_code}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "无法连接到 MCP 服务器，请检查网络连接和 URL"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "连接 MCP 服务器超时"
            }
        except Exception as e:
            logger.error(f"测试连接时发生错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _try_list_tools(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """尝试列出可用的工具"""
        try:
            # MCP 协议：列出工具的请求
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            response = requests.post(
                self.mcp_url,
                headers=headers,
                json=list_tools_request,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                tools = result.get("result", {}).get("tools", [])
                return {
                    "success": True,
                    "message": "MCP 服务器连接成功",
                    "url": self.mcp_url,
                    "status_code": response.status_code,
                    "available_tools": [tool.get("name") for tool in tools]
                }
            else:
                return {
                    "success": False,
                    "error": f"调用工具列表失败，状态码: {response.status_code}",
                    "status_code": response.status_code
                }
        except Exception as e:
            logger.error(f"尝试列出工具时发生错误: {e}")
            return {
                "success": False,
                "error": f"连接到 MCP 服务器成功，但调用工具失败: {str(e)}"
            }
    
    def get_business_filtered_tech_owners(
        self,
        board_url: str,
        business_line: Optional[str] = None,
        view_id: Optional[str] = None,
        project_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取指定业务线的 Tech Owner（按业务线过滤工作项）"""
        logger.info(f"获取业务线过滤的 Tech Owner: {board_url}, 业务线: {business_line}")
        
        # 1. 先获取所有工作项及其业务线信息
        business_result = self.get_business_lines_from_board(board_url, "story")
        if not business_result.get("success"):
            return {"success": False, "error": business_result.get("error", "获取业务线信息失败")}
        
        workitems = business_result.get("workitems", [])
        logger.info(f"获取到 {len(workitems)} 个工作项")
        
        # 2. 按业务线过滤
        filtered_workitems = []
        if business_line:
            for item in workitems:
                # 从 business 字段中解析业务线标签
                business_info = item.get("business")
                item_business_label = "未设置"
                if business_info:
                    label = business_info.get("label", "")
                    children = business_info.get("children", [])
                    if children:
                        child = children[0] if children else None
                        if child:
                            item_business_label = f"{label}/{child.get('label', '')}"
                    elif label:
                        item_business_label = label
                
                # 比较业务线
                if item_business_label and business_line.lower() in item_business_label.lower():
                    filtered_workitems.append(item)
            
            logger.info(f"按业务线 '{business_line}' 过滤后，剩余 {len(filtered_workitems)} 个工作项")
        else:
            filtered_workitems = workitems
        
        if not filtered_workitems:
            return {
                "success": True,
                "workitem_count": 0,
                "tech_owners": [],
                "owner_count": {},
                "filtered_workitems": []
            }
        
        # 3. 获取过滤后的工作项的 Tech Owner
        workitem_ids = [item.get("work_item_id") for item in filtered_workitems if item.get("work_item_id")]
        project_key = project_key or self.project_key
        
        owner_count_by_key = {}
        owner_count_by_email = {}
        owner_info = {}
        
        max_items_to_check = min(len(workitem_ids), self.max_workitems)
        
        for i, workitem_id in enumerate(workitem_ids[:max_items_to_check]):
            try:
                brief_result = self._call_mcp_tool("get_workitem_brief", {
                    "project_key": project_key,
                    "work_item_id": workitem_id
                })
                
                brief_content = self._extract_mcp_content(brief_result, expect_json=True)
                
                tech_owners = self._extract_tech_owners_from_brief(brief_content)
                
                for owner in tech_owners:
                    owner_key = owner.get("key", "")
                    owner_email = owner.get("email", "")
                    
                    if owner_key:
                        if owner_key in owner_count_by_key:
                            owner_count_by_key[owner_key] += 1
                        else:
                            owner_count_by_key[owner_key] = 1
                            owner_info[owner_key] = owner
                        
                        if owner_email:
                            if owner_email in owner_count_by_email:
                                owner_count_by_email[owner_email] += 1
                            else:
                                owner_count_by_email[owner_email] = 1
                
            except Exception as e:
                logger.warning(f"获取工作项 {workitem_id} 信息失败: {e}")
        
        tech_owners = list(owner_info.values())
        
        return {
            "success": True,
            "workitem_count": len(filtered_workitems),
            "tech_owners": tech_owners,
            "owner_count": owner_count_by_key,
            "filtered_workitems": filtered_workitems
        }
    
    def get_board_tech_owners(self, board_url: str, view_id: Optional[str] = None, project_key: Optional[str] = None) -> Dict[str, Any]:
        """获取看板的 Tech Owner（从所有工作项中收集）"""
        logger.info(f"获取看板 Tech Owner: {board_url}")
        
        #  # 如果没有提供 view_id，从 URL 中解析
        if not view_id:
            view_id = self._parse_view_id_from_url(board_url)
            
        if not view_id:
            return {"success": False, "error": "无法从 URL 中解析 view_id"}
        
        # 使用提供的 project_key 或默认值
        project_key = project_key or self.project_key
        
        # 首先测试 MCP 连接
        connection_test = self.test_mcp_connection()
        if not connection_test.get("success"):
            error_msg = f"MCP 连接测试失败: {connection_test.get('error')}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # 1. 获取视图详情，得到工作项列表
            view_result = self._call_mcp_tool("get_view_detail", {
                "project_key": project_key,
                "view_id": view_id
            })
            
            view_content = self._extract_mcp_content(view_result, expect_json=False)
            
            # 2. 解析视图内容，提取工作项 ID
            workitem_ids = self._extract_workitem_ids_from_view(view_content)
            
            if not workitem_ids:
                error_msg = "未从视图中获取到工作项"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            logger.info(f"从视图中获取到 {len(workitem_ids)} 个工作项")
            
            # 3. 遍历所有工作项，收集 Tech Owner 并统计次数
            owner_count_by_key = {}  # 按 key 统计出现次数 {key: count}
            owner_count_by_email = {}  # 按 email 统计出现次数 {email: count}
            owner_info = {}  # 保存 owner 信息 {key: owner}
            
            # 限制只检查前 N 个工作项以提高性能
            max_items_to_check = min(len(workitem_ids), self.max_workitems)
            
            for i, workitem_id in enumerate(workitem_ids[:max_items_to_check]):
                try:
                    brief_result = self._call_mcp_tool("get_workitem_brief", {
                        "project_key": project_key,
                        "work_item_id": workitem_id
                    })
                    
                    brief_content = self._extract_mcp_content(brief_result, expect_json=True)
                    
                    tech_owners = self._extract_tech_owners_from_brief(brief_content)
                    
                    for owner in tech_owners:
                        owner_key = owner.get("key", "")
                        owner_email = owner.get("email", "")
                        
                        if owner_key:
                            # 统计次数
                            if owner_key in owner_count_by_key:
                                owner_count_by_key[owner_key] += 1
                            else:
                                owner_count_by_key[owner_key] = 1
                                owner_info[owner_key] = owner
                            
                            # 同时按 email 统计
                            if owner_email:
                                if owner_email in owner_count_by_email:
                                    owner_count_by_email[owner_email] += 1
                                else:
                                    owner_count_by_email[owner_email] = 1
                            
                except Exception as e:
                    logger.warning(f"获取工作项 {workitem_id} 信息失败: {e}")
                    continue
            
            if not owner_info:
                error_msg = "未找到 Tech Owner"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            logger.info(f"共收集到 {len(owner_info)} 个不重复的 Tech Owner")
            
            # 构建结果
            all_tech_owners = list(owner_info.values())
            
            return {
                "success": True,
                "board_url": board_url,
                "view_id": view_id,
                "tech_owners": all_tech_owners,
                "owner_count": owner_count_by_email,  # 保存 email 到 count 的映射
                "workitem_count": len(workitem_ids),
                "checked_count": max_items_to_check,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"获取 Tech Owner 时发生错误: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _call_mcp_tool(self, tool_name: str, arguments: dict) -> dict:
        """调用 MCP 工具"""
        headers = {
            "X-Mcp-Token": self.mcp_token,
            "Content-Type": "application/json"
        }
        
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
            self.mcp_url,
            headers=headers,
            json=request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                return result["result"]
            return result
        else:
            logger.error(f"工具调用失败，状态码: {response.status_code}")
            return {"error": f"状态码: {response.status_code}"}
    
    def _extract_mcp_content(self, result: dict, expect_json: bool = False) -> any:
        """从 MCP 结果中提取内容
        
        Args:
            result: MCP 结果
            expect_json: 是否期望 JSON 格式（对于工作项详情）
        """
        # 调试输出完整结果
        logger.debug(f"MCP 完整结果: {json.dumps(result, ensure_ascii=False)[:500]}")
        
        content_text = ""
        
        # 先处理 content 字段
        if "content" in result:
            content = result["content"]
            
            # 处理常见格式：[{"type": "text", "text": "..."}]
            if isinstance(content, list):
                for content_item in content:
                    if isinstance(content_item, dict):
                        text = content_item.get("text", "")
                        if text and not text.startswith("log_id:"):
                            content_text += text
            elif isinstance(content, dict):
                # 尝试直接获取 text
                if "text" in content:
                    content_text = content["text"]
                else:
                    content_text = str(content)
            else:
                content_text = str(content)
        else:
            content_text = str(result)
        
        if expect_json and content_text:
            # 尝试解析为 JSON
            try:
                parsed = json.loads(content_text)
                # 返回完整的解析结果，不要过滤
                return parsed
            except Exception as e:
                logger.debug(f"JSON 解析失败: {e}")
                # 尝试查找 JSON 部分
                try:
                    # 查找第一个 { 和对应的 }
                    start_idx = content_text.find("{")
                    if start_idx >= 0:
                        brace_count = 1
                        end_idx = start_idx + 1
                        while end_idx < len(content_text) and brace_count > 0:
                            if content_text[end_idx] == "{":
                                brace_count += 1
                            elif content_text[end_idx] == "}":
                                brace_count -= 1
                            end_idx += 1
                        json_str = content_text[start_idx:end_idx]
                        parsed = json.loads(json_str)
                        # 返回完整的解析结果，不要过滤
                        return parsed
                except Exception as e2:
                    logger.error(f"第二次 JSON 解析失败: {e2}")
                    logger.error(f"原始内容: {content_text[:1000]}")
        
        return content_text if content_text else result
    
    def _extract_workitem_ids_from_view(self, view_content) -> List[str]:
        """从视图内容中提取工作项 ID"""
        workitem_ids = []
        
        logger.debug(f"开始解析视图内容，类型: {type(view_content)}")
        
        # 先尝试解析 JSON
        content_str = str(view_content)
        
        # 尝试从 JSON 中提取
        try:
            import json
            parsed = json.loads(content_str)
            logger.debug(f"成功解析为 JSON: {type(parsed)}")
            
            # 尝试从多种结构中获取工作项
            if isinstance(parsed, dict):
                if "list" in parsed:
                    items = parsed["list"]
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict) and "work_item_id" in item:
                                workitem_ids.append(str(item["work_item_id"]))
                elif "items" in parsed:
                    items = parsed["items"]
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict) and "work_item_id" in item:
                                workitem_ids.append(str(item["work_item_id"]))
                elif "data" in parsed:
                    data = parsed["data"]
                    if isinstance(data, dict):
                        for key in ["list", "items", "work_items"]:
                            if key in data:
                                items = data[key]
                                if isinstance(items, list):
                                    for item in items:
                                        if isinstance(item, dict) and "work_item_id" in item:
                                            workitem_ids.append(str(item["work_item_id"]))
        except Exception as e:
            logger.debug(f"解析 JSON 失败: {e}")
        
        # 如果 JSON 解析没找到，尝试 Markdown 表格
        if not workitem_ids and isinstance(view_content, str):
            lines = view_content.split("\n")
            logger.debug(f"解析 Markdown 表格，共 {len(lines)} 行")
            for line in lines:
                # 跳过表头和分隔线
                if line.startswith("| 需求标题") or line.startswith("| 工作项 ID") or line.startswith("| ---"):
                    continue
                if line.startswith("|"):
                    # 解析表格行
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    # 找到数字部分作为工作项 ID
                    for part in parts:
                        if part.isdigit():
                            workitem_ids.append(part)
                            break
        
        # 最后的尝试：直接用正则查找所有数字
        if not workitem_ids:
            import re
            numbers = re.findall(r'\b(\d{6,})\b', content_str)
            if numbers:
                workitem_ids = list(set(numbers))  # 去重
                logger.debug(f"通过正则找到 {len(workitem_ids)} 个可能的工作项 ID")
        
        logger.info(f"最终提取到 {len(workitem_ids)} 个工作项 ID: {workitem_ids[:10]}")
        return workitem_ids
    
    def _extract_tech_owners_from_brief(self, brief_content: dict) -> List[dict]:
        """从工作项概要中提取 Tech Owner"""
        tech_owners = []
        
        if isinstance(brief_content, dict):
            work_item_attribute = brief_content.get("work_item_attribute", {})
            role_members = work_item_attribute.get("role_members", [])
            
            for role in role_members:
                if role.get("key") == "Tech_Owner":
                    members = role.get("members", [])
                    for member in members:
                        tech_owners.append({
                            "name": member.get("name", ""),
                            "email": member.get("email", ""),
                            "key": member.get("key", ""),
                            "open_id": member.get("key", "")  # 使用 key 作为 open_id
                        })
        
        return tech_owners
    
    def send_meego_notification(
        self,
        chat_id: str,
        board_url: str,
        template: str = "default",
        recipients: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """发送 Meego 看板通知
        
        Args:
            chat_id: 群聊 ID
            board_url: Meego 看板 URL
            template: 通知模板类型
            recipients: 额外的收件人列表
        """
        logger.info(f"发送 Meego 通知到群聊: {chat_id}")
        
        # 获取看板 Tech Owner
        owners_result = self.get_board_tech_owners(board_url)
        if not owners_result.get("success"):
            return {"success": False, "error": "获取 Tech Owner 失败"}
        
        tech_owners = owners_result.get("tech_owners", [])
        owner_names = [owner.get("name") for owner in tech_owners]
        owner_ids = [owner.get("open_id") for owner in tech_owners if owner.get("open_id")]
        
        # 构建通知内容
        if template == "default":
            text_message, _ = self._build_default_template(owner_names)
        else:
            text_message, _ = self._build_custom_template(template, owner_names)
        
        # 发送到群聊（使用文本消息）
        result = self.feishu_client.send_text_message(
            user_id=chat_id,
            text=text_message,
            receive_id_type="chat_id"
        )
        
        # 发送给 Tech Owner 个人（如果需要）
        individual_results = []
        if recipients:
            for recipient in recipients:
                individual_result = self.feishu_client.send_text_message(
                    user_id=recipient,
                    text=text_message
                )
                individual_results.append({"recipient": recipient, "result": individual_result})
        
        return {
            "success": result.get("code") == 0,
            "chat_id": chat_id,
            "board_url": board_url,
            "tech_owners": owner_names,
            "message": text_message,
            "feishu_result": result,
            "individual_results": individual_results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_default_template(self, owner_names: List[str]) -> tuple:
        """构建默认通知模板，返回 (文本消息, 富文本内容)"""
        owners_text = "、".join(owner_names) if owner_names else "相关同学"
        
        if not self.template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {self.template_path}")
        
        with open(self.template_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        # 移除 Markdown 标题（第一行）
        lines = template.split("\n")
        if lines and lines[0].startswith("#"):
            lines = lines[1:]
            template = "\n".join(lines)
        
        # 替换占位符
        message = template.replace("{owners_text}", owners_text).strip()
        
        # 构建富文本内容
        rich_content = self._parse_to_rich_text(lines, owners_text)
        
        return message, rich_content
    
    def _parse_to_rich_text(self, template_content: str, placeholder_values: Dict[str, str]) -> List[List[Dict[str, Any]]]:
        """解析模板为飞书富文本格式
        
        Args:
            template_content: 模板内容
            placeholder_values: 占位符值的字典，如 {"owners_text_1": "张三、李四"}
        """
        result = []
        lines = template_content.split('\n')
        
        for line in lines:
            if not line.strip():
                continue
                
            # 跳过标题行（以 # 开头）
            if line.startswith('#'):
                continue
            
            # 替换所有占位符
            processed_line = line
            for placeholder, value in placeholder_values.items():
                processed_line = processed_line.replace(placeholder, value)
            
            # 解析链接格式：[链接文字](链接地址)
            # 同时解析艾特标签：<at user_id="xxx">姓名</at>
            line_elements = []
            
            import re
            # 匹配模式：链接 或 艾特标签
            pattern = r'(\[.*?\]\(https?://[^\)]+\))|(<at user_id="[^"]+">[^<]+</at>)'
            
            # 逐个匹配
            last_pos = 0
            for match in re.finditer(pattern, processed_line):
                # 添加链接前的文字
                if match.start() > last_pos:
                    text_before = processed_line[last_pos:match.start()]
                    if text_before.strip() or len(text_before) > 0:
                        line_elements.append({"tag": "text", "text": text_before})
                
                matched_text = match.group(0)
                
                # 判断是链接还是艾特
                if matched_text.startswith('['):
                    # 解析链接
                    link_match = re.match(r'\[(.*?)\]\((https?://[^\)]+)\)', matched_text)
                    if link_match:
                        link_text = link_match.group(1)
                        link_url = link_match.group(2)
                        line_elements.append({"tag": "a", "text": link_text, "href": link_url})
                else:
                    # 解析艾特标签
                    at_match = re.match(r'<at user_id="([^"]+)">([^<]+)</at>', matched_text)
                    if at_match:
                        at_id = at_match.group(1)
                        at_name = at_match.group(2)
                        line_elements.append({"tag": "at", "user_id": at_id, "user_name": at_name})
                
                last_pos = match.end()
            
            # 添加剩余的文字
            if last_pos < len(processed_line):
                text_after = processed_line[last_pos:]
                if text_after.strip() or len(text_after) > 0:
                    line_elements.append({"tag": "text", "text": text_after})
            
            # 如果没有找到任何元素，直接添加整行
            if not line_elements:
                line_elements.append({"tag": "text", "text": processed_line})
            
            result.append(line_elements)
        
        return result
    
    def _build_custom_template(self, template: str, owner_names: List[str]) -> tuple:
        """构建自定义通知模板"""
        # 这里可以扩展其他模板类型
        return self._build_default_template(owner_names)
    
    def _parse_view_id_from_url(self, board_url: str) -> Optional[str]:
        """从 Meego URL 中解析 view_id"""
        # URL 格式类似: https://meego.larkoffice.com/pnsi/storyView/Ztxhe1ZDR
        # 或者: https://meego.larkoffice.com/pnsi/storyView/2FwTFmZDR?scope=workspaces&node=63579615
        
        # 查找 storyView 后面的 ID
        match = re.search(r'storyView/([^/?]+)', board_url)
        if match:
            return match.group(1)
        return None
    
    def extract_meego_links(self, template_content: str) -> List[str]:
        """从模板内容中提取 Meego 看板链接（按出现顺序）"""
        # 提取 Markdown 链接格式 [text](url) 中的 URL，保持顺序
        link_pattern = r'\[(.*?)\]\((https://meego\.larkoffice\.com[^\)]+)\)'
        links = []
        for match in re.finditer(link_pattern, template_content):
            links.append(match.group(2))
        
        logger.info(f"从模板中提取到 {len(links)} 个看板链接")
        return links
    
    def get_business_line_config(self, project_key: Optional[str] = None, work_item_type: str = "story") -> Dict[str, Any]:
        """获取业务线字段配置树
        
        Args:
            project_key: 项目 key，使用默认配置如果不提供
            work_item_type: 工作项类型，默认为 story
            
        Returns:
            业务线字段配置结果
        """
        project_key = project_key or self.project_key
        logger.info(f"获取业务线配置树，project_key: {project_key}, work_item_type: {work_item_type}")
        
        try:
            # 调用 MCP 工具获取工作项字段配置
            result = self._call_mcp_tool("list_workitem_field_config", {
                "project_key": project_key,
                "work_item_type": work_item_type,
                "field_keys": ["business"]
            })
            
            content = self._extract_mcp_content(result, expect_json=True)
            logger.debug(f"业务线配置结果: {content}")
            return {"success": True, "content": content}
        except Exception as e:
            error_msg = f"获取业务线配置失败: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def find_data_protection_sub_lines(self, project_key: Optional[str] = None, target_name: str = "Data Protection") -> Dict[str, Any]:
        """查找指定业务线及其子业务线
        
        Args:
            project_key: 项目 key，使用默认配置如果不提供
            target_name: 要查找的业务线名称
            
        Returns:
            包含目标业务线及其子业务线的结果
        """
        config_result = self.get_business_line_config(project_key)
        
        if not config_result.get("success"):
            return config_result
        
        content = config_result.get("content", {})
        
        # 调试输出：打印完整的返回内容
        logger.info(f"配置返回内容类型: {type(content)}")
        
        # 解析配置，找到 business 字段的 options
        business_field = None
        fields_list = None
        
        # 尝试多种可能的数据结构
        if isinstance(content, dict):
            # 尝试直接找 fields
            if "fields" in content:
                fields_list = content.get("fields", [])
            # 尝试找 data 字段，可能是分页包装
            elif "data" in content:
                data = content.get("data", {})
                if isinstance(data, dict) and "fields" in data:
                    fields_list = data.get("fields", [])
            # 尝试找其他可能的键
            else:
                for key in ["work_item_fields", "items", "list", "result"]:
                    if key in content:
                        fields_list = content.get(key, [])
                        if isinstance(fields_list, dict) and "fields" in fields_list:
                            fields_list = fields_list.get("fields", [])
                        break
        
        # 如果找到字段列表，查找 business 字段
        if fields_list:
            logger.info(f"找到 {len(fields_list)} 个字段")
            for field in fields_list:
                if isinstance(field, dict) and field.get("field_key") == "business":
                    business_field = field
                    break
        
        # 如果还没找到，尝试更全面的递归搜索
        if not business_field:
            def find_fields_recursive(obj, depth=0):
                """递归查找 fields 列表"""
                if depth > 5:
                    return None
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key == "fields" and isinstance(value, list):
                            return value
                        found = find_fields_recursive(value, depth + 1)
                        if found:
                            return found
                elif isinstance(obj, list):
                    for item in obj:
                        found = find_fields_recursive(item, depth + 1)
                        if found:
                            return found
                return None
            
            deep_fields = find_fields_recursive(content)
            if deep_fields:
                logger.info(f"递归找到 {len(deep_fields)} 个字段")
                for field in deep_fields:
                    if isinstance(field, dict) and field.get("field_key") == "business":
                        business_field = field
                        break
        
        if not business_field:
            return {
                "success": False, 
                "error": "未找到 business 字段配置",
                "raw_content": str(content)[:2000]
            }
        
        # 尝试 options 或 option 字段
        options = business_field.get("options", [])
        if not options:
            options = business_field.get("option", [])
        logger.info(f"找到 {len(options)} 个顶级业务线选项")
        
        # 递归查找目标业务线节点
        def find_node_recursive(opts: List[Dict], name: str) -> Optional[Dict]:
            for opt in opts:
                opt_name = opt.get("option_name", "")
                if opt_name == name or (isinstance(opt_name, str) and name.lower() in opt_name.lower()):
                    return opt
                # 检查子节点，同时尝试 children 和 child 字段
                children = opt.get("children", [])
                if not children:
                    children = opt.get("child", [])
                if children:
                    found = find_node_recursive(children, name)
                    if found:
                        return found
            return None
        
        target_node = find_node_recursive(options, target_name)
        
        if not target_node:
            return {"success": False, "error": f"未找到 '{target_name}' 业务线"}
        
        # 获取子业务线，尝试 children 和 child 字段
        sub_lines = target_node.get("children", [])
        if not sub_lines:
            sub_lines = target_node.get("child", [])
        
        return {
            "success": True,
            "target_node": target_node,
            "sub_lines": sub_lines
        }
    
    def print_business_lines(self, target_name: str = "Data Protection") -> str:
        """打印指定业务线及其子业务线（默认 Data Protection）
        
        Args:
            target_name: 要查找的业务线名称
            
        Returns:
            格式化的输出字符串
        """
        output = []
        output.append("=" * 60)
        output.append("业务线查询结果")
        output.append("=" * 60)
        
        # 先获取并打印所有业务线
        config_result = self.get_business_line_config()
        
        if not config_result.get("success"):
            output.append(f"获取配置失败: {config_result.get('error')}")
            output.append("=" * 60)
            return "\n".join(output)
        
        content = config_result.get("content", {})
        
        # 查找 business 字段
        business_field = None
        fields_list = None
        
        # 尝试多种可能的数据结构
        if isinstance(content, dict):
            if "fields" in content:
                fields_list = content.get("fields", [])
            elif "data" in content:
                data = content.get("data", {})
                if isinstance(data, dict) and "fields" in data:
                    fields_list = data.get("fields", [])
            else:
                for key in ["work_item_fields", "items", "list", "result"]:
                    if key in content:
                        fields_list = content.get(key, [])
                        if isinstance(fields_list, dict) and "fields" in fields_list:
                            fields_list = fields_list.get("fields", [])
                        break
        
        # 如果没找到，递归查找
        if not fields_list:
            def find_fields_recursive(obj, depth=0):
                if depth > 5:
                    return None
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key == "fields" and isinstance(value, list):
                            return value
                        found = find_fields_recursive(value, depth + 1)
                        if found:
                            return found
                elif isinstance(obj, list):
                    for item in obj:
                        found = find_fields_recursive(item, depth + 1)
                        if found:
                            return found
                return None
            fields_list = find_fields_recursive(content)
        
        if fields_list:
            for field in fields_list:
                if isinstance(field, dict) and field.get("field_key") == "business":
                    business_field = field
                    break
        
        if not business_field:
            output.append("未找到 business 字段配置")
            output.append(f"原始内容前2000字符: {str(content)[:2000]}")
            output.append("=" * 60)
            return "\n".join(output)
        
        # 尝试 options 或 option 字段
        options = business_field.get("options", [])
        if not options:
            options = business_field.get("option", [])
        
        # 打印所有业务线树形结构
        output.append("\n完整业务线树形结构:")
        output.append("-" * 60)
        
        def print_tree(opts: List[Dict], level: int = 0):
            """递归打印树结构"""
            prefix = "  " * level
            for opt in opts:
                name = opt.get("option_name", "N/A")
                opt_id = opt.get("option_id", "N/A")
                output.append(f"{prefix}- {name} (option_id: {opt_id})")
                # 尝试 children 和 child 字段
                children = opt.get("children", [])
                if not children:
                    children = opt.get("child", [])
                if children:
                    print_tree(children, level + 1)
        
        print_tree(options)
        
        # 查找目标业务线
        result = self.find_data_protection_sub_lines(target_name=target_name)
        
        if not result.get("success"):
            error = result.get("error", "")
            output.append("\n")
            output.append("-" * 60)
            if "未找到" in error and target_name in error:
                output.append(f"错误: {error}")
                output.append("请查看上面的业务线树形结构，确认业务线名称是否正确")
            else:
                output.append(f"错误: {error}")
            if "raw_content" in result:
                output.append(f"\n原始内容前2000字符: {result.get('raw_content')}")
        else:
            output.append("\n")
            output.append("=" * 60)
            output.append(f"{target_name} 及其子业务线详情")
            output.append("=" * 60)
            
            target_node = result.get("target_node", {})
            sub_lines = result.get("sub_lines", [])
            
            output.append(f"\n主业务线: {target_node.get('option_name')}")
            output.append(f"option_id: {target_node.get('option_id')}")
            output.append(f"\n子业务线数量: {len(sub_lines)}")
            output.append("")
            
            if sub_lines:
                output.append("子业务线列表:")
                output.append("-" * 60)
                for i, line in enumerate(sub_lines, 1):
                    output.append(f"{i}. {line.get('option_name')}")
                    output.append(f"   option_id: {line.get('option_id')}")
                    # 如果有子子业务线也一并显示
                    grandchildren = line.get("children", [])
                    if not grandchildren:
                        grandchildren = line.get("child", [])
                    if grandchildren:
                        output.append(f"   下一级子业务线 ({len(grandchildren)}):")
                        for j, gc in enumerate(grandchildren, 1):
                            output.append(f"     {j}. {gc.get('option_name')}")
                            output.append(f"        option_id: {gc.get('option_id')}")
                    output.append("")
            else:
                output.append("没有找到子业务线")
        
        output.append("=" * 60)
        return "\n".join(output)
    
    def build_owners_text(self, owners_result: Dict[str, Any], owner_count: Optional[Dict[str, int]] = None, group_members: Optional[List[Dict[str, Any]]] = None) -> str:
        """构建 Tech Owner 文本（支持艾特，显示出现次数）
        
        Args:
            owners_result: Tech Owner 查询结果
            owner_count: 可选，每个 owner 出现的次数字典 {email: count}
            group_members: 可选，群组成员列表，用于匹配用户 ID
        """
        if owners_result.get("success"):
            tech_owners = owners_result.get("tech_owners", [])
            if not tech_owners:
                return "相关同学"
            
            # 收集所有邮箱
            emails = [owner.get("email") for owner in tech_owners if owner.get("email")]
            
            # 优先使用群成员匹配
            name_to_user_id = {}
            if group_members:
                logger.info(f"使用群组成员匹配，共 {len(group_members)} 人")
                for member in group_members:
                    member_name = member.get("name", "")
                    member_id = member.get("member_id", "")
                    if member_name and member_id:
                        name_to_user_id[member_name] = member_id
                        logger.debug(f"群成员: {member_name} -> {member_id}")
            
            # 如果群成员没有匹配到，再尝试邮箱查找
            email_to_user_id = {}
            if emails and not name_to_user_id:
                email_to_user_id = self.feishu_client.find_users_by_emails(emails)
            
            # 构建文本
            owner_parts = []
            for owner in tech_owners:
                name = owner.get("name", "")
                email = owner.get("email", "")
                
                # 构建显示文本（名字 + 出现次数）
                display_text = name
                if owner_count and email in owner_count and owner_count[email] > 1:
                    display_text = f"{name}（{owner_count[email]}）"
                
                # 优先通过姓名在群成员中查找
                user_id = None
                if name and name in name_to_user_id:
                    user_id = name_to_user_id[name]
                    logger.info(f"通过群成员匹配到: {name} -> {user_id}")
                # 没有的话再通过邮箱查找
                elif email and email in email_to_user_id and email_to_user_id[email]:
                    user_id = email_to_user_id[email]
                    logger.info(f"通过邮箱匹配到: {email} -> {user_id}")
                
                if user_id:
                    # 有用户 ID，艾特
                    owner_parts.append(f"<at user_id=\"{user_id}\">{display_text}</at>")
                else:
                    # 没有用户 ID，只显示名字
                    owner_parts.append(display_text)
            
            return "、".join(owner_parts)
        
        return "相关同学"
    
    def send_dual_board_notification(
        self,
        recipient_user_id: Optional[str] = None,
        recipient_chat_id: Optional[str] = None,
        template_path: Optional[Path] = None,
        project_key: Optional[str] = None,
        mention_admin: bool = True,
        mention_name: str = "管理员",
        business_line: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送双看板通知
        
        Args:
            recipient_user_id: 接收通知的用户 open_id（优先级高于 chat_id）
            recipient_chat_id: 接收通知的群聊 chat_id
            template_path: 自定义模板路径
            project_key: 自定义 project_key
            mention_admin: 是否艾特管理员（默认 True）
            mention_name: 艾特显示的名称（默认 "管理员"）
            business_line: 业务线过滤条件（如 "Data Protection/GCCC"），为空则不过滤
            
        Returns:
            通知发送结果
        """
        logger.info("开始发送双看板通知")
        
        # 优先使用传入的参数，其次使用配置
        recipient_user_id = recipient_user_id or self.settings.MEEGO_NOTIFICATION_RECIPIENT_USER_ID
        recipient_chat_id = recipient_chat_id or self.settings.MEEGO_NOTIFICATION_RECIPIENT_CHAT_ID
        
        # 使用配置的模板路径或默认路径
        template_path = template_path or self.template_path
        
        if not template_path.exists():
            error_msg = f"模板文件不存在: {template_path}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # 读取模板
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        

        
        # 1. 提取看板链接
        links = self.extract_meego_links(template_content)
        
        if not links:
            error_msg = "模板中未找到任何看板链接"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # 2. 获取每个链接的 Tech Owner
        link_owners = {}
        
        for link in links:
            view_id = self._parse_view_id_from_url(link)
            if not view_id:
                logger.warning(f"无法从链接解析 view_id: {link}")
                continue
            
            # 根据业务线参数决定使用哪个方法
            if business_line:
                logger.info(f"使用业务线过滤: {business_line}")
                owners_result = self.get_business_filtered_tech_owners(
                    board_url=link,
                    business_line=business_line,
                    view_id=view_id,
                    project_key=project_key
                )
            else:
                owners_result = self.get_board_tech_owners(
                    board_url=link,
                    view_id=view_id,
                    project_key=project_key
                )
            link_owners[link] = {
                "view_id": view_id,
                "owners_result": owners_result
            }
        
        # 2.5 如果发送到群组，先获取群组成员
        group_members = None
        if recipient_chat_id:
            logger.info(f"获取群组成员: {recipient_chat_id}")
            group_members = self.feishu_client.get_group_members(recipient_chat_id)
            if group_members:
                logger.info(f"获取到 {len(group_members)} 位群成员")
        
        # 3. 构建占位符值字典，并保留文本版本用于日志
        placeholder_values = {}
        message_content = template_content
        
        # 首先，全局替换业务线占位符
        business_placeholder = "{business_line}"
        if business_line:
            business_text = business_line
            placeholder_values[business_placeholder] = business_text
            message_content = message_content.replace(business_placeholder, business_text)
            logger.info(f"占位符 {business_placeholder} 对应值: {business_text}")
        
        # 然后，逐个替换看板相关的占位符
        for i, link in enumerate(links):
            # 替换需求数量占位符
            count_placeholder = f"{{workitems_count_{i+1}}}"
            owners_result = link_owners[link]["owners_result"]
            workitems_count = owners_result.get("workitem_count", 0) if owners_result.get("success") else 0
            placeholder_values[count_placeholder] = str(workitems_count)
            message_content = message_content.replace(count_placeholder, str(workitems_count))
            logger.info(f"占位符 {count_placeholder} 对应值: {workitems_count}")
            
            # 替换 Tech Owner 占位符
            owners_placeholder = f"{{owners_text_{i+1}}}"
            owner_count = owners_result.get("owner_count", {}) if owners_result.get("success") else {}
            owners_text = self.build_owners_text(owners_result, owner_count, group_members)
            placeholder_values[owners_placeholder] = owners_text
            message_content = message_content.replace(owners_placeholder, owners_text)
            logger.info(f"占位符 {owners_placeholder} 对应值: {owners_text}")
        
        # 替换管理员艾特占位符
        admin_placeholder = "{admin_mention}"
        if mention_admin and self.settings.FEISHU_ADMIN_USER_ID:
            admin_text = f"<at user_id=\"{self.settings.FEISHU_ADMIN_USER_ID}\">{mention_name}</at>"
            placeholder_values[admin_placeholder] = admin_text
            message_content = message_content.replace(admin_placeholder, admin_text)
            logger.info(f"占位符 {admin_placeholder} 对应值: {admin_text}")
        else:
            placeholder_values[admin_placeholder] = mention_name
            message_content = message_content.replace(admin_placeholder, mention_name)
            logger.info(f"占位符 {admin_placeholder} 对应值: {mention_name}")
        
        # 移除 Markdown 标题（保留文本版本的完整格式）
        if message_content.startswith("# "):
            lines = message_content.split("\n")
            message_content = "\n".join(lines[1:])
        
        message_content = message_content.strip()
        
        # 4. 发送通知（使用文本消息，先确保基础功能正常）
        send_result = None
        receive_id_type = None
        receive_id = None
        
        if recipient_user_id:
            receive_id = recipient_user_id
            receive_id_type = "open_id"
            send_result = self.feishu_client.send_text_message(
                user_id=recipient_user_id,
                text=message_content,
                receive_id_type="open_id"
            )
        elif recipient_chat_id:
            receive_id = recipient_chat_id
            receive_id_type = "chat_id"
            send_result = self.feishu_client.send_text_message(
                user_id=recipient_chat_id,
                text=message_content,
                receive_id_type="chat_id"
            )
        else:
            # 使用配置的管理员
            if self.settings.FEISHU_ADMIN_USER_ID:
                receive_id = self.settings.FEISHU_ADMIN_USER_ID
                receive_id_type = "open_id"
                send_result = self.feishu_client.send_text_message(
                    user_id=self.settings.FEISHU_ADMIN_USER_ID,
                    text=message_content,
                    receive_id_type="open_id"
                )
            else:
                error_msg = "没有配置接收者，请提供 recipient_user_id 或 recipient_chat_id 或配置 FEISHU_ADMIN_USER_ID"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
        
        success = send_result.get("code") == 0 if send_result else False
        
        result = {
            "success": success,
            "message_content": message_content,
            "receive_id": receive_id,
            "receive_id_type": receive_id_type,
            "feishu_result": send_result,
            "link_owners": link_owners,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            logger.info("双看板通知发送成功")
        else:
            logger.error(f"双看板通知发送失败: {send_result}")
        
        return result

    def _parse_meego_url(self, board_url: str) -> Dict[str, Optional[str]]:
        """从 Meego URL 中解析 simple_name、view_id、project_key、node_id
        
        Args:
            board_url: Meego 看板 URL
            
        Returns:
            包含 simple_name、view_id、project_key、node_id 的字典
        """
        result = {
            "simple_name": None,
            "view_id": None,
            "project_key": None,
            "node_id": None
        }
        
        # URL 格式: https://meego.larkoffice.com/<simple_name>/storyView/<view_id>?scope=workspaces&node=<node_id>
        # 解析 simple_name
        simple_name_match = re.search(r'meego\.larkoffice\.com/([^/]+)/storyView', board_url)
        if simple_name_match:
            result["simple_name"] = simple_name_match.group(1)
            result["project_key"] = result["simple_name"]
        
        # 解析 view_id
        view_id_match = re.search(r'storyView/([^/?]+)', board_url)
        if view_id_match:
            result["view_id"] = view_id_match.group(1)
        
        # 解析 node_id
        node_id_match = re.search(r'[?&]node=([^&]+)', board_url)
        if node_id_match:
            result["node_id"] = node_id_match.group(1)
        
        logger.info(f"从 URL 解析: simple_name={result['simple_name']}, view_id={result['view_id']}, project_key={result['project_key']}, node_id={result['node_id']}")
        return result

    def _parse_business_field(self, business_field: dict) -> Optional[Dict[str, Any]]:
        """解析业务线字段 (cascade_key_label_value 结构)
        
        Args:
            business_field: 业务线字段数据，可以是以下两种格式之一：
                           1. {"cascade_key_label_value": {...}} - MQL 查询返回的格式
                           2. {"key": "...", "value": {"cascade_key_label_value": {...}}} - 完整字段格式
            
        Returns:
            解析后的业务线信息，包含 label、key、children 等
        """
        if not business_field or not isinstance(business_field, dict):
            return None
        
        # 获取 cascade_key_label_value
        # 格式1: {"cascade_key_label_value": {...}} - MQL 查询返回
        cascade_data = business_field.get("cascade_key_label_value")
        
        # 如果没找到，尝试格式2: {"key": "...", "value": {"cascade_key_label_value": {...}}}
        if not cascade_data:
            value = business_field.get("value", {})
            if isinstance(value, dict):
                cascade_data = value.get("cascade_key_label_value")
        
        # 如果还是没找到，尝试直接使用 business_field（可能已经是 cascade_key_label_value）
        if not cascade_data and "key" in business_field and "label" in business_field:
            cascade_data = business_field
        
        if not cascade_data or not isinstance(cascade_data, dict):
            return None
        
        # 构建结果
        result = {
            "key": cascade_data.get("key", ""),
            "label": cascade_data.get("label", ""),
            "children": []
        }
        
        # 解析子业务线
        children = cascade_data.get("children", [])
        if children and isinstance(children, list):
            for child in children:
                if isinstance(child, dict) and child.get("label"):
                    result["children"].append({
                        "key": child.get("key", ""),
                        "label": child.get("label", ""),
                        "children": child.get("children", [])
                    })
        
        return result

    def _query_workitems_by_mql(self, project_key: str, workitem_ids: List[str], work_item_type: str = "story") -> List[Dict[str, Any]]:
        """通过 MQL 批量查询工作项信息
        
        Args:
            project_key: 项目 key
            workitem_ids: 工作项 ID 列表
            work_item_type: 工作项类型，默认为 story
            
        Returns:
            工作项信息列表
        """
        if not workitem_ids:
            return []
        
        results = []
        batch_size = 50  # 每批最多 50 个 ID
        
        # 分批处理
        for i in range(0, len(workitem_ids), batch_size):
            batch_ids = workitem_ids[i:i + batch_size]
            ids_str = ",".join(batch_ids)
            
            # 构建 MQL
            mql = f'SELECT work_item_id, name, business FROM `{project_key}`.`{work_item_type}` WHERE work_item_id IN ({ids_str}) LIMIT {batch_size}'
            
            logger.info(f"执行 MQL 查询: {mql}")
            
            try:
                # 调用 MCP 工具
                mcp_result = self._call_mcp_tool("search_by_mql", {
                    "project_key": project_key,
                    "mql": mql
                })
                
                # 解析结果
                content = self._extract_mcp_content(mcp_result, expect_json=True)
                logger.info(f"MQL 查询结果类型: {type(content)}")
                logger.info(f"MQL 查询结果内容: {str(content)[:500]}")
                
                # 处理返回的数据
                if isinstance(content, dict):
                    # MQL 返回的数据结构可能有多种形式:
                    # 形式1: {"data": {"1": [{moql_field_list: [...]}, ...]}}
                    # 形式2: {"list": [{...}], "data": {"1": [...]}}
                    # 形式3: {"fields": [...]} - 只有字段信息，没有数据
                    
                    # 优先尝试从 data 获取
                    data = content.get("data", {})
                    if isinstance(data, dict):
                        # 数据在 data["1"] 中（分组ID为"1"）
                        group_data = data.get("1", [])
                        if isinstance(group_data, list):
                            for item in group_data:
                                # 解析 moql_field_list
                                field_list = item.get("moql_field_list", [])
                                if isinstance(field_list, list):
                                    workitem_dict = {}
                                    for field in field_list:
                                        key = field.get("key", "")
                                        value_type = field.get("value_type", "")
                                        value_data = field.get("value", {})
                                        
                                        # 根据 value_type 提取值
                                        if key == "work_item_id" and value_type == "long_value":
                                            workitem_dict["work_item_id"] = str(value_data.get("long_value", ""))
                                        elif key == "name" and value_type == "string_value":
                                            workitem_dict["name"] = value_data.get("string_value", "")
                                        elif key == "business" and value_type == "cascade_key_label_value":
                                            workitem_dict["business"] = value_data
                                    
                                    if workitem_dict:
                                        results.append(workitem_dict)
                
            except Exception as e:
                logger.error(f"MQL 查询失败: {e}")
                continue
        
        # 如果批量查询没有返回数据，尝试单个查询
        if not results and len(workitem_ids) > 0:
            logger.warning("批量查询未返回数据，尝试单个查询")
            for workitem_id in workitem_ids[:10]:  # 最多尝试前10个
                try:
                    mql = f'SELECT work_item_id, name, business FROM `{project_key}`.`{work_item_type}` WHERE work_item_id = {workitem_id}'
                    logger.info(f"执行单条 MQL 查询: {mql}")
                    
                    mcp_result = self._call_mcp_tool("search_by_mql", {
                        "project_key": project_key,
                        "mql": mql
                    })
                    
                    content = self._extract_mcp_content(mcp_result, expect_json=True)
                    if isinstance(content, dict):
                        data = content.get("data", {})
                        if isinstance(data, dict):
                            group_data = data.get("1", [])
                            if isinstance(group_data, list) and len(group_data) > 0:
                                item = group_data[0]
                                field_list = item.get("moql_field_list", [])
                                if isinstance(field_list, list):
                                    workitem_dict = {}
                                    for field in field_list:
                                        key = field.get("key", "")
                                        value_type = field.get("value_type", "")
                                        value_data = field.get("value", {})
                                        
                                        if key == "work_item_id" and value_type == "long_value":
                                            workitem_dict["work_item_id"] = str(value_data.get("long_value", ""))
                                        elif key == "name" and value_type == "string_value":
                                            workitem_dict["name"] = value_data.get("string_value", "")
                                        elif key == "business" and value_type == "cascade_key_label_value":
                                            workitem_dict["business"] = value_data
                                    
                                    if workitem_dict:
                                        results.append(workitem_dict)
                except Exception as e:
                    logger.error(f"单条查询失败 {workitem_id}: {e}")
                    continue
        
        logger.info(f"MQL 查询完成，共获取 {len(results)} 条工作项数据")
        return results

    def get_business_lines_from_board(self, board_url: str, work_item_type: str = "story") -> Dict[str, Any]:
        """从 Meego 看板 URL 获取所有工作项的业务线信息
        
        Args:
            board_url: Meego 看板 URL
            work_item_type: 工作项类型，默认为 story
            
        Returns:
            包含工作项及其业务线信息的结果
        """
        logger.info(f"从看板获取业务线信息: {board_url}")
        
        try:
            # 1. 解析 URL
            url_info = self._parse_meego_url(board_url)
            simple_name = url_info["simple_name"]
            view_id = url_info["view_id"]
            node_id = url_info["node_id"]
            project_key = url_info["project_key"] or self.project_key
            
            if not simple_name or not view_id:
                return {
                    "success": False,
                    "error": "无法从 URL 中解析 simple_name 或 view_id",
                    "board_url": board_url
                }
            
            # 2. 测试 MCP 连接
            connection_test = self.test_mcp_connection()
            if not connection_test.get("success"):
                return {
                    "success": False,
                    "error": f"MCP 连接失败: {connection_test.get('error')}",
                    "board_url": board_url
                }
            
            # 3. 构建 get_view_detail 参数
            get_view_params = {
                "project_key": project_key,
                "view_id": view_id,
                "page_num": 1
            }
            if node_id:
                get_view_params["node_id"] = node_id
                logger.info(f"添加 node_id 参数: {node_id}")
            
            # 4. 获取视图详情（工作项列表）
            logger.info(f"获取视图详情，参数: {get_view_params}")
            view_result = self._call_mcp_tool("get_view_detail", get_view_params)
            
            # 调试：输出原始结果
            logger.debug(f"get_view_detail 原始结果: {view_result}")
            
            view_content = self._extract_mcp_content(view_result, expect_json=False)
            logger.debug(f"提取的视图内容: {view_content}")
            
            workitem_ids = self._extract_workitem_ids_from_view(view_content)
            
            if not workitem_ids:
                return {
                    "success": False,
                    "error": "未从视图中获取到工作项",
                    "board_url": board_url,
                    "view_content": str(view_content)[:1000]
                }
            
            logger.info(f"从视图获取到 {len(workitem_ids)} 个工作项")
            
            # 4. 通过 MQL 批量查询业务线信息
            workitems_data = self._query_workitems_by_mql(
                project_key=project_key,
                workitem_ids=workitem_ids,
                work_item_type=work_item_type
            )
            
            # 5. 解析业务线字段并构建结果
            workitems_with_business = []
            business_count = {}  # 统计每个业务线的工作项数量
            
            for item in workitems_data:
                if not isinstance(item, dict):
                    continue
                
                work_item_id = str(item.get("work_item_id", ""))
                name = item.get("name", "")
                
                # 解析 business 字段
                business_field = item.get("business", {})
                business_info = self._parse_business_field(business_field)
                
                workitem_result = {
                    "work_item_id": work_item_id,
                    "name": name,
                    "business": business_info
                }
                
                workitems_with_business.append(workitem_result)
                
                # 统计业务线
                if business_info:
                    business_label = business_info.get("label", "未设置")
                    # 如果有子业务线，使用完整路径
                    if business_info.get("children"):
                        child = business_info["children"][0] if business_info["children"] else None
                        if child:
                            business_label = f"{business_label}/{child.get('label', '')}"
                    
                    business_count[business_label] = business_count.get(business_label, 0) + 1
            
            return {
                "success": True,
                "board_url": board_url,
                "simple_name": simple_name,
                "view_id": view_id,
                "node_id": node_id,
                "project_key": project_key,
                "total_workitems": len(workitems_with_business),
                "workitems": workitems_with_business,
                "business_count": business_count,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            error_msg = f"获取业务线信息失败: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "board_url": board_url
            }

    def format_business_lines_result(self, result: Dict[str, Any], group_by_business: bool = True) -> str:
        """格式化业务线查询结果为可读文本
        
        Args:
            result: get_business_lines_from_board 的返回结果
            group_by_business: 是否按业务线分组显示（默认 True）
            
        Returns:
            格式化后的文本
        """
        if not result.get("success"):
            output = []
            output.append("=" * 80)
            output.append("Meego 看板业务线查询失败")
            output.append("=" * 80)
            output.append(f"错误信息: {result.get('error')}")
            output.append(f"看板 URL: {result.get('board_url')}")
            if "view_content" in result:
                output.append("")
                output.append("原始视图内容预览:")
                output.append("-" * 80)
                output.append(str(result.get("view_content")))
            output.append("=" * 80)
            return "\n".join(output)
        
        output = []
        output.append("=" * 80)
        output.append("Meego 看板业务线查询结果")
        output.append("=" * 80)
        output.append(f"看板 URL: {result.get('board_url')}")
        output.append(f"简单名称: {result.get('simple_name')}")
        output.append(f"视图 ID: {result.get('view_id')}")
        output.append(f"节点 ID: {result.get('node_id', 'N/A')}")
        output.append(f"总工作项数: {result.get('total_workitems')}")
        output.append("")
        
        # 业务线统计
        business_count = result.get("business_count", {})
        if business_count:
            output.append("业务线统计:")
            output.append("-" * 80)
            # 按数量降序排序
            sorted_business = sorted(business_count.items(), key=lambda x: x[1], reverse=True)
            for business, count in sorted_business:
                output.append(f"  {business}: {count} 个工作项")
            output.append("")
        
        # 工作项详情（按业务线分组）
        workitems = result.get("workitems", [])
        if workitems:
            if group_by_business:
                # 按业务线分组
                output.append("工作项按业务线分组:")
                output.append("-" * 80)
                
                # 构建分组字典
                business_groups = {}
                for item in workitems:
                    work_item_id = item.get("work_item_id", "")
                    name = item.get("name", "")
                    business = item.get("business")
                    
                    # 构建业务线文本
                    business_text = "未设置"
                    if business:
                        label = business.get("label", "")
                        children = business.get("children", [])
                        if children:
                            child_labels = [c.get("label", "") for c in children if c.get("label")]
                            business_text = f"{label}/{', '.join(child_labels)}" if label else "/".join(child_labels)
                        elif label:
                            business_text = label
                    
                    if business_text not in business_groups:
                        business_groups[business_text] = []
                    business_groups[business_text].append({
                        "work_item_id": work_item_id,
                        "name": name
                    })
                
                # 按业务线名称排序输出
                for business_name in sorted(business_groups.keys()):
                    items = business_groups[business_name]
                    output.append(f"【{business_name}】")
                    output.append(f"  共 {len(items)} 个需求")
                    output.append("")
                    for i, item in enumerate(items, 1):
                        output.append(f"  {i}. [{item['work_item_id']}] {item['name']}")
                    output.append("")
            else:
                # 不分组，按原有方式显示
                output.append("工作项详情:")
                output.append("-" * 80)
                for item in workitems:
                    work_item_id = item.get("work_item_id", "")
                    name = item.get("name", "")
                    business = item.get("business")
                    
                    # 构建业务线文本
                    business_text = "未设置"
                    if business:
                        label = business.get("label", "")
                        children = business.get("children", [])
                        if children:
                            child_labels = [c.get("label", "") for c in children if c.get("label")]
                            business_text = f"{label}/{', '.join(child_labels)}" if label else "/".join(child_labels)
                        elif label:
                            business_text = label
                    
                    output.append(f"  [{work_item_id}] {name}")
                    output.append(f"    业务线: {business_text}")
                    output.append("")
        
        output.append("=" * 80)
        return "\n".join(output)
