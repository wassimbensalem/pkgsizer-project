"""Parse Poetry pyproject.toml and poetry.lock files."""

import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


def parse_poetry(file_path: Path) -> list[str]:
    """
    Parse a Poetry pyproject.toml or poetry.lock file.
    
    Args:
        file_path: Path to pyproject.toml or poetry.lock
    
    Returns:
        List of package names
    """
    packages: list[str] = []
    
    if file_path.name == "poetry.lock":
        return parse_poetry_lock(file_path)
    
    # Parse pyproject.toml
    with open(file_path, "rb") as f:
        data = tomllib.load(f)
    
    # Get dependencies from [tool.poetry.dependencies]
    poetry_section = data.get("tool", {}).get("poetry", {})
    dependencies = poetry_section.get("dependencies", {})
    
    for pkg_name in dependencies:
        # Skip python itself
        if pkg_name.lower() == "python":
            continue
        packages.append(pkg_name)
    
    # Get dev dependencies
    dev_dependencies = poetry_section.get("dev-dependencies", {})
    for pkg_name in dev_dependencies:
        if pkg_name.lower() == "python":
            continue
        if pkg_name not in packages:
            packages.append(pkg_name)
    
    # Get group dependencies (Poetry 1.2+)
    groups = poetry_section.get("group", {})
    for group_name, group_data in groups.items():
        group_deps = group_data.get("dependencies", {})
        for pkg_name in group_deps:
            if pkg_name.lower() == "python":
                continue
            if pkg_name not in packages:
                packages.append(pkg_name)
    
    return packages


def parse_poetry_lock(file_path: Path) -> list[str]:
    """
    Parse a poetry.lock file.
    
    Args:
        file_path: Path to poetry.lock
    
    Returns:
        List of package names
    """
    packages: list[str] = []
    
    with open(file_path, "rb") as f:
        data = tomllib.load(f)
    
    # Get all packages from [[package]] sections
    for package in data.get("package", []):
        name = package.get("name")
        if name:
            packages.append(name)
    
    return packages

