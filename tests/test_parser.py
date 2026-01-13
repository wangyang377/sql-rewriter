#!/usr/bin/env python3
"""
Simple test script

Usage:
    python3 tests/test_parser.py
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from antlr4 import *
from sql_rewriter._generated import HiveLexer, HiveParser


def test_parse(sql_text):
    """Test parsing SQL statement"""
    try:
        input_stream = InputStream(sql_text)
        lexer = HiveLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = HiveParser(token_stream)
        tree = parser.statement()
        print(f"✓ Parse successful: {sql_text}")
        return True
    except Exception as e:
        print(f"✗ Parse failed: {sql_text}")
        print(f"  Error: {e}")
        return False


def main():
    """Run tests"""
    test_cases = [
        "SELECT * FROM users;",
        "SELECT id, name FROM users WHERE age > 18;",
        "CREATE TABLE test (id INT, name STRING);",
        "INSERT INTO TABLE test VALUES (1, 'hello');",
        "SELECT COUNT(*) FROM orders GROUP BY status;",
    ]
    
    print("Running test cases...")
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
    print(f"Test results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    main()
