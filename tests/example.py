#!/usr/bin/env python3
"""
Internal test: Test add_where_condition functionality

Usage:
    python3 tests/example.py
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sql_rewriter import add_where_condition

def main():
    print('=' * 60)
    print('sql-rewriter Usage Examples')
    print('=' * 60)
    print()
    
    # Example 1: Basic usage
    print('Example 1: Add condition to complex SQL with existing WHERE clause')
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
    print(f'Original SQL: {sql}')
    print(f'Modified SQL: {new_sql}')
    print()
    
    # Example 2: Append condition
    print('Example 2: Append condition to SQL with existing WHERE clause')
    sql = 'SELECT * FROM users WHERE age > 18;'
    new_sql = add_where_condition(sql, "status = 'active'", 'users')
    print(f'Original SQL: {sql}')
    print(f'Modified SQL: {new_sql}')
    print()
    
    # Example 3: JOIN query
    print('Example 3: JOIN query - add condition only for specific table')
    sql = 'SELECT * FROM users u JOIN orders o ON u.id = o.user_id;'
    new_sql = add_where_condition(sql, 'users.status = \'active\'', 'users')
    print(f'Original SQL: {sql}')
    print(f'Modified SQL: {new_sql}')
    print()

if __name__ == '__main__':
    main()
