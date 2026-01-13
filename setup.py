"""
构建脚本 - 在构建时自动生成 ANTLR 代码

这个文件用于在构建分发包时自动生成 ANTLR 解析器代码。
生成的代码会被包含在分发包中，用户安装后即可使用。
"""

from setuptools import setup
from setuptools.command.build_py import build_py
from pathlib import Path
import subprocess
import sys


class BuildPyCommand(build_py):
    """自定义 build_py 命令，在构建前生成 ANTLR 代码"""
    
    def run(self):
        """运行构建前，先生成 ANTLR 代码"""
        print("正在生成 ANTLR 解析器代码...")
        
        # 获取项目根目录
        project_root = Path(__file__).parent
        grammar_dir = project_root / "grammar"
        output_dir = project_root / "src" / "sql_rewriter" / "_generated"
        script_path = project_root / "scripts" / "generate_parser.sh"
        
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查语法文件是否存在
        if not (grammar_dir / "HiveLexer.g4").exists():
            print("警告: 未找到 HiveLexer.g4，跳过代码生成")
            print("      如果从 Git 克隆，请先运行: ./scripts/generate_parser.sh")
        else:
            # 运行生成脚本
            try:
                result = subprocess.run(
                    [str(script_path)],
                    cwd=str(project_root),
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(result.stdout)
                print("✓ ANTLR 代码生成成功")
            except subprocess.CalledProcessError as e:
                print(f"错误: ANTLR 代码生成失败")
                print(e.stderr)
                print("\n提示: 如果从 Git 克隆，请先运行:")
                print("  ./scripts/generate_parser.sh")
                print("\n或者安装 ANTLR4 工具:")
                print("  macOS: brew install antlr")
                print("  Linux: sudo apt-get install antlr4")
                # 不抛出异常，允许继续构建（如果代码已存在）
                if not (output_dir / "HiveParser.py").exists():
                    raise
            except FileNotFoundError:
                print("警告: 未找到生成脚本，跳过代码生成")
                print("      如果从 Git 克隆，请先运行: ./scripts/generate_parser.sh")
        
        # 调用父类的 run 方法继续构建
        super().run()


# 读取 pyproject.toml 中的配置
# 这里我们只定义构建命令，其他配置在 pyproject.toml 中
setup(
    cmdclass={
        'build_py': BuildPyCommand,
    },
)
