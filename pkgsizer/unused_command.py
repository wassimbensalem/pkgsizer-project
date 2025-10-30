"""Unused command - find dependencies that are never imported."""

import ast
import os
from pathlib import Path
from typing import Optional, Set

from pkgsizer.dist_metadata import enumerate_distributions
from pkgsizer.env_locator import locate_site_packages


def extract_imports_from_file(file_path: Path) -> Set[str]:
    """
    Extract all import statements from a Python file.
    
    Args:
        file_path: Path to Python file
    
    Returns:
        Set of imported module names
    """
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Extract top-level module
                    module = alias.name.split('.')[0]
                    imports.add(module)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Extract top-level module
                    module = node.module.split('.')[0]
                    imports.add(module)
    
    except (SyntaxError, UnicodeDecodeError):
        # Skip files with syntax errors or encoding issues
        pass
    
    return imports


def scan_codebase_for_imports(
    code_path: Path,
    exclude_patterns: Optional[list[str]] = None,
) -> Set[str]:
    """
    Scan entire codebase for import statements.
    
    Args:
        code_path: Path to code directory
        exclude_patterns: Patterns to exclude (e.g., ['test_', '__pycache__'])
    
    Returns:
        Set of all imported module names
    """
    if exclude_patterns is None:
        exclude_patterns = [
            '__pycache__',
            '.git',
            '.tox',
            '.nox',
            'venv',
            'env',
            '.venv',
            'node_modules',
            'build',
            'dist',
            '*.egg-info',
        ]
    
    all_imports = set()
    
    # Walk through all Python files
    for root, dirs, files in os.walk(code_path):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if not any(
            pattern in d or d.startswith('.') 
            for pattern in exclude_patterns
        )]
        
        for file in files:
            if file.endswith('.py'):
                # Check if file matches exclude pattern
                if any(pattern in file for pattern in exclude_patterns if pattern.startswith('*')):
                    continue
                
                file_path = Path(root) / file
                imports = extract_imports_from_file(file_path)
                all_imports.update(imports)
    
    return all_imports


def analyze_unused_dependencies(
    site_packages_path: Path,
    code_path: Optional[Path] = None,
    include_dev: bool = False,
) -> dict:
    """
    Analyze which dependencies are unused.
    
    Args:
        site_packages_path: Path to site-packages
        code_path: Path to code to scan (None = skip code scanning)
        include_dev: Include dev dependencies in analysis
    
    Returns:
        Dictionary with analysis results
    """
    # Enumerate distributions
    distributions = enumerate_distributions(site_packages_path)
    
    # Get all installed packages and their top-level modules
    installed_packages = {}
    for name, dist_info in distributions.items():
        top_level = dist_info.top_level if dist_info.top_level else [name]
        installed_packages[name] = {
            "top_level": top_level,
            "version": dist_info.version,
            "size": 0,  # Will calculate if needed
            "files": len(dist_info.files) if dist_info.files else 0,
        }
    
    # Scan code for imports if path provided
    imported_modules = set()
    if code_path and code_path.exists():
        imported_modules = scan_codebase_for_imports(code_path)
    
    # Categorize packages
    used_packages = []
    unused_packages = []
    uncertain_packages = []
    
    for pkg_name, pkg_info in installed_packages.items():
        top_level_modules = pkg_info["top_level"]
        
        # Check if any top-level module is imported
        is_used = any(module in imported_modules for module in top_level_modules)
        
        # Some packages have different import names than package names
        # Also check the package name itself
        if not is_used:
            is_used = pkg_name.replace('-', '_') in imported_modules or pkg_name in imported_modules
        
        if code_path is None:
            # Can't determine without code scanning
            uncertain_packages.append(pkg_name)
        elif is_used:
            used_packages.append(pkg_name)
        else:
            unused_packages.append(pkg_name)
    
    return {
        "total_packages": len(installed_packages),
        "used": used_packages,
        "unused": unused_packages,
        "uncertain": uncertain_packages,
        "imported_modules": list(imported_modules) if code_path else [],
        "code_scanned": code_path is not None,
        "packages_info": installed_packages,
    }


def calculate_unused_size(
    unused_packages: list[str],
    distributions: dict,
) -> int:
    """Calculate total size of unused packages."""
    total_size = 0
    
    for pkg_name in unused_packages:
        dist = distributions.get(pkg_name.lower())
        if dist and dist.files:
            seen_inodes = set()
            for file_path in dist.files:
                try:
                    if file_path.exists():
                        stat = file_path.stat()
                        inode_key = (stat.st_dev, stat.st_ino)
                        if inode_key not in seen_inodes:
                            seen_inodes.add(inode_key)
                            total_size += stat.st_size
                except (OSError, PermissionError):
                    pass
    
    return total_size

