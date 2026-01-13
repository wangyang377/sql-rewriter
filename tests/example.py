#!/usr/bin/env python3
"""
项目内部测试：测试 add_where_condition 功能

运行方法:
    python3 tests/example_usage.py
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sql_rewriter import add_where_condition

def main():
    print('=' * 60)
    print('sql-rewriter 使用示例')
    print('=' * 60)
    print()
    
    # 示例1：基础使用
    print('示例1: 为已有 WHERE 子句的复杂 SQL 添加条件')
    sql = '''SELECT 
    order_date, 
    ROUND(SUM(amount), 2) AS total_amount
FROM 
    sales.orders
WHERE 
    status = 'active' 
    AND order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY 
    order_date
ORDER BY 
    order_date DESC
LIMIT 100;'''
    new_sql = add_where_condition(sql, "(category in ('A','B','C')) or (priority = 'high' and category = 'D')", 'sales.orders')
    print(f'原始SQL: {sql}')
    print(f'修改后: {new_sql}')
    print()
    
    # 示例2：追加条件
    print('示例2: 为已有 WHERE 子句的 SQL 追加条件')
    sql = 'SELECT * FROM users WHERE age > 18;'
    new_sql = add_where_condition(sql, "status = 'active'", 'users')
    print(f'原始SQL: {sql}')
    print(f'修改后: {new_sql}')
    print()
    
    # 示例3：JOIN 查询
    print('示例3: JOIN 查询，只针对特定表添加条件')
    sql = 'SELECT * FROM users JOIN orders ON users.id = orders.user_id;'
    new_sql = add_where_condition(sql, 'users.status = \'active\'', 'users')
    print(f'原始SQL: {sql}')
    print(f'修改后: {new_sql}')
    print()

if __name__ == '__main__':
    main()
