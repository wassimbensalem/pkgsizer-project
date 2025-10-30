# 📦 pkgsizer - Complete Command Reference

**Version:** 0.3.0  
**Total Commands:** 7

---

## 📋 Command Overview

| # | Command | Purpose | Speed | Output |
|---|---------|---------|-------|--------|
| 1 | `scan-env` | Scan environment for package sizes | Fast | Table/Tree/JSON |
| 2 | `analyze-file` | Analyze dependency file | Fast | Table/Tree/JSON |
| 3 | `why` | Trace why package is installed | < 1s | Analysis/JSON |
| 4 | `unused` | Find unused dependencies | 2-30s | List/JSON |
| 5 | `alternatives` | Suggest better alternatives | < 0.5s | Suggestions/JSON |
| 6 | `updates` | Check for outdated packages | 0.5s/pkg | List/JSON |
| 7 | `compare` | Compare two environments | 1-3s | Comparison/JSON |

---

## 1️⃣ `pkgsizer scan-env`

**Purpose:** Scan an installed Python environment and measure package sizes.

**Syntax:**
```bash
pkgsizer scan-env [OPTIONS]
```

**Key Options:**
```bash
--package NAME              # Scan specific package(s)
--depth N                   # Show dependencies up to depth N
--module-depth N            # Show subpackages up to depth N
--include-deps              # Show cumulative size with dependencies
--tree                      # Display dependency tree
--top N                     # Show only top N packages
--by {size|files}          # Sort by size or file count
--json FILE                 # Export to JSON
--python PATH               # Specify Python interpreter
--venv PATH                 # Specify virtual environment
--site-packages PATH        # Specify site-packages directory
```

**Examples:**
```bash
# Scan entire environment
pkgsizer scan-env

# Scan specific package with dependencies
pkgsizer scan-env --package numpy --depth 2

# Show top 10 largest packages
pkgsizer scan-env --top 10

# Include subpackages and cumulative sizes
pkgsizer scan-env --package pandas --module-depth 2 --include-deps

# Export to JSON
pkgsizer scan-env --json environment.json

# Scan specific environment
pkgsizer scan-env --venv ./my_venv
```

**Output:**
- Package name, version, size, file count
- Dependency depth and type (direct/transitive)
- Editable install indicator
- Optional tree visualization
- Summary statistics

---

## 2️⃣ `pkgsizer analyze-file`

**Purpose:** Analyze a dependency file and measure package sizes.

**Syntax:**
```bash
pkgsizer analyze-file DEPENDENCY_FILE [OPTIONS]
```

**Supported Formats:**
- `requirements.txt`
- `pyproject.toml` (Poetry)
- `Pipfile` / `Pipfile.lock`
- `environment.yml` (Conda)
- `uv.lock` (uv)

**Key Options:**
```bash
--depth N                   # Show dependencies up to depth N
--module-depth N            # Show subpackages up to depth N
--include-deps              # Show cumulative size with dependencies
--tree                      # Display dependency tree
--json FILE                 # Export to JSON
--python PATH               # Specify Python interpreter
--venv PATH                 # Specify virtual environment
--site-packages PATH        # Specify site-packages directory
```

**Examples:**
```bash
# Analyze requirements.txt
pkgsizer analyze-file requirements.txt

# Analyze Poetry project
pkgsizer analyze-file pyproject.toml --depth 2

# Analyze with tree view
pkgsizer analyze-file requirements.txt --tree

# Export to JSON
pkgsizer analyze-file requirements.txt --json analysis.json
```

**Output:**
- Same as `scan-env` but filtered to packages in file
- Shows which packages are installed vs missing

---

## 3️⃣ `pkgsizer why`

**Purpose:** Show why a package is installed and all dependency paths to it.

**Syntax:**
```bash
pkgsizer why PACKAGE [OPTIONS]
```

**Key Options:**
```bash
--json FILE                 # Export to JSON
--python PATH               # Specify Python interpreter
--venv PATH                 # Specify virtual environment
--site-packages PATH        # Specify site-packages directory
```

**Examples:**
```bash
# Trace why numpy is installed
pkgsizer why numpy

# Check if you can remove a package
pkgsizer why boto3

# Export dependency paths to JSON
pkgsizer why tensorflow --json why-tf.json

# Check in specific environment
pkgsizer why requests --venv ./my_venv
```

**Output:**
- Package name, version, size
- Direct vs transitive dependency status
- All dependency paths from root packages
- List of packages that depend on it
- Removal safety advice
- Potential space savings

**Use Cases:**
- "Why is this package installed?"
- "What depends on this package?"
- "Can I safely remove this?"
- "How did this get here?"

---

## 4️⃣ `pkgsizer unused`

**Purpose:** Find dependencies that are never imported in your code.

**Syntax:**
```bash
pkgsizer unused [CODE_PATH] [OPTIONS]
```

