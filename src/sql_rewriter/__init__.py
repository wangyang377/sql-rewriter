"""
SQL Rewriter - ANTLR4-based SQL Rewriting Tool

Main functionality: Add WHERE conditions to SQL statements, especially suitable for 
permission management in LLM-generated SQL.
"""

from .parser import add_where_condition

__version__ = "0.1.2"
__all__ = ["add_where_condition"]
