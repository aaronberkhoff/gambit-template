import sys
import pathlib
import shutil
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

sys.path.insert(0, "scripts/")

from build import build_all, get_extension_suffix, PACKAGE_NAME


class BazelBuild(build_ext):
    """Custom build extension that uses Bazel for compilation."""
    
    def run(self):
        # Run the Bazel build process
        print("Building with Bazel...")
        try:
            build_all()
        except Exception as e:
            print(f"Bazel build failed: {e}", file=sys.stderr)
            raise
        
        # Copy each built extension to the expected location
        for ext in self.extensions:
            self.build_extension_artifact(ext)
    
    def build_extension_artifact(self, ext):
        """Copy the Bazel-built artifact to setuptools expected location."""
        # Get the expected path for this extension
        ext_path = pathlib.Path(self.get_ext_fullpath(ext.name)).resolve()
        ext_path.parent.mkdir(parents=True, exist_ok=True)
        
        # The build script already copied the extension to python/
        # Now we need to copy it to the setuptools build directory
        extension_suffix = get_extension_suffix()
        source_path = pathlib.Path("python") / f"{PACKAGE_NAME}.{extension_suffix}"
        
        if not source_path.exists():
            raise FileNotFoundError(
                f"Extension not found at {source_path}. "
                f"Build script should have copied it there."
            )
        
        print(f"Copying {source_path} -> {ext_path}")
        shutil.copy2(source_path, ext_path)
    
    def get_ext_filename(self, ext_name):
        """Override to use platform-specific extension suffix."""
        # This ensures setuptools uses the correct extension
        ext_suffix = get_extension_suffix()
        return f"{ext_name}.{ext_suffix}"


# Define dummy extensions - these tell setuptools what to expect
# but the actual building is done by Bazel
ext_modules = [
    Extension(
        PACKAGE_NAME,
        sources=[],  # Empty sources, Bazel handles compilation
    ),
]

# Minimal setup - metadata comes from pyproject.toml
setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": BazelBuild},
    zip_safe=False,  # C extensions can't be zipped
)