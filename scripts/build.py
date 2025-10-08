# build.py
#!/usr/bin/env python3
"""Build script that orchestrates Bazel builds for Python packaging."""

import subprocess
import argparse
import shutil
import sys
import os
from pathlib import Path
import tomllib 
import platform

# Read package name from pyproject.toml
def get_package_name():
    """Read the package name from pyproject.toml."""
    toml_path = Path("pyproject.toml")
    if not toml_path.exists():
        raise FileNotFoundError("pyproject.toml not found")
    
    with open(toml_path, "rb") as f:
        config = tomllib.load(f)
    
    # Get PyPI package name and convert to Python module name
    package_name = config["project"]["name"]
    # Convert hyphens to underscores for Python module name
    module_name = package_name.replace("-", "_")
    return module_name

PACKAGE_NAME = get_package_name()

DIR_CPP = Path("cpp/")
DIR_PYTHON = Path("python/")

DIR_BAZEL_CPP = Path("bazel-bin/cpp")
DIR_BAZEL_PYTHON = Path("bazel-bin/python")

DIST_PYTHON = Path("dist/")
DIST_CPP = Path("build/")

os.makedirs(DIST_CPP, exist_ok=True)
os.makedirs(DIST_PYTHON, exist_ok=True)

def get_extension_suffix():
    """Get platform-specific extension suffix."""
    system = platform.system()
    if system == "Windows":
        return "pyd"
    elif system == "Darwin":
        return "so"
    else:
        return "so"


def build_all():
    """Run Bazel build."""
    print("Building all...")
    subprocess.run(["bazel", "build", "//..."], check=True)

    copy_python()
    copy_cpp()


def build_cpp():
    """Run Bazel build for cpp."""
    print("Building cpp...")
    subprocess.run(["bazel", "build", "//cpp:all"], check=True)


def copy_python():
    """Copy Python wheel and extension to appropriate directories."""
    
    # ---- Move whl to dist directory
    wheel = list(DIR_BAZEL_PYTHON.glob("*.whl"))

    if not wheel:
        raise FileNotFoundError(f"No .whl file found in {DIR_BAZEL_PYTHON}")
    
    dest_wheel = DIST_PYTHON / wheel[0].name
    
    # Remove existing wheel if it exists
    if dest_wheel.exists():
        dest_wheel.unlink()
    
    shutil.copy2(wheel[0], dest_wheel)
    print(f"Copied wheel: {wheel[0]} -> {dest_wheel}")

    # ----- Move .so to python/gambit_template directory
    extension = get_extension_suffix()
    so_files = list(DIR_BAZEL_CPP.glob(f"{PACKAGE_NAME}.{extension}"))

    if not so_files:
        raise FileNotFoundError(f"No .{extension} file found matching pattern '*{PACKAGE_NAME}*.{extension}' in {DIR_BAZEL_CPP}")
    
    # Destination is inside the package directory
    dest_so = DIR_PYTHON / so_files[0].name
    
    # Remove existing extension if it exists
    if dest_so.exists():
        dest_so.unlink()
    
    shutil.copy2(so_files[0], DIR_PYTHON)  # Changed: copy to dest_so, not DIR_PYTHON
    print(f"Copied extension: {so_files[0]} -> {dest_so}")


def copy_cpp():
    """Copy C++ static library to build directory."""
    
    cpp_library = list(DIR_BAZEL_CPP.glob("*.a"))

    if not cpp_library:
        raise FileNotFoundError(f"No .a file found in {DIR_BAZEL_CPP}")
    
    dest_lib = DIST_CPP / cpp_library[0].name
    
    # Remove existing library if it exists
    if dest_lib.exists():
        dest_lib.unlink()

    shutil.copy2(cpp_library[0], dest_lib)
    print(f"Copied library: {cpp_library[0]} -> {dest_lib}")


def clean():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    subprocess.run(["bazel", "clean"], check=True)
    
    # Clean Python package extensions
    for ext in ["*.so", "*.pyd"]:
        for ext_file in DIR_PYTHON.glob(ext):
            ext_file.unlink()
            print(f"Removed: {ext_file}")
    
    # Clean distribution directories
    if DIST_PYTHON.exists():
        shutil.rmtree(DIST_PYTHON)
        os.makedirs(DIST_PYTHON, exist_ok=True)
        print(f"Cleaned: {DIST_PYTHON}")
    
    if DIST_CPP.exists():
        shutil.rmtree(DIST_CPP)
        os.makedirs(DIST_CPP, exist_ok=True)
        print(f"Cleaned: {DIST_CPP}")

def cli(args):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Build script for C++ extensions with Bazel"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts"
    )
    
    return parser.parse_args(args)


def main(args):
    """Execute the requested command."""
    if args.clean:
        clean()
    else:
        build_all()
        print("Build complete!")


if __name__ == "__main__":
    main(cli(sys.argv[1:]))