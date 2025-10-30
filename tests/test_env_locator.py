"""Tests for env_locator module."""

import sys
from pathlib import Path
import pytest

from pkgsizer.env_locator import locate_site_packages


def test_locate_site_packages_current_env():
    """Test locating site-packages for current environment."""
    site_packages = locate_site_packages()
    assert site_packages.exists()
    assert site_packages.is_dir()
    assert "site-packages" in str(site_packages)


def test_locate_site_packages_invalid_path():
    """Test error handling for invalid paths."""
    with pytest.raises(ValueError):
        locate_site_packages(site_packages_path=Path("/nonexistent/path"))


def test_locate_site_packages_invalid_venv():
    """Test error handling for invalid venv."""
    with pytest.raises(ValueError):
        locate_site_packages(venv_path=Path("/nonexistent/venv"))

