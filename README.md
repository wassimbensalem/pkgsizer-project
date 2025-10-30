# pkgsizer

A Python package size analyzer that measures installed on-disk sizes of Python packages and their subpackages.

## Features

### Core Features
- 📦 **Measure Package Sizes**: Calculate on-disk sizes for installed Python packages
- 🌳 **Dependency Tree Analysis**: Track sizes through dependency graph with configurable depth
- 📂 **Subpackage Enumeration**: Drill down into package submodules to specific depth levels
- 🔄 **Multiple Input Formats**: Support for `requirements.txt`, Poetry, uv, pip-tools, and Conda files
- 📊 **Rich Output**: Beautiful terminal tables and JSON export
- 🎯 **Editable Install Support**: Detect and properly handle editable installs
- 🚀 **Performance**: Fast parallel scanning with inode deduplication

### 🆕 Week 1 Features
- 🔍 **`pkgsizer why`**: Trace why a package is installed - see all dependency paths
- 🗑️ **`pkgsizer unused`**: Find dependencies never imported in your code
- 🌲 **Fixed Tree Display**: Proper parent-child relationships in dependency trees

### 🎉 Week 2 Features (NEW!)
- 💡 **`pkgsizer alternatives`**: Suggest lighter or better alternative packages
- ⬆️ **`pkgsizer updates`**: Check for outdated packages and available updates
- 🔄 **`pkgsizer compare`**: Compare two Python environments side-by-side

## Installation

```bash
pip install pkgsizer
```

Or install from source:

```bash
git clone https://github.com/yourusername/pkgsizer.git
cd pkgsizer
pip install -e .
```

## Quick Start

### Scan Current Environment

```bash
# Scan all packages in current Python environment
pkgsizer scan-env

# Show only top 10 largest packages
pkgsizer scan-env --top 10

# Include dependency tree visualization
pkgsizer scan-env --tree

# Export results to JSON
pkgsizer scan-env --json results.json
```

### 🆕 Find Why a Package is Installed

```bash
# See all dependency paths to a package
pkgsizer why numpy

# Find out if you can safely remove it
pkgsizer why boto3

# Export to JSON
pkgsizer why tensorflow --json why-tf.json
```

### 🆕 Find Unused Dependencies

```bash
# Scan your code for unused packages
pkgsizer unused ./src

# See potential space savings
pkgsizer unused ./app

# Export for automation
pkgsizer unused ./src --json unused.json
```

### 🎉 Find Alternative Packages

```bash
# Get alternatives for a specific package
pkgsizer alternatives pandas

# Browse all known alternatives
pkgsizer alternatives --list-all

# Check all installed packages with alternatives
pkgsizer alternatives
```

### 🎉 Check for Package Updates

```bash
# Check specific packages
pkgsizer updates numpy pandas

# Check all packages (can be slow)
pkgsizer updates --all

# Export results
pkgsizer updates typer rich --json updates.json
```

### 🎉 Compare Two Environments

```bash
# Compare two environments
pkgsizer compare ./dev_venv ./prod_venv

# With custom names
pkgsizer compare env1 env2 --name1 "Development" --name2 "Production"

# Export comparison
pkgsizer compare env1 env2 --json comparison.json
```

### Analyze Dependency File

```bash
# Analyze packages from requirements.txt
pkgsizer analyze-file requirements.txt

# Analyze Poetry project
pkgsizer analyze-file pyproject.toml

# Analyze uv project
pkgsizer analyze-file uv.lock

# Analyze Conda environment
pkgsizer analyze-file environment.yml
```

## Usage Examples

### Basic Scanning

```bash
# Scan with default Python environment
pkgsizer scan-env

# Scan specific virtual environment
pkgsizer scan-env --venv /path/to/venv

# Scan specific Python interpreter
pkgsizer scan-env --python /usr/bin/python3.11

# Scan specific site-packages directory
pkgsizer scan-env --site-packages /path/to/site-packages
```

### Depth Control

```bash
# Limit dependency graph depth to 2 levels
pkgsizer scan-env --depth 2

# Limit subpackage enumeration to 3 levels
pkgsizer scan-env --module-depth 3

# Combine both limits
pkgsizer scan-env --depth 2 --module-depth 3
```

### Filtering and Sorting

```bash
# Show only top 20 packages by size
pkgsizer scan-env --top 20

# Sort by file count instead of size
pkgsizer scan-env --by files

# Exclude patterns
pkgsizer scan-env --exclude "*.pyc" --exclude "__pycache__"

# Analyze specific packages only
pkgsizer scan-env --package numpy --package pandas
```

### Editable Installs

```bash
# Mark editable installs (default)
pkgsizer scan-env --include-editable mark

# Include editable installs without special marking
pkgsizer scan-env --include-editable include

# Exclude editable installs completely
pkgsizer scan-env --include-editable exclude
```

### JSON Output

```bash
# Save to file
pkgsizer scan-env --json results.json

# Output to stdout (useful for piping)
pkgsizer scan-env --json -

# Pretty JSON with tree view
pkgsizer scan-env --json results.json --tree
```

### CI/CD Integration

```bash
# Fail if total size exceeds threshold
pkgsizer scan-env --fail-over 500MB

# Exit code 1 if threshold exceeded
pkgsizer analyze-file requirements.txt --fail-over 1GB --json - > sizes.json
```

