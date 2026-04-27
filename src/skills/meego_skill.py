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
        if "content" in result and len(result["content"]) > 0:
            # 合并所有 content 项的文本，但过滤掉 log_id
            content_texts = []
            for content_item in result["content"]:
                text = content_item.get("text", "")
                if text and not text.startswith("log_id:"):
                    content_texts.append(text)
            
            content_text = "\n".join(content_texts)
            
            if expect_json:
                # 尝试解析为 JSON
                try:
                    return json.loads(content_text)
                except Exception as e:
                    logger.error(f"解析 JSON 失败: {e}")
                    logger.error(f"内容: {content_text}")
                    return content_text
            else:
                # 直接返回文本
                return content_text
        return result
    
    def _extract_workitem_ids_from_view(self, view_content: str) -> List[str]:
        """从视图内容中提取工作项 ID"""
        workitem_ids = []
        
        # 视图内容格式是 Markdown 表格，我们需要解析它
        # 格式可能是：
        # | 需求标题 | 工作项 ID |
        # | --- | --- |
        # | xxx | 123456 |
        # 或者：
        # | 工作项 ID | 需求标题 |
        # | --- | --- |
        # | 123456 | xxx |
        if isinstance(view_content, str):
            lines = view_content.split("\n")
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
    
    def _parse_to_rich_text(self, lines: List[str], owners_text: str) -> List[List[Dict[str, Any]]]:
        """解析模板为飞书富文本格式"""
        result = []
        for line in lines:
            if not line.strip():
                continue
                
            # 替换占位符
            line = line.replace("{owners_text}", owners_text)
            
            # 解析链接格式：[链接文字](链接地址)
            line_elements = []
            
            # 简单解析链接
            import re
            # 查找所有 [text](url) 格式的链接
            link_pattern = r'\[(.*?)\]\((https?://[^\)]+)\)'
            
            # 逐个匹配
            last_pos = 0
            for match in re.finditer(link_pattern, line):
                # 添加链接前的文字
                if match.start() > last_pos:
                    text_before = line[last_pos:match.start()]
                    if text_before.strip():
                        line_elements.append({"tag": "text", "text": text_before})
                
                # 添加链接
                link_text = match.group(1)
                link_url = match.group(2)
                line_elements.append({"tag": "a", "text": link_text, "href": link_url})
                
                last_pos = match.end()
            
            # 添加剩余的文字
            if last_pos < len(line):
                text_after = line[last_pos:]
                if text_after.strip():
                    line_elements.append({"tag": "text", "text": text_after})
            
            # 如果没有找到链接，直接添加整行
            if not line_elements:
                line_elements.append({"tag": "text", "text": line})
            
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
    
    def build_owners_text(self, owners_result: Dict[str, Any], owner_count: Optional[Dict[str, int]] = None) -> str:
        """构建 Tech Owner 文本（支持艾特，显示出现次数）
        
        Args:
            owners_result: Tech Owner 查询结果
            owner_count: 可选，每个 owner 出现的次数字典 {email: count}
        """
        if owners_result.get("success"):
            tech_owners = owners_result.get("tech_owners", [])
            if not tech_owners:
                return "相关同学"
            
            # 收集所有邮箱
            emails = [owner.get("email") for owner in tech_owners if owner.get("email")]
            
            # 批量查找用户 ID
            email_to_user_id = {}
            if emails:
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
                
                if email and email in email_to_user_id and email_to_user_id[email]:
                    # 有用户 ID，艾特
                    user_id = email_to_user_id[email]
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
        mention_name: str = "管理员"
    ) -> Dict[str, Any]:
        """发送双看板通知
        
        Args:
            recipient_user_id: 接收通知的用户 open_id（优先级高于 chat_id）
            recipient_chat_id: 接收通知的群聊 chat_id
            template_path: 自定义模板路径
            project_key: 自定义 project_key
            mention_admin: 是否艾特管理员（默认 True）
            mention_name: 艾特显示的名称（默认 "管理员"）
            
        Returns:
            通知发送结果
        """
        logger.info("开始发送双看板通知")
        
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
            
            owners_result = self.get_board_tech_owners(
                board_url=link,
                view_id=view_id,
                project_key=project_key
            )
            link_owners[link] = {
                "view_id": view_id,
                "owners_result": owners_result
            }
        
        # 3. 构建通知内容
        message_content = template_content
        
        # 按顺序替换占位符
        for i, link in enumerate(links):
            # 替换需求数量占位符
            count_placeholder = f"{{workitems_count_{i+1}}}"
            if count_placeholder in message_content:
                owners_result = link_owners[link]["owners_result"]
                workitems_count = owners_result.get("workitem_count", 0) if owners_result.get("success") else 0
                message_content = message_content.replace(count_placeholder, str(workitems_count))
                logger.info(f"替换占位符 {count_placeholder} 为: {workitems_count}")
            
            # 替换 Tech Owner 占位符
            owners_placeholder = f"{{owners_text_{i+1}}}"
            if owners_placeholder in message_content:
                owners_result = link_owners[link]["owners_result"]
                # 直接使用 get_board_tech_owners 返回的 owner_count
                owner_count = owners_result.get("owner_count", {}) if owners_result.get("success") else {}
                owners_text = self.build_owners_text(owners_result, owner_count)
                message_content = message_content.replace(owners_placeholder, owners_text)
                logger.info(f"替换占位符 {owners_placeholder} 为: {owners_text}")
        
        # 替换管理员艾特占位符
        if "{admin_mention}" in message_content:
            if mention_admin and self.settings.FEISHU_ADMIN_USER_ID:
                admin_text = f"<at user_id=\"{self.settings.FEISHU_ADMIN_USER_ID}\">{mention_name}</at>"
                message_content = message_content.replace("{admin_mention}", admin_text)
                logger.info(f"替换占位符 {{admin_mention}} 为: {admin_text}")
            else:
                message_content = message_content.replace("{admin_mention}", mention_name)
                logger.info(f"替换占位符 {{admin_mention}} 为: {mention_name}")
        
        # 移除 Markdown 标题
        if message_content.startswith("# "):
            lines = message_content.split("\n")
            message_content = "\n".join(lines[1:])
        
        message_content = message_content.strip()
        
        # 4. 发送通知
        # 注意：因为消息内容里已经包含了艾特标签，所以直接发送文本消息即可
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
