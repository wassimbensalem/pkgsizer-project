"""Alternative package suggestions - suggest lighter alternatives."""

from pathlib import Path
from typing import Optional

from pkgsizer.dist_metadata import enumerate_distributions


# Database of known alternatives (package_name -> list of alternatives)
ALTERNATIVES_DB = {
    # Web frameworks
    "flask": [
        {"name": "fastapi", "reason": "Modern, faster, async support", "size_diff": "similar"},
        {"name": "bottle", "reason": "Minimal, single-file framework", "size_diff": "smaller"},
    ],
    "django": [
        {"name": "fastapi", "reason": "Modern, lighter, API-focused", "size_diff": "much_smaller"},
        {"name": "flask", "reason": "Simpler, more flexible", "size_diff": "much_smaller"},
    ],
    
    # HTTP clients
    "requests": [
        {"name": "httpx", "reason": "Modern, async support, HTTP/2", "size_diff": "similar"},
        {"name": "urllib3", "reason": "Lower-level, fewer dependencies", "size_diff": "smaller"},
    ],
    
    # Date/time
    "arrow": [
        {"name": "pendulum", "reason": "Better timezone handling", "size_diff": "similar"},
        {"name": "python-dateutil", "reason": "Standard, fewer dependencies", "size_diff": "smaller"},
    ],
    
    # Parsing
    "beautifulsoup4": [
        {"name": "selectolax", "reason": "Much faster, C-based", "size_diff": "smaller"},
        {"name": "pyquery", "reason": "jQuery-like API", "size_diff": "similar"},
    ],
    
    # CLI
    "click": [
        {"name": "typer", "reason": "Type hints, better completion", "size_diff": "similar"},
        {"name": "argparse", "reason": "Standard library, no deps", "size_diff": "much_smaller"},
    ],
    
    # Serialization
    "pyyaml": [
        {"name": "ruamel.yaml", "reason": "Better YAML 1.2 support", "size_diff": "similar"},
    ],
    "pickle": [
        {"name": "dill", "reason": "More types supported", "size_diff": "similar"},
        {"name": "cloudpickle", "reason": "Better for distributed computing", "size_diff": "similar"},
    ],
    
    # Validation
    "cerberus": [
        {"name": "pydantic", "reason": "Type hints, better performance", "size_diff": "similar"},
        {"name": "marshmallow", "reason": "More flexible", "size_diff": "similar"},
    ],
    
    # Database
    "sqlalchemy": [
        {"name": "peewee", "reason": "Simpler, lighter ORM", "size_diff": "much_smaller"},
        {"name": "sqlite3", "reason": "Standard library", "size_diff": "much_smaller"},
    ],
    
    # Testing
    "pytest": [
        {"name": "unittest", "reason": "Standard library, no deps", "size_diff": "much_smaller"},
    ],
    "nose": [
        {"name": "pytest", "reason": "More actively maintained", "size_diff": "similar"},
        {"name": "unittest", "reason": "Standard library", "size_diff": "smaller"},
    ],
    
    # Numerical
    "numpy": [
        {"name": "jax", "reason": "GPU support, auto-diff", "size_diff": "similar"},
        # Note: numpy is hard to replace for most use cases
    ],
    
    # Data processing
    "pandas": [
        {"name": "polars", "reason": "Much faster, better memory usage", "size_diff": "smaller"},
        {"name": "dask", "reason": "Distributed computing", "size_diff": "larger"},
    ],
    
    # Plotting
    "matplotlib": [
        {"name": "plotly", "reason": "Interactive, modern", "size_diff": "similar"},
        {"name": "seaborn", "reason": "Simpler API, statistical", "size_diff": "smaller"},
    ],
    
    # Image processing
    "pillow": [
        {"name": "opencv-python", "reason": "More features, faster", "size_diff": "larger"},
        {"name": "imageio", "reason": "Simpler, fewer deps", "size_diff": "smaller"},
    ],
    
    # JSON
    "simplejson": [
        {"name": "json", "reason": "Standard library", "size_diff": "much_smaller"},
        {"name": "ujson", "reason": "Ultra-fast", "size_diff": "smaller"},
        {"name": "orjson", "reason": "Fastest, Rust-based", "size_diff": "smaller"},
    ],
    
    # Environment
    "python-dotenv": [
        {"name": "environs", "reason": "Type casting, validation", "size_diff": "similar"},
    ],
    
    # AWS
    "boto3": [
        {"name": "aioboto3", "reason": "Async support", "size_diff": "similar"},
    ],
    
    # Caching
    "redis": [
        {"name": "redis-py-cluster", "reason": "Cluster support", "size_diff": "similar"},
        {"name": "aioredis", "reason": "Async support", "size_diff": "similar"},
    ],
    
    # Task queues
    "celery": [
        {"name": "rq", "reason": "Simpler, Redis-based", "size_diff": "much_smaller"},
        {"name": "dramatiq", "reason": "Better reliability", "size_diff": "smaller"},
    ],
    
    # Logging
    "loguru": [
        {"name": "logging", "reason": "Standard library", "size_diff": "much_smaller"},
    ],
    
    # Configuration
    "configparser": [
        {"name": "dynaconf", "reason": "Multiple formats, environments", "size_diff": "larger"},
    ],
}


