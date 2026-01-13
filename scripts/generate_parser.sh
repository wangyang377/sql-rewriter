#!/bin/bash
# Generate ANTLR4 parser code
# Output generated code to src/sql_rewriter/_generated/ directory

# Check if antlr4 is installed, supports both 'antlr' and 'antlr4' command names
ANTLR_CMD=""
if command -v antlr &> /dev/null; then
    ANTLR_CMD="antlr"
elif command -v antlr4 &> /dev/null; then
    ANTLR_CMD="antlr4"
else
    echo "Error: antlr4 command not found"
    echo "Please install ANTLR4 first:"
    echo "  macOS: brew install antlr"
    echo "  Linux: sudo apt-get install antlr4"
    echo "  Or download: https://www.antlr.org/download/antlr-4.13.2-complete.jar"
    exit 1
fi

# Get parent directory of script directory (project root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
GRAMMAR_DIR="$PROJECT_ROOT/grammar"
OUTPUT_DIR="$PROJECT_ROOT/src/sql_rewriter/_generated"

# Check if grammar directory exists
if [ ! -d "$GRAMMAR_DIR" ]; then
    echo "Error: grammar directory does not exist: $GRAMMAR_DIR"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Generate parser code
echo "Generating parser code..."
echo "Grammar directory: $GRAMMAR_DIR"
echo "Output directory: $OUTPUT_DIR"

cd "$GRAMMAR_DIR" || exit 1

$ANTLR_CMD -Dlanguage=Python3 -visitor -o "$OUTPUT_DIR" HiveLexer.g4 HiveParser.g4

if [ $? -eq 0 ]; then
    echo "✓ Parser code generated successfully!"
    echo "Generated files are located at: $OUTPUT_DIR"
    echo ""
    echo "Note: Generated code is in _generated/ directory to keep main code directory clean."
else
    echo "✗ Parser code generation failed"
    exit 1
fi
