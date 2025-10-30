"""Update checker - check for outdated packages and size changes."""

import json
import urllib.request
import urllib.error
import time
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from packaging import version as pkg_version

from pkgsizer.dist_metadata import enumerate_distributions

# Cache configuration
CACHE_DIR = Path.home() / ".pkgsizer" / "cache"
CACHE_DURATION = 3600  # 1 hour in seconds


def _get_cached_version(package_name: str) -> Optional[dict]:
    """Get version from cache if fresh."""
    cache_file = CACHE_DIR / f"{package_name}.json"
    
    if not cache_file.exists():
        return None
    
    # Check if cache is fresh
    try:
        if time.time() - cache_file.stat().st_mtime > CACHE_DURATION:
            return None
        
        with open(cache_file) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _cache_version(package_name: str, data: dict) -> None:
    """Save version to cache."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f"{package_name}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    except OSError:
        pass  # Silently fail if can't cache


def get_latest_version_from_pypi(package_name: str, timeout: int = 5, use_cache: bool = True) -> Optional[dict]:
    """
    Get latest version info from PyPI (with caching).
    
    Args:
        package_name: Package name to check
        timeout: Request timeout in seconds
        use_cache: Whether to use cached results
    
    Returns:
        Dictionary with version info or None if unavailable
    """
    # Check cache first
    if use_cache:
        cached = _get_cached_version(package_name)
        if cached:
            return cached
    
    # Fetch from PyPI
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        req = urllib.request.Request(url, headers={"User-Agent": "pkgsizer/0.3.0"})
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode())
            
            latest_version = data["info"]["version"]
            releases = data.get("releases", {})
            
            # Get upload date of latest version
            upload_date = None
            if latest_version in releases and releases[latest_version]:
                upload_date = releases[latest_version][0].get("upload_time")
            
            result = {
                "version": latest_version,
                "upload_date": upload_date,
                "homepage": data["info"].get("home_page"),
                "summary": data["info"].get("summary"),
            }
            
            # Cache result
            if use_cache:
                _cache_version(package_name, result)
            
            return result
    
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, KeyError):
        return None


def compare_versions(current: str, latest: str) -> dict:
    """
    Compare two version strings.
    
    Args:
        current: Current version
        latest: Latest version
    
    Returns:
        Dictionary with comparison results
    """
    try:
        current_v = pkg_version.parse(current)
        latest_v = pkg_version.parse(latest)
        
        if current_v < latest_v:
            status = "outdated"
        elif current_v == latest_v:
            status = "up_to_date"
        else:
            status = "ahead"  # Dev version or beta
        
        return {
            "status": status,
            "current": current,
            "latest": latest,
            "behind": status == "outdated",
        }
    
    except Exception:
        return {
            "status": "unknown",
            "current": current,
            "latest": latest,
            "behind": False,
        }


def check_updates(
    site_packages_path: Path,
    packages: Optional[list[str]] = None,
    check_all: bool = False,
    max_workers: int = 10,
) -> dict:
    """
    Check for package updates.
    
    Args:
        site_packages_path: Path to site-packages
        packages: Optional list of specific packages to check
        check_all: Check all packages (can be slow)
    
    Returns:
        Dictionary with update information
    """
    # Enumerate distributions
    distributions = enumerate_distributions(site_packages_path)
    
    # Determine which packages to check
    if packages:
        packages_to_check = [p.lower() for p in packages]
    elif check_all:
        packages_to_check = list(distributions.keys())
    else:
        # By default, only check direct dependencies (depth 0)
        # This requires building a simple dependency map
        packages_to_check = list(distributions.keys())[:20]  # Limit to 20 for speed
    
    results = []
    
    def check_single_package(pkg_name: str) -> Optional[dict]:
        """Check a single package for updates."""
        if pkg_name not in distributions:
            return None
        
        dist = distributions[pkg_name]
        current_version = dist.version
        
        # Get latest version from PyPI
        pypi_info = get_latest_version_from_pypi(pkg_name)
        
        if not pypi_info:
            return {
                "package": pkg_name,
                "current_version": current_version,
                "status": "unavailable",
                "error": "Could not fetch from PyPI",
            }
        
        latest_version = pypi_info["version"]
        comparison = compare_versions(current_version, latest_version)
        
        # Calculate current package size
        pkg_size = 0
        if dist.files:
            seen_inodes = set()
            for file_path in dist.files:
                try:
                    if file_path.exists():
                        stat = file_path.stat()
                        inode_key = (stat.st_dev, stat.st_ino)
                        if inode_key not in seen_inodes:
                            seen_inodes.add(inode_key)
                            pkg_size += stat.st_size
                except (OSError, PermissionError):
                    pass
        
        return {
            "package": pkg_name,
            "current_version": current_version,
            "latest_version": latest_version,
            "status": comparison["status"],
            "behind": comparison["behind"],
            "current_size": pkg_size,
            "upload_date": pypi_info.get("upload_date"),
            "homepage": pypi_info.get("homepage"),
            "summary": pypi_info.get("summary"),
        }
    
    # Check packages in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_pkg = {
            executor.submit(check_single_package, pkg): pkg
            for pkg in packages_to_check
        }
        
        for future in as_completed(future_to_pkg):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception:
                # Skip packages that error
                pass
    
    # Categorize results
    outdated = [r for r in results if r["status"] == "outdated"]
    up_to_date = [r for r in results if r["status"] == "up_to_date"]
    unavailable = [r for r in results if r["status"] == "unavailable"]
    
    return {
        "total_checked": len(results),
        "outdated_count": len(outdated),
        "up_to_date_count": len(up_to_date),
        "unavailable_count": len(unavailable),
        "outdated": outdated,
        "up_to_date": up_to_date,
        "unavailable": unavailable,
        "all_results": results,
    }

