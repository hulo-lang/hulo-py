"""
Hulo programming language package
"""
import tomllib
import os


def get_version_from_pyproject():
    """从 pyproject.toml 读取版本号"""
    try:
        # 获取项目根目录
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        pyproject_path = os.path.join(project_root, 'pyproject.toml')
        
        with open(pyproject_path, 'rb') as f:
            data = tomllib.load(f)
            return data['project']['version']
    except Exception:
        raise Exception("Failed to get version from pyproject.toml")


__version__ = get_version_from_pyproject()
__author__ = "The Hulo Authors"
__license__ = "MIT"

from .cli import main

__all__ = ["main"] 