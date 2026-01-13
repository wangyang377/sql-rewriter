"""
SQL Rewriter - 基于 ANTLR4 的通用 SQL 重写工具

主要功能：在 SQL 语句中添加 WHERE 条件，特别适用于 LLM 生成的 SQL 权限管理
"""

from .parser import add_where_condition

__version__ = "0.1.0"
__all__ = ["add_where_condition"]
