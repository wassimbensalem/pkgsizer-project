"""Parse various dependency file formats."""

from pathlib import Path
from typing import Optional

from pkgsizer.file_parsers.requirements import parse_requirements
from pkgsizer.file_parsers.poetry import parse_poetry
from pkgsizer.file_parsers.uv import parse_uv
from pkgsizer.file_parsers.conda import parse_conda


def parse_dependency_file(file_path: Path) -> list[str]:
    """
    Parse a dependency file and extract package names.
    
    Args:
        file_path: Path to dependency file
    
    Returns:
        List of package names
    
    Raises:
        ValueError: If file format is not supported
    """
    file_name = file_path.name.lower()
    
    # Requirements.txt and variants
    if "requirements" in file_name or file_name.endswith(".txt"):
        return parse_requirements(file_path)
    
    # Poetry
    if file_name == "pyproject.toml":
        # Check if it's Poetry or uv
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            if "[tool.poetry]" in content:
                return parse_poetry(file_path)
            elif "[tool.uv]" in content or "[project]" in content:
                # Try uv first, fall back to pyproject.toml [project] parsing
                return parse_uv(file_path)
            elif "[project]" in content:
                # Standard pyproject.toml with [project] section
                return parse_uv(file_path)  # Reuse uv parser for [project]
    
    if file_name == "poetry.lock":
        return parse_poetry(file_path)
    
    # UV
    if file_name == "uv.lock":
        return parse_uv(file_path)
    
    # Conda
    if file_name in ("environment.yml", "environment.yaml"):
        return parse_conda(file_path)
    
    raise ValueError(f"Unsupported dependency file format: {file_path}")

