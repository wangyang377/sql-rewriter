# SQL Rewriter - 基于 ANTLR4 的 SQL 重写工具

基于g4词法分析和语法分析文件解析sql语法树进行sql改写。

目前提供了 `add_where_condition` 一个函数，主要针对大模型生成sql提供权限管理工具。用语法解析代替正则匹配，让用户在处理大模型生成的各种奇葩 SQL 时更方便的进行权限管理。

## 工作原理

使用 ANTLR4 把 SQL 语句解析成语法树，然后用 Visitor 模式遍历语法树，找到目标表的查询位置，智能地添加或合并 WHERE 条件。如果原 SQL 已经有 WHERE 子句，会先给原条件加个括号，然后再用 AND 连接新的权限条件（避免大模型sql注入）。

## 安装

```bash
pip install sql-rewriter
```

或者从源码安装（如果你要改代码的话）：

```bash
git clone https://github.com/wangyang377/sql-rewriter.git
cd sql-rewriter
./scripts/generate_parser.sh  # 需要先安装 ANTLR4，见下方开发部分
pip install -e .
```

## 使用方法

### 基本用法

```python
from sql_rewriter import add_where_condition

# 没有 WHERE 子句的情况，直接添加
sql = "SELECT * FROM users;"
new_sql = add_where_condition(sql, "age > 18", "users")
# 结果: SELECT * FROM users WHERE age > 18;

# 已有 WHERE 子句的情况，会加括号后追加
sql = "SELECT * FROM users WHERE age > 18;"
new_sql = add_where_condition(sql, "status = 'active'", "users")
# 结果: SELECT * FROM users WHERE (age > 18) AND status = 'active';

# JOIN 查询，只针对特定表添加条件
sql = "SELECT * FROM users JOIN orders ON users.id = orders.user_id;"
new_sql = add_where_condition(sql, "users.status = 'active'", "users")
# 结果: SELECT * FROM users JOIN orders ON users.id = orders.user_id WHERE users.status = 'active';

# 嵌套查询也没问题，会精准定位到目标表
sql = "SELECT * FROM orders WHERE status = 'pending' AND EXISTS (SELECT 1 FROM users WHERE users.id = orders.user_id);"
new_sql = add_where_condition(sql, "users.status = 'active'", "users")
# 结果: SELECT * FROM orders WHERE status = 'pending' AND EXISTS (SELECT 1 FROM users WHERE users.id = orders.user_id AND users.status = 'active');
```

### API 说明

```python
add_where_condition(sql_text, new_condition, table_name=None)
```

**参数：**
- `sql_text`: 原始 SQL 语句
- `new_condition`: 要添加的 WHERE 条件（不需要包含 WHERE 关键字）
- `table_name`: 目标表名，只有查询中包含这个表时才会添加条件。传 `None` 的话就不处理

**返回值：**
- 修改后的 SQL 语句（字符串）

**异常：**
- `ValueError`: SQL 解析失败时会抛出

## 开发指南

如果你从 Git 克隆了项目，需要先生成 ANTLR 解析器代码：

```bash
# 安装 ANTLR4（macOS）
brew install antlr

# Linux (Ubuntu/Debian)
sudo apt-get install antlr4

# 然后生成代码
./scripts/generate_parser.sh
```

运行测试：

```bash
cd tests
python test_parser.py
```
