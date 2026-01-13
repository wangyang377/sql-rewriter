"""
SQL WHERE 条件添加器 - 基于解析树的 SQL 修改工具

主要功能：在 SQL 语句中添加或追加 WHERE 条件
"""

from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from ._generated import HiveLexer, HiveParser, HiveParserVisitor


class WhereClauseVisitor(HiveParserVisitor):
    """Visitor：在fromClause中定位targettable，从父节点访问WhereClause，然后rewriter SQL"""
    
    def __init__(self, rewriter, new_condition, target_table_name):
        self.rewriter = rewriter
        self.new_condition = new_condition
        self.target_table_name = target_table_name.lower() if target_table_name else None
        self.current_table_name = None  # 当前FROM子句中的表名
        
    def visitFromClause(self, ctx):
        """在FROM子句中定位targettable，从父节点访问WhereClause，然后rewriter SQL"""
        # 如果没有指定表名，不处理
        if not self.target_table_name:
            return self.visitChildren(ctx)
        
        # 收集当前FROM子句中的表名
        # 路径：fromClause -> fromSource -> joinSource -> atomjoinSource -> tableSource -> tableName
        self.current_table_name = None
        from_source = ctx.fromSource()
        if from_source:
            join_source = from_source.joinSource()
            if join_source:
                atom_join_source = join_source.atomjoinSource()
                if atom_join_source:
                    table_source = atom_join_source.tableSource()
                    self.current_table_name = table_source.getText().lower()
        
        # 检查是否匹配目标表名
        should_process = self.current_table_name == self.target_table_name
        
        if should_process:
            # fromClause的直接父节点就是atomSelectStatement（根据语法规则）
            atom_select_ctx = ctx.parentCtx
            if atom_select_ctx:
                # 从父节点访问WhereClause（根据语法规则，atomSelectStatement: ... w=whereClause? ...）
                # w是属性，可能是None（如果没有WHERE子句）或WhereClauseContext对象
                where_clause = atom_select_ctx.w
                if where_clause:
                    # whereClause的结构是: KW_WHERE searchCondition
                    # where_clause.start 是 KW_WHERE 的位置
                    # 在 WHERE 关键字之后插入 '('，在searchCondition之后插入 ')' AND 新条件
                    where_keyword_token = where_clause.start
                    stop_token = where_clause.searchCondition().stop
                    self.rewriter.insertAfter(where_keyword_token.tokenIndex, ' (')
                    self.rewriter.insertAfter(stop_token.tokenIndex, ') AND ' + self.new_condition)
                else:
                    # 没有WHERE子句，在FROM子句后插入WHERE条件
                    self.rewriter.insertAfter(ctx.stop.tokenIndex, ' WHERE ' + self.new_condition)
        
        return None


def add_where_condition(sql_text, new_condition, table_name=None):
    """
    在SQL语句中添加或追加WHERE条件（基于解析树）
    
    Args:
        sql_text: 原始SQL语句
        new_condition: 要添加的WHERE条件（不包含WHERE关键字）
        table_name: 目标表名，只有FROM子句包含此表名时才添加WHERE条件。如果为None，则不处理
    
    Returns:
        修改后的SQL语句
    
    Raises:
        ValueError: 如果SQL解析失败
    
    Example:
        >>> sql = "SELECT * FROM users;"
        >>> new_sql = add_where_condition(sql, "age > 18", "users")
        >>> print(new_sql)
        SELECT * FROM users WHERE age > 18;
        
        >>> sql = "SELECT * FROM users WHERE age > 18;"
        >>> new_sql = add_where_condition(sql, "status = 'active'", "users")
        >>> print(new_sql)
        SELECT * FROM users WHERE age > 18 AND status = 'active';
    """
    sql_clean = sql_text.rstrip().rstrip(';').strip()
    new_condition = new_condition.strip()
    
    # 创建输入流
    input_stream = InputStream(sql_clean)
    lexer = HiveLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = HiveParser(token_stream)
    
    try:
        # 解析SQL
        tree = parser.statement()
        
        # 创建TokenStreamRewriter用于修改token流
        rewriter = TokenStreamRewriter(token_stream)
        
        # 使用Visitor访问fromClause，定位targettable并添加WHERE条件
        visitor = WhereClauseVisitor(rewriter, new_condition, table_name)
        visitor.visit(tree)
        
        # 获取修改后的SQL文本
        # TokenStreamRewriter的getText方法：getText(program_name, start_index, stop_index)
        new_sql = rewriter.getText('default', 0, len(token_stream.tokens) - 1)
        
        # 如果没有修改（可能是因为表名不匹配），返回原SQL
        if new_sql == sql_clean and table_name:
            return sql_text  # 返回原始SQL（包含分号）
        
        # 添加分号
        if not new_sql.rstrip().endswith(';'):
            new_sql += ';'
 
        return new_sql
        
    except Exception as e:
        # 如果解析失败，抛出异常
        raise ValueError(f"SQL解析失败: {e}") from e
