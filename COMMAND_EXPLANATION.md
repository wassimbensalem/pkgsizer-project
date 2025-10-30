# pkgsizer Command Explanation

## What Do the Commands Do?

### `scan-env` Command

**Purpose**: Scans an **installed** Python environment and analyzes package sizes.

**What it does:**
1. Locates your Python environment's `site-packages` directory
2. Enumerates all installed distributions (packages)
3. Builds a dependency graph showing which packages depend on others
4. Calculates the on-disk size for each package
5. Optionally explores subpackages/modules within each package
6. Displays results in a table and/or JSON

**Example workflow:**
```bash
pkgsizer scan-env --package numpy --module-depth 2
```

This will:
- Find where numpy is installed
- Calculate numpy's total size (32.39 MB in your case)
- Enumerate numpy's subpackages up to 2 levels deep (e.g., numpy.linalg, numpy.random)
- Show how much space each subpackage takes

**Use cases:**
- "Which packages are taking up the most space in my environment?"
- "How big are numpy's submodules?"
- "What are my top 10 largest dependencies?"
- "How much space would removing this package save?"

### `analyze-file` Command

**Purpose**: Analyzes package sizes from a **dependency file** (like requirements.txt).

**What it does:**
1. Parses your dependency file (requirements.txt, pyproject.toml, etc.)
2. Extracts the list of package names
3. Looks up those packages in an installed environment
4. Builds a dependency graph (finds transitive dependencies)
5. Calculates sizes for all packages
6. Displays results

**Example workflow:**
```bash
pkgsizer analyze-file requirements.txt
```

This will:
- Read requirements.txt
- Find all packages listed (e.g., numpy, pandas, requests)
- Look them up in your current Python environment
- Calculate their sizes plus their dependencies
- Show you the total footprint

**Use cases:**
- "How big will my Docker image be if I install these requirements?"
- "Which dependency in my requirements.txt pulls in the most stuff?"
- "What's the total size budget for this project?"
- "Before I deploy, how much space will this need?"

## Key Differences

