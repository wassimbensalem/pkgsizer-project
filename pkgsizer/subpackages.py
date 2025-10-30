"""Enumerate subpackages and modules within distributions."""

import os
from pathlib import Path
from typing import Optional

from pkgsizer.size_calc import SizeInfo, calculate_path_size


class SubpackageInfo:
    """Information about a subpackage or module."""
    
    def __init__(
        self,
        name: str,
        qualified_name: str,
        path: Path,
        depth: int = 0,
        is_package: bool = False,
    ):
        self.name = name
        self.qualified_name = qualified_name
        self.path = path
        self.depth = depth
        self.is_package = is_package
        self.size_info = SizeInfo()
        self.children: list[SubpackageInfo] = []
    
    def __repr__(self) -> str:
        return f"SubpackageInfo({self.qualified_name}, size={self.size_info.size_bytes})"


def enumerate_subpackages(
    package_path: Path,
    package_name: str,
    max_depth: Optional[int] = None,
    current_depth: int = 0,
    follow_symlinks: bool = False,
    exclude_patterns: Optional[list[str]] = None,
) -> SubpackageInfo:
    """
    Recursively enumerate subpackages and modules.
    
    Args:
        package_path: Path to the package directory
        package_name: Name of the package
        max_depth: Maximum depth to traverse (None = unlimited)
        current_depth: Current depth in the tree
        follow_symlinks: Whether to follow symbolic links
        exclude_patterns: List of glob patterns to exclude
    
    Returns:
        SubpackageInfo for the package
    """
    exclude_patterns = exclude_patterns or []
    
    # Create info for this package
    info = SubpackageInfo(
        name=package_name.split(".")[-1],
        qualified_name=package_name,
        path=package_path,
        depth=current_depth,
        is_package=package_path.is_dir(),
    )
    
    # If it's a file (module), just calculate its size
    if package_path.is_file():
        info.size_info = calculate_path_size(
            package_path,
            follow_symlinks=follow_symlinks,
            exclude_patterns=exclude_patterns,
        )
        return info
    
    # If it's not a directory, return empty
    if not package_path.is_dir():
        return info
    
    # Check if we've reached max depth
    if max_depth is not None and current_depth >= max_depth:
        # Just calculate total size without recursing
        info.size_info = calculate_path_size(
            package_path,
            follow_symlinks=follow_symlinks,
            exclude_patterns=exclude_patterns,
        )
        return info
    
    # Track files we've already accounted for in subpackages
    accounted_files: set[Path] = set()
    
    # Enumerate subpackages and modules
    try:
        entries = sorted(os.scandir(package_path), key=lambda e: e.name)
        
        for entry in entries:
            entry_path = Path(entry.path)
            entry_name = entry.name
            
            # Skip __pycache__ and other common directories
            if entry_name in ("__pycache__", ".git", ".svn", "__pyinstaller"):
                continue
            
            # Skip excluded patterns
            from pkgsizer.size_calc import should_exclude
            if should_exclude(entry_path, exclude_patterns):
                continue
            
            is_package = False
            subpackage_path = None
            
            # Check if it's a package (directory with __init__.py)
            if entry.is_dir():
                init_file = entry_path / "__init__.py"
                if init_file.exists():
                    is_package = True
                    subpackage_path = entry_path
            
            # Check if it's a module (.py file)
            elif entry.is_file() and entry_name.endswith(".py") and not entry_name.startswith("__"):
                module_name = entry_name[:-3]  # Remove .py
                qualified_name = f"{package_name}.{module_name}"
                
                submodule_info = SubpackageInfo(
                    name=module_name,
                    qualified_name=qualified_name,
                    path=entry_path,
                    depth=current_depth + 1,
                    is_package=False,
                )
                
                submodule_info.size_info = calculate_path_size(
                    entry_path,
                    follow_symlinks=follow_symlinks,
                    exclude_patterns=exclude_patterns,
                )
                
                info.children.append(submodule_info)
                info.size_info.add(submodule_info.size_info)
                accounted_files.add(entry_path)
            
            # Recurse into subpackages
            if is_package and subpackage_path:
                qualified_name = f"{package_name}.{entry_name}"
                
                subpackage_info = enumerate_subpackages(
                    subpackage_path,
                    qualified_name,
                    max_depth=max_depth,
                    current_depth=current_depth + 1,
                    follow_symlinks=follow_symlinks,
                    exclude_patterns=exclude_patterns,
                )
                
                info.children.append(subpackage_info)
                info.size_info.add(subpackage_info.size_info)
                
                # Mark all files in this subpackage as accounted
                accounted_files.add(subpackage_path)
    
    except (OSError, PermissionError):
        pass
    
    # Add any remaining files in this directory (non-Python files, __init__.py, etc.)
    try:
        for entry in os.scandir(package_path):
            entry_path = Path(entry.path)
            
            if entry_path not in accounted_files:
                # Don't recurse, just add the size
                file_size_info = calculate_path_size(
                    entry_path,
                    follow_symlinks=follow_symlinks,
                    exclude_patterns=exclude_patterns,
                )
                info.size_info.add(file_size_info)
    
    except (OSError, PermissionError):
        pass
    
    return info


def find_top_level_packages(
    site_packages: Path,
    top_level_names: list[str],
) -> list[Path]:
    """
    Find the paths to top-level packages/modules.
    
    Args:
        site_packages: Path to site-packages directory
        top_level_names: List of top-level module/package names
    
    Returns:
        List of paths to top-level packages/modules
    """
    paths: list[Path] = []
    
    for name in top_level_names:
        # Check for package (directory with __init__.py)
        package_dir = site_packages / name
        if package_dir.is_dir() and (package_dir / "__init__.py").exists():
            paths.append(package_dir)
            continue
        
        # Check for module (.py file)
        module_file = site_packages / f"{name}.py"
        if module_file.is_file():
            paths.append(module_file)
            continue
        
        # Check for other extensions (.so, .pyd, etc.)
        for ext in [".so", ".pyd", ".dylib"]:
            ext_file = site_packages / f"{name}{ext}"
            if ext_file.exists():
                paths.append(ext_file)
                break
    
    return paths


def enumerate_distribution_subpackages(
    site_packages: Path,
    top_level_names: list[str],
    max_depth: Optional[int] = None,
    follow_symlinks: bool = False,
    exclude_patterns: Optional[list[str]] = None,
) -> list[SubpackageInfo]:
    """
    Enumerate all subpackages for a distribution.
    
    Args:
        site_packages: Path to site-packages directory
        top_level_names: List of top-level module/package names
        max_depth: Maximum depth to traverse (None = unlimited)
        follow_symlinks: Whether to follow symbolic links
        exclude_patterns: List of glob patterns to exclude
    
    Returns:
        List of SubpackageInfo objects for each top-level package/module
    """
    results: list[SubpackageInfo] = []
    
    paths = find_top_level_packages(site_packages, top_level_names)
    
    for path in paths:
        name = path.stem if path.is_file() else path.name
        
        subpackage_info = enumerate_subpackages(
            path,
            name,
            max_depth=max_depth,
            current_depth=0,
            follow_symlinks=follow_symlinks,
            exclude_patterns=exclude_patterns,
        )
        
        results.append(subpackage_info)
    
    return results

