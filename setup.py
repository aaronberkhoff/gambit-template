# setup.py
import sys

from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scripts.build import build_all
from scripts.make_stubs import main as stubs_main

class BazelBuild(build_ext):
    """Build C++ extensions with Bazel"""
    def run(self):
        # Build the .so with Bazel
        build_all()
        stubs_main("gambit_template")

class DevelopWithBazel(develop):
    """Custom develop command that builds with Bazel first"""
    def run(self):
        # Build C++ before setting up editable install
        self.run_command('build_ext')
        develop.run(self)

class InstallWithBazel(install):
    """Custom install command that builds with Bazel first"""
    def run(self):
        self.run_command('build_ext')
        install.run(self)

# Everything else comes from pyproject.toml!
setup(
    cmdclass={
        'build_ext': BazelBuild,
        'develop': DevelopWithBazel,
    },
    ext_modules=[],  # Dummy to trigger build_ext
)