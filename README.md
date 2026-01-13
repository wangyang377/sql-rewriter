# SQL Rewriter - 基于 ANTLR4 的通用 SQL 重写工具

这个项目使用 ANTLR4 来解析 SQL 语句（目前支持 Hive SQL），并提供了一个 Python 包来方便地进行 SQL 重写，特别适用于 LLM 生成的 SQL 权限管理。

## 安装包

### 从 PyPI 安装（推荐）

```bash
pip install sql-rewriter
```

或者使用 uv：

```bash
uv pip install sql-rewriter
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/sql-rewriter.git
cd sql-rewriter

# 重要：从 Git 克隆需要先生成 ANTLR 代码
./scripts/generate_parser.sh

# 安装（开发模式）
pip install -e .

# 或直接安装
pip install .
```

**注意**：从 Git 克隆的项目不包含生成的代码（保持仓库干净），需要先运行生成脚本。从 PyPI 安装的包已包含生成的代码，可直接使用。

### 构建分发包

```bash
# 安装构建工具
pip install build twine

# 构建分发包（源码包和 wheel 包）
python -m build

# 检查分发包
twine check dist/*
```

## 使用包

安装后，可以在其他Python项目中使用：

```python
from sql_rewriter import add_where_condition

# 示例1：为没有 WHERE 子句的 SQL 添加条件
sql = "SELECT * FROM users;"
new_sql = add_where_condition(sql, "age > 18", "users")
print(new_sql)
# 输出: SELECT * FROM users WHERE age > 18;

# 示例2：为已有 WHERE 子句的 SQL 追加条件
sql = "SELECT * FROM users WHERE age > 18;"
new_sql = add_where_condition(sql, "status = 'active'", "users")
print(new_sql)
# 输出: SELECT * FROM users WHERE age > 18 AND status = 'active';

# 示例3：JOIN 查询，只针对特定表添加条件
sql = "SELECT * FROM users JOIN orders ON users.id = orders.user_id;"
new_sql = add_where_condition(sql, "users.status = 'active'", "users")
print(new_sql)
# 输出: SELECT * FROM users JOIN orders ON users.id = orders.user_id WHERE users.status = 'active';

# 示例4：嵌套查询，只针对最内层的指定表添加条件
sql = "SELECT * FROM orders WHERE status = 'pending' AND EXISTS (SELECT 1 FROM users WHERE users.id = orders.user_id);"
new_sql = add_where_condition(sql, "users.status = 'active'", "users")
print(new_sql)
# 输出: SELECT * FROM orders WHERE status = 'pending' AND EXISTS (SELECT 1 FROM users WHERE users.id = orders.user_id AND users.status = 'active');
```

### API 说明

```python
add_where_condition(sql_text, new_condition, table_name=None)
```

**参数：**
- `sql_text`: 原始SQL语句
- `new_condition`: 要添加的WHERE条件（不包含WHERE关键字）
- `table_name`: 目标表名，只有FROM子句包含此表名时才添加WHERE条件。如果为None，则不处理

**返回值：**
- 修改后的SQL语句

**异常：**
- `ValueError`: 如果SQL解析失败

## 开发指南

### 快速开始

### 1. 环境要求

**安装ANTLR4工具** (用于生成解析器代码)
```bash
# macOS
brew install antlr

# Linux (Ubuntu/Debian)
sudo apt-get install antlr4

# 或者下载jar文件
wget https://www.antlr.org/download/antlr-4.13.1-complete.jar
```

**安装Python依赖**
```bash
# macOS/Linux 通常使用 pip3
pip3 install -r requirements.txt

# 或者使用 python3 -m pip
python3 -m pip install -r requirements.txt

# 如果遇到权限问题，可以使用用户安装
pip3 install --user -r requirements.txt

# 或者使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. 生成解析器代码

**重要说明**：
- **从 PyPI 安装**：生成的代码已包含在分发包中，无需生成
- **从 Git 克隆**：需要先运行生成脚本（见下方）

**方法一：使用脚本（推荐）**
```bash
./scripts/generate_parser.sh
```

**方法二：手动生成**
```bash
# 如果使用brew安装的antlr
cd grammar
antlr -Dlanguage=Python3 -visitor -o ../src/sql_rewriter/_generated HiveLexer.g4 HiveParser.g4