## CLI Reference

### `scan-env` Command

Scan an installed Python environment.

```
pkgsizer scan-env [OPTIONS]
```

**Options:**

- `--python PATH` - Path to Python interpreter
- `--venv PATH` - Path to virtual environment
- `--site-packages PATH` - Direct path to site-packages directory
- `--depth N` - Maximum dependency graph depth (default: unlimited)
- `--module-depth N` - Maximum subpackage depth (default: unlimited)
- `--include-editable {mark,include,exclude}` - How to handle editable installs (default: mark)
- `--json PATH` - Output JSON to file (use '-' for stdout)
- `--tree` - Show tree view of packages
- `--group-by {dist,module,file}` - Group results by (default: dist)
- `--exclude PATTERN` - Patterns to exclude (can be used multiple times)
- `--top N` - Show only top N packages by size
- `--by {size,files}` - Sort by size or file count (default: size)
- `--follow-symlinks` - Follow symbolic links
- `--fail-over THRESHOLD` - Exit with error if total exceeds threshold (e.g., '1GB')
- `--package NAME` - Specific packages to analyze (can be used multiple times)

### `analyze-file` Command

Analyze a dependency file.

```
pkgsizer analyze-file FILE [OPTIONS]
```

**Arguments:**

- `FILE` - Path to dependency file (requirements.txt, pyproject.toml, etc.)

**Options:** Same as `scan-env`, plus:

- `--env-site-packages PATH` - Path to site-packages for size lookup

## JSON Schema

The JSON output follows this schema:

```json
{
  "version": "1.0",
  "site_packages": "/path/to/site-packages",
  "total_size_bytes": 123456789,
  "total_files": 1234,
  "package_count": 50,
  "packages": [
    {
      "name": "numpy",
      "version": "1.24.0",
      "size_bytes": 45678901,
      "file_count": 234,
      "depth": 0,
      "direct": true,
      "editable": false,
      "location": "/path/to/site-packages/numpy-1.24.0.dist-info",
      "subpackages": [
        {
          "name": "numpy",
          "qualified_name": "numpy",
          "path": "/path/to/site-packages/numpy",
          "depth": 0,
          "is_package": true,
          "size_bytes": 45000000,
          "file_count": 200,
          "children": [
            {
              "name": "linalg",
              "qualified_name": "numpy.linalg",
              "path": "/path/to/site-packages/numpy/linalg",
              "depth": 1,
              "is_package": true,
              "size_bytes": 5000000,
              "file_count": 20
            }
          ]
        }
      ]
    }
  ]
}
```

## Supported File Formats

### requirements.txt

Standard pip requirements format:

```txt
numpy>=1.20.0
pandas==1.3.0
requests
```

### Poetry (pyproject.toml / poetry.lock)

```toml
[tool.poetry.dependencies]
numpy = "^1.20.0"
pandas = "^1.3.0"
```

### uv (pyproject.toml / uv.lock)

PEP 621 format:

```toml
[project]
dependencies = [
    "numpy>=1.20.0",
    "pandas>=1.3.0",
]
```

### Conda (environment.yml)

```yaml
dependencies:
  - numpy=1.20.0
  - pandas>=1.3.0
  - pip:
    - requests>=2.26.0
```

## Use Cases

### Optimize Docker Images

```bash
# Analyze production dependencies
pkgsizer analyze-file requirements.txt --json sizes.json

# Find largest dependencies
pkgsizer analyze-file requirements.txt --top 20

# Set size budget
pkgsizer analyze-file requirements.txt --fail-over 500MB
```

### Machine Learning Dependencies

```bash
# Analyze ML stack
pkgsizer scan-env --package torch --package tensorflow --tree

# Compare environments
pkgsizer scan-env --venv env1 --json env1.json
pkgsizer scan-env --venv env2 --json env2.json
```

### Monorepo Analysis

```bash
# Scan with editable installs
pkgsizer scan-env --include-editable mark --tree

# Check nested packages
pkgsizer scan-env --module-depth 5 --package mypackage
```

## Performance

- **Parallel Scanning**: Uses thread pool for I/O-bound operations
- **Inode Deduplication**: Avoids counting hardlinks multiple times
- **Smart Caching**: Caches directory size calculations
- **Pattern Exclusion**: Early pruning of excluded paths

## Limitations

- Phase 1 focuses on installed on-disk sizes (not wheel/download sizes)
- Import-time memory footprint analysis is planned for later
- Windows support coming in future release

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check pkgsizer

# Type checking
mypy pkgsizer
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Roadmap

- [ ] Wheel download size estimation
- [ ] Import-time memory sampling
- [ ] Docker layer attribution
- [ ] Windows support
- [ ] HTML report generation
- [ ] Cache integration for faster repeated scans
- [ ] Plugin system for custom analyzers

## Related Projects

- [pipdeptree](https://github.com/tox-dev/pipdeptree) - Display dependency tree
- [pip-audit](https://github.com/pypa/pip-audit) - Security vulnerability scanner
- [deptry](https://github.com/fpgmaas/deptry) - Find unused dependencies

## Acknowledgments

Built with:
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [packaging](https://packaging.pypa.io/) - Python packaging utilities

