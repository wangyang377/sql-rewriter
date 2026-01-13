#!/bin/bash
# 生成 ANTLR4 解析器代码
# 将生成的代码输出到 src/sql_rewriter/_generated/ 目录

# 检查是否安装了 antlr4，支持 antlr 和 antlr4 两种命令名
ANTLR_CMD=""
if command -v antlr &> /dev/null; then
    ANTLR_CMD="antlr"
elif command -v antlr4 &> /dev/null; then
    ANTLR_CMD="antlr4"
else
    echo "错误: 未找到 antlr4 命令"
    echo "请先安装 ANTLR4:"
    echo "  macOS: brew install antlr"
    echo "  Linux: sudo apt-get install antlr4"
    echo "  或下载: https://www.antlr.org/download/antlr-4.13.2-complete.jar"
    exit 1
fi

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
GRAMMAR_DIR="$PROJECT_ROOT/grammar"
OUTPUT_DIR="$PROJECT_ROOT/src/sql_rewriter/_generated"

# 检查 grammar 目录是否存在
if [ ! -d "$GRAMMAR_DIR" ]; then
    echo "错误: grammar 目录不存在: $GRAMMAR_DIR"
    exit 1
fi

# 创建输出目录（如果不存在）
mkdir -p "$OUTPUT_DIR"

# 生成解析器代码
echo "正在生成解析器代码..."
echo "语法文件目录: $GRAMMAR_DIR"
echo "输出目录: $OUTPUT_DIR"

cd "$GRAMMAR_DIR" || exit 1

$ANTLR_CMD -Dlanguage=Python3 -visitor -o "$OUTPUT_DIR" HiveLexer.g4 HiveParser.g4

if [ $? -eq 0 ]; then
    echo "✓ 解析器代码生成成功！"
    echo "生成的文件位于: $OUTPUT_DIR"
    echo ""
    echo "注意: 生成的代码位于 _generated/ 目录中，保持主代码目录干净。"
else
    echo "✗ 解析器代码生成失败"
    exit 1
fi
