"""Render reports in various formats."""

import json
import sys
from pathlib import Path
from typing import Optional, Any

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from pkgsizer.scanner import ScanResults, PackageResult
from pkgsizer.subpackages import SubpackageInfo


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def parse_size_threshold(threshold: str) -> int:
    """Parse a size threshold string like '1GB' to bytes."""
    threshold = threshold.strip().upper()
    
    multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
    }
    
    for unit, multiplier in multipliers.items():
        if threshold.endswith(unit):
            try:
                value = float(threshold[:-len(unit)])
                return int(value * multiplier)
            except ValueError:
                pass
    
    # Try to parse as plain number (bytes)
    try:
        return int(threshold)
    except ValueError:
        raise ValueError(f"Invalid size threshold: {threshold}")


def _traverse_tree_order(packages: list[PackageResult]) -> list[PackageResult]:
    """
    Traverse packages in tree order (depth-first, parent before children).
    
    Args:
        packages: List of package results
    
    Returns:
        List of packages in tree order
    """
    # Build map for quick lookup
    pkg_map = {pkg.dist_info.name.lower(): pkg for pkg in packages}
    visited = set()
    result = []
    
    def visit(pkg: PackageResult, visited_set: set) -> None:
        """Recursively visit package and its dependencies."""
        pkg_key = pkg.dist_info.name.lower()
        if pkg_key in visited_set:
            return
        
        visited_set.add(pkg_key)
        result.append(pkg)
        
        # Visit dependencies in order
        for dep_node in pkg.node.dependencies:
            dep_name = dep_node.dist_info.name.lower()
            if dep_name in pkg_map and dep_name not in visited_set:
                visit(pkg_map[dep_name], visited_set)
    
    # Start with root packages (depth 0)
    roots = [pkg for pkg in packages if pkg.node.depth == 0]
    roots.sort(key=lambda p: p.total_size, reverse=True)
    
    for root in roots:
        visit(root, visited)
    
    # Add any remaining packages (shouldn't happen, but safety)
    for pkg in packages:
        if pkg.dist_info.name.lower() not in visited:
            result.append(pkg)
    
    return result


