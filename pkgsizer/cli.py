"""CLI entry point for pkgsizer."""

import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from pkgsizer import __version__
from pkgsizer.env_locator import locate_site_packages
from pkgsizer.scanner import scan_environment
from pkgsizer.file_parsers import parse_dependency_file
from pkgsizer.report import render_report, format_size
from pkgsizer.why_command import analyze_why_package
from pkgsizer.unused_command import analyze_unused_dependencies, calculate_unused_size
from pkgsizer.dist_metadata import enumerate_distributions
from pkgsizer.alternatives import analyze_alternatives, get_all_known_alternatives
from pkgsizer.updates import check_updates
from pkgsizer.compare import compare_environments

app = typer.Typer(
    name="pkgsizer",
    help="Measure installed on-disk sizes of Python packages and their subpackages",
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"pkgsizer version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True,
                     help="Show version and exit"),
    ] = None,
) -> None:
    """Package size analyzer for Python packages and subpackages."""
    pass


@app.command(name="scan-env")
def scan_env(
    python: Annotated[
        Optional[Path],
        typer.Option(help="Path to Python interpreter"),
    ] = None,
    venv: Annotated[
        Optional[Path],
        typer.Option(help="Path to virtual environment"),
    ] = None,
    site_packages: Annotated[
        Optional[Path],
        typer.Option(help="Path to site-packages directory"),
    ] = None,
    depth: Annotated[
        Optional[int],
        typer.Option(help="Maximum dependency graph depth (None = unlimited)"),
    ] = None,
    module_depth: Annotated[
        Optional[int],
        typer.Option(help="Maximum module subpackage depth (None = unlimited)"),
    ] = None,
    include_editable: Annotated[
        str,
        typer.Option(help="How to handle editable installs: mark, include, exclude"),
    ] = "mark",
    json_output: Annotated[
        Optional[Path],
        typer.Option("--json", help="Output JSON to file (use '-' for stdout)"),
    ] = None,
    tree: Annotated[
        bool,
        typer.Option(help="Show tree view of packages"),
    ] = False,
    group_by: Annotated[
        str,
        typer.Option(help="Group results by: dist, module, file"),
    ] = "dist",
    exclude: Annotated[
        Optional[list[str]],
        typer.Option(help="Patterns to exclude (can be used multiple times)"),
    ] = None,
    top: Annotated[
        Optional[int],
        typer.Option(help="Show only top N packages by size"),
    ] = None,
    by: Annotated[
        str,
        typer.Option(help="Sort by: size, files"),
    ] = "size",
    follow_symlinks: Annotated[
        bool,
        typer.Option(help="Follow symbolic links when calculating sizes"),
    ] = False,
    fail_over: Annotated[
        Optional[str],
        typer.Option(help="Exit with error if total size exceeds threshold (e.g., '1GB')"),
    ] = None,
    packages: Annotated[
        Optional[list[str]],
        typer.Option("--package", "-p", help="Specific packages to analyze (can be used multiple times)"),
    ] = None,
    include_dependencies: Annotated[
        bool,
        typer.Option("--include-deps", help="Show cumulative size including dependencies"),
    ] = False,
) -> None:
    """Scan an installed Python environment and measure package sizes."""
    try:
        # Validate options
        if include_editable not in ("mark", "include", "exclude"):
            console.print(
                f"[red]Error:[/red] --include-editable must be one of: mark, include, exclude"
            )
            raise typer.Exit(1)

        if group_by not in ("dist", "module", "file"):
            console.print(
                f"[red]Error:[/red] --group-by must be one of: dist, module, file"
            )
            raise typer.Exit(1)

        if by not in ("size", "files"):
            console.print(
                f"[red]Error:[/red] --by must be one of: size, files"
            )
            raise typer.Exit(1)

        # Locate site-packages
        site_packages_path = locate_site_packages(
            python_path=python,
            venv_path=venv,
            site_packages_path=site_packages,
        )
        
        console.print(f"[dim]Scanning:[/dim] {site_packages_path}")

        # Scan environment
        results = scan_environment(
            site_packages_path=site_packages_path,
            depth=depth,
            module_depth=module_depth,
            include_editable=include_editable,
            exclude_patterns=exclude or [],
            follow_symlinks=follow_symlinks,
            target_packages=packages,
        )

        # Render report
        exit_code = render_report(
            results=results,
            json_output=json_output,
            tree=tree,
            group_by=group_by,
            top=top,
            sort_by=by,
            fail_over=fail_over,
            console=console,
            include_dependencies=include_dependencies,
        )

        raise typer.Exit(exit_code)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command(name="analyze-file")
