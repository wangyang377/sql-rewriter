"""
SQL WHERE Condition Adder - SQL Modification Tool Based on Parse Tree

Main functionality: Add or append WHERE conditions to SQL statements
"""

from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from ._generated import HiveLexer, HiveParser, HiveParserVisitor


class WhereClauseVisitor(HiveParserVisitor):
    """Visitor: Locates target table in fromClause, accesses WhereClause from parent node, then rewrites SQL"""
    
    def __init__(self, rewriter, new_condition, target_table_name):
        self.rewriter = rewriter
        self.new_condition = new_condition
        self.target_table_name = target_table_name.lower() if target_table_name else None
        self.current_table_name = None  # Table name in current FROM clause
        
    def visitFromClause(self, ctx):
        """Locates target table in FROM clause, accesses WhereClause from parent node, then rewrites SQL"""
        # If no table name specified, skip processing
        if not self.target_table_name:
            return self.visitChildren(ctx)
        
        # Collect table name from current FROM clause
        # Path: fromClause -> fromSource -> joinSource -> atomjoinSource -> tableSource -> tableName
        self.current_table_name = None
        from_source = ctx.fromSource()
        if from_source:
            join_source = from_source.joinSource()
            if join_source:
                atom_join_source = join_source.atomjoinSource()
                if atom_join_source:
                    table_name = atom_join_source.tableSource().tableName()
                    self.current_table_name = table_name.getText().lower()
        
        # Check if matches target table name
        should_process = self.current_table_name == self.target_table_name
        
        if should_process:
            # Direct parent of fromClause is atomSelectStatement (according to grammar rules)
            atom_select_ctx = ctx.parentCtx
            if atom_select_ctx:
                # Access WhereClause from parent node (grammar: atomSelectStatement: ... w=whereClause? ...)
                # w is an attribute, can be None (if no WHERE clause) or WhereClauseContext object
                where_clause = atom_select_ctx.w
                if where_clause:
                    # Structure of whereClause: KW_WHERE searchCondition
                    # where_clause.start is the position of KW_WHERE
                    # Insert '(' after WHERE keyword, insert ')' AND new condition after searchCondition
                    where_keyword_token = where_clause.start
                    stop_token = where_clause.searchCondition().stop
                    self.rewriter.insertAfter(where_keyword_token.tokenIndex, ' (')
                    self.rewriter.insertAfter(stop_token.tokenIndex, ') AND ' + self.new_condition)
                else:
                    # No WHERE clause, insert WHERE condition after FROM clause
                    self.rewriter.insertAfter(ctx.stop.tokenIndex, ' WHERE ' + self.new_condition)
        
        return None


def add_where_condition(sql_text, new_condition, table_name=None):
    """
    Add or append WHERE condition to SQL statement (based on parse tree)
    
    Args:
        sql_text: Original SQL statement
        new_condition: WHERE condition to add (without WHERE keyword)
        table_name: Target table name. WHERE condition is only added if FROM clause contains 
                   this table name. If None, no processing is performed
    
    Returns:
        Modified SQL statement
    
    Raises:
        ValueError: If SQL parsing fails
    
    Example:
        >>> sql = "SELECT * FROM users;"
        >>> new_sql = add_where_condition(sql, "age > 18", "users")
        >>> print(new_sql)
        SELECT * FROM users WHERE age > 18;
        
        >>> sql = "SELECT * FROM users WHERE age > 18;"
        >>> new_sql = add_where_condition(sql, "status = 'active'", "users")
        >>> print(new_sql)
        SELECT * FROM users WHERE (age > 18) AND status = 'active';
    """
    sql_clean = sql_text.rstrip().rstrip(';').strip()
    new_condition = new_condition.strip()
    
    # Create input stream
    input_stream = InputStream(sql_clean)
    lexer = HiveLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = HiveParser(token_stream)
    
    try:
        # Parse SQL
        tree = parser.statement()
        
        # Create TokenStreamRewriter to modify token stream
        rewriter = TokenStreamRewriter(token_stream)
        
        # Use Visitor to access fromClause, locate target table and add WHERE condition
        visitor = WhereClauseVisitor(rewriter, new_condition, table_name)
        visitor.visit(tree)
        
        # Get modified SQL text
        # TokenStreamRewriter.getText method: getText(program_name, start_index, stop_index)
        new_sql = rewriter.getText('default', 0, len(token_stream.tokens) - 1)
        
        # If no modification (possibly due to table name mismatch), return original SQL
        if new_sql == sql_clean and table_name:
            return sql_text  # Return original SQL (with semicolon)
        
        # Add semicolon
        if not new_sql.rstrip().endswith(';'):
            new_sql += ';'
 
        return new_sql
        
    except Exception as e:
        # If parsing fails, raise exception
        raise ValueError(f"SQL parsing failed: {e}") from e
