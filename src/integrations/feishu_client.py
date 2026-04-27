"""飞书 API 客户端"""

import logging
import json
from typing import Dict, Any, Optional, List
from config.settings import Settings

logger = logging.getLogger(__name__)


class FeishuClient:
    """飞书 API 客户端"""
    
    BASE_URL = "https://open.feishu.cn/open-apis"
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.app_id = settings.FEISHU_APP_ID
        self.app_secret = settings.FEISHU_APP_SECRET
        self.tenant_access_token = None
        self.token_expire_time = 0
        
        # 检查是否配置了凭证
        self.use_mock = not (self.app_id and self.app_secret)
        if self.use_mock:
            logger.info("未配置飞书凭证，使用模拟模式")
        else:
            logger.info("飞书凭证已配置，使用真实 API")
    
    def _get_tenant_access_token(self) -> Optional[str]:
        """获取 tenant_access_token"""
        if self.use_mock:
            return "mock_token_123"
            
        if self.tenant_access_token and self.token_expire_time > self._get_current_timestamp():
            return self.tenant_access_token
        
        try:
            import requests
            url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
            payload = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            response = requests.post(url, json=payload)
            data = response.json()
            
            if data.get("code") == 0:
                self.tenant_access_token = data["tenant_access_token"]
                self.token_expire_time = self._get_current_timestamp() + data["expire"] - 60
                return self.tenant_access_token
            else:
                logger.error(f"获取飞书 token 失败: {data}")
                return None
        except ImportError:
            logger.warning("requests 库未安装，使用模拟模式")
            self.use_mock = True
            return "mock_token_123"
        except Exception as e:
            logger.error(f"请求飞书 API 失败: {e}")
            return None
    
    def _get_current_timestamp(self) -> int:
        """获取当前时间戳"""
        import time
        return int(time.time())
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        token = self._get_tenant_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def send_message(self, receive_id: str, msg_type: str, content: Dict[str, Any], receive_id_type: str = "open_id") -> Dict[str, Any]:
        """发送消息 - 支持多种 ID 类型"""
        if self.use_mock:
            logger.info(f"[模拟] 发送消息给 {receive_id}: {content}")
            return {
                "code": 0,
                "msg": "success",
                "data": {
                    "message_id": "mock_msg_123",
                    "mock": True
                }
            }
        
        try:
            import requests
            url = f"{self.BASE_URL}/im/v1/messages"
            params = {"receive_id_type": receive_id_type}
            
            payload = {
                "receive_id": receive_id,
                "msg_type": msg_type,
                "content": json.dumps(content, ensure_ascii=False)
            }
            
            response = requests.post(url, params=params, headers=self._get_headers(), json=payload)
            return response.json()
        except ImportError:
            logger.warning("requests 库未安装")
            return {"code": -1, "msg": "requests library not installed"}
        except Exception as e:
            logger.error(f"发送飞书消息失败: {e}")
            return {"code": -1, "msg": str(e)}
    
    def send_text_message(self, user_id: str, text: str, receive_id_type: str = "open_id") -> Dict[str, Any]:
        """发送文本消息 - 支持多种 ID 类型"""
        return self.send_message(user_id, "text", {"text": text}, receive_id_type)
    
    def send_text_with_mention(
        self,
        user_id: str,
        text: str,
        mention_user_id: str,
        mention_name: str = "用户",
        receive_id_type: str = "open_id"
    ) -> Dict[str, Any]:
        """发送带艾特的文本消息
        
        Args:
            user_id: 接收用户 ID
            text: 消息文本
            mention_user_id: 要艾特的用户 ID
            mention_name: 艾特显示的名称
            receive_id_type: ID 类型
            
        Returns:
            API 响应
        """
        content = {
            "text": f"{text} <at user_id=\"{mention_user_id}\">{mention_name}</at>"
        }
        return self.send_message(user_id, "text", content, receive_id_type)
    
    def send_rich_text(self, user_id: str, title: str, elements: list, receive_id_type: str = "open_id") -> Dict[str, Any]:
        """发送富文本消息 - 支持多种 ID 类型"""
        content = {
            "title": title,
            "content": elements
        }
        return self.send_message(user_id, "post", content, receive_id_type)
    
    def send_card_message(self, user_id: str, card: Dict[str, Any]) -> Dict[str, Any]:
        """发送卡片消息"""
        return self.send_message(user_id, "interactive", card)
    
    def create_document(self, title: str, content: str, folder_token: Optional[str] = None, notify_admin: bool = True, grant_admin_permission: bool = True, transfer_owner: bool = True) -> Dict[str, Any]:
        """创建飞书文档（Docx 格式）
        
        需要权限:
        - docx:document:create
        
        参数:
        - notify_admin: 是否自动发送文档链接给管理员（默认 True）
        - grant_admin_permission: 是否自动授予管理员文档权限（默认 True）
        - transfer_owner: 是否自动将文档所有者转移给管理员（默认 True）
        """
        if self.use_mock:
            logger.info(f"[模拟] 创建飞书文档: {title}")
            return {
                "success": True,
                "document_url": "https://feishu.cn/docx/mock_doc_123",
                "title": title,
                "mock": True
            }
        
        try:
            import requests
            url = f"{self.BASE_URL}/docx/v1/documents"
            
            payload = {
                "title": title,
                "content": content
            }
            
            if folder_token:
                payload["folder_token"] = folder_token
            
            logger.info(f"创建飞书文档: {title}")
            response = requests.post(url, headers=self._get_headers(), json=payload)
            result = response.json()
            
            if result.get("code") == 0:
                data = result.get("data", {})
                document = data.get("document", {})
                doc_id = document.get("document_id", "")
                doc_url = f"https://feishu.cn/docx/{doc_id}"
                
                # 自动授予管理员权限
                if grant_admin_permission and self.settings.FEISHU_ADMIN_USER_ID:
                    try:
                        self._grant_admin_permission_to_doc(doc_id, title)
                    except Exception as e:
                        logger.warning(f"设置文档权限失败: {e}")
                
                # 自动转移文档所有者
                if transfer_owner and self.settings.FEISHU_ADMIN_USER_ID:
                    try:
                        transfer_result = self.transfer_document_owner(doc_id, self.settings.FEISHU_ADMIN_USER_ID)
                        if not transfer_result.get("success"):
                            logger.warning(f"转移文档所有者失败: {transfer_result.get('msg')}")
                    except Exception as e:
                        logger.warning(f"转移文档所有者异常: {e}")
                
                # 自动发送链接给管理员
                if notify_admin and self.settings.FEISHU_ADMIN_USER_ID:
                    try:
                        self._send_doc_link_to_admin(title, doc_url)
                    except Exception as e:
                        logger.warning(f"发送文档链接失败: {e}")
                
                return {
                    "success": True,
                    "document_url": doc_url,
                    "document_id": doc_id,
                    "revision_id": document.get("revision_id"),
                    "title": title
                }
            else:
                logger.error(f"创建文档失败: {result}")
                return {
                    "success": False,
                    "code": result.get("code"),
                    "msg": result.get("msg")
                }
                
        except ImportError:
            logger.warning("requests 库未安装")
            return {"success": False, "msg": "requests library not installed"}
        except Exception as e:
            logger.error(f"创建文档异常: {e}")
            return {"success": False, "msg": str(e)}
    
    def _grant_admin_permission_to_doc(self, doc_id: str, title: str):
        """为管理员设置文档权限（使用docx专门的API）"""
        import requests
        
        admin_user_id = self.settings.FEISHU_ADMIN_USER_ID
        if not admin_user_id:
            return
        
        # 使用docx专门的API来添加协作者
        url = f"{self.BASE_URL}/docx/v1/documents/{doc_id}/members"
        
        payload = {
            "member_id": admin_user_id,
            "member_type": "user",
            "member_id_type": "open_id",
            "role": "edit"
        }
        
        logger.info(f"为管理员设置文档权限: {title}")
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    if result.get("code") == 0:
                        logger.info(f"文档权限设置成功: {admin_user_id} (edit)")
                    else:
                        logger.warning(f"文档权限设置失败: {result}")
                        # 如果这个也失败了，试试drive API
                        logger.info("尝试使用通用drive API...")
                        self._try_drive_permission_api(doc_id, title, admin_user_id)
                except Exception as json_err:
                    logger.warning(f"JSON解析失败: {json_err}，尝试使用通用drive API...")
                    self._try_drive_permission_api(doc_id, title, admin_user_id)
            else:
                logger.warning(f"请求失败，状态码: {response.status_code}，尝试使用通用drive API...")
                self._try_drive_permission_api(doc_id, title, admin_user_id)
        
        except Exception as e:
            logger.error(f"设置文档权限异常: {e}")
            logger.info("尝试使用通用drive API...")
            self._try_drive_permission_api(doc_id, title, admin_user_id)
    
    def _try_drive_permission_api(self, doc_id: str, title: str, admin_user_id: str):
        """尝试使用通用的drive权限API（备选方案）"""
        import requests
        
        url = f"{self.BASE_URL}/drive/v1/permissions/{doc_id}/members"
        
        payload = {
            "member_type": "openid",
            "member_id": admin_user_id,
            "perm": "full_access"
        }
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                params={"type": "docx"}
            )
            
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"文档权限设置成功 (drive API): {admin_user_id}")
            else:
                logger.warning(f"drive API也失败: {result}")
                logger.info("💡 提示: 如果需要自动设置权限，请在飞书开放平台申请以下权限之一:")
                logger.info("   - docs:permission.member:create")
                logger.info("   - docs:doc")
                logger.info("   或者在飞书中手动设置文档权限")
        
        except Exception as e:
            logger.error(f"drive API异常: {e}")
    
    def transfer_document_owner(self, document_id: str, new_owner_id: str, new_owner_type: str = "openid") -> Dict[str, Any]:
        """转移文档所有者
        
        需要权限:
        - 文档的所有者权限
        
        Args:
            document_id: 文档ID
            new_owner_id: 新所有者的ID
            new_owner_type: 新所有者ID类型，默认为"openid"
        """
        if self.use_mock:
            logger.info(f"[模拟] 转移文档所有者: {document_id} → {new_owner_id}")
            return {
                "success": True,
                "mock": True
            }
        
        try:
            import requests
            
            url = f"{self.BASE_URL}/drive/v1/permissions/{document_id}/members/transfer_owner"
            
            payload = {
                "member_type": new_owner_type,
                "member_id": new_owner_id
            }
            
            logger.info(f"转移文档所有者: {document_id} → {new_owner_id}")
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                params={"type": "docx"}
            )
            
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"文档所有者转移成功: {new_owner_id}")
                return {
                    "success": True,
                    "message": f"文档所有者已转移给 {new_owner_id}"
                }
            else:
                logger.error(f"转移所有者失败: {result}")
                return {
                    "success": False,
                    "code": result.get("code"),
                    "msg": result.get("msg")
                }
                
        except ImportError:
            logger.warning("requests 库未安装")
            return {"success": False, "msg": "requests library not installed"}
        except Exception as e:
            logger.error(f"转移所有者异常: {e}")
            return {"success": False, "msg": str(e)}
    
    def _send_doc_link_to_admin(self, title: str, doc_url: str):
        """发送文档链接给管理员"""
        admin_user_id = self.settings.FEISHU_ADMIN_USER_ID
        if not admin_user_id:
            return
        
        message = f"""
📄 新文档已创建！

**标题**: {title}
**链接**: {doc_url}

✅ 你已拥有文档编辑权限！
现在可以直接点击链接编辑文档了！
        """.strip()
        
        self.send_text_message(admin_user_id, message)
        logger.info(f"文档链接已发送给管理员: {admin_user_id}")
    
    def create_docx_content(self, text_blocks: list) -> str:
        """创建飞书文档内容（简单格式）"""
        content = []
        
        for block in text_blocks:
            content.append({
                "type": "text",
                "text": {
                    "content": block
                }
            })
        
        return json.dumps(content)
    
    def add_document_collaborator(self, document_id: str, user_id: str, role: str = "edit", user_id_type: str = "open_id") -> Dict[str, Any]:
        """给文档添加协作者
        
        需要权限:
        - docx:document:edit
        
        role 参数:
        - "edit": 可编辑
        - "view": 只读
        - "comment": 可评论
        """
        if self.use_mock:
            logger.info(f"[模拟] 给文档 {document_id} 添加协作者 {user_id}")
            return {
                "success": True,
                "mock": True
            }
        
        try:
            import requests
            url = f"{self.BASE_URL}/docx/v1/documents/{document_id}/members"
            
            payload = {
                "member_id": user_id,
                "member_type": "user",
                "member_id_type": user_id_type,
                "role": role
            }
            
            logger.info(f"添加文档协作者: {user_id} ({role})")
            response = requests.post(url, headers=self._get_headers(), json=payload)
            result = response.json()
            
            if result.get("code") == 0:
                return {
                    "success": True,
                    "message": f"已给用户 {user_id} 添加为协作者"
                }
            else:
                logger.error(f"添加协作者失败: {result}")
                return {
                    "success": False,
                    "code": result.get("code"),
                    "msg": result.get("msg")
                }
                
        except ImportError:
            logger.warning("requests 库未安装")
            return {"success": False, "msg": "requests library not installed"}
        except Exception as e:
            logger.error(f"添加协作者异常: {e}")
            return {"success": False, "msg": str(e)}
    
    def find_user_by_email(self, email: str) -> Optional[str]:
        """通过邮箱查找用户 open_id
        
        Args:
            email: 用户邮箱
            
        Returns:
            用户 open_id，未找到返回 None
        """
        if self.use_mock:
            logger.info(f"[模拟] 通过邮箱查找用户: {email}")
            return f"mock_user_{email.replace('@', '_').replace('.', '_')}"
        
        token = self._get_tenant_access_token()
        if not token:
            logger.error("无法获取 token")
            return None
        
        url = f"{self.BASE_URL}/contact/v3/users/batch_get_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        data = {
            "emails": [email]
        }
        
        try:
            import requests
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if result.get("code") == 0:
                users = result.get("data", {}).get("user_list", [])
                if users:
                    user = users[0]
                    user_id = user.get('user_id')
                    logger.info(f"找到用户: {email} -> {user_id}")
                    return user_id
                else:
                    logger.warning(f"未找到邮箱为 {email} 的用户")
                    return None
            else:
                logger.error(f"查找用户失败: {result.get('code')} - {result.get('msg')}")
                return None
                
        except Exception as e:
            logger.error(f"查找用户异常: {e}")
            return None
    
    def find_users_by_emails(self, emails: List[str]) -> Dict[str, Optional[str]]:
        """批量通过邮箱查找用户 open_id
        
        Args:
            emails: 邮箱列表
            
        Returns:
            {email: user_id} 字典
        """
        result = {}
        
        if self.use_mock:
            for email in emails:
                result[email] = f"mock_user_{email.replace('@', '_').replace('.', '_')}"
            return result
        
        token = self._get_tenant_access_token()
        if not token:
            logger.error("无法获取 token")
            return result
        
        url = f"{self.BASE_URL}/contact/v3/users/batch_get_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        data = {
            "emails": emails
        }
        
        try:
            import requests
            response = requests.post(url, headers=headers, json=data)
            result_data = response.json()
            
            if result_data.get("code") == 0:
                users = result_data.get("data", {}).get("user_list", [])
                for user in users:
                    email = user.get('email')
                    user_id = user.get('user_id')
                    if email and user_id:
                        result[email] = user_id
                        logger.info(f"找到用户: {email} -> {user_id}")
                
                # 标记未找到的用户
                for email in emails:
                    if email not in result:
                        result[email] = None
                        logger.warning(f"未找到邮箱为 {email} 的用户")
            else:
                logger.error(f"批量查找用户失败: {result_data.get('code')} - {result_data.get('msg')}")
                
        except Exception as e:
            logger.error(f"批量查找用户异常: {e}")
        
        return result

