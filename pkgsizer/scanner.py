"""Main scanner that coordinates all analysis."""

from pathlib import Path
from typing import Optional

from pkgsizer.dist_metadata import enumerate_distributions, DistributionInfo
from pkgsizer.graph import build_dependency_graph, DependencyNode
from pkgsizer.size_calc import calculate_distribution_size, calculate_editable_size
from pkgsizer.subpackages import enumerate_distribution_subpackages, SubpackageInfo


class PackageResult:
    """Result for a single package."""
    
    def __init__(
        self,
        dist_info: DistributionInfo,
        node: DependencyNode,
        total_size: int,
        file_count: int,
        subpackages: Optional[list[SubpackageInfo]] = None,
    ):
        self.dist_info = dist_info
        self.node = node
        self.total_size = total_size
        self.file_count = file_count
        self.subpackages = subpackages or []
    
    def __repr__(self) -> str:
        return f"PackageResult({self.dist_info.name}, size={self.total_size})"


class ScanResults:
    """Results from scanning an environment."""
    
    def __init__(self):
        self.packages: list[PackageResult] = []
        self.total_size: int = 0
        self.total_files: int = 0
        self.site_packages_path: Optional[Path] = None
    
    def add_package(self, result: PackageResult) -> None:
        """Add a package result."""
        self.packages.append(result)
        self.total_size += result.total_size
        self.total_files += result.file_count


def scan_environment(
    site_packages_path: Path,
    depth: Optional[int] = None,
    module_depth: Optional[int] = None,
    include_editable: str = "mark",
    exclude_patterns: Optional[list[str]] = None,
    follow_symlinks: bool = False,
    target_packages: Optional[list[str]] = None,
) -> ScanResults:
    """
    Scan a Python environment and measure package sizes.
    
    Args:
        site_packages_path: Path to site-packages directory
        depth: Maximum dependency graph depth (None = unlimited)
        module_depth: Maximum module subpackage depth (None = unlimited)
        include_editable: How to handle editable installs ("mark", "include", "exclude")
        exclude_patterns: List of glob patterns to exclude
        follow_symlinks: Whether to follow symbolic links
        target_packages: Optional list of specific packages to analyze
    
    Returns:
        ScanResults object
    """
    results = ScanResults()
    results.site_packages_path = site_packages_path
    
    # Enumerate all distributions
    distributions = enumerate_distributions(site_packages_path)
    
    if not distributions:
        return results
    
    # Build dependency graph
    graph = build_dependency_graph(distributions, target_packages, depth)
    
    # Process each package in the graph
    for pkg_name, node in graph.items():
        dist_info = node.dist_info
        
        # Handle editable installs
        if dist_info.editable:
            if include_editable == "exclude":
                continue
        
        # Calculate size
        if dist_info.editable and dist_info.editable_location:
            # For editable installs, calculate size from source location
            size_info = calculate_editable_size(
                dist_info.editable_location,
                follow_symlinks=follow_symlinks,
                exclude_patterns=exclude_patterns,
            )
        else:
            # For regular installs, use RECORD files
            size_info = calculate_distribution_size(
                dist_info.files,
                follow_symlinks=follow_symlinks,
                exclude_patterns=exclude_patterns,
            )
        
        # Enumerate subpackages if requested
        subpackages: list[SubpackageInfo] = []
        if module_depth is not None or module_depth != 0:
            if dist_info.top_level:
                subpackages = enumerate_distribution_subpackages(
                    site_packages_path,
                    dist_info.top_level,
                    max_depth=module_depth,
                    follow_symlinks=follow_symlinks,
                    exclude_patterns=exclude_patterns,
                )
        
        # Create result
        package_result = PackageResult(
            dist_info=dist_info,
            node=node,
            total_size=size_info.size_bytes,
            file_count=size_info.file_count,
            subpackages=subpackages,
        )
        
        results.add_package(package_result)
    
    return results

