"""Parse Conda environment.yml files."""

from pathlib import Path


def parse_conda(file_path: Path) -> list[str]:
    """
    Parse a Conda environment.yml file.
    
    Args:
        file_path: Path to environment.yml
    
    Returns:
        List of package names
    """
    packages: list[str] = []

    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Parsing Conda files requires PyYAML. Install pkgsizer[yaml] and retry."
        ) from exc

    with open(file_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    if not data:
        return packages
    
    # Get dependencies
    dependencies = data.get("dependencies", [])
    
    for dep in dependencies:
        if isinstance(dep, str):
            # Handle conda dependencies like "numpy=1.20.0" or "python>=3.9"
            pkg_name = extract_conda_package_name(dep)
            if pkg_name and pkg_name.lower() != "python":
                packages.append(pkg_name)
        
        elif isinstance(dep, dict):
            # Handle pip dependencies
            if "pip" in dep:
                pip_deps = dep["pip"]
                if isinstance(pip_deps, list):
                    for pip_dep in pip_deps:
                        pkg_name = extract_conda_package_name(pip_dep)
                        if pkg_name and pkg_name not in packages:
                            packages.append(pkg_name)
    
    return packages


def extract_conda_package_name(dep_spec: str) -> str:
    """
    Extract package name from a conda dependency specifier.
    
    Args:
        dep_spec: Dependency specifier (e.g., "numpy=1.20.0" or "numpy>=1.20")
    
    Returns:
        Package name
    """
    # Remove channel prefix if present (e.g., "conda-forge::numpy")
    if "::" in dep_spec:
        dep_spec = dep_spec.split("::")[-1]
    
    # Extract package name before version specifier
    for sep in ["==", ">=", "<=", ">", "<", "=", " "]:
        if sep in dep_spec:
            return dep_spec.split(sep)[0].strip()
    
    return dep_spec.strip()

