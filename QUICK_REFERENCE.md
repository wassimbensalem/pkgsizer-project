# 🚀 pkgsizer Quick Reference

## Command Overview

| Command | Purpose | Speed |
|---------|---------|-------|
| `scan-env` | Scan environment for package sizes | Fast |
| `analyze-file` | Analyze dependency file | Fast |
| `why` | Trace why a package is installed | Fast |
| `unused` | Find unused dependencies | Medium |

---

## 📦 `scan-env` - Scan Environment

**Basic Usage:**
```bash
# Scan current environment
pkgsizer scan-env

# Scan specific packages
pkgsizer scan-env --package numpy --package pandas

# Show dependency tree
pkgsizer scan-env --package myapp --depth 2

# Include cumulative sizes
pkgsizer scan-env --package myapp --depth 2 --include-deps
```

**Common Flags:**
- `--package NAME` - Scan specific package(s)
- `--depth N` - Show dependencies up to depth N
- `--module-depth N` - Show subpackages up to depth N
- `--include-deps` - Show cumulative size with dependencies
- `--tree` - Show dependency tree
- `--json FILE` - Output to JSON

**Examples:**
```bash
# Find largest packages
pkgsizer scan-env --top 10

# Deep dive into a package
pkgsizer scan-env --package tensorflow --depth 3 --module-depth 2

# Export to JSON
pkgsizer scan-env --json report.json
```

---

## 🔍 `why` - Why is Package Installed?

**Basic Usage:**
```bash
# Find out why a package is installed
pkgsizer why numpy

# Export to JSON
pkgsizer why numpy --json why-numpy.json
```

**What It Shows:**
- ✅ All dependency paths to the package
- ✅ Which packages depend on it
- ✅ Package size and version
- ✅ Whether you can safely remove it

**Examples:**
```bash
# Why is protobuf installed?
pkgsizer why protobuf

# Check if you can remove a package
pkgsizer why boto3

# Find all dependents
pkgsizer why requests --json requests-deps.json
```

**Use Cases:**
- 🔍 Debug unexpected dependencies
- 🗑️ Check if package is safe to remove
- 📊 Understand dependency chains
- 🎯 Find bloat sources

---

## 🗑️ `unused` - Find Unused Dependencies

**Basic Usage:**
```bash
# Scan code directory for unused packages
pkgsizer unused ./src

# Scan current directory
pkgsizer unused .

# Just list all packages (no scan)
pkgsizer unused
```

**What It Shows:**
- ✅ Packages never imported in your code
- ✅ Total wasted disk space
- ✅ Removal recommendations
- ✅ Used vs unused breakdown

**Examples:**
```bash
# Find unused dependencies
pkgsizer unused ./app

# Export to JSON for automation
pkgsizer unused ./src --json unused.json

# Clean up based on results
pkgsizer unused ./app --json unused.json
cat unused.json | jq -r '.unused[]' | xargs pip uninstall -y
```

**Use Cases:**
- 🧹 Clean up bloated environments
- 📦 Optimize Docker images
- 💰 Reduce deployment size
- 🎯 Identify truly needed packages

---

## 📄 `analyze-file` - Analyze Dependency File

**Basic Usage:**
```bash
# Analyze requirements.txt
pkgsizer analyze-file requirements.txt

# Analyze Poetry project
pkgsizer analyze-file pyproject.toml

# Analyze with depth
pkgsizer analyze-file requirements.txt --depth 2
```

**Supported Formats:**
- `requirements.txt`
- `pyproject.toml` (Poetry)
- `Pipfile` / `Pipfile.lock`
- `environment.yml` (Conda)
- `uv.lock` (uv)

---

## 🎯 Common Workflows

### Workflow 1: Optimize Docker Image
```bash
# Step 1: Find unused packages
pkgsizer unused ./app --json unused.json

# Step 2: Check sizes
cat unused.json | jq '.unused_size_bytes'

# Step 3: Remove if safe
cat unused.json | jq -r '.unused[]' | xargs pip uninstall -y

# Result: 30-50% smaller image
```