def render_table(
    results: ScanResults,
    console: Console,
    top: Optional[int] = None,
    sort_by: str = "size",
    show_tree: bool = False,
    include_dependencies: bool = False,
) -> None:
    """
    Render results as a table.
    
    Args:
        results: Scan results
        console: Rich console
        top: Show only top N packages
        sort_by: Sort by "size" or "files"
        show_tree: Show dependency tree
        include_dependencies: Show package with dependencies included
    """
    # Check if we need to show dependency tree structure
    show_chains = any(pkg.node.depth > 0 for pkg in results.packages)
    
    if show_chains:
        # Use tree order when showing dependencies
        packages = _traverse_tree_order(results.packages)
    else:
        # Sort by size or files when not showing tree
        if sort_by == "size":
            packages = sorted(results.packages, key=lambda p: p.total_size, reverse=True)
        else:  # files
            packages = sorted(results.packages, key=lambda p: p.file_count, reverse=True)
    
    # Limit to top N (after tree ordering for context)
    if top and not show_chains:
        packages = packages[:top]
    
    # Find parent packages if showing chains
    parents = {}
    if show_chains:
        parents = _find_parent_packages(results.packages)
    
    # Create table with improved styling
    table = Table(
        title="📦 Package Size Analysis",
        title_style="bold cyan",
        show_header=True,
        header_style="bold white on blue",
        border_style="blue",
        padding=(0, 1),
    )
    
    # Adjust package column width based on whether we're showing tree structure
    pkg_col_width = 35 if show_chains else 25
    
    table.add_column("Package", style="cyan bold", no_wrap=False, width=pkg_col_width)
    table.add_column("Version", style="magenta", width=12)
    table.add_column("Size", justify="right", style="green bold", width=12)
    
    if include_dependencies:
        table.add_column("With Deps", justify="right", style="yellow bold", width=12)
    
    table.add_column("Files", justify="right", style="blue", width=8)
    table.add_column("Depth", justify="right", style="yellow", width=7)
    
    # Add dependency chain column if any package has depth > 0
    if show_chains:
        table.add_column("From", style="dim italic", width=25)
    
    table.add_column("Type", style="white", width=11)
    table.add_column("Editable", justify="center", style="dim", width=8, header_style="dim")
    
    # Calculate dependency sizes if requested
    dep_sizes = {}
    if include_dependencies:
        dep_sizes = _calculate_dependency_sizes(results.packages)
    
    for pkg_result in packages:
        dist_info = pkg_result.dist_info
        node = pkg_result.node
        
        type_str = "📍 direct" if node.direct else "🔗 transitive"
        editable_str = "✏️" if dist_info.editable else ""
        
        # Create tree-style indentation based on depth
        indent = "  " * node.depth
        tree_prefix = ""
        if node.depth > 0:
            tree_prefix = "└─ " if node.depth > 0 else ""
        
        # Package name with tree structure
        pkg_name_display = f"{indent}{tree_prefix}{dist_info.name}"
        
        row_data = [
            pkg_name_display,
            dist_info.version,
            format_size(pkg_result.total_size),
        ]
        
        if include_dependencies:
            dep_size = dep_sizes.get(dist_info.name.lower(), pkg_result.total_size)
            row_data.append(format_size(dep_size))
        
        row_data.append(str(pkg_result.file_count))
        row_data.append(str(node.depth))
        
        # Add dependency chain if showing
        if show_chains:
            chain = _format_dependency_chain(dist_info.name, parents, node.depth)
            row_data.append(chain if chain else "")
        
        row_data.append(type_str)
        
        # Only show editable icon if package is actually editable
        if dist_info.editable:
            row_data.append(editable_str)
        else:
            row_data.append("")
        
        table.add_row(*row_data)
    
    console.print()
    console.print(table)
    console.print()
    
    # Print enhanced summary with visual separators
    console.print("─" * 60, style="dim")
    console.print()
    
    # Summary statistics
    from rich.panel import Panel
    from rich.columns import Columns
    
    summary_items = []
    summary_items.append(
        Panel(
            f"[bold cyan]{len(results.packages)}[/bold cyan]",
            title="📦 Packages",
            border_style="cyan",
            padding=(0, 2),
        )
    )
    summary_items.append(
        Panel(
            f"[bold green]{format_size(results.total_size)}[/bold green]",
            title="💾 Total Size",
            border_style="green",
            padding=(0, 2),
        )
    )
    summary_items.append(
        Panel(
            f"[bold blue]{results.total_files:,}[/bold blue]",
            title="📄 Files",
            border_style="blue",
            padding=(0, 2),
        )
    )
    
    if include_dependencies:
        total_with_deps = sum(dep_sizes.values())
        summary_items.append(
            Panel(
                f"[bold yellow]{format_size(total_with_deps)}[/bold yellow]",
                title="🔗 With Deps",
                border_style="yellow",
                padding=(0, 2),
            )
        )
    
    console.print(Columns(summary_items, equal=True, expand=True))
    console.print()
    console.print("─" * 60, style="dim")
    
    # Show tree if requested
    if show_tree and packages:
        console.print()
        console.print("🌳 [bold cyan]Package Structure:[/bold cyan]")
        console.print()
        
        # Build tree for top packages
        display_count = min(10, len(packages))
        for i, pkg_result in enumerate(packages[:display_count], 1):
            tree = build_dependency_tree(pkg_result, include_dependencies)
            console.print(tree)
            if i < display_count:
                console.print()


def _calculate_dependency_sizes(packages: list[PackageResult]) -> dict[str, int]:
    """
    Calculate cumulative sizes including dependencies.
    
    Args:
        packages: List of package results
    
    Returns:
        Dictionary mapping package name to size with dependencies
    """
    # Build dependency map
    pkg_map = {pkg.dist_info.name.lower(): pkg for pkg in packages}
    dep_sizes = {}
    
    def get_total_size(pkg_name: str, visited: set[str]) -> int:
        """Recursively calculate size including dependencies."""
        pkg_name_lower = pkg_name.lower()
        
        if pkg_name_lower in visited:
            return 0  # Avoid cycles
        
        if pkg_name_lower in dep_sizes:
            return dep_sizes[pkg_name_lower]
        
        visited.add(pkg_name_lower)
        
        if pkg_name_lower not in pkg_map:
            return 0
        
        pkg = pkg_map[pkg_name_lower]
        total = pkg.total_size
        
        # Add dependency sizes
        for dep_node in pkg.node.dependencies:
            dep_name = dep_node.dist_info.name
            total += get_total_size(dep_name, visited.copy())
        
        dep_sizes[pkg_name_lower] = total
        return total
    
    # Calculate for all packages
    for pkg in packages:
        if pkg.dist_info.name.lower() not in dep_sizes:
            get_total_size(pkg.dist_info.name, set())
    
    return dep_sizes