**Key Options:**
```bash
--json FILE                 # Export to JSON
--python PATH               # Specify Python interpreter
--venv PATH                 # Specify virtual environment
--site-packages PATH        # Specify site-packages directory
```

**Examples:**
```bash
# Scan current directory
pkgsizer unused .

# Scan specific directory
pkgsizer unused ./src

# Scan without code path (lists all packages)
pkgsizer unused

# Export to JSON
pkgsizer unused ./app --json unused.json

# Check specific environment
pkgsizer unused ./src --venv ./my_venv
```

**Output:**
- List of unused packages with versions
- Top-level modules for each package
- Total wasted disk space
- Removal recommendations
- Used vs unused breakdown

**Algorithm:**
- AST-based parsing of all `.py` files
- Extracts `import X` and `from X import Y`
- Maps packages to top-level modules
- Excludes common directories (`.git`, `__pycache__`, etc.)

**Use Cases:**
- "Which packages can I remove?"
- "How much space am I wasting?"
- "What's actually being used?"
- "Clean up before deployment"

---

## 5️⃣ `pkgsizer alternatives`

**Purpose:** Suggest lighter or better alternative packages.

**Syntax:**
```bash
pkgsizer alternatives [PACKAGE] [OPTIONS]
```

**Key Options:**
```bash
--list-all                  # List all known alternatives in database
--json FILE                 # Export to JSON
--python PATH               # Specify Python interpreter
--venv PATH                 # Specify virtual environment
--site-packages PATH        # Specify site-packages directory
```

**Examples:**
```bash
# Get alternatives for specific package
pkgsizer alternatives requests

# Browse all known alternatives
pkgsizer alternatives --list-all

# Check all installed packages with alternatives
pkgsizer alternatives

# Export to JSON
pkgsizer alternatives pandas --json alt-pandas.json
```

**Output:**
- Current package version and size
- List of alternatives with:
  - Alternative name
  - Reason to use it
  - Size expectation (smaller/similar/larger)
  - Installation status
  - Actual size comparison if installed
- Installation recommendations

**Database Coverage (24 packages, 45 alternatives):**
- **Web:** django, flask → fastapi, bottle
- **HTTP:** requests → httpx, urllib3
- **Data:** pandas → polars, dask | numpy → jax
- **CLI:** click → typer, argparse
- **Testing:** pytest → unittest | nose → pytest
- **Database:** sqlalchemy → peewee, sqlite3
- **JSON:** simplejson → orjson, ujson
- **Image:** pillow → opencv-python, imageio
- **Plotting:** matplotlib → plotly, seaborn
- **Date:** arrow → pendulum, python-dateutil
- **Parsing:** beautifulsoup4 → selectolax, pyquery
- **Tasks:** celery → rq, dramatiq
- **And more...**

**How It Works:**
- ✅ **Hardcoded database** in `pkgsizer/alternatives.py`
- Each entry includes: name, reason, size expectation
- Checks if alternatives are already installed
- Compares actual sizes if both are installed

**Use Cases:**
- "Are there better options?"
- "Can I use something lighter?"
- "What are modern alternatives?"
- "Optimize dependencies"

---

## 6️⃣ `pkgsizer updates`

**Purpose:** Check for outdated packages and available updates.

**Syntax:**
```bash
pkgsizer updates [PACKAGES...] [OPTIONS]
```

**Key Options:**
```bash
--all                       # Check all packages (can be slow)
--json FILE                 # Export to JSON
--python PATH               # Specify Python interpreter
--venv PATH                 # Specify virtual environment
--site-packages PATH        # Specify site-packages directory
```

**Examples:**
```bash
# Check specific packages
pkgsizer updates numpy pandas

# Check all packages (may take 1-5 minutes)
pkgsizer updates --all

# Export to JSON
pkgsizer updates typer rich --json updates.json

# Check in specific environment
pkgsizer updates --all --venv ./my_venv
```

**Output:**
- List of outdated packages with:
  - Current version
  - Latest version
  - Current size
  - Upgrade command
- List of up-to-date packages
- Unavailable packages (not on PyPI)
- Summary statistics

**Algorithm:**
- Queries PyPI JSON API for each package
- Uses `packaging` library for version comparison
- Timeout of 5 seconds per package
- Graceful handling of network errors

**Performance:**
- 2-3 packages: ~1-2 seconds
- 20 packages: ~5-10 seconds
- All packages (--all): 1-5 minutes

**Use Cases:**
- "Am I up-to-date?"
- "What needs updating?"
- "Security updates available?"
- "Bulk update planning"

---

## 7️⃣ `pkgsizer compare`

**Purpose:** Compare two Python environments.

**Syntax:**
```bash
pkgsizer compare ENV1 ENV2 [OPTIONS]
```