### Workflow 2: Debug Dependency Bloat
```bash
# Step 1: Find largest packages
pkgsizer scan-env --top 10

# Step 2: Check why each is installed
pkgsizer why tensorflow
pkgsizer why numpy
pkgsizer why scipy

# Step 3: Decide if you can remove or replace
```

### Workflow 3: Pre-Deployment Check
```bash
# Step 1: Scan for unused deps
pkgsizer unused ./src

# Step 2: Generate report
pkgsizer scan-env --include-deps --json deployment-report.json

# Step 3: Review and optimize
```

### Workflow 4: CI/CD Integration
```bash
# In your CI pipeline
pkgsizer unused ./app --json unused.json

# Fail if wasted space > threshold
WASTED=$(cat unused.json | jq '.unused_size_bytes')
if [ $WASTED -gt 100000000 ]; then
  echo "Too much wasted space: $WASTED bytes"
  exit 1
fi
```

---

## 💡 Tips & Tricks

### Tip 1: Find Heavy Transitive Dependencies
```bash
# Scan with depth and sort by "With Deps" column
pkgsizer scan-env --depth 2 --include-deps | grep MB | sort -rh
```

### Tip 2: Export Everything to JSON
```bash
# Create comprehensive report
pkgsizer scan-env --json full-report.json
pkgsizer unused ./src --json unused.json

# Combine in your own scripts
python analyze_reports.py full-report.json unused.json
```

### Tip 3: Check Before Removing
```bash
# Always check dependencies before removing
pkgsizer why <package>

# If it says "Only if you remove: X, Y, Z"
# Then check if you need X, Y, or Z first
```

### Tip 4: Regular Cleanup
```bash
# Add to your monthly maintenance
pkgsizer unused ./src
# Review and remove unused packages
```

### Tip 5: Compare Environments
```bash
# Before
pkgsizer scan-env --json before.json

# After changes
pkgsizer scan-env --json after.json

# Compare
python -c "
import json
before = json.load(open('before.json'))
after = json.load(open('after.json'))
print(f'Size change: {after[\"total_size\"] - before[\"total_size\"]} bytes')
"
```

---

## 🚨 Common Issues

### Issue: "Package not found"
**Solution:** Check spelling or install the package first
```bash
pip install <package>
pkgsizer why <package>
```

### Issue: "unused" shows too many false positives
**Reason:** Dynamic imports not detected
**Solution:** Review JSON output manually
```bash
pkgsizer unused ./src --json unused.json
# Review unused.json and verify each package
```

### Issue: "why" command is slow
**Reason:** Very large environment (> 500 packages)
**Solution:** It's limited to 10 paths and max depth 5 for performance

### Issue: Sizes don't match `du -sh`
**Reason:** Hardlinks and symlinks
**Solution:** pkgsizer uses inode-based deduplication for accuracy

---

## 📊 Understanding Output

### Tree Display:
```
myapp (10 MB)
  └─ numpy (32 MB)     ← numpy is required by myapp
     └─ mkl (100 MB)   ← mkl is required by numpy
```

### Dependency Chain:
```
Package    From
numpy      myapp
mkl        myapp → numpy
```

### Size Columns:
- **Size**: Package's own files only
- **With Deps**: Package + all its dependencies (cumulative)

### Editable Column:
- ✏️ = Editable install (pip install -e)
- (empty) = Normal install

---

## 🔗 See Also

- `WEEK1_FEATURES.md` - Detailed feature documentation
- `WEEK1_COMPLETE.md` - Implementation summary
- `DEEP_FEATURE_ANALYSIS.md` - Future features
- `README.md` - Full documentation

---

## 🆘 Need Help?

```bash
# Show help for any command
pkgsizer --help
pkgsizer scan-env --help
pkgsizer why --help
pkgsizer unused --help
```

---

**Last Updated:** October 30, 2025  
**Version:** 0.2.0 (Week 1 Complete)