| Feature | scan-env | analyze-file |
|---------|----------|--------------|
| **Input** | Current environment | Dependency file |
| **Packages analyzed** | All installed OR specific ones via `--package` | Only those in the file + their dependencies |
| **Use case** | Audit existing environment | Plan before installing |
| **Requires installation** | Yes (scans what's there) | Yes (needs packages installed to measure) |

## Important Flags

### Depth Control (Both Commands)

#### `--depth N` (Dependency Graph Depth)
Controls how deep to traverse the dependency tree.

**Examples:**
```bash
# Only direct dependencies
pkgsizer scan-env --depth 0

# Direct + one level of transitive
pkgsizer scan-env --depth 1

# Unlimited (default)
pkgsizer scan-env
```

**What it means:**
- Depth 0: Only packages you explicitly requested
- Depth 1: Your packages + their immediate dependencies
- Depth 2: Your packages + dependencies + dependencies of dependencies
- etc.

#### `--module-depth N` (Subpackage Depth)
Controls how deep to explore WITHIN each package.

**Examples:**
```bash
# Top-level modules only
pkgsizer scan-env --package numpy --module-depth 0

# Show subpackages 2 levels deep
pkgsizer scan-env --package numpy --module-depth 2
```

**What it means:**
- Depth 0: Just the package as a whole (numpy: 32 MB)
- Depth 1: Top-level modules (numpy, numpy.linalg, numpy.random)
- Depth 2: Sub-submodules (numpy.linalg.tests, numpy.random.mtrand)

### Output Control

#### `--tree`
Shows a tree visualization of packages and their subpackages.

```bash
pkgsizer scan-env --package numpy --tree
```

Output:
```
numpy (32.39 MB)
├── numpy.linalg (5 MB)
├── numpy.random (8 MB)
└── numpy.fft (2 MB)
```

#### `--json PATH`
Exports results to JSON (useful for automation).

```bash
# Save to file
pkgsizer scan-env --json results.json

# Output to stdout (pipe to jq, etc.)
pkgsizer scan-env --json -
```

#### `--top N`
Shows only the N largest packages.

```bash
pkgsizer scan-env --top 10
```

### Filtering

#### `--package NAME`
Analyzes only specific packages (can use multiple times).

```bash
# Single package
pkgsizer scan-env --package numpy

# Multiple packages
pkgsizer scan-env --package numpy --package pandas --package scipy
```

#### `--exclude PATTERN`
Excludes files matching patterns.

```bash
# Exclude compiled files
pkgsizer scan-env --exclude "*.pyc" --exclude "__pycache__"
```

### CI/CD

#### `--fail-over THRESHOLD`
Exits with error code 1 if total size exceeds threshold.

```bash
# Fail if over 1 GB
pkgsizer scan-env --fail-over 1GB

# Check exit code
echo $?  # 0 = success, 1 = exceeded
```

## Common Workflows

### 1. Quick Environment Check
```bash
pkgsizer scan-env --top 10
```
**Shows:** Your 10 largest packages

### 2. Analyze Before Installing
```bash
# Create requirements.txt
cat > requirements.txt << EOF
torch>=2.0.0
transformers>=4.30.0
EOF

# See what size you'd get
pkgsizer analyze-file requirements.txt
```
**Shows:** Total size if you install these packages

### 3. Deep Dive into a Package
```bash
pkgsizer scan-env --package torch --module-depth 3 --tree
```
**Shows:** torch's submodules and their sizes

### 4. Docker Optimization
```bash
pkgsizer analyze-file requirements.txt --json sizes.json --fail-over 500MB
```
**Shows:** All packages, fails if over 500MB, saves JSON for analysis

### 5. Compare Environments
```bash
# Production
pkgsizer scan-env --venv /path/to/prod --json prod.json

# Staging
pkgsizer scan-env --venv /path/to/staging --json staging.json

# Compare with jq or Python
```
**Shows:** Size differences between environments

## Real-World Example

**Scenario:** You're deploying a ML app to AWS Lambda (size limit: 250 MB).

```bash
# Check current size
pkgsizer analyze-file requirements.txt --fail-over 250MB

# Find culprits
pkgsizer analyze-file requirements.txt --top 5

# Output:
# 1. torch - 150 MB
# 2. transformers - 80 MB
# 3. pandas - 30 MB
# Total: 260 MB ❌ (exceeds 250 MB)

# Optimize: remove pandas, use lightweight alternatives
# Re-check:
pkgsizer analyze-file requirements-optimized.txt --fail-over 250MB
# Total: 230 MB ✅
```

## Understanding the Output

### Table Columns

```
Package   Version   Size       Files  Depth  Type        Editable
numpy     2.3.3     32.39 MB   1519   0      direct      
pandas    1.5.0     20.10 MB   892    1      transitive  ✓
```

- **Package**: Package name
- **Version**: Installed version
- **Size**: On-disk size (human-readable)
- **Files**: Number of files in the package
- **Depth**: Dependency depth (0 = direct, 1+ = transitive)
- **Type**: direct (you requested) or transitive (pulled in as dependency)
- **Editable**: ✓ if installed with `pip install -e`

### JSON Output

```json
{
  "version": "1.0",
  "total_size_bytes": 33932288,
  "total_files": 1519,
  "packages": [
    {
      "name": "numpy",
      "version": "2.3.3",
      "size_bytes": 33932288,
      "depth": 0,
      "direct": true,
      "subpackages": [...]
    }
  ]
}
```

## Tips

1. **Start simple**: `pkgsizer scan-env` to see everything
2. **Focus down**: Use `--package` and `--top` to narrow
3. **Go deep**: Add `--module-depth` to see internal structure
4. **Visualize**: Use `--tree` for hierarchical view
5. **Automate**: Use `--json` and `--fail-over` in CI/CD

## Bug Fix Applied

**Issue:** The error you encountered was caused by Rich's `Console.print()` not supporting the `file=` parameter.

**Fix:** Removed all `file=sys.stderr` arguments from `console.print()` calls.

**Status:** ✅ Fixed - the command should now work correctly!

## Try It Now

```bash
# This should work now (bug fixed!)
pkgsizer scan-env --package numpy --module-depth 2 --tree

# Other commands to try:
pkgsizer scan-env --top 10
pkgsizer scan-env --package pandas --tree
pkgsizer scan-env --json /tmp/sizes.json
```

