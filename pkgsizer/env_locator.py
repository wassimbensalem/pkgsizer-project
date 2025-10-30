"""Locate site-packages directories and detect editable installs."""

import subprocess
import sys
from pathlib import Path
from typing import Optional


def locate_site_packages(
    python_path: Optional[Path] = None,
    venv_path: Optional[Path] = None,
    site_packages_path: Optional[Path] = None,
) -> Path:
    """
    Locate the site-packages directory for a Python environment.
    
    Args:
        python_path: Path to Python interpreter
        venv_path: Path to virtual environment
        site_packages_path: Direct path to site-packages
    
    Returns:
        Path to site-packages directory
    
    Raises:
        ValueError: If site-packages cannot be located
    """
    # Priority 1: Direct site-packages path
    if site_packages_path:
        if not site_packages_path.exists():
            raise ValueError(f"site-packages path does not exist: {site_packages_path}")
        if not site_packages_path.is_dir():
            raise ValueError(f"site-packages path is not a directory: {site_packages_path}")
        return site_packages_path.resolve()
    
    # Priority 2: Virtual environment path
    if venv_path:
        if not venv_path.exists():
            raise ValueError(f"Virtual environment does not exist: {venv_path}")
        
        # Look for site-packages in common locations
        candidates = [
            venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages",
            venv_path / "Lib" / "site-packages",  # Windows
        ]
        
        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate.resolve()
        
        raise ValueError(f"Could not find site-packages in virtual environment: {venv_path}")
    
    # Priority 3: Python interpreter path
    if python_path:
        if not python_path.exists():
            raise ValueError(f"Python interpreter does not exist: {python_path}")
        
        try:
            result = subprocess.run(
                [str(python_path), "-c", "import site; print(site.getsitepackages()[0])"],
                capture_output=True,
                text=True,
                check=True,
            )
            site_packages = Path(result.stdout.strip())
            if site_packages.exists() and site_packages.is_dir():
                return site_packages.resolve()
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to get site-packages from Python interpreter: {e}")
    
    # Priority 4: Current Python environment
    try:
        import site
        site_packages_list = site.getsitepackages()
        if site_packages_list:
            site_packages = Path(site_packages_list[0])
            if site_packages.exists() and site_packages.is_dir():
                return site_packages.resolve()
    except Exception as e:
        raise ValueError(f"Failed to get site-packages from current environment: {e}")
    
    raise ValueError("Could not locate site-packages directory")


def is_editable_install(dist_path: Path) -> bool:
    """
    Check if a distribution is an editable install.
    
    Args:
        dist_path: Path to the distribution's .dist-info directory
    
    Returns:
        True if this is an editable install
    """
    # Check for direct_url.json with "editable": true
    direct_url_file = dist_path / "direct_url.json"
    if direct_url_file.exists():
        try:
            import json
            with open(direct_url_file) as f:
                data = json.load(f)
                if data.get("dir_info", {}).get("editable") is True:
                    return True
        except Exception:
            pass
    
    # Check for .pth files (legacy editable installs)
    pth_files = list(dist_path.glob("*.pth"))
    if pth_files:
        return True
    
    return False


def get_editable_location(dist_path: Path) -> Optional[Path]:
    """
    Get the actual source location for an editable install.
    
    Args:
        dist_path: Path to the distribution's .dist-info directory
    
    Returns:
        Path to the editable source, or None if not editable
    """
    # Check direct_url.json
    direct_url_file = dist_path / "direct_url.json"
    if direct_url_file.exists():
        try:
            import json
            with open(direct_url_file) as f:
                data = json.load(f)
                if data.get("dir_info", {}).get("editable"):
                    url = data.get("url", "")
                    if url.startswith("file://"):
                        path = url[7:]  # Remove file:// prefix
                        return Path(path)
        except Exception:
            pass
    
    # Check .pth files
    pth_files = list(dist_path.glob("*.pth"))
    for pth_file in pth_files:
        try:
            with open(pth_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        path = Path(line)
                        if path.exists():
                            return path.resolve()
        except Exception:
            pass
    
    return None

