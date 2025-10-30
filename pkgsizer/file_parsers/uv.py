"""Parse uv.lock and pyproject.toml files for uv."""

import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


def parse_uv(file_path: Path) -> list[str]:
    """
    Parse a uv.lock or pyproject.toml file.
    
    Args:
        file_path: Path to uv.lock or pyproject.toml
    
    Returns:
        List of package names
    """
    packages: list[str] = []
    
    if file_path.name == "uv.lock":
        return parse_uv_lock(file_path)
    
    # Parse pyproject.toml
    with open(file_path, "rb") as f:
        data = tomllib.load(f)
    
    # Check [project.dependencies] (PEP 621)
    project = data.get("project", {})
    dependencies = project.get("dependencies", [])
    
    for dep in dependencies:
        # Extract package name from dependency specifier
        # Format: "package>=1.0.0" or "package[extra]>=1.0.0"
        pkg_name = extract_package_name(dep)
        if pkg_name:
            packages.append(pkg_name)
    
    # Check [project.optional-dependencies]
    optional_deps = project.get("optional-dependencies", {})
    for group_name, group_deps in optional_deps.items():
        for dep in group_deps:
            pkg_name = extract_package_name(dep)
            if pkg_name and pkg_name not in packages:
                packages.append(pkg_name)
    
    return packages


def parse_uv_lock(file_path: Path) -> list[str]:
    """
    Parse a uv.lock file.
    
    Args:
        file_path: Path to uv.lock
    
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


def extract_package_name(dep_spec: str) -> str:
    """
    Extract package name from a dependency specifier.
    
    Args:
        dep_spec: Dependency specifier (e.g., "package>=1.0.0" or "package[extra]")
    
    Returns:
        Package name
    """
    from packaging.requirements import Requirement
    
    try:
        req = Requirement(dep_spec)
        return req.name
    except Exception:
        # Fallback: try to extract manually
        for sep in ["==", ">=", "<=", ">", "<", "~=", "!=", "[", " "]:
            if sep in dep_spec:
                return dep_spec.split(sep)[0].strip()
        return dep_spec.strip()

