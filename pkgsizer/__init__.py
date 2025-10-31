"""
pkgsizer: Python Package Size Analyzer

A comprehensive tool for analyzing Python package disk sizes and dependencies.
Helps developers optimize Docker images, find unused dependencies, analyze
dependency trees, compare environments, and reduce project footprints.

Key Features:
- Measure on-disk sizes of installed Python packages
- Analyze dependency trees with configurable depth
- Find unused dependencies by scanning code
- Suggest lighter package alternatives
- Compare different Python environments
- Support for requirements.txt, Poetry, uv, Conda files
- JSON export for CI/CD integration

Use Cases:
- Docker image optimization
- Dependency cleanup and auditing
- Environment size comparison
- CI/CD size threshold enforcement

Example:
    >>> from pkgsizer import scan_environment
    >>> results = scan_environment()
    >>> print(f"Total size: {results.total_size_bytes} bytes")

Command Line:
    $ pkgsizer scan-env --top 10
    $ pkgsizer why numpy
    $ pkgsizer unused ./src
    $ pkgsizer alternatives pandas
    $ pkgsizer compare env1 env2

Project: https://github.com/YOUR_USERNAME/pkgsizer
PyPI: https://pypi.org/project/pkgsizer/
"""

__version__ = "0.1.1"

__all__ = ["__version__"]