def analyze_file(
    file_path: Annotated[
        Path,
        typer.Argument(help="Path to dependency file (requirements.txt, pyproject.toml, etc.)"),
    ],
    env_site_packages: Annotated[
        Optional[Path],
        typer.Option(help="Path to site-packages for size lookup"),
    ] = None,
    python: Annotated[
        Optional[Path],
        typer.Option(help="Path to Python interpreter (for site-packages lookup)"),
    ] = None,
    venv: Annotated[
        Optional[Path],
        typer.Option(help="Path to virtual environment (for site-packages lookup)"),
    ] = None,
    depth: Annotated[
        Optional[int],
        typer.Option(help="Maximum dependency graph depth (None = unlimited)"),
    ] = None,
    module_depth: Annotated[
        Optional[int],
        typer.Option(help="Maximum module subpackage depth (None = unlimited)"),
    ] = None,
    include_editable: Annotated[
        str,
        typer.Option(help="How to handle editable installs: mark, include, exclude"),
    ] = "mark",
    json_output: Annotated[
        Optional[Path],
        typer.Option("--json", help="Output JSON to file (use '-' for stdout)"),
    ] = None,
    tree: Annotated[
        bool,
        typer.Option(help="Show tree view of packages"),
    ] = False,
    group_by: Annotated[
        str,
        typer.Option(help="Group results by: dist, module, file"),
    ] = "dist",
    exclude: Annotated[
        Optional[list[str]],
        typer.Option(help="Patterns to exclude (can be used multiple times)"),
    ] = None,
    top: Annotated[
        Optional[int],
        typer.Option(help="Show only top N packages by size"),
    ] = None,
    by: Annotated[
        str,
        typer.Option(help="Sort by: size, files"),
    ] = "size",
    follow_symlinks: Annotated[
        bool,
        typer.Option(help="Follow symbolic links when calculating sizes"),
    ] = False,
    fail_over: Annotated[
        Optional[str],
        typer.Option(help="Exit with error if total size exceeds threshold (e.g., '1GB')"),
    ] = None,
    include_dependencies: Annotated[
        bool,
        typer.Option("--include-deps", help="Show cumulative size including dependencies"),
    ] = False,
) -> None:
    """Analyze a dependency file and measure package sizes from an environment."""
    try:
        # Validate options
        if include_editable not in ("mark", "include", "exclude"):
            console.print(
                f"[red]Error:[/red] --include-editable must be one of: mark, include, exclude"
            )
            raise typer.Exit(1)

        if group_by not in ("dist", "module", "file"):
            console.print(
                f"[red]Error:[/red] --group-by must be one of: dist, module, file"
            )
            raise typer.Exit(1)

        if by not in ("size", "files"):
            console.print(
                f"[red]Error:[/red] --by must be one of: size, files"
            )
            raise typer.Exit(1)

        if not file_path.exists():
            console.print(f"[red]Error:[/red] File not found: {file_path}")
            raise typer.Exit(1)

        # Locate site-packages
        site_packages_path = locate_site_packages(
            python_path=python,
            venv_path=venv,
            site_packages_path=env_site_packages,
        )

        console.print(f"[dim]Parsing:[/dim] {file_path}")
        console.print(f"[dim]Using environment:[/dim] {site_packages_path}")

        # Parse dependency file
        package_names = parse_dependency_file(file_path)

        # Scan environment with filtered packages
        results = scan_environment(
            site_packages_path=site_packages_path,
            depth=depth,
            module_depth=module_depth,
            include_editable=include_editable,
            exclude_patterns=exclude or [],
            follow_symlinks=follow_symlinks,
            target_packages=package_names,
        )

        # Render report
        exit_code = render_report(
            results=results,
            json_output=json_output,
            tree=tree,
            group_by=group_by,
            top=top,
            sort_by=by,
            fail_over=fail_over,
            console=console,
            include_dependencies=include_dependencies,
        )

        raise typer.Exit(exit_code)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command(name="why")