def _find_parent_packages(packages: list[PackageResult]) -> dict[str, list[str]]:
    """
    Find parent packages (which packages depend on this one).
    
    Args:
        packages: List of package results
    
    Returns:
        Dictionary mapping package name to list of parent package names
    """
    parents: dict[str, list[str]] = {}
    
    # Initialize all packages
    for pkg in packages:
        parents[pkg.dist_info.name.lower()] = []
    
    # Build reverse dependency map
    for pkg in packages:
        pkg_name = pkg.dist_info.name.lower()
        for dep_node in pkg.node.dependencies:
            dep_name = dep_node.dist_info.name.lower()
            if dep_name in parents:
                parents[dep_name].append(pkg_name)
    
    return parents


def _format_dependency_chain(pkg_name: str, parents: dict[str, list[str]], depth: int) -> str:
    """
    Format the dependency chain showing where a package comes from.
    
    Args:
        pkg_name: Package name
        parents: Dictionary of parent packages
        depth: Current depth in dependency tree
    
    Returns:
        Formatted string showing the chain
    """
    pkg_name_lower = pkg_name.lower()
    
    if depth == 0:
        # Direct dependency - no chain needed
        return ""
    
    parent_list = parents.get(pkg_name_lower, [])
    
    if not parent_list:
        return ""
    
    # Show primary parent (first one that depends on this)
    primary_parent = parent_list[0]
    
    if len(parent_list) == 1:
        return f"[dim]← {primary_parent}[/dim]"
    else:
        # Multiple parents
        return f"[dim]← {primary_parent} (+{len(parent_list)-1} more)[/dim]"


def build_dependency_tree(pkg_result: PackageResult, show_deps: bool = False) -> Tree:
    """Build a Rich Tree for a package's subpackages and dependencies."""
    dist_info = pkg_result.dist_info
    
    # Create root with emojis based on type
    pkg_icon = "📦" if pkg_result.node.direct else "🔗"
    edit_icon = " ✏️" if dist_info.editable else ""
    label = f"{pkg_icon} [bold cyan]{dist_info.name}[/bold cyan] [magenta]{dist_info.version}[/magenta]{edit_icon} [green]({format_size(pkg_result.total_size)})[/green]"
    tree = Tree(label)
    
    # Add subpackages if available
    if pkg_result.subpackages:
        # Sort by size
        sorted_subpkgs = sorted(
            pkg_result.subpackages,
            key=lambda s: s.size_info.size_bytes,
            reverse=True
        )
        
        for subpkg in sorted_subpkgs[:10]:  # Limit to top 10
            _add_subpackage_tree(tree, subpkg, depth=0, max_depth=2)
    
    # Add dependencies if requested
    if show_deps and pkg_result.node.dependencies:
        deps_branch = tree.add("🔗 [bold yellow]Dependencies[/bold yellow]")
        for dep_node in pkg_result.node.dependencies[:5]:  # Top 5 deps
            dep_pkg = next(
                (p for p in [pkg_result] if p.dist_info.name == dep_node.dist_info.name),
                None
            )
            if dep_pkg:
                dep_label = f"[cyan]{dep_node.dist_info.name}[/cyan] [dim]({format_size(dep_pkg.total_size)})[/dim]"
            else:
                dep_label = f"[cyan]{dep_node.dist_info.name}[/cyan]"
            deps_branch.add(dep_label)
    
    return tree


