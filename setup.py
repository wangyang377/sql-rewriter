"""
Build script - Automatically generate ANTLR code during build

This file is used to automatically generate ANTLR parser code when building distribution packages.
The generated code will be included in the distribution package, ready for users after installation.
"""

from setuptools import setup
from setuptools.command.build_py import build_py
from pathlib import Path
import subprocess
import sys


class BuildPyCommand(build_py):
    """Custom build_py command that generates ANTLR code before building"""
    
    def run(self):
        """Generate ANTLR code before running build"""
        print("Generating ANTLR parser code...")
        
        # Get project root directory
        project_root = Path(__file__).parent
        grammar_dir = project_root / "grammar"
        output_dir = project_root / "src" / "sql_rewriter" / "_generated"
        script_path = project_root / "scripts" / "generate_parser.sh"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if grammar files exist
        if not (grammar_dir / "HiveLexer.g4").exists():
            print("Warning: HiveLexer.g4 not found, skipping code generation")
            print("      If cloning from Git, please run: ./scripts/generate_parser.sh")
        else:
            # Run generation script
            try:
                result = subprocess.run(
                    [str(script_path)],
                    cwd=str(project_root),
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(result.stdout)
                print("✓ ANTLR code generated successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error: ANTLR code generation failed")
                print(e.stderr)
                print("\nHint: If cloning from Git, please run:")
                print("  ./scripts/generate_parser.sh")
                print("\nOr install ANTLR4 tool:")
                print("  macOS: brew install antlr")
                print("  Linux: sudo apt-get install antlr4")
                # Don't raise exception, allow build to continue (if code already exists)
                if not (output_dir / "HiveParser.py").exists():
                    raise
            except FileNotFoundError:
                print("Warning: Generation script not found, skipping code generation")
                print("      If cloning from Git, please run: ./scripts/generate_parser.sh")
        
        # Call parent's run method to continue build
        super().run()


# Read configuration from pyproject.toml
# Here we only define build commands, other configuration is in pyproject.toml
setup(
    cmdclass={
        'build_py': BuildPyCommand,
    },
)