def why(
    package: Annotated[
        str,
        typer.Argument(help="Package name to trace"),
    ],
    python: Annotated[
        Optional[Path],
        typer.Option(help="Path to Python interpreter"),
    ] = None,
    venv: Annotated[
        Optional[Path],
        typer.Option(help="Path to virtual environment"),
    ] = None,
    site_packages: Annotated[
        Optional[Path],
        typer.Option(help="Path to site-packages directory"),
    ] = None,
    json_output: Annotated[
        Optional[Path],
        typer.Option("--json", help="Output JSON to file (use '-' for stdout)"),
    ] = None,
) -> None:
    """Show why a package is installed and all dependency paths to it."""
    try:
        # Locate site-packages
        site_packages_path = locate_site_packages(
            python_path=python,
            venv_path=venv,
            site_packages_path=site_packages,
        )
        
        console.print(f"[dim]Analyzing:[/dim] {package}")
        console.print(f"[dim]Environment:[/dim] {site_packages_path}")
        console.print()
        
        # Analyze why package is installed
        result = analyze_why_package(package, site_packages_path)
        
        if not result["found"]:
            console.print(f"[red]✗ Package '{package}' not found in environment[/red]")
            console.print()
            console.print("[dim]Suggestion:[/dim] Check spelling or install the package first")
            raise typer.Exit(1)
        
        # Output JSON if requested
        if json_output:
            import json
            json_data = {
                "package": result["package"],
                "version": result["version"],
                "size_bytes": result["size"],
                "is_direct": result["is_direct"],
                "depth": result["depth"],
                "editable": result["editable"],
                "location": result["location"],
                "paths": [
                    {
                        "packages": path.packages,
                        "sizes": path.sizes,
                        "total_size": path.total_size,
                    }
                    for path in result["paths"]
                ],
                "dependents": result["dependents"],
            }
            
            json_str = json.dumps(json_data, indent=2)
            if str(json_output) == "-":
                console.print(json_str)
            else:
                with open(json_output, "w") as f:
                    f.write(json_str)
                console.print(f"[dim]JSON written to:[/dim] {json_output}")
                console.print()
        
        # Render beautiful output
        from rich.panel import Panel
        from rich.tree import Tree
        
        # Header
        status = "📍 Direct dependency" if result["is_direct"] else "🔗 Transitive dependency"
        edit_str = " ✏️ (editable)" if result["editable"] else ""
        
        header = f"[bold cyan]{result['package']}[/bold cyan] [magenta]{result['version']}[/magenta]{edit_str}"
        subheader = f"{status} • [green]{format_size(result['size'])}[/green] • Depth: {result['depth']}"
        
        console.print(Panel(
            f"{header}\n{subheader}",
            title="🔍 Package Analysis",
            border_style="cyan",
        ))
        console.print()
        
        # Show why it's installed
        if result["is_direct"]:
            console.print("📍 [bold]This is a direct dependency[/bold]")
            console.print("   You explicitly installed or listed this package")
            console.print()
        else:
            console.print(f"🔗 [bold]Required by {len(result['dependents'])} package(s):[/bold]")
            console.print()
            
            # Show all dependency paths
            if result["paths"]:
                for i, path in enumerate(result["paths"][:10], 1):  # Limit to 10 paths
                    tree = Tree(f"[dim]Path {i}:[/dim]")
                    
                    current_tree = tree
                    for j, pkg_name in enumerate(path.packages):
                        size_str = format_size(path.sizes[j]) if j < len(path.sizes) else ""
                        
                        if j == len(path.packages) - 1:
                            # Target package
                            label = f"[bold cyan]{pkg_name}[/bold cyan] [green]({size_str})[/green] ← [yellow]TARGET[/yellow]"
                        else:
                            label = f"{pkg_name} [dim]({size_str})[/dim]"
                        
                        if j == 0:
                            current_tree = tree.add(label)
                        else:
                            current_tree = current_tree.add(label)
                    
                    console.print(tree)
                    console.print()
                
                if len(result["paths"]) > 10:
                    console.print(f"[dim]... and {len(result['paths']) - 10} more paths[/dim]")
                    console.print()
            
            # Summary of dependents
            console.print("📊 [bold]Summary:[/bold]")
            console.print(f"   • Required by: [cyan]{', '.join(result['dependents'][:5])}[/cyan]")
            if len(result["dependents"]) > 5:
                console.print(f"     [dim]... and {len(result['dependents']) - 5} more[/dim]")
            console.print(f"   • Total dependency paths: {len(result['paths'])}")
            console.print(f"   • Package size: [green]{format_size(result['size'])}[/green]")
            console.print()
        
        # Removal advice
        if not result["is_direct"] and len(result["dependents"]) > 0:
            console.print("🗑️  [bold]Can I remove this?[/bold]")
            if len(result["dependents"]) == 1:
                console.print(f"   Only if you remove: [cyan]{result['dependents'][0]}[/cyan]")
            else:
                console.print(f"   Only if you remove ALL of: [cyan]{', '.join(result['dependents'])}[/cyan]")
            console.print(f"   Savings: [green]{format_size(result['size'])}[/green]")
        elif result["is_direct"]:
            console.print("🗑️  [bold]Can I remove this?[/bold]")
            console.print("   Yes! It's a direct dependency.")
            console.print(f"   Savings: [green]{format_size(result['size'])}[/green]")
            if result["dependents"]:
                console.print(f"   [yellow]Warning:[/yellow] {len(result['dependents'])} package(s) depend on this")
        
        console.print()
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command(name="unused")
def unused(
    code_path: Annotated[
        Optional[Path],
        typer.Argument(help="Path to code directory to scan for imports"),
    ] = None,
    python: Annotated[
        Optional[Path],
        typer.Option(help="Path to Python interpreter"),
    ] = None,
    venv: Annotated[
        Optional[Path],
        typer.Option(help="Path to virtual environment"),
    ] = None,
    site_packages: Annotated[
        Optional[Path],
        typer.Option(help="Path to site-packages directory"),
    ] = None,
    json_output: Annotated[
        Optional[Path],
        typer.Option("--json", help="Output JSON to file (use '-' for stdout)"),
    ] = None,
) -> None:
    """Find dependencies that are never imported in your code."""
    try:
        # Locate site-packages
        site_packages_path = locate_site_packages(
            python_path=python,
            venv_path=venv,
            site_packages_path=site_packages,
        )
        
        console.print(f"[dim]Environment:[/dim] {site_packages_path}")
        if code_path:
            if not code_path.exists():
                console.print(f"[red]✗ Code path not found:[/red] {code_path}")
                raise typer.Exit(1)
            console.print(f"[dim]Scanning code:[/dim] {code_path}")
        else:
            console.print("[yellow]⚠  No code path provided - will list all packages[/yellow]")
        console.print()
        
        # Analyze unused dependencies
        result = analyze_unused_dependencies(
            site_packages_path,
            code_path,
        )
        
        # Calculate sizes
        distributions = enumerate_distributions(site_packages_path)
        unused_size = calculate_unused_size(result["unused"], distributions)
        
        # Output JSON if requested
        if json_output:
            import json
            json_data = {
                "total_packages": result["total_packages"],
                "used_count": len(result["used"]),
                "unused_count": len(result["unused"]),
                "uncertain_count": len(result["uncertain"]),
                "unused_size_bytes": unused_size,
                "used": result["used"],
                "unused": result["unused"],
                "uncertain": result["uncertain"],
                "code_scanned": result["code_scanned"],
            }
            
            json_str = json.dumps(json_data, indent=2)
            if str(json_output) == "-":
                console.print(json_str)
            else:
                with open(json_output, "w") as f:
                    f.write(json_str)
                console.print(f"[dim]JSON written to:[/dim] {json_output}")
                console.print()
        
        # Render beautiful output
        from rich.panel import Panel
        from rich.table import Table
        
        # Header
        console.print(Panel(
            f"[bold cyan]Unused Dependency Analysis[/bold cyan]\n"
            f"Total packages: {result['total_packages']} • "
            f"Code scanned: {'✓' if result['code_scanned'] else '✗'}",
            border_style="cyan",
        ))
        console.print()
        
        if not result["code_scanned"]:
            console.print("[yellow]💡 Tip:[/yellow] Provide a code path to scan for imports:")
            console.print("   [dim]pkgsizer unused ./src[/dim]")
            console.print()
            console.print("Without code scanning, showing all installed packages:")
            console.print()
            
            # Show all packages
            table = Table(title="📦 Installed Packages")
            table.add_column("Package", style="cyan")
            table.add_column("Version", style="magenta")
            table.add_column("Files", justify="right", style="blue")
            
            for pkg_name in sorted(result["uncertain"]):
                pkg_info = result["packages_info"][pkg_name]
                table.add_row(
                    pkg_name,
                    pkg_info["version"],
                    str(pkg_info["files"]),
                )
            
            console.print(table)
            raise typer.Exit(0)
        
        # Show results
        if result["unused"]:
            console.print(f"🗑️  [bold red]Unused Dependencies ({len(result['unused'])})[/bold red]")
            console.print(f"    Total waste: [red]{format_size(unused_size)}[/red]")
            console.print()
            
            # Create table
            table = Table()
            table.add_column("Package", style="cyan bold")
            table.add_column("Version", style="magenta")
            table.add_column("Top-level Modules", style="dim")
            
            for pkg_name in sorted(result["unused"]):
                pkg_info = result["packages_info"][pkg_name]
                modules_str = ", ".join(pkg_info["top_level"][:3])
                if len(pkg_info["top_level"]) > 3:
                    modules_str += f" (+{len(pkg_info['top_level']) - 3} more)"
                
                table.add_row(
                    pkg_name,
                    pkg_info["version"],
                    modules_str,
                )
            
            console.print(table)
            console.print()
            
            # Recommendations
            console.print("💡 [bold]Recommendations:[/bold]")
            console.print("   1. Review the list above")
            console.print("   2. Remove unused packages:")
            console.print(f"      [dim]pip uninstall {' '.join(result['unused'][:3])}[/dim]")
            console.print(f"   3. Potential savings: [green]{format_size(unused_size)}[/green]")
            console.print()
        else:
            console.print("✅ [bold green]No unused dependencies found![/bold green]")
            console.print("   All installed packages are imported in your code.")
            console.print()
        
        # Show used packages summary
        if result["used"]:
            console.print(f"✓ [bold green]Used Dependencies ({len(result['used'])})[/bold green]")
            console.print(f"   [dim]{', '.join(sorted(result['used'][:10]))}[/dim]")
            if len(result["used"]) > 10:
                console.print(f"   [dim]... and {len(result['used']) - 10} more[/dim]")
            console.print()
        
        # Summary
        console.print("📊 [bold]Summary:[/bold]")
        console.print(f"   • Total packages: {result['total_packages']}")
        console.print(f"   • Used: [green]{len(result['used'])}[/green]")
        console.print(f"   • Unused: [red]{len(result['unused'])}[/red]")
        if unused_size > 0:
            console.print(f"   • Wasted space: [red]{format_size(unused_size)}[/red]")
        console.print()
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command(name="alternatives")
def alternatives(
    package: Annotated[
        Optional[str],
        typer.Argument(help="Package name to find alternatives for (optional)"),
    ] = None,
    python: Annotated[
        Optional[Path],
        typer.Option(help="Path to Python interpreter"),
    ] = None,
    venv: Annotated[
        Optional[Path],
        typer.Option(help="Path to virtual environment"),
    ] = None,
    site_packages: Annotated[
        Optional[Path],
        typer.Option(help="Path to site-packages directory"),
    ] = None,
    list_all: Annotated[
        bool,
        typer.Option("--list-all", help="List all known alternatives in database"),
    ] = False,
    json_output: Annotated[
        Optional[Path],
        typer.Option("--json", help="Output JSON to file (use '-' for stdout)"),
    ] = None,
) -> None:
    """Suggest lighter or better alternative packages."""
    try:
        # If list_all, show all known alternatives
        if list_all:
            all_alternatives = get_all_known_alternatives()
            
            from rich.table import Table
            
            console.print("[bold cyan]Known Package Alternatives Database[/bold cyan]")
            console.print()
            
            table = Table()
            table.add_column("Package", style="cyan")
            table.add_column("Alternatives", style="green")
            table.add_column("Count", justify="right", style="blue")
            
            for pkg, alts in sorted(all_alternatives.items()):
                alt_names = ", ".join(a["name"] for a in alts[:3])
                if len(alts) > 3:
                    alt_names += f" (+{len(alts) - 3} more)"
                table.add_row(pkg, alt_names, str(len(alts)))
            
            console.print(table)
            console.print()
            console.print(f"[dim]Total packages with alternatives: {len(all_alternatives)}[/dim]")
            return
        
        # Locate site-packages
        site_packages_path = locate_site_packages(
            python_path=python,
            venv_path=venv,
            site_packages_path=site_packages,
        )
        
        console.print(f"[dim]Environment:[/dim] {site_packages_path}")
        console.print()
        
        # Analyze alternatives
        result = analyze_alternatives(site_packages_path, package)
        
        # Handle JSON output
        if json_output:
            import json
            json_str = json.dumps(result, indent=2)
            if str(json_output) == "-":
                console.print(json_str)
            else:
                with open(json_output, "w") as f:
                    f.write(json_str)
                console.print(f"[dim]JSON written to:[/dim] {json_output}")
            return
        
        # Render output based on mode
        if package:
            # Single package mode
            if not result.get("found"):
                console.print(f"[red]✗ Package '{package}' not found in environment[/red]")
                raise typer.Exit(1)
            
            if not result.get("has_alternatives"):
                console.print(f"[yellow]No known alternatives for '{package}'[/yellow]")
                console.print()
                console.print("[dim]This doesn't mean alternatives don't exist,[/dim]")
                console.print("[dim]just that they're not in our database yet.[/dim]")
                raise typer.Exit(0)
            
            from rich.panel import Panel
            from rich.table import Table
            
            # Header
            header = f"[bold cyan]{result['package']}[/bold cyan] [magenta]{result['version']}[/magenta]"
            subheader = f"Current size: [green]{format_size(result['size'])}[/green]"
            
            console.print(Panel(
                f"{header}\n{subheader}",
                title="💡 Alternative Packages",
                border_style="cyan",
            ))
            console.print()
            
            # Alternatives table
            table = Table()
            table.add_column("Alternative", style="cyan bold")
            table.add_column("Reason", style="dim")
            table.add_column("Size Expectation", style="yellow")
            table.add_column("Status", style="green")
            
            for alt in result["alternatives"]:
                size_icon = {
                    "much_smaller": "⬇️⬇️ Much smaller",
                    "smaller": "⬇️ Smaller",
                    "similar": "≈ Similar",
                    "larger": "⬆️ Larger",
                }.get(alt["size_diff"], "❓ Unknown")
                
                if alt.get("installed"):
                    status = f"✓ Installed ({format_size(alt['actual_size'])})"
                    if alt.get("size_comparison"):
                        diff = alt["size_comparison"]
                        if diff < 0:
                            status += f" [green](-{format_size(abs(diff))})[/green]"
                        else:
                            status += f" [red](+{format_size(diff)})[/red]"
                else:
                    status = "○ Not installed"
                
                table.add_row(
                    alt["name"],
                    alt["reason"],
                    size_icon,
                    status,
                )
            
            console.print(table)
            console.print()
            
            # Recommendations
            not_installed = [a for a in result["alternatives"] if not a.get("installed")]
            if not_installed:
                console.print("💡 [bold]Try these alternatives:[/bold]")
                for alt in not_installed[:3]:
                    console.print(f"   [cyan]pip install {alt['name']}[/cyan]")
                    console.print(f"   └─ {alt['reason']}")
                console.print()
        
        else:
            # All packages mode
            if result["total_count"] == 0:
                console.print("[yellow]No packages with known alternatives found in environment[/yellow]")
                raise typer.Exit(0)
            
            from rich.table import Table
            
            console.print(f"[bold cyan]Packages with Known Alternatives ({result['total_count']})[/bold cyan]")
            console.print()
            
            table = Table()
            table.add_column("Package", style="cyan")
            table.add_column("Version", style="magenta")
            table.add_column("Size", style="green")
            table.add_column("Alternatives", style="dim")
            table.add_column("Installed", style="blue")
            
            for pkg_info in result["packages_with_alternatives"]:
                alt_names = ", ".join(a["name"] for a in pkg_info["alternatives"][:2])
                if len(pkg_info["alternatives"]) > 2:
                    alt_names += f" (+{len(pkg_info['alternatives']) - 2})"
                
                installed_alts = sum(1 for a in pkg_info["alternatives"] if a.get("installed"))
                
                table.add_row(
                    pkg_info["package"],
                    pkg_info["version"],
                    format_size(pkg_info["size"]),
                    alt_names,
                    str(installed_alts),
                )
            
            console.print(table)
            console.print()
            console.print(f"[dim]Use 'pkgsizer alternatives <package>' for details[/dim]")
            console.print()
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command(name="updates")
def updates(
    packages: Annotated[
        Optional[list[str]],
        typer.Argument(help="Specific packages to check (optional)"),
    ] = None,
    python: Annotated[
        Optional[Path],
        typer.Option(help="Path to Python interpreter"),
    ] = None,
    venv: Annotated[
        Optional[Path],
        typer.Option(help="Path to virtual environment"),
    ] = None,
    site_packages: Annotated[
        Optional[Path],
        typer.Option(help="Path to site-packages directory"),
    ] = None,
    check_all: Annotated[
        bool,
        typer.Option("--all", help="Check all packages (can be slow)"),
    ] = False,
    json_output: Annotated[
        Optional[Path],
        typer.Option("--json", help="Output JSON to file (use '-' for stdout)"),
    ] = None,
) -> None:
    """Check for outdated packages and available updates."""
    try:
        # Locate site-packages
        site_packages_path = locate_site_packages(
            python_path=python,
            venv_path=venv,
            site_packages_path=site_packages,
        )
        
        console.print(f"[dim]Environment:[/dim] {site_packages_path}")
        
        if packages:
            console.print(f"[dim]Checking:[/dim] {', '.join(packages)}")
        elif check_all:
            console.print("[dim]Checking:[/dim] All packages (this may take a while...)")
        else:
            console.print("[dim]Checking:[/dim] First 20 packages")
        
        console.print()
        
        # Check updates
        result = check_updates(site_packages_path, packages, check_all)
        
        # Handle JSON output
        if json_output:
            import json
            json_str = json.dumps(result, indent=2)
            if str(json_output) == "-":
                console.print(json_str)
            else:
                with open(json_output, "w") as f:
                    f.write(json_str)
                console.print(f"[dim]JSON written to:[/dim] {json_output}")
            return
        
        # Render output
        from rich.panel import Panel
        from rich.table import Table
        
        # Header
        console.print(Panel(
            f"[bold cyan]Package Update Check[/bold cyan]\n"
            f"Checked: {result['total_checked']} • "
            f"Outdated: [red]{result['outdated_count']}[/red] • "
            f"Up-to-date: [green]{result['up_to_date_count']}[/green]",
            border_style="cyan",
        ))
        console.print()
        
        # Show outdated packages
        if result["outdated"]:
            console.print(f"[bold red]⚠️  Outdated Packages ({result['outdated_count']})[/bold red]")
            console.print()
            
            table = Table()
            table.add_column("Package", style="cyan")
            table.add_column("Current", style="yellow")
            table.add_column("Latest", style="green bold")
            table.add_column("Size", style="blue")
            table.add_column("Command", style="dim")
            
            for pkg in result["outdated"]:
                table.add_row(
                    pkg["package"],
                    pkg["current_version"],
                    pkg["latest_version"],
                    format_size(pkg["current_size"]),
                    f"pip install --upgrade {pkg['package']}",
                )
            
            console.print(table)
            console.print()
            
            # Recommendations
            console.print("💡 [bold]To update all:[/bold]")
            outdated_names = " ".join(p["package"] for p in result["outdated"][:5])
            if result["outdated_count"] <= 5:
                console.print(f"   [cyan]pip install --upgrade {outdated_names}[/cyan]")
            else:
                console.print(f"   [cyan]pip install --upgrade {outdated_names} ...[/cyan]")
                console.print(f"   [dim](and {result['outdated_count'] - 5} more)[/dim]")
            console.print()
        
        # Show up-to-date packages
        if result["up_to_date"] and not result["outdated"]:
            console.print("✅ [bold green]All packages are up-to-date![/bold green]")
            console.print()
        elif result["up_to_date"]:
            console.print(f"✓ [green]Up-to-date ({result['up_to_date_count']})[/green]")
            up_to_date_names = ", ".join(p["package"] for p in result["up_to_date"][:10])
            if result["up_to_date_count"] > 10:
                up_to_date_names += f" (+{result['up_to_date_count'] - 10} more)"
            console.print(f"  [dim]{up_to_date_names}[/dim]")
            console.print()
        
        # Show unavailable
        if result["unavailable"]:
            console.print(f"⚠️  [yellow]Unavailable on PyPI ({result['unavailable_count']})[/yellow]")
            unavail_names = ", ".join(p["package"] for p in result["unavailable"][:5])
            if result["unavailable_count"] > 5:
                unavail_names += f" (+{result['unavailable_count'] - 5} more)"
            console.print(f"  [dim]{unavail_names}[/dim]")
            console.print()
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command(name="compare")
def compare(
    env1: Annotated[
        Path,
        typer.Argument(help="First environment's site-packages path or venv path"),
    ],
    env2: Annotated[
        Path,
        typer.Argument(help="Second environment's site-packages path or venv path"),
    ],
    name1: Annotated[
        Optional[str],
        typer.Option(help="Name for first environment"),
    ] = None,
    name2: Annotated[
        Optional[str],
        typer.Option(help="Name for second environment"),
    ] = None,
    json_output: Annotated[
        Optional[Path],
        typer.Option("--json", help="Output JSON to file (use '-' for stdout)"),
    ] = None,
) -> None:
    """Compare two Python environments."""
    try:
        # Resolve paths (handle both venv and site-packages paths)
        def resolve_env_path(p: Path) -> Path:
            if (p / "site-packages").exists():
                return p / "site-packages"
            elif (p / "lib").exists():
                # Try to find site-packages in lib
                for item in (p / "lib").iterdir():
                    if item.is_dir() and item.name.startswith("python"):
                        sp = item / "site-packages"
                        if sp.exists():
                            return sp
            return p
        
        env1_path = resolve_env_path(env1)
        env2_path = resolve_env_path(env2)
        
        if not env1_path.exists():
            console.print(f"[red]✗ Environment 1 path not found:[/red] {env1_path}")
            raise typer.Exit(1)
        
        if not env2_path.exists():
            console.print(f"[red]✗ Environment 2 path not found:[/red] {env2_path}")
            raise typer.Exit(1)
        
        console.print(f"[dim]Comparing environments:[/dim]")
        console.print(f"  [cyan]1.[/cyan] {env1_path}")
        console.print(f"  [cyan]2.[/cyan] {env2_path}")
        console.print()
        
        # Compare environments
        result = compare_environments(env1_path, env2_path, name1, name2)
        
        # Handle JSON output
        if json_output:
            import json
            json_str = json.dumps(result, indent=2)
            if str(json_output) == "-":
                console.print(json_str)
            else:
                with open(json_output, "w") as f:
                    f.write(json_str)
                console.print(f"[dim]JSON written to:[/dim] {json_output}")
            return
        
        # Render output
        from rich.panel import Panel
        from rich.table import Table
        
        # Header
        env1_name = result["env1"]["name"]
        env2_name = result["env2"]["name"]
        
        header = f"[cyan]{env1_name}[/cyan] vs [magenta]{env2_name}[/magenta]"
        size_diff = result["comparison"]["size_diff"]
        if size_diff > 0:
            size_str = f"[red]+{format_size(size_diff)}[/red]"
        elif size_diff < 0:
            size_str = f"[green]{format_size(size_diff)}[/green]"
        else:
            size_str = "[dim]Same size[/dim]"
        
        console.print(Panel(
            f"{header}\n"
            f"Total size difference: {size_str}",
            title="📊 Environment Comparison",
            border_style="cyan",
        ))
        console.print()
        
        # Summary
        console.print("[bold]Summary:[/bold]")
        console.print(f"  [cyan]{env1_name}:[/cyan] {result['env1']['total_packages']} packages, {format_size(result['env1']['total_size'])}")
        console.print(f"  [magenta]{env2_name}:[/magenta] {result['env2']['total_packages']} packages, {format_size(result['env2']['total_size'])}")
        console.print()
        console.print(f"  • Common packages: {result['comparison']['common_packages']}")
        console.print(f"  • Same version: [green]{result['comparison']['same_version']}[/green]")
        console.print(f"  • Different versions: [yellow]{result['comparison']['version_diffs']}[/yellow]")
        console.print(f"  • Only in {env1_name}: [cyan]{result['comparison']['only_in_env1']}[/cyan] ({format_size(result['summary']['env1_unique_size'])})")
        console.print(f"  • Only in {env2_name}: [magenta]{result['comparison']['only_in_env2']}[/magenta] ({format_size(result['summary']['env2_unique_size'])})")
        console.print()
        
        # Version differences
        if result["details"]["version_differences"]:
            console.print(f"[bold yellow]📦 Version Differences (Top 10)[/bold yellow]")
            console.print()
            
            table = Table()
            table.add_column("Package", style="cyan")
            table.add_column(f"{env1_name} Ver", style="blue")
            table.add_column(f"{env2_name} Ver", style="magenta")
            table.add_column("Size Diff", style="yellow")
            
            for diff in result["details"]["version_differences"][:10]:
                size_diff_val = diff["size_diff"]
                if size_diff_val > 0:
                    size_str = f"[red]+{format_size(size_diff_val)}[/red]"
                elif size_diff_val < 0:
                    size_str = f"[green]{format_size(abs(size_diff_val))}[/green]"
                else:
                    size_str = "[dim]same[/dim]"
                
                table.add_row(
                    diff["package"],
                    diff["env1_version"],
                    diff["env2_version"],
                    size_str,
                )
            
            console.print(table)
            console.print()
        
        # Only in env1
        if result["details"]["only_in_env1"]:
            console.print(f"[bold cyan]📦 Only in {env1_name} (Top 10)[/bold cyan]")
            
            table = Table()
            table.add_column("Package", style="cyan")
            table.add_column("Version", style="blue")
            table.add_column("Size", style="green")
            
            for pkg in result["details"]["only_in_env1"][:10]:
                table.add_row(pkg["package"], pkg["version"], format_size(pkg["size"]))
            
            console.print(table)
            if len(result["details"]["only_in_env1"]) > 10:
                console.print(f"  [dim]... and {len(result['details']['only_in_env1']) - 10} more[/dim]")
            console.print()
        
        # Only in env2
        if result["details"]["only_in_env2"]:
            console.print(f"[bold magenta]📦 Only in {env2_name} (Top 10)[/bold magenta]")
            
            table = Table()
            table.add_column("Package", style="magenta")
            table.add_column("Version", style="blue")
            table.add_column("Size", style="green")
            
            for pkg in result["details"]["only_in_env2"][:10]:
                table.add_row(pkg["package"], pkg["version"], format_size(pkg["size"]))
            
            console.print(table)
            if len(result["details"]["only_in_env2"]) > 10:
                console.print(f"  [dim]... and {len(result['details']['only_in_env2']) - 10} more[/dim]")
            console.print()
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

