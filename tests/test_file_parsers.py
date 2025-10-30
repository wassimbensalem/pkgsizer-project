"""Tests for file parsers."""

import tempfile
from pathlib import Path

from pkgsizer.file_parsers.requirements import parse_requirements
from pkgsizer.file_parsers.poetry import parse_poetry
from pkgsizer.file_parsers.uv import parse_uv, extract_package_name
from pkgsizer.file_parsers.conda import parse_conda, extract_conda_package_name


def test_parse_requirements():
    """Test parsing requirements.txt."""
    content = """
# This is a comment
numpy>=1.20.0
pandas==1.3.0
requests
# Another comment
scipy>=1.7.0
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)
    
    try:
        packages = parse_requirements(temp_path)
        assert "numpy" in packages
        assert "pandas" in packages
        assert "requests" in packages
        assert "scipy" in packages
    finally:
        temp_path.unlink()


def test_parse_poetry_pyproject():
    """Test parsing Poetry pyproject.toml."""
    content = """
[tool.poetry]
name = "test-project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.9"
numpy = "^1.20.0"
pandas = "^1.3.0"

[tool.poetry.dev-dependencies]
pytest = "^7.0.0"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)
    
    try:
        packages = parse_poetry(temp_path)
        assert "numpy" in packages
        assert "pandas" in packages
        assert "pytest" in packages
        assert "python" not in packages
    finally:
        temp_path.unlink()


def test_parse_uv_pyproject():
    """Test parsing pyproject.toml with [project] section."""
    content = """
[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "numpy>=1.20.0",
    "pandas>=1.3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
]
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)
    
    try:
        packages = parse_uv(temp_path)
        assert "numpy" in packages
        assert "pandas" in packages
        assert "pytest" in packages
    finally:
        temp_path.unlink()


def test_extract_package_name():
    """Test extracting package names from dependency specifiers."""
    assert extract_package_name("numpy>=1.20.0") == "numpy"
    assert extract_package_name("pandas[extra]>=1.3.0") == "pandas"
    assert extract_package_name("requests") == "requests"
    assert extract_package_name("scipy==1.7.0") == "scipy"


def test_parse_conda():
    """Test parsing Conda environment.yml."""
    content = """
name: test-env
dependencies:
  - python=3.9
  - numpy=1.20.0
  - pandas>=1.3.0
  - pip:
    - requests>=2.26.0
    - scipy
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)
    
    try:
        packages = parse_conda(temp_path)
        assert "numpy" in packages
        assert "pandas" in packages
        assert "requests" in packages
        assert "scipy" in packages
        assert "python" not in packages
    finally:
        temp_path.unlink()


def test_extract_conda_package_name():
    """Test extracting package names from conda specifiers."""
    assert extract_conda_package_name("numpy=1.20.0") == "numpy"
    assert extract_conda_package_name("pandas>=1.3.0") == "pandas"
    assert extract_conda_package_name("conda-forge::numpy") == "numpy"
    assert extract_conda_package_name("requests") == "requests"