def _add_subpackage_tree(parent: Tree, subpkg: SubpackageInfo, depth: int, max_depth: int) -> None:
    """Recursively add subpackage nodes to tree."""
    if depth >= max_depth:
        return
    
    # Icon based on whether it's a package or module
    icon = "📁" if subpkg.is_package else "📄"
    
    # Format size with percentage if we have parent info
    size_str = format_size(subpkg.size_info.size_bytes)
    
    # Color based on size
    if subpkg.size_info.size_bytes > 10 * 1024 * 1024:  # > 10 MB
        color = "red"
    elif subpkg.size_info.size_bytes > 1 * 1024 * 1024:  # > 1 MB
        color = "yellow"
    else:
        color = "green"
    
    label = f"{icon} [white]{subpkg.name}[/white] [{color}]({size_str})[/{color}] [dim]{subpkg.size_info.file_count} files[/dim]"
    branch = parent.add(label)
    
    # Add children
    if subpkg.children:
        sorted_children = sorted(
            subpkg.children,
            key=lambda c: c.size_info.size_bytes,
            reverse=True
        )
        for child in sorted_children[:5]:  # Top 5 children
            _add_subpackage_tree(branch, child, depth + 1, max_depth)


def to_json(results: ScanResults) -> dict[str, Any]:
    """
    Convert results to JSON-serializable format.
    
    Args:
        results: Scan results
    
    Returns:
        Dictionary in JSON schema format
    """
    packages_data = []
    
    for pkg_result in results.packages:
        dist_info = pkg_result.dist_info
        node = pkg_result.node
        
        pkg_data = {
            "name": dist_info.name,
            "version": dist_info.version,
            "size_bytes": pkg_result.total_size,
            "file_count": pkg_result.file_count,
            "depth": node.depth,
            "direct": node.direct,
            "editable": dist_info.editable,
            "location": str(dist_info.location),
        }
        
        if dist_info.editable and dist_info.editable_location:
            pkg_data["editable_location"] = str(dist_info.editable_location)
        
        # Add subpackages
        if pkg_result.subpackages:
            pkg_data["subpackages"] = [
                subpackage_to_json(subpkg) for subpkg in pkg_result.subpackages
            ]
        
        packages_data.append(pkg_data)
    
    return {
        "version": "1.0",
        "site_packages": str(results.site_packages_path) if results.site_packages_path else None,
        "total_size_bytes": results.total_size,
        "total_files": results.total_files,
        "package_count": len(results.packages),
        "packages": packages_data,
    }


def subpackage_to_json(subpkg: SubpackageInfo) -> dict[str, Any]:
    """Convert a SubpackageInfo to JSON format."""
    data = {
        "name": subpkg.name,
        "qualified_name": subpkg.qualified_name,
        "path": str(subpkg.path),
        "depth": subpkg.depth,
        "is_package": subpkg.is_package,
        "size_bytes": subpkg.size_info.size_bytes,
        "file_count": subpkg.size_info.file_count,
    }
    
    if subpkg.children:
        data["children"] = [subpackage_to_json(child) for child in subpkg.children]
    
    return data


def render_report(
    results: ScanResults,
    json_output: Optional[Path],
    tree: bool,
    group_by: str,
    top: Optional[int],
    sort_by: str,
    fail_over: Optional[str],
    console: Console,
    include_dependencies: bool = False,
) -> int:
    """
    Render the final report.
    
    Args:
        results: Scan results
        json_output: Path to output JSON (or "-" for stdout)
        tree: Show tree view
        group_by: Group by "dist", "module", or "file"
        top: Show only top N packages
        sort_by: Sort by "size" or "files"
        fail_over: Fail if total size exceeds threshold
        console: Rich console
        include_dependencies: Include dependency sizes in totals
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    # Check fail_over threshold
    exit_code = 0
    if fail_over:
        try:
            threshold_bytes = parse_size_threshold(fail_over)
            if results.total_size > threshold_bytes:
                console.print(
                    f"[red]Error:[/red] Total size {format_size(results.total_size)} "
                    f"exceeds threshold {format_size(threshold_bytes)}"
                )
                exit_code = 1
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            exit_code = 1
    
    # Output JSON if requested
    if json_output:
        json_data = to_json(results)
        json_str = json.dumps(json_data, indent=2)
        
        if str(json_output) == "-":
            console.print(json_str)
        else:
            with open(json_output, "w") as f:
                f.write(json_str)
            console.print(f"[dim]JSON output written to:[/dim] {json_output}")
    
    # Render table (unless JSON to stdout)
    if not json_output or str(json_output) != "-":
        render_table(results, console, top, sort_by, tree, include_dependencies)
    
    return exit_code