def get_alternatives(package_name: str) -> list[dict]:
    """
    Get alternative packages for a given package.
    
    Args:
        package_name: Package name to find alternatives for
    
    Returns:
        List of alternative packages with metadata
    """
    pkg_lower = package_name.lower()
    return ALTERNATIVES_DB.get(pkg_lower, [])


def analyze_alternatives(
    site_packages_path: Path,
    package_name: Optional[str] = None,
) -> dict:
    """
    Analyze alternatives for installed packages.
    
    Args:
        site_packages_path: Path to site-packages
        package_name: Optional specific package to analyze
    
    Returns:
        Dictionary with alternatives analysis
    """
    # Enumerate distributions
    distributions = enumerate_distributions(site_packages_path)
    
    results = []
    
    if package_name:
        # Analyze specific package
        pkg_lower = package_name.lower()
        if pkg_lower not in distributions:
            return {
                "found": False,
                "package": package_name,
                "error": "Package not found in environment",
            }
        
        alternatives = get_alternatives(pkg_lower)
        if not alternatives:
            return {
                "found": True,
                "package": package_name,
                "has_alternatives": False,
                "alternatives": [],
            }
        
        # Calculate package size
        dist = distributions[pkg_lower]
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
        
        # Check if alternatives are installed
        for alt in alternatives:
            alt_name = alt["name"].lower()
            alt["installed"] = alt_name in distributions
            if alt["installed"]:
                # Get size of alternative
                alt_dist = distributions[alt_name]
                alt_size = 0
                if alt_dist.files:
                    seen_inodes = set()
                    for file_path in alt_dist.files:
                        try:
                            if file_path.exists():
                                stat = file_path.stat()
                                inode_key = (stat.st_dev, stat.st_ino)
                                if inode_key not in seen_inodes:
                                    seen_inodes.add(inode_key)
                                    alt_size += stat.st_size
                        except (OSError, PermissionError):
                            pass
                alt["actual_size"] = alt_size
                alt["size_comparison"] = alt_size - pkg_size
        
        return {
            "found": True,
            "package": package_name,
            "version": dist.version,
            "size": pkg_size,
            "has_alternatives": True,
            "alternatives": alternatives,
        }
    
    else:
        # Analyze all packages with alternatives
        for pkg_name in distributions.keys():
            alternatives = get_alternatives(pkg_name)
            if alternatives:
                dist = distributions[pkg_name]
                
                # Calculate size
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
                
                # Check if alternatives are installed
                for alt in alternatives:
                    alt_name = alt["name"].lower()
                    alt["installed"] = alt_name in distributions
                
                results.append({
                    "package": pkg_name,
                    "version": dist.version,
                    "size": pkg_size,
                    "alternatives": alternatives,
                })
        
        return {
            "packages_with_alternatives": results,
            "total_count": len(results),
        }


def get_all_known_alternatives() -> dict:
    """
    Get all packages in the alternatives database.
    
    Returns:
        Dictionary mapping package names to their alternatives
    """
    return ALTERNATIVES_DB.copy()

