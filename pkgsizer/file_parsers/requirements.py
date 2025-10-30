"""Parse requirements.txt and pip-tools files."""

from pathlib import Path
from packaging.requirements import Requirement


def parse_requirements(file_path: Path) -> list[str]:
    """
    Parse a requirements.txt file.
    
    Args:
        file_path: Path to requirements.txt
    
    Returns:
        List of package names
    """
    packages: list[str] = []
    
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Skip options
            if line.startswith("-"):
                continue
            
            # Handle inline comments
            if "#" in line:
                line = line.split("#")[0].strip()
            
            # Try to parse as requirement
            try:
                req = Requirement(line)
                packages.append(req.name)
            except Exception:
                # If parsing fails, try to extract just the package name
                # Handle cases like "package==1.0.0" or "package>=1.0.0"
                for sep in ["==", ">=", "<=", ">", "<", "~=", "!="]:
                    if sep in line:
                        pkg_name = line.split(sep)[0].strip()
                        if pkg_name:
                            packages.append(pkg_name)
                        break
                else:
                    # No version specifier, treat whole line as package name
                    if line and not line.startswith("http"):
                        packages.append(line)
    
    return packages

