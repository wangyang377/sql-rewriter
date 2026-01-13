"""
ANTLR 生成的代码目录

此目录包含由 ANTLR4 自动生成的解析器代码。
这些文件不应手动编辑，它们会在构建分发包时自动生成。

如果从 Git 克隆项目，需要先运行生成脚本：
    ./scripts/generate_parser.sh
"""

# 导出主要的类，方便外部使用
# 如果文件不存在（从 Git 克隆但未生成），会抛出 ImportError
# 这是预期的行为，提示用户需要先运行生成脚本
try:
    from .HiveLexer import HiveLexer
    from .HiveParser import HiveParser
    from .HiveParserVisitor import HiveParserVisitor
    from .HiveParserListener import HiveParserListener
    
    __all__ = [
        "HiveLexer",
        "HiveParser",
        "HiveParserVisitor",
        "HiveParserListener",
    ]
except ImportError as e:
    raise ImportError(
        "ANTLR 生成的代码未找到。\n"
        "如果从 Git 克隆项目，请先运行：\n"
        "  ./scripts/generate_parser.sh\n"
        "或者安装 ANTLR4 工具后运行生成脚本。"
    ) from e
