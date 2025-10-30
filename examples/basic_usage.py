"""
Basic usage examples for pkgsizer.

This script demonstrates how to use pkgsizer programmatically.
"""

from pathlib import Path
from pkgsizer.env_locator import locate_site_packages
from pkgsizer.scanner import scan_environment
from pkgsizer.report import format_size

# Example 1: Scan current environment
print("=" * 60)
print("Example 1: Scanning current environment")
print("=" * 60)

site_packages = locate_site_packages()
print(f"Site-packages: {site_packages}\n")

results = scan_environment(
    site_packages_path=site_packages,
    depth=2,  # Limit to 2 levels of dependencies
    module_depth=1,  # Show 1 level of subpackages
)

print(f"Total packages: {len(results.packages)}")
print(f"Total size: {format_size(results.total_size)}")
print(f"Total files: {results.total_files:,}\n")

# Show top 5 packages
print("Top 5 largest packages:")
sorted_packages = sorted(results.packages, key=lambda p: p.total_size, reverse=True)
for i, pkg_result in enumerate(sorted_packages[:5], 1):
    dist = pkg_result.dist_info
    print(f"{i}. {dist.name:20s} {dist.version:10s} {format_size(pkg_result.total_size):>12s}")

print("\n" + "=" * 60)
print("Example 2: Analyzing specific packages")
print("=" * 60)

# Example 2: Analyze specific packages
target_packages = ["pip", "setuptools"]
results2 = scan_environment(
    site_packages_path=site_packages,
    target_packages=target_packages,
)

print(f"\nAnalyzing: {', '.join(target_packages)}")
for pkg_result in results2.packages:
    dist = pkg_result.dist_info
    print(f"  {dist.name}: {format_size(pkg_result.total_size)} ({pkg_result.file_count} files)")
    
    # Show subpackages
    if pkg_result.subpackages:
        for subpkg in pkg_result.subpackages[:3]:
            print(f"    - {subpkg.qualified_name}: {format_size(subpkg.size_info.size_bytes)}")

print("\n" + "=" * 60)
print("Example 3: Filtering with patterns")
print("=" * 60)

# Example 3: Exclude certain patterns
results3 = scan_environment(
    site_packages_path=site_packages,
    exclude_patterns=["*.pyc", "__pycache__", "*.so"],
    target_packages=["pip"],
)

print("\nExcluding .pyc, __pycache__, and .so files:")
for pkg_result in results3.packages:
    dist = pkg_result.dist_info
    print(f"  {dist.name}: {format_size(pkg_result.total_size)}")

print("\n" + "=" * 60)
print("Complete!")
print("=" * 60)

