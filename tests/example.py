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
    print('示例1: 为没有 WHERE 子句的 SQL 添加条件')
    sql = '''SELECT 
    date_time, 
    ROUND(SUM(gmv_sum), 2) AS total_gmv
FROM 
    jdi_ge.jdi_ge_income_gmv_new_shard
WHERE 
    is_reject = '0' 
    AND date_time >= formatDateTime(now() - INTERVAL 7 DAY, '%Y-%m-%d')
GROUP BY 
    date_time
ORDER BY 
    date_time DESC
LIMIT 100;'''
    new_sql = add_where_condition(sql, "(trade_type in ('SMB','纯C','C中B')) or (dual_calculate in ('1_1') and trade_type = 'KA')", 'jdi_ge.jdi_ge_income_gmv_new_shard')
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
