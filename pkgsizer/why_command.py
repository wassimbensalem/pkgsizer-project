"""Why command - trace why a package is installed."""

from pathlib import Path
from typing import Optional

from pkgsizer.dist_metadata import enumerate_distributions
from pkgsizer.graph import build_dependency_graph
from pkgsizer.env_locator import locate_site_packages


class DependencyPath:
    """Represents a path from root to target package."""
    
    def __init__(self, packages: list[str], sizes: list[int]):
        self.packages = packages  # List of package names in path
        self.sizes = sizes  # Size of each package
        self.total_size = sum(sizes)
    
    def __repr__(self) -> str:
        return f"Path({' → '.join(self.packages)})"


def find_all_paths_to_package(
    target_package: str,
    graph: dict,
    distributions: dict,
    max_paths: int = 20,
) -> list[DependencyPath]:
    """
    Find all dependency paths from root packages to target package.
    
    Args:
        target_package: Package name to find paths to
        graph: Dependency graph (from build_dependency_graph)
        distributions: Dictionary of all distributions
        max_paths: Maximum number of paths to find (prevents infinite loops)
    
    Returns:
        List of DependencyPath objects
    """
    target_lower = target_package.lower()
    
    if target_lower not in graph:
        return []
    
    # Find all root packages (depth 0)
    roots = [name for name, node in graph.items() if node.depth == 0]
    
    paths = []
    
    # Cache for package sizes
    size_cache = {}
    
    def get_package_size(pkg_name: str) -> int:
        """Get package size in bytes (cached)."""
        if pkg_name in size_cache:
            return size_cache[pkg_name]
        
        dist = distributions.get(pkg_name.lower())
        if not dist or not dist.files:
            size_cache[pkg_name] = 0
            return 0
        
        total = 0
        seen_inodes = set()
        for file_path in dist.files:
            try:
                if file_path.exists():
                    stat = file_path.stat()
                    inode_key = (stat.st_dev, stat.st_ino)
                    if inode_key not in seen_inodes:
                        seen_inodes.add(inode_key)
                        total += stat.st_size
            except (OSError, PermissionError):
                pass
        
        size_cache[pkg_name] = total
        return total
    
    def find_paths_dfs(current: str, path: list[str], sizes: list[int], visited: set[str]):
        """DFS to find all paths to target."""
        # Stop if we've found enough paths
        if len(paths) >= max_paths:
            return
        
        # Check if we found the target
        if current == target_lower:
            # Found a path!
            paths.append(DependencyPath(path + [current], sizes + [get_package_size(current)]))
            return
        
        # Prevent cycles
        if current in visited:
            return
        
        # Prevent too deep searches (max depth 10)
        if len(path) >= 10:
            return
        
        # Get current node
        node = graph.get(current)
        if not node:
            return
        
        # Mark as visited for this path
        visited.add(current)
        
        # Check dependencies
        for dep_node in node.dependencies:
            dep_name = dep_node.dist_info.name.lower()
            # Create new visited set for this branch
            new_visited = visited.copy()
            find_paths_dfs(
                dep_name,
                path + [current],
                sizes + [get_package_size(current)],
                new_visited
            )
        
        # Backtrack: remove from visited after exploring all branches
        visited.discard(current)
    
    # Search from each root
    for root in roots:
        if len(paths) >= max_paths:
            break
        find_paths_dfs(root, [], [], set())
    
    return paths


def analyze_why_package(
    package_name: str,
    site_packages_path: Path,
) -> dict:
    """
    Analyze why a package is installed.
    
    Args:
        package_name: Package name to analyze
        site_packages_path: Path to site-packages
    
    Returns:
        Dictionary with analysis results
    """
    # Enumerate distributions
    distributions = enumerate_distributions(site_packages_path)
    
    # Check if package exists
    pkg_lower = package_name.lower()
    if pkg_lower not in distributions:
        return {
            "found": False,
            "package": package_name,
            "error": "Package not found in environment",
        }
    
    # Get package info
    pkg_dist = distributions[pkg_lower]
    
    # Find direct dependents (packages that list this as a requirement)
    dependents = []
    for name, dist in distributions.items():
        if name == pkg_lower:
            continue
        # Check if this package requires our target
        if dist.requires:
            for req in dist.requires:
                # Parse requirement (e.g., "numpy>=1.0" -> "numpy")
                req_name = req.split('[')[0].split('>=')[0].split('<=')[0].split('==')[0].split('!=')[0].split('~=')[0].split('>')[0].split('<')[0].strip()
                if req_name.lower() == pkg_lower:
                    dependents.append(name)
                    break
    
    # Determine if it's a direct dependency (not required by anything)
    is_direct = len(dependents) == 0
    
    # For simplicity, use a basic depth calculation
    # If no dependents, depth = 0; otherwise depth = 1+
    depth = 0 if is_direct else 1
    
    # Calculate package size
    pkg_size = 0
    if pkg_dist.files:
        seen_inodes = set()
        for file_path in pkg_dist.files:
            try:
                if file_path.exists():
                    stat = file_path.stat()
                    inode_key = (stat.st_dev, stat.st_ino)
                    if inode_key not in seen_inodes:
                        seen_inodes.add(inode_key)
                        pkg_size += stat.st_size
            except (OSError, PermissionError):
                pass
    
    # Only build graph and find paths if it's not a direct dependency
    paths = []
    if not is_direct:
        try:
            # Build limited dependency graph with timeout protection
            # Only build from packages that depend on this one
            graph = build_dependency_graph(distributions, target_packages=None, max_depth=5)
            paths = find_all_paths_to_package(package_name, graph, distributions, max_paths=10)
        except Exception:
            # If graph building fails, continue with simple analysis
            paths = []
    
    return {
        "found": True,
        "package": package_name,
        "version": pkg_dist.version,
        "size": pkg_size,
        "is_direct": is_direct,
        "depth": depth,
        "paths": paths,
        "dependents": dependents,
        "editable": pkg_dist.editable,
        "location": str(pkg_dist.location),
    }

