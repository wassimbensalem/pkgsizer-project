"""Enumerate distributions and extract metadata."""

import sys
from importlib.metadata import distributions, Distribution, PackageNotFoundError
from pathlib import Path
from typing import Optional

from packaging.requirements import Requirement
from packaging.markers import default_environment

from pkgsizer.env_locator import is_editable_install, get_editable_location


class DistributionInfo:
    """Information about a Python distribution."""
    
    def __init__(
        self,
        name: str,
        version: str,
        location: Path,
        editable: bool = False,
        editable_location: Optional[Path] = None,
    ):
        self.name = name
        self.version = version
        self.location = location
        self.editable = editable
        self.editable_location = editable_location
        self.requires: list[str] = []
        self.top_level: list[str] = []
        self.files: list[Path] = []
    
    def __repr__(self) -> str:
        return f"DistributionInfo({self.name}=={self.version}, editable={self.editable})"


def enumerate_distributions(site_packages: Path) -> dict[str, DistributionInfo]:
    """
    Enumerate all distributions in a site-packages directory.
    
    Args:
        site_packages: Path to site-packages directory
    
    Returns:
        Dictionary mapping distribution name to DistributionInfo
    """
    result: dict[str, DistributionInfo] = {}
    
    # Find all .dist-info directories
    dist_info_dirs = list(site_packages.glob("*.dist-info"))
    
    for dist_info_dir in dist_info_dirs:
        try:
            # Extract name from directory (remove .dist-info and version suffix)
            dir_name = dist_info_dir.name
            if not dir_name.endswith(".dist-info"):
                continue
            
            # Parse METADATA file for canonical name
            metadata_file = dist_info_dir / "METADATA"
            if not metadata_file.exists():
                continue
            
            name = None
            version = None
            
            with open(metadata_file, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.startswith("Name: "):
                        name = line[6:].strip()
                    elif line.startswith("Version: "):
                        version = line[9:].strip()
                    
                    if name and version:
                        break
            
            if not name or not version:
                continue
            
            # Check if editable
            editable = is_editable_install(dist_info_dir)
            editable_location = get_editable_location(dist_info_dir) if editable else None
            
            dist_info = DistributionInfo(
                name=name,
                version=version,
                location=dist_info_dir,
                editable=editable,
                editable_location=editable_location,
            )
            
            # Get requires
            requires_file = dist_info_dir / "METADATA"
            if requires_file.exists():
                with open(requires_file, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.startswith("Requires-Dist: "):
                            req_str = line[15:].strip()
                            dist_info.requires.append(req_str)
            
            # Get top-level modules
            top_level_file = dist_info_dir / "top_level.txt"
            if top_level_file.exists():
                with open(top_level_file, encoding="utf-8") as f:
                    dist_info.top_level = [line.strip() for line in f if line.strip()]
            
            # Get files list
            record_file = dist_info_dir / "RECORD"
            if record_file.exists():
                with open(record_file, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        parts = line.strip().split(",")
                        if parts:
                            file_path = site_packages / parts[0]
                            if file_path.exists():
                                dist_info.files.append(file_path)
            
            result[name.lower()] = dist_info
            
        except Exception as e:
            # Skip distributions that fail to parse
            print(f"Warning: Failed to parse {dist_info_dir}: {e}", file=sys.stderr)
            continue
    
    return result


def get_dependencies(
    dist_info: DistributionInfo,
    include_extras: Optional[set[str]] = None,
) -> list[str]:
    """
    Get the dependencies for a distribution.
    
    Args:
        dist_info: Distribution information
        include_extras: Optional set of extras to include
    
    Returns:
        List of dependency package names
    """
    deps: list[str] = []
    env = default_environment()
    
    for req_str in dist_info.requires:
        try:
            req = Requirement(req_str)
            
            # Check if markers match current environment
            if req.marker and not req.marker.evaluate(env):
                continue
            
            # Check if this is an extra requirement
            if req.marker and "extra" in str(req.marker):
                if not include_extras:
                    continue
                # Parse extra from marker (simplified)
                extra_matched = False
                for extra in include_extras:
                    if f"extra == '{extra}'" in str(req.marker) or f'extra == "{extra}"' in str(req.marker):
                        extra_matched = True
                        break
                if not extra_matched:
                    continue
            
            deps.append(req.name.lower())
        except Exception:
            continue
    
    return deps

