#!/usr/bin/env python3
"""
简单的测试脚本

运行方法:
    python3 tests/test_parser.py
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from antlr4 import *
from sql_rewriter._generated import HiveLexer, HiveParser


def test_parse(sql_text):
    """测试解析SQL语句"""
    try:
        input_stream = InputStream(sql_text)
        lexer = HiveLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = HiveParser(token_stream)
        tree = parser.statement()
        print(f"✓ 解析成功: {sql_text}")
        return True
    except Exception as e:
        print(f"✗ 解析失败: {sql_text}")
        print(f"  错误: {e}")
        return False


def main():
    """运行测试"""
    test_cases = [
        "SELECT * FROM users;",
        "SELECT id, name FROM users WHERE age > 18;",
        "CREATE TABLE test (id INT, name STRING);",
        "INSERT INTO TABLE test VALUES (1, 'hello');",
        "SELECT COUNT(*) FROM orders GROUP BY status;",
    ]
    
    print("运行测试用例...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for sql in test_cases:
        if test_parse(sql):
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")


if __name__ == "__main__":
    main()
