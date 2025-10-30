"""Build and traverse dependency graphs."""

from collections import deque
from typing import Optional

from pkgsizer.dist_metadata import DistributionInfo, get_dependencies


class DependencyNode:
    """A node in the dependency graph."""
    
    def __init__(self, dist_info: DistributionInfo, depth: int = 0, direct: bool = True):
        self.dist_info = dist_info
        self.depth = depth
        self.direct = direct
        self.dependencies: list[DependencyNode] = []
    
    def __repr__(self) -> str:
        return f"DependencyNode({self.dist_info.name}, depth={self.depth}, direct={self.direct})"


def build_dependency_graph(
    distributions: dict[str, DistributionInfo],
    target_packages: Optional[list[str]] = None,
    max_depth: Optional[int] = None,
) -> dict[str, DependencyNode]:
    """
    Build a dependency graph from distributions.
    
    Args:
        distributions: Dictionary of all available distributions
        target_packages: Optional list of package names to start from (if None, use all)
        max_depth: Maximum depth to traverse (None = unlimited)
    
    Returns:
        Dictionary mapping package name to DependencyNode
    """
    # Determine root packages
    if target_packages:
        roots = [name.lower() for name in target_packages if name.lower() in distributions]
    else:
        roots = list(distributions.keys())
    
    result: dict[str, DependencyNode] = {}
    visited: dict[str, int] = {}  # Track minimum depth seen for each package
    
    # BFS to build graph
    queue: deque[tuple[str, int, bool]] = deque()
    
    # Initialize with roots
    for root in roots:
        queue.append((root, 0, True))
        visited[root] = 0
    
    while queue:
        pkg_name, depth, is_direct = queue.popleft()
        
        # Skip if max depth exceeded
        if max_depth is not None and depth > max_depth:
            continue
        
        # Get distribution
        dist_info = distributions.get(pkg_name)
        if not dist_info:
            continue
        
        # Create or update node
        if pkg_name not in result:
            node = DependencyNode(dist_info, depth, is_direct)
            result[pkg_name] = node
        else:
            # Update if we found a shorter path
            if depth < result[pkg_name].depth:
                result[pkg_name].depth = depth
                result[pkg_name].direct = is_direct
        
        # Get dependencies
        deps = get_dependencies(dist_info)
        
        for dep_name in deps:
            dep_name_lower = dep_name.lower()
            
            # Skip if not in distributions
            if dep_name_lower not in distributions:
                continue
            
            # Check if we should visit this dependency
            new_depth = depth + 1
            should_visit = False
            
            if dep_name_lower not in visited:
                should_visit = True
                visited[dep_name_lower] = new_depth
            elif new_depth < visited[dep_name_lower]:
                should_visit = True
                visited[dep_name_lower] = new_depth
            
            # Add to queue if we should visit
            if should_visit and (max_depth is None or new_depth <= max_depth):
                queue.append((dep_name_lower, new_depth, False))
    
    # Build dependency relationships
    for pkg_name, node in result.items():
        deps = get_dependencies(node.dist_info)
        for dep_name in deps:
            dep_name_lower = dep_name.lower()
            if dep_name_lower in result:
                node.dependencies.append(result[dep_name_lower])
    
    return result


def get_all_dependencies(
    distributions: dict[str, DistributionInfo],
    package_names: list[str],
    max_depth: Optional[int] = None,
) -> set[str]:
    """
    Get all transitive dependencies for a list of packages.
    
    Args:
        distributions: Dictionary of all available distributions
        package_names: List of package names to start from
        max_depth: Maximum depth to traverse (None = unlimited)
    
    Returns:
        Set of all package names (including the originals)
    """
    graph = build_dependency_graph(distributions, package_names, max_depth)
    return set(graph.keys())

