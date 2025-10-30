# pkgsizer Quick Start Guide

Get up and running with pkgsizer in 5 minutes!

## Installation

```bash
# Clone the repository
cd /Users/wassimbensalem/pkgsizer-project

# Install in development mode
pip install -e .
```

Or install directly:

```bash
pip install pkgsizer
```

## Your First Scan

### 1. Scan Your Current Environment

```bash
pkgsizer scan-env
```

This will show you all packages in your current Python environment with their sizes.

### 2. See Top 10 Largest Packages

```bash
pkgsizer scan-env --top 10
```

### 3. Export to JSON

```bash
pkgsizer scan-env --json my-packages.json
```

## Common Use Cases

### Check a Requirements File

```bash
# Create a test requirements file
cat > /tmp/test-requirements.txt << 'EOF'
requests>=2.26.0
numpy>=1.20.0
pandas>=1.3.0
EOF

# Analyze it
pkgsizer analyze-file /tmp/test-requirements.txt
```

### Analyze Specific Package

```bash
# Look at just one package
pkgsizer scan-env --package numpy

# See its subpackages
pkgsizer scan-env --package numpy --module-depth 2 --tree
```

### Limit Dependency Depth

```bash
# Only show direct dependencies (depth 0)
pkgsizer scan-env --depth 0

# Show direct + 1 level of transitive
pkgsizer scan-env --depth 1
```

### Set Size Limits

```bash
# Fail if environment exceeds 1GB
pkgsizer scan-env --fail-over 1GB
echo "Exit code: $?"
```

## Understanding the Output

### Table Columns

- **Package**: Package name
- **Version**: Installed version
- **Size**: On-disk size (human-readable)
- **Files**: Number of files
- **Depth**: Dependency depth (0 = direct, 1+ = transitive)
- **Type**: direct or transitive
- **Editable**: ✓ if installed in editable mode

### Size Units

- B = Bytes
- KB = Kilobytes (1,024 bytes)
- MB = Megabytes (1,024 KB)
- GB = Gigabytes (1,024 MB)
- TB = Terabytes (1,024 GB)

## Advanced Examples

### Exclude Patterns

```bash
# Exclude compiled files and caches
pkgsizer scan-env --exclude "*.pyc" --exclude "__pycache__"
```

### Multiple Packages

```bash
# Analyze multiple packages at once
pkgsizer scan-env --package numpy --package pandas --package scipy
```

### Virtual Environment

```bash
# Scan a specific venv
pkgsizer scan-env --venv /path/to/venv
```

### Sort by File Count

```bash
# See which packages have the most files
pkgsizer scan-env --by files --top 10
```

## JSON Output Format

The JSON output contains:

```json
{
  "version": "1.0",
  "site_packages": "/path/to/site-packages",
  "total_size_bytes": 123456789,
  "total_files": 1234,
  "package_count": 50,
  "packages": [...]
}
```

Each package includes:
- name, version
- size_bytes, file_count
- depth, direct (boolean)
- editable (boolean)
- location (path)
- subpackages (if requested)

## Programmatic Usage

You can also use pkgsizer as a Python library:

```python
from pathlib import Path
from pkgsizer.env_locator import locate_site_packages
from pkgsizer.scanner import scan_environment
from pkgsizer.report import format_size

# Scan current environment
site_packages = locate_site_packages()
results = scan_environment(
    site_packages_path=site_packages,
    depth=2,
)

# Show results
print(f"Total: {format_size(results.total_size)}")
for pkg in results.packages[:5]:
    print(f"  {pkg.dist_info.name}: {format_size(pkg.total_size)}")
```

## Troubleshooting

### Package Not Found

If pkgsizer can't find a package:
1. Make sure it's installed: `pip list | grep package-name`
2. Check you're using the right environment: `which python`
3. Specify the environment explicitly: `--venv /path/to/venv`

### Permission Errors

If you see permission errors:
1. You might be scanning a system Python
2. Try using a virtual environment instead
3. Or use `--exclude` to skip problematic directories

### Slow Scans

For large environments:
1. Use `--depth` to limit dependency traversal
2. Use `--module-depth` to limit subpackage scanning
3. Use `--top N` to limit output
4. Target specific `--package` names

## Getting Help

```bash
# General help
pkgsizer --help

# Command-specific help
pkgsizer scan-env --help
pkgsizer analyze-file --help

# Version
pkgsizer --version
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [examples/](examples/) for more use cases
- See [IMPLEMENTATION.md](IMPLEMENTATION.md) for technical details

## Tips

1. **Start small**: Use `--top 10` to see just the largest packages
2. **Use JSON**: Export to JSON for further analysis with jq or Python
3. **Set budgets**: Use `--fail-over` in CI/CD to enforce size limits
4. **Combine flags**: Mix depth, module-depth, and patterns for precise control
5. **Compare environments**: Export multiple environments to JSON and diff them

Happy analyzing! 🎉

