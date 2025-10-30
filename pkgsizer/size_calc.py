"""Calculate on-disk sizes with deduplication and exclusions."""

import os
import fnmatch
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


class SizeInfo:
    """Size information for a path."""
    
    def __init__(self):
        self.size_bytes: int = 0
        self.file_count: int = 0
        self.files: list[tuple[Path, int]] = []  # (path, size) pairs
    
    def add(self, other: 'SizeInfo') -> None:
        """Add another SizeInfo to this one."""
        self.size_bytes += other.size_bytes
        self.file_count += other.file_count
        self.files.extend(other.files)
    
    def __repr__(self) -> str:
        return f"SizeInfo(size={self.size_bytes}, files={self.file_count})"


def should_exclude(path: Path, exclude_patterns: list[str]) -> bool:
    """
    Check if a path matches any exclude pattern.
    
    Args:
        path: Path to check
        exclude_patterns: List of glob patterns to exclude
    
    Returns:
        True if the path should be excluded
    """
    if not exclude_patterns:
        return False
    
    path_str = str(path)
    path_name = path.name
    
    for pattern in exclude_patterns:
        # Check against full path
        if fnmatch.fnmatch(path_str, pattern):
            return True
        # Check against basename
        if fnmatch.fnmatch(path_name, pattern):
            return True
        # Check with ** pattern
        if "**" in pattern:
            pattern_parts = pattern.split("**")
            if any(part in path_str for part in pattern_parts if part):
                return True
    
    return False


def calculate_path_size(
    path: Path,
    follow_symlinks: bool = False,
    exclude_patterns: Optional[list[str]] = None,
    seen_inodes: Optional[set[tuple[int, int]]] = None,
) -> SizeInfo:
    """
    Calculate the size of a path (file or directory).
    
    Args:
        path: Path to calculate size for
        follow_symlinks: Whether to follow symbolic links
        exclude_patterns: List of glob patterns to exclude
        seen_inodes: Set of (device, inode) tuples to deduplicate hardlinks
    
    Returns:
        SizeInfo object with size information
    """
    exclude_patterns = exclude_patterns or []
    seen_inodes = seen_inodes or set()
    
    info = SizeInfo()
    
    try:
        # Check if path exists
        if not path.exists():
            return info
        
        # Check if should exclude
        if should_exclude(path, exclude_patterns):
            return info
        
        # Handle symlinks
        if path.is_symlink() and not follow_symlinks:
            # Count the symlink itself, not what it points to
            try:
                stat = path.lstat()
                inode_key = (stat.st_dev, stat.st_ino)
                if inode_key not in seen_inodes:
                    seen_inodes.add(inode_key)
                    info.size_bytes = stat.st_size
                    info.file_count = 1
                    info.files.append((path, stat.st_size))
            except (OSError, PermissionError):
                pass
            return info
        
        # Handle files
        if path.is_file():
            try:
                stat = path.stat()
                inode_key = (stat.st_dev, stat.st_ino)
                
                # Deduplicate hardlinks
                if inode_key not in seen_inodes:
                    seen_inodes.add(inode_key)
                    info.size_bytes = stat.st_size
                    info.file_count = 1
                    info.files.append((path, stat.st_size))
            except (OSError, PermissionError):
                pass
            return info
        
        # Handle directories
        if path.is_dir():
            try:
                for entry in os.scandir(path):
                    entry_path = Path(entry.path)
                    entry_info = calculate_path_size(
                        entry_path,
                        follow_symlinks=follow_symlinks,
                        exclude_patterns=exclude_patterns,
                        seen_inodes=seen_inodes,
                    )
                    info.add(entry_info)
            except (OSError, PermissionError):
                pass
            return info
        
    except Exception:
        pass
    
    return info


def calculate_distribution_size(
    dist_files: list[Path],
    follow_symlinks: bool = False,
    exclude_patterns: Optional[list[str]] = None,
) -> SizeInfo:
    """
    Calculate the total size of a distribution's files.
    
    Args:
        dist_files: List of file paths belonging to the distribution
        follow_symlinks: Whether to follow symbolic links
        exclude_patterns: List of glob patterns to exclude
    
    Returns:
        SizeInfo object with size information
    """
    seen_inodes: set[tuple[int, int]] = set()
    total_info = SizeInfo()
    
    for file_path in dist_files:
        file_info = calculate_path_size(
            file_path,
            follow_symlinks=follow_symlinks,
            exclude_patterns=exclude_patterns,
            seen_inodes=seen_inodes,
        )
        total_info.add(file_info)
    
    return total_info


def calculate_editable_size(
    editable_location: Path,
    follow_symlinks: bool = False,
    exclude_patterns: Optional[list[str]] = None,
) -> SizeInfo:
    """
    Calculate the size of an editable install.
    
    Args:
        editable_location: Path to the editable source
        follow_symlinks: Whether to follow symbolic links
        exclude_patterns: List of glob patterns to exclude
    
    Returns:
        SizeInfo object with size information
    """
    # Add common patterns to exclude for editable installs
    common_excludes = [
        "*.pyc",
        "__pycache__",
        "*.egg-info",
        ".git",
        ".svn",
        ".hg",
        "node_modules",
        ".tox",
        ".nox",
        "build",
        "dist",
    ]
    
    all_excludes = (exclude_patterns or []) + common_excludes
    
    return calculate_path_size(
        editable_location,
        follow_symlinks=follow_symlinks,
        exclude_patterns=all_excludes,
    )


def calculate_sizes_parallel(
    items: list[tuple[str, list[Path]]],
    follow_symlinks: bool = False,
    exclude_patterns: Optional[list[str]] = None,
    max_workers: int = 4,
) -> dict[str, SizeInfo]:
    """
    Calculate sizes for multiple distributions in parallel.
    
    Args:
        items: List of (name, files) tuples
        follow_symlinks: Whether to follow symbolic links
        exclude_patterns: List of glob patterns to exclude
        max_workers: Maximum number of worker threads
    
    Returns:
        Dictionary mapping name to SizeInfo
    """
    results: dict[str, SizeInfo] = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        
        for name, files in items:
            future = executor.submit(
                calculate_distribution_size,
                files,
                follow_symlinks,
                exclude_patterns,
            )
            futures[future] = name
        
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception:
                results[name] = SizeInfo()
    
    return results

