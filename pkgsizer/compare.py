"""Environment comparison - compare two Python environments."""

from pathlib import Path
from typing import Optional

from pkgsizer.dist_metadata import enumerate_distributions


def compare_environments(
    env1_path: Path,
    env2_path: Path,
    env1_name: Optional[str] = None,
    env2_name: Optional[str] = None,
) -> dict:
    """
    Compare two Python environments.
    
    Args:
        env1_path: Path to first environment's site-packages
        env2_path: Path to second environment's site-packages
        env1_name: Optional name for first environment
        env2_name: Optional name for second environment
    
    Returns:
        Dictionary with comparison results
    """
    # Default names
    if not env1_name:
        env1_name = str(env1_path.parent.name)
    if not env2_name:
        env2_name = str(env2_path.parent.name)
    
    # Enumerate both environments
    env1_dists = enumerate_distributions(env1_path)
    env2_dists = enumerate_distributions(env2_path)
    
    # Get package sets
    env1_packages = set(env1_dists.keys())
    env2_packages = set(env2_dists.keys())
    
    # Find differences
    only_in_env1 = env1_packages - env2_packages
    only_in_env2 = env2_packages - env1_packages
    common = env1_packages & env2_packages
    
    # Analyze common packages for version differences
    version_diffs = []
    same_version = []
    
    for pkg_name in common:
        v1 = env1_dists[pkg_name].version
        v2 = env2_dists[pkg_name].version
        
        if v1 != v2:
            # Calculate sizes
            size1 = _calculate_package_size(env1_dists[pkg_name])
            size2 = _calculate_package_size(env2_dists[pkg_name])
            
            version_diffs.append({
                "package": pkg_name,
                "env1_version": v1,
                "env2_version": v2,
                "env1_size": size1,
                "env2_size": size2,
                "size_diff": size2 - size1,
            })
        else:
            same_version.append(pkg_name)
    
    # Calculate sizes for unique packages
    only_env1_details = []
    for pkg_name in only_in_env1:
        dist = env1_dists[pkg_name]
        size = _calculate_package_size(dist)
        only_env1_details.append({
            "package": pkg_name,
            "version": dist.version,
            "size": size,
        })
    
    only_env2_details = []
    for pkg_name in only_in_env2:
        dist = env2_dists[pkg_name]
        size = _calculate_package_size(dist)
        only_env2_details.append({
            "package": pkg_name,
            "version": dist.version,
            "size": size,
        })
    
    # Calculate total sizes
    env1_total_size = sum(_calculate_package_size(d) for d in env1_dists.values())
    env2_total_size = sum(_calculate_package_size(d) for d in env2_dists.values())
    
    only_env1_size = sum(p["size"] for p in only_env1_details)
    only_env2_size = sum(p["size"] for p in only_env2_details)
    
    return {
        "env1": {
            "name": env1_name,
            "path": str(env1_path),
            "total_packages": len(env1_packages),
            "total_size": env1_total_size,
        },
        "env2": {
            "name": env2_name,
            "path": str(env2_path),
            "total_packages": len(env2_packages),
            "total_size": env2_total_size,
        },
        "comparison": {
            "common_packages": len(common),
            "same_version": len(same_version),
            "version_diffs": len(version_diffs),
            "only_in_env1": len(only_in_env1),
            "only_in_env2": len(only_in_env2),
            "size_diff": env2_total_size - env1_total_size,
        },
        "details": {
            "version_differences": sorted(version_diffs, key=lambda x: abs(x["size_diff"]), reverse=True),
            "only_in_env1": sorted(only_env1_details, key=lambda x: x["size"], reverse=True),
            "only_in_env2": sorted(only_env2_details, key=lambda x: x["size"], reverse=True),
            "same_version_packages": sorted(same_version),
        },
        "summary": {
            "env1_unique_size": only_env1_size,
            "env2_unique_size": only_env2_size,
            "total_size_diff": env2_total_size - env1_total_size,
        },
    }


def _calculate_package_size(dist_info) -> int:
    """
    Calculate package size in bytes.
    
    Args:
        dist_info: Distribution info object
    
    Returns:
        Size in bytes
    """
    if not dist_info.files:
        return 0
    
    total = 0
    seen_inodes = set()
    
    for file_path in dist_info.files:
        try:
            if file_path.exists():
                stat = file_path.stat()
                inode_key = (stat.st_dev, stat.st_ino)
                if inode_key not in seen_inodes:
                    seen_inodes.add(inode_key)
                    total += stat.st_size
        except (OSError, PermissionError):
            pass
    
    return total

