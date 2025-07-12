#!/usr/bin/env python3
"""
Hulo CLI interface
"""
import os
import sys
import platform
import subprocess
from pathlib import Path


def get_binary_path():
    """获取hulo二进制文件路径"""
    # 直接在hulo包目录下查找二进制文件
    hulo_dir = Path(__file__).parent
    
    # 查找可执行文件
    if platform.system() == 'Windows':
        # Windows: 查找 .exe 文件
        for file in hulo_dir.iterdir():
            if file.is_file() and file.suffix == '.exe':
                return str(file)
    else:
        # Unix/Linux/Mac: 查找可执行文件（排除 .exe）
        for file in hulo_dir.iterdir():
            if file.is_file() and file.suffix != '.exe' and os.access(file, os.X_OK):
                return str(file)
    
    # 如果找不到，尝试从当前目录查找（开发模式）
    current_dir = Path(__file__).parent.parent.parent
    for file in current_dir.glob('hulo*'):
        if file.is_file():
            if platform.system() == 'Windows':
                if file.suffix == '.exe':
                    return str(file)
            else:
                if file.suffix != '.exe' and os.access(file, os.X_OK):
                    return str(file)
    
    return None


def main():
    """主函数"""
    binary_path = get_binary_path()
    
    if not binary_path:
        print("Error: Hulo binary not found!")
        print("Please make sure the package is installed correctly.")
        sys.exit(1)
    
    if not os.path.exists(binary_path):
        print(f"Error: Binary file not found at {binary_path}")
        sys.exit(1)
    
    # 将命令行参数传递给二进制文件
    try:
        result = subprocess.run([binary_path] + sys.argv[1:], check=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running hulo binary: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 