# 或者如果使用jar文件
cd grammar
java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor -o ../src/sql_rewriter/_generated HiveLexer.g4 HiveParser.g4
```

这将生成以下Python文件到 `src/sql_rewriter/_generated/` 目录：
- `HiveLexer.py` - 词法分析器
- `HiveParser.py` - 语法分析器
- `HiveLexer.tokens` - 词法分析器token定义（可忽略）
- `HiveParser.tokens` - 语法分析器token定义（可忽略）
- `HiveParserListener.py` - Listener接口
- `HiveParserVisitor.py` - Visitor接口

**关于生成的代码**：
- 生成的代码位于 `_generated/` 子目录中
- **Git 仓库中不包含生成的代码**（在 `.gitignore` 中忽略）
- **构建分发包时会自动生成**并包含在分发包中
- 从 PyPI 安装的用户：开箱即用（分发包已包含生成的代码）
- 从 Git 克隆的用户：需要先运行生成脚本（开发场景）

### 3. 运行测试

**运行WHERE条件添加测试**
```bash
cd tests
python testwhereparser.py
```

**其他示例**
```bash
cd tests
python test_parser.py
python example.py
python visitor_example.py
```

## 使用说明

### 基本用法

```python
from antlr4 import *
from sql_rewriter._generated import HiveLexer, HiveParser

# 创建输入流
sql = "SELECT * FROM users;"
input_stream = InputStream(sql)

# 创建词法分析器
lexer = HiveLexer(input_stream)

# 创建token流
token_stream = CommonTokenStream(lexer)

# 创建解析器
parser = HiveParser(token_stream)

# 解析SQL语句（从statement规则开始）
tree = parser.statement()

# 打印解析树
print(tree.toStringTree(recog=parser))
```

### 使用Visitor模式

Visitor模式允许你遍历解析树并提取信息：

```python
from sql_rewriter._generated import HiveParserVisitor

class MyVisitor(HiveParserVisitor):
    def visitSelectStatement(self, ctx):
        print("发现SELECT语句")
        return self.visitChildren(ctx)

visitor = MyVisitor()
visitor.visit(tree)
```

## 项目结构

```
.
├── src/                      # 源代码目录
│   └── sql_rewriter/         # Python包目录
│       ├── __init__.py       # 包初始化文件，导出 add_where_condition
│       ├── parser.py         # 核心业务代码：WhereClauseVisitor 和 add_where_condition
│       └── _generated/       # ANTLR 生成的代码目录（保持主代码目录干净）
│           ├── __init__.py   # 导出生成的类
│           ├── HiveLexer.py      # ANTLR4 生成的词法分析器
│           ├── HiveParser.py     # ANTLR4 生成的语法分析器
│           ├── HiveParserVisitor.py  # ANTLR4 生成的访问器基类
│           └── HiveParserListener.py # ANTLR4 生成的监听器基类
├── tests/                    # 测试和示例文件
│   ├── testwhereparser.py    # WHERE条件添加测试
│   ├── test_parser.py        # 基础解析测试
│   ├── example.py            # 基础使用示例
│   └── visitor_example.py    # Visitor模式示例
├── grammar/                  # ANTLR 语法文件目录
│   ├── HiveLexer.g4          # 词法规则文件（源文件）
│   └── HiveParser.g4         # 语法规则文件（源文件）
├── scripts/                  # 构建脚本
│   └── generate_parser.sh    # 生成解析器脚本（输出到 _generated/）
├── pyproject.toml            # 项目配置文件（现代 Python 标准）
├── requirements.txt          # Python依赖（可选，也可在 pyproject.toml 中）
├── LICENSE                   # 许可证文件
├── .gitignore                # Git忽略文件
└── README.md                 # 本文件
```

## 常见问题

**Q: 如何解析不同的SQL语句？**

A: 根据你的需求，可以从不同的规则开始解析：
- `parser.statement()` - 解析完整语句（推荐）
- `parser.selectStatement()` - 只解析SELECT语句
- `parser.createTableStatement()` - 只解析CREATE TABLE语句

**Q: 如何获取解析错误信息？**

A: 可以添加错误监听器：
```python
from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"语法错误: 行{line}, 列{column}: {msg}")

parser.removeErrorListeners()
parser.addErrorListener(MyErrorListener())
```

## 参考资源

- [ANTLR4官方文档](https://github.com/antlr/antlr4/blob/master/doc/index.md)
- [ANTLR4 Python运行时](https://github.com/antlr/antlr4/blob/master/doc/python-target.md)
