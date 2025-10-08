import argparse
import subprocess
import sys
import os
import shutil
import ast
from pathlib import Path

PY_FOLDER = Path("python")
STUB_TMP = PY_FOLDER / "stubs_tmp"


def run_stubgen(module: str) -> Path:
    """Run pybind11-stubgen and return the path to the generated .pyi."""
    subprocess.run(
        [sys.executable, "-m", "pybind11_stubgen", module, "--output-dir", str(STUB_TMP)],
        check=True,
        env={**os.environ, "PYTHONPATH": "python"} # points to the python directory
    )
    mod_parts = module.split(".")
    if len(mod_parts) > 1:
        return STUB_TMP.joinpath(*mod_parts).with_suffix(".pyi")
    else:
        return STUB_TMP.joinpath(mod_parts[0])


def get_definitions(tree: ast.AST):
    """Extract top-level function and class names."""
    defs = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            defs[node.name] = node
        elif isinstance(node, ast.ClassDef):
            defs[node.name] = node
    return defs


def get_class_members(node: ast.ClassDef):
    """Extract method/attribute names from a class AST."""
    members = {}
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            members[item.name] = item
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            members[item.target.id] = item
    return members


def merge_stubs(old_path: Path, new_path: Path):
    """Merge new stub definitions into old stub (AST-aware)."""
    with old_path.open("r", encoding="utf-8") as f:
        old_src = f.read()
    with new_path.open("r", encoding="utf-8") as f:
        new_src = f.read()

    old_tree = ast.parse(old_src)
    new_tree = ast.parse(new_src)

    old_defs = get_definitions(old_tree)
    new_defs = get_definitions(new_tree)

    changes = []

    for name, new_def in new_defs.items():
        if name not in old_defs:
            # New top-level def/class → append
            old_tree.body.append(new_def)
            changes.append(f"Added {name}")
        else:
            # If it's a class, merge members
            if isinstance(new_def, ast.ClassDef) and isinstance(old_defs[name], ast.ClassDef):
                old_members = get_class_members(old_defs[name])
                new_members = get_class_members(new_def)
                for mname, mdef in new_members.items():
                    if mname not in old_members:
                        old_defs[name].body.append(mdef)
                        changes.append(f"Added {name}.{mname}")

    if changes:
        print(f"Merged changes into {old_path}: {changes}")
        new_code = ast.unparse(old_tree)  # requires Python 3.9+
        with old_path.open("w", encoding="utf-8") as f:
            f.write(new_code)
    else:
        print(f"No new definitions to merge for {old_path}")


def generate_and_merge(module: str):
    print(f"Processing {module}...")
    new_stub = run_stubgen(module)  # returns Path to .pyi or directory

    if new_stub.is_dir():
        # Usually looks like <tmp>//
        top_level_dirs = list(new_stub.iterdir())
        if len(top_level_dirs) == 1 and top_level_dirs[0].is_dir():
            # This is the package directory (e.g., /)
            package_root = top_level_dirs[0]
        else:
            # In rare cases pybind11-stubgen outputs directly here
            package_root = new_stub

        for path in package_root.rglob("*.pyi"):
            # compute relative path *inside the package folder*
            rel_path = path.relative_to(package_root)

            # mirror under python/
            dest = PY_FOLDER / package_root.name / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)

            if dest.exists():
                merge_stubs(dest, path)
            else:
                shutil.copy2(path, dest)
                print(f"Created new stub: {dest}")

    else:
        # single file case
        rel_path = Path(*module.split(".")[1:]).with_suffix(".pyi")
        dest = PY_FOLDER / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)

        if dest.exists():
            merge_stubs(dest, new_stub)
        else:
            shutil.copy2(new_stub, dest)
            print(f"Created new stub: {dest}")

def main(args):

    for module in args.modules:
        generate_and_merge(module)
        
    shutil.rmtree(STUB_TMP)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Incrementally generate and merge stubs (AST-aware)"
    )
    parser.add_argument(
        "modules",
        nargs="+",
        help="Modules to stub (e.g. .planets .dynamics)",
    )
    args = parser.parse_args()

    main(args)
