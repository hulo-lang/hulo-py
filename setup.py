#!/usr/bin/env python3
"""
Setup script for hulo package - 跳板包，自动选择平台特定的wheel
"""
import os
import sys
import platform
import subprocess
import glob
import tomllib
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


def get_version_from_pyproject():
    """从 pyproject.toml 读取版本号"""
    try:
        with open('pyproject.toml', 'rb') as f:
            data = tomllib.load(f)
            return data['project']['version']
    except Exception:
        raise Exception("Failed to get version from pyproject.toml")

def get_platform_info():
    """获取当前平台信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # 映射平台名称
    platform_map = {
        'windows': 'windows',
        'darwin': 'darwin', 
        'linux': 'linux'
    }
    
    # 映射架构名称
    arch_map = {
        'x86_64': 'x86_64',
        'amd64': 'x86_64',
        'arm64': 'arm64',
        'aarch64': 'arm64',
        'i386': 'i386',
        'i686': 'i386'
    }
    
    platform_name = platform_map.get(system, system)
    arch_name = arch_map.get(machine, machine)
    
    return platform_name, arch_name


def find_platform_wheel():
    """查找对应平台的wheel文件"""
    platform_name, arch_name = get_platform_info()
    version = get_version_from_pyproject()
    
    # 构建wheel文件名模式
    wheel_pattern = f"hulo-{version}-py3-none-{platform_name}_{arch_name}.whl"
    
    # 在dist目录中查找
    dist_dir = os.path.join(os.path.dirname(__file__), "dist")
    if os.path.exists(dist_dir):
        wheel_files = glob.glob(os.path.join(dist_dir, wheel_pattern))
        if wheel_files:
            return wheel_files[0]
    
    print(f"Warning: No wheel found for {platform_name}-{arch_name}")
    print(f"Looking for: {wheel_pattern}")
    print(f"Available wheels:")
    if os.path.exists(dist_dir):
        for wheel in glob.glob(os.path.join(dist_dir, "*.whl")):
            print(f"  - {os.path.basename(wheel)}")
    
    return None


def install_platform_wheel():
    """安装对应平台的wheel文件"""
    wheel_path = find_platform_wheel()
    
    if not wheel_path:
        print("No suitable wheel found for this platform")
        return False
    
    print(f"Installing platform-specific wheel: {os.path.basename(wheel_path)}")
    
    try:
        # 安装wheel文件
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", wheel_path
        ])
        print("Platform-specific wheel installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing wheel: {e}")
        return False


class CustomInstallCommand(install):
    """自定义安装命令"""
    def run(self):
        # 安装平台特定的wheel
        if install_platform_wheel():
            print("Platform-specific wheel installed successfully")
        else:
            print("Failed to install platform-specific wheel")
            # 如果安装失败，继续安装当前包
            install.run(self)


class CustomDevelopCommand(develop):
    """自定义开发安装命令"""
    def run(self):
        # 开发模式下，直接安装当前包
        develop.run(self)


# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Hulo programming language"


setup(
    name="hulo",
    version=get_version_from_pyproject(),
    description="Hulo programming language compiler and runtime",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="The Hulo Authors",
    author_email="",
    url="https://github.com/hulo-lang/hulo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
    ],
    python_requires=">=3.7",
    install_requires=[],
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
    },
    entry_points={
        'console_scripts': [
            'hulo=hulo.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 