**Key Options:**
```bash
--name1 NAME                # Name for first environment
--name2 NAME                # Name for second environment
--json FILE                 # Export to JSON
```

**Examples:**
```bash
# Compare two environments
pkgsizer compare ./dev_venv ./prod_venv

# With custom names
pkgsizer compare env1 env2 --name1 "Development" --name2 "Production"

# Compare Python versions
pkgsizer compare ~/.pyenv/versions/3.11.11 ~/.pyenv/versions/3.12.0

# Export to JSON
pkgsizer compare env1 env2 --json comparison.json
```

**Output:**
- Summary statistics (package counts, total sizes)
- Version differences with size impact
- Packages only in environment 1
- Packages only in environment 2
- Size difference breakdown

**Path Resolution:**
- Accepts venv paths or site-packages paths
- Automatically finds site-packages if given venv
- Works with any Python environment type

**Use Cases:**
- "Do dev and prod match?"
- "What changed after update?"
- "Environment drift detection"
- "Validate replication"

---

## 🎯 Common Workflows

### Workflow 1: Initial Environment Audit
```bash
# 1. Get inventory
pkgsizer scan-env --json inventory.json

# 2. Find unused packages
pkgsizer unused ./src

# 3. Check for alternatives
pkgsizer alternatives
```

### Workflow 2: Dependency Investigation
```bash
# 1. Why is X installed?
pkgsizer why <mysterious-package>

# 2. What depends on it?
# (shown in output)

# 3. Can I remove it?
# (removal advice shown)
```

### Workflow 3: Optimization
```bash
# 1. Find biggest packages
pkgsizer scan-env --top 10

# 2. Check for alternatives
pkgsizer alternatives <big-package>

# 3. Find unused
pkgsizer unused ./app

# 4. Remove waste
pip uninstall <unused-packages>
```

### Workflow 4: Maintenance
```bash
# Weekly routine
pkgsizer updates --all          # Check for updates
pkgsizer unused ./src           # Find unused
pkgsizer alternatives           # Consider better options
```

### Workflow 5: Pre-Deployment
```bash
# 1. Compare with production
pkgsizer compare ./staging ./production

# 2. Find unused in staging
pkgsizer unused ./staging_app

# 3. Verify no dev tools
# (check output for jupyter, ipython, etc.)
```

---

## 🚀 Quick Reference Table

| Task | Command |
|------|---------|
| Scan environment | `pkgsizer scan-env` |
| Largest packages | `pkgsizer scan-env --top 10` |
| Why installed? | `pkgsizer why <package>` |
| Find unused | `pkgsizer unused ./src` |
| Check updates | `pkgsizer updates --all` |
| Find alternatives | `pkgsizer alternatives <package>` |
| Compare envs | `pkgsizer compare env1 env2` |
| Export inventory | `pkgsizer scan-env --json inventory.json` |
| Deep dive | `pkgsizer scan-env --package X --depth 2 --module-depth 2` |

---

## 💡 Pro Tips

1. **Always use JSON for automation:**
   ```bash
   pkgsizer <command> --json output.json
   ```

2. **Combine with other tools:**
   ```bash
   # Get list of outdated packages
   pkgsizer updates --all --json updates.json
   cat updates.json | jq -r '.outdated[].package'
   ```

3. **Regular audits:**
   ```bash
   # Weekly cron job
   pkgsizer unused ./app --json unused.json
   pkgsizer updates --all --json updates.json
   ```

4. **CI/CD integration:**
   ```bash
   # Fail if wasted space > 100MB
   WASTE=$(pkgsizer unused ./app --json - | jq '.unused_size_bytes')
   [ $WASTE -gt 100000000 ] && exit 1
   ```

5. **Environment validation:**
   ```bash
   # Ensure prod matches staging
   pkgsizer compare staging prod --json diff.json
   [ $(jq '.comparison.only_in_env1' diff.json) -eq 0 ]
   ```

---

## 📊 Performance Summary

| Command | Typical Time | Notes |
|---------|--------------|-------|
| `scan-env` | 1-5s | Fast even with large envs |
| `analyze-file` | 1-5s | Similar to scan-env |
| `why` | < 1s | Very fast |
| `unused` | 2-30s | Depends on codebase size |
| `alternatives` | < 0.5s | Instant lookup |
| `updates` | 0.5s/pkg | Network dependent |
| `compare` | 1-3s | Fast comparison |

---

## 🎓 Learning Resources

- `README.md` - Full documentation
- `QUICK_REFERENCE.md` - Command cheat sheet
- `WEEK1_FEATURES.md` - Week 1 features guide
- `WEEK2_COMPLETE.md` - Week 2 features guide
- `WEEKS_1_AND_2_SUMMARY.md` - Complete overview

---

**Total:** 7 powerful commands to manage your Python dependencies! 🚀

