#!/usr/bin/env python3
"""
构建正确格式的平台特定wheel文件
"""
import os
import sys
import platform
import zipfile
import tarfile
import shutil
import subprocess
import tomllib
from pathlib import Path


def get_version_from_pyproject():
    """从 pyproject.toml 读取版本号"""
    try:
        with open('pyproject.toml', 'rb') as f:
            data = tomllib.load(f)
            return data['project']['version']
    except Exception:
        raise Exception("Failed to get version from pyproject.toml")


def get_platform_tag():
    """获取正确的平台标签"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == 'windows':
        if machine in ['x86_64', 'amd64']:
            return 'win_amd64'
        elif machine == 'arm64':
            return 'win_arm64'
        elif machine in ['i386', 'i686']:
            return 'win32'
    elif system == 'darwin':
        if machine in ['x86_64', 'amd64']:
            return 'macosx_10_9_x86_64'
        elif machine == 'arm64':
            return 'macosx_11_0_arm64'
    elif system == 'linux':
        if machine in ['x86_64', 'amd64']:
            return 'manylinux_2_17_x86_64'
        elif machine == 'arm64':
            return 'manylinux_2_17_aarch64'
        elif machine in ['i386', 'i686']:
            return 'manylinux_2_17_i686'
    
    return 'unknown'


def get_python_tag():
    """获取Python标签"""
    version = sys.version_info
    return f"py{version.major}{version.minor}"


def get_binary_filename(platform_tag):
    """根据平台标签获取二进制文件名"""
    if platform_tag.startswith('win'):
        if platform_tag == 'win_amd64':
            return "hulo_Windows_x86_64.zip"
        elif platform_tag == 'win_arm64':
            return "hulo_Windows_arm64.zip"
        elif platform_tag == 'win32':
            return "hulo_Windows_i386.zip"
    elif platform_tag.startswith('macosx'):
        if 'x86_64' in platform_tag:
            return "hulo_Darwin_x86_64.tar.gz"
        elif 'arm64' in platform_tag:
            return "hulo_Darwin_arm64.tar.gz"
    elif platform_tag.startswith('manylinux'):
        if 'x86_64' in platform_tag:
            return "hulo_Linux_x86_64.tar.gz"
        elif 'aarch64' in platform_tag:
            return "hulo_Linux_arm64.tar.gz"
        elif 'i686' in platform_tag:
            return "hulo_Linux_i386.tar.gz"
    
    return None


def extract_binary(binary_path, extract_to):
    """解压二进制文件"""
    if binary_path.endswith('.zip'):
        with zipfile.ZipFile(binary_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    elif binary_path.endswith('.tar.gz'):
        with tarfile.open(binary_path, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_to)


def build_platform_wheel(platform_tag):
    """为特定平台构建wheel"""
    print(f"Building wheel for {platform_tag}...")
    
    # 获取二进制文件名
    binary_filename = get_binary_filename(platform_tag)
    if not binary_filename:
        print(f"No binary file mapping for {platform_tag}")
        return False
    
    binary_path = Path(binary_filename)
    if not binary_path.exists():
        print(f"Binary file {binary_filename} not found!")
        return False
    
    # 创建临时目录
    temp_dir = Path(f"temp_{platform_tag}")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # 复制Python包文件
    shutil.copytree("hulo", temp_dir / "hulo")

    # 解压二进制到 hulo/ 目录
    extract_binary(str(binary_path), str(temp_dir / "hulo"))

    # 复制 std/ 目录（如果存在）到 hulo/std/
    std_src = Path("std")
    std_dst = temp_dir / "hulo" / "std"
    if std_src.exists():
        shutil.copytree(std_src, std_dst)

    # 复制所有 .md 文件到 hulo/ 目录
    for md_file in Path().glob("*.md"):
        shutil.copy(md_file, temp_dir / "hulo" / md_file.name)

    # 生成 setup.py
    # 搜集所有要打包的文件
    package_data_lines = []
    # 可执行文件
    for f in (temp_dir / "hulo").iterdir():
        if f.is_file() and (f.suffix in [".exe", ""] or f.name.endswith(".so") or f.name.endswith(".dylib")):
            package_data_lines.append(f'        "{f.name}",')
    # .md 文件
    for f in (temp_dir / "hulo").glob("*.md"):
        package_data_lines.append(f'        "{f.name}",')
    # std/*.md
    if (temp_dir / "hulo" / "std").exists():
        for f in (temp_dir / "hulo" / "std").glob("*.md"):
            package_data_lines.append(f'        "std/{f.name}",')
    package_data_str = "\n".join(package_data_lines)

    setup_content = f'''#!/usr/bin/env python3
"""
Setup script for hulo package - {platform_tag}
"""
from setuptools import setup, find_packages

def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "Hulo programming language"

setup(
    name="hulo",
    version="{get_version_from_pyproject()}",
    description="Hulo programming language compiler and runtime",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="The Hulo Authors",
    author_email="",
    url="https://github.com/hulo-lang/hulo",
    packages=find_packages(),
    package_data={{
        "hulo": [
{package_data_str}
        ]
    }},
    include_package_data=True,
    entry_points={{
        'console_scripts': [
            'hulo=hulo.cli:main',
        ],
    }},
    python_requires=">=3.7",
    zip_safe=False,
)
'''
    with open(temp_dir / "setup.py", "w", encoding="utf-8") as f:
        f.write(setup_content)
    
    # 复制其他必要文件
    shutil.copy("README.md", temp_dir)
    shutil.copy("LICENSE", temp_dir)
    shutil.copy("MANIFEST.in", temp_dir)
    shutil.copy(binary_path, temp_dir)
    
    # 构建wheel
    try:
        subprocess.run([
            sys.executable, "-m", "build", "--wheel"
        ], cwd=temp_dir, check=True)
        
        # 移动生成的wheel文件
        dist_dir = temp_dir / "dist"
        if dist_dir.exists():
            for wheel_file in dist_dir.glob("*.whl"):
                # 重命名wheel文件以包含正确的平台标签
                new_name = wheel_file.name.replace(
                    "py3-none-any.whl", 
                    f"py3-none-{platform_tag}.whl"
                )
                new_path = Path("dist") / new_name
                shutil.move(wheel_file, new_path)
                print(f"Created: {new_path}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building wheel for {platform_tag}: {e}")
        return False
    finally:
        # 清理临时目录
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def main():
    """主函数"""
    # 确保dist目录存在
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # 定义所有支持的平台标签
    platform_tags = [
        "win_amd64",
        "win_arm64", 
        "win32",
        "macosx_10_9_x86_64",
        "macosx_11_0_arm64",
        "manylinux_2_17_x86_64",
        "manylinux_2_17_aarch64",
        "manylinux_2_17_i686",
    ]
    
    success_count = 0
    total_count = len(platform_tags)
    
    for platform_tag in platform_tags:
        if build_platform_wheel(platform_tag):
            success_count += 1
    
    print(f"\nBuild completed: {success_count}/{total_count} wheels created successfully")
    
    if success_count > 0:
        print("\nGenerated wheel files:")
        for wheel_file in dist_dir.glob("*.whl"):
            print(f"  - {wheel_file.name}")


if __name__ == "__main__":
    main() 