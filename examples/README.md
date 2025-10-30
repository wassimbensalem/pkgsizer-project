# pkgsizer Examples

This directory contains example scripts demonstrating various uses of pkgsizer.

## Basic Usage

Run the basic usage example:

```bash
python examples/basic_usage.py
```

This demonstrates:
- Scanning the current environment
- Analyzing specific packages
- Using exclusion patterns
- Displaying results

## Command Line Examples

### Quick Scan

```bash
# Scan current environment and show top 10
pkgsizer scan-env --top 10
```

### Analyze Dependencies

```bash
# Create a sample requirements.txt
cat > /tmp/requirements.txt << EOF
requests>=2.26.0
numpy>=1.20.0
pandas>=1.3.0
EOF

# Analyze it
pkgsizer analyze-file /tmp/requirements.txt
```

### Dependency Depth

```bash
# Show only direct dependencies (depth 0)
pkgsizer scan-env --depth 0

# Show direct and first-level transitive (depth 1)
pkgsizer scan-env --depth 1 --tree
```

### Module Depth

```bash
# Analyze numpy with subpackages
pkgsizer scan-env --package numpy --module-depth 2 --tree
```

### JSON Export

```bash
# Export to JSON
pkgsizer scan-env --json /tmp/sizes.json

# Pretty print the JSON
cat /tmp/sizes.json | python -m json.tool | head -50
```

### Size Thresholds

```bash
# Fail if environment exceeds 1GB
pkgsizer scan-env --fail-over 1GB
echo "Exit code: $?"
```

## Integration Examples

### Docker Optimization

```dockerfile
# In your Dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Analyze what was installed
RUN pip install pkgsizer && \
    pkgsizer analyze-file requirements.txt --json /sizes.json && \
    cat /sizes.json
```

### CI/CD Pipeline

```yaml
# In .github/workflows/check-size.yml
name: Check Package Sizes
on: [pull_request]
jobs:
  check-sizes:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pkgsizer
      - name: Check sizes
        run: |
          pkgsizer analyze-file requirements.txt --fail-over 500MB --json sizes.json
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: package-sizes
          path: sizes.json
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
if [ -f requirements.txt ]; then
    pkgsizer analyze-file requirements.txt --fail-over 1GB
    if [ $? -ne 0 ]; then
        echo "Error: Package sizes exceed 1GB limit"
        exit 1
    fi
fi
```

