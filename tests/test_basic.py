"""基础测试"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """测试模块导入"""
    from config.settings import Settings
    from src.skills.base_skill import BaseSkill
    from src.document.document_generator import DocumentGenerator
    
    assert Settings is not None
    assert BaseSkill is not None
    assert DocumentGenerator is not None
    print("✓ 所有模块导入成功")


def test_document_generator():
    """测试文档生成器"""
    from src.document.document_generator import DocumentGenerator
    
    generator = DocumentGenerator("templates")
    template = generator.load_template("project_report")
    
    assert template is not None
    assert len(template) > 0
    print("✓ 文档生成器测试通过")


if __name__ == "__main__":
    test_imports()
    test_document_generator()
    print("\n所有测试通过！")
