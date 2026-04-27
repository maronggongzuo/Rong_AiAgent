"""问答机器人"""

import logging
from typing import List, Dict, Any, Optional
from config.settings import Settings

logger = logging.getLogger(__name__)


class QABot:
    """基于文档的问答机器人"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.documents = []
        self.vector_store = None
    
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """添加文档"""
        doc = {
            "content": content,
            "metadata": metadata or {}
        }
        self.documents.append(doc)
        logger.info(f"已添加文档，当前共 {len(self.documents)} 个文档")
    
    def query(self, question: str) -> Dict[str, Any]:
        """查询问题"""
        logger.info(f"收到问题: {question}")
        
        return {
            "question": question,
            "answer": "这是一个示例回答（实际需要集成 LLM）",
            "sources": [],
            "confidence": 0.8
        }
    
    def batch_add_documents(self, docs: List[Dict[str, str]]):
        """批量添加文档"""
        for doc in docs:
            self.add_document(doc.get("content", ""), doc.get("metadata"))
