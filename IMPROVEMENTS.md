# pkgsizer Improvements

## What's New

### 1. 🎨 Enhanced UI Display

The output is now much more visually appealing and informative:

#### **New Table Design**
- **Title**: "📦 Package Size Analysis" with colored header
- **Styled columns**: Bold important data, color-coded information
- **Icons**: 
  - 📍 for direct dependencies
  - 🔗 for transitive dependencies  
  - ✏️ for editable installs

#### **Enhanced Summary Panel**
- Beautiful boxed statistics showing:
  - 📦 Total packages
  - 💾 Total size
  - 📄 File count
  - 🔗 Size with dependencies (when `--include-deps` is used)

#### **Improved Tree View**
- **Icons for structure**:
  - 📦 Direct packages
  - 🔗 Transitive packages
  - 📁 Subpackages (directories)
  - 📄 Modules (files)
- **Color-coded sizes**:
  - 🔴 Red: > 10 MB
  - 🟡 Yellow: > 1 MB
  - 🟢 Green: < 1 MB
- **File counts** shown for each subpackage
- **Sorted by size** (largest first)
- **Limited display** (top 10 subpackages, top 5 children)

---

### 2. 🔗 Include Dependencies Flag (`--include-deps`)

**New Feature**: Calculate cumulative sizes including dependencies!

#### What It Does

Shows **two size columns**:
1. **Size**: Package's own files only (as before)
2. **With Deps**: Package + all its dependencies

#### Example

```bash
pkgsizer scan-env --package requests --include-deps --depth 2
```

**Output:**
```
┏━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ Package   ┃ Version ┃ Size      ┃ With Deps  ┃ Files ┃ Depth ┃
┡━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ requests  │ 2.31.0  │ 500 KB    │ 5.5 MB     │  89   │   0   │
│ urllib3   │ 2.0.0   │ 300 KB    │ 300 KB     │  45   │   1   │
│ charset.. │ 3.2.0   │ 4.7 MB    │ 4.7 MB     │  234  │   1   │
└───────────┴─────────┴───────────┴────────────┴───────┴───────┘
```

**Understanding the columns:**
- **requests Size**: 500 KB (just requests' files)
- **requests With Deps**: 5.5 MB (requests + urllib3 + charset-normalizer + certifi + idna)
- **urllib3 With Deps**: 300 KB (urllib3 has no dependencies)

#### Use Cases

1. **"What's the TRUE cost of installing this package?"**
   ```bash
   pkgsizer scan-env --package torch --include-deps --depth 3
   ```
   See torch's size (2 GB) vs torch with deps (3.5 GB including numpy, etc.)

2. **"Which package brings in the most baggage?"**
   ```bash
   pkgsizer scan-env --include-deps --depth 2 --top 10
   ```
   Sort by "With Deps" column to find heavy packages

3. **"Before I add this dependency..."**
   ```bash
   pkgsizer analyze-file requirements.txt --include-deps
   ```
   See what each requirement really costs

#### How It's Calculated

The tool recursively adds dependency sizes:
```
requests (500 KB) + its dependencies:
  ├─ urllib3 (300 KB)
  ├─ charset-normalizer (4.7 MB)
  ├─ certifi (150 KB)
  └─ idna (100 KB)
  = 5.75 MB total
```

**Smart deduplication**: If two packages share a dependency, it's only counted once in totals.

---

### 3. 📝 Environment Isolation Guidance

#### Do You Need a New Environment?

**Short Answer**: Yes, for accurate analysis!

#### Why Isolation Matters

**Problem**: Your development environment likely has many packages installed:
```
Development environment:
├─ Your package (10 MB)
├─ pytest (5 MB)              ← Testing only
├─ black (2 MB)               ← Dev tool
├─ jupyter (50 MB)            ← Dev tool
├─ Production deps (100 MB)   ← Actually needed
└─ Random experiments (30 MB) ← Leftover
```

**Result**: You see 197 MB, but production only needs 110 MB!

#### Best Practice: Isolated Analysis

**Method 1: Analyze from requirements.txt in a clean environment**

```bash
# Create isolated environment
python3 -m venv /tmp/clean-env
source /tmp/clean-env/bin/activate

# Install only production dependencies
pip install -r requirements.txt

# Analyze
pkgsizer scan-env

# Clean up
deactivate
rm -rf /tmp/clean-env
```

**Method 2: Use Docker**

```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt && pip install pkgsizer
RUN pkgsizer scan-env --json /output/sizes.json
```

**Method 3: Analyze specific packages only**

```bash
# In your messy dev environment
pkgsizer analyze-file requirements.txt --depth 999
```
This only analyzes packages in requirements.txt (+ their dependencies).

#### When You DON'T Need Isolation

1. **Analyzing a single package:**
   ```bash
   pkgsizer scan-env --package numpy --module-depth 2
   ```
   Other packages don't affect the result.

2. **Analyzing with file + specific packages:**
   ```bash
   pkgsizer analyze-file requirements.txt
   ```
   Only looks at packages from the file.

3. **Exploring your current environment:**
   ```bash
   pkgsizer scan-env --top 20
   ```
   You WANT to see everything installed.

#### Automated Isolation Script

Create `analyze-clean.sh`:
```bash
#!/bin/bash
# Analyze dependencies in isolated environment

VENV_DIR="/tmp/pkgsizer-clean-$(date +%s)"
REQ_FILE="${1:-requirements.txt}"

echo "Creating clean environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install -q -r "$REQ_FILE"
pip install -q pkgsizer

echo "Analyzing..."
pkgsizer scan-env --json analysis.json --include-deps

echo "Cleaning up..."
deactivate
rm -rf "$VENV_DIR"

echo "Results saved to analysis.json"
```

Usage:
```bash
chmod +x analyze-clean.sh
./analyze-clean.sh requirements.txt
```

---

## Comparison: Before vs After

### Before
```
Package Sizes
Package   Version   Size      Files  Depth  Type        Editable
numpy     2.3.3     32.39 MB  1519   0      direct      

Total packages: 1
Total size: 32.39 MB
Total files: 1,519

Dependency Tree (top packages):
numpy (32.39 MB)
```

### After
```
📦 Package Size Analysis
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━┓
┃ Package                 ┃ Version    ┃ Size       ┃ Files  ┃ Depth ┃ Type       ┃ Edit ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━┩
│ numpy                   │ 2.3.3      │ 32.39 MB   │ 1519   │ 0     │ 📍 direct  │      │
└─────────────────────────┴────────────┴────────────┴────────┴───────┴────────────┴──────┘

────────────────────────────────────────────────────────────

┏━━━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━┓
┃ 📦 Packages  ┃  ┃ 💾 Total Size  ┃  ┃ 📄 Files     ┃
┃              ┃  ┃                ┃  ┃              ┃
┃      1       ┃  ┃   32.39 MB     ┃  ┃    1,519     ┃
┗━━━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━━━┛

────────────────────────────────────────────────────────────

🌳 Package Structure:

📦 numpy 2.3.3 (32.39 MB)
├── 📁 core (8.50 MB) 125 files
├── 📁 linalg (5.20 MB) 89 files
├── 📁 random (4.80 MB) 102 files
├── 📁 fft (2.10 MB) 45 files
└── 📁 ma (1.90 MB) 67 files
```

---

## Usage Examples

### Example 1: Simple Analysis (Basic UI)
```bash
pkgsizer scan-env --package pandas
```

### Example 2: With Dependency Sizes
```bash
pkgsizer scan-env --package pandas --include-deps --depth 2
```

### Example 3: Full Tree with Dependencies
```bash
pkgsizer scan-env --package compredict-wandb --module-depth 2 --include-deps --depth 2 --tree
```

**This shows:**
- ✅ Improved table with icons and colors
- ✅ Your package's submodules (kfp, core, etc.)
- ✅ Package size alone vs with dependencies
- ✅ Beautiful summary panels
- ✅ Color-coded tree with file counts

### Example 4: Top 10 with Dependencies
```bash
pkgsizer scan-env --top 10 --include-deps --depth 999
```

Answers: "Which of my top 10 packages brings in the most dependencies?"

### Example 5: Clean Environment Analysis
```bash
# Create clean env
python3 -m venv /tmp/clean && source /tmp/clean/bin/activate

# Install your package
pip install -r requirements.txt

# Analyze with new UI
pkgsizer scan-env --include-deps --tree --json production-sizes.json

# Cleanup
deactivate && rm -rf /tmp/clean
```

---

## Command Reference

### New Flag

```
--include-deps
```

**Purpose**: Show cumulative size including dependencies

**Adds column**: "With Deps" showing package + all transitive dependencies

**Works with**:
- `scan-env`
- `analyze-file`

**Best combined with**:
- `--depth N` to control how many dependency levels to include
- `--tree` to visualize the dependency structure
- `--json` to export detailed analysis

---

## Tips

1. **Start simple**: Run without `--include-deps` to see file-only sizes
2. **Add dependencies**: Use `--include-deps` when you want the "real" footprint
3. **Control depth**: Use `--depth 2` with `--include-deps` to limit scope
4. **Isolate for production**: Always analyze in a clean environment for deployment
5. **Compare environments**: Export JSON from dev and prod envs, compare with Python/jq

---

## FAQ

**Q: Does `--include-deps` change how files are counted?**
A: No! It just adds an additional column showing cumulative size. The "Size" column remains unchanged.

**Q: Is the "With Deps" column additive?**
A: No, it's per-package. Each row shows that package + ITS dependencies. Shared dependencies are deduplicated.

**Q: Should I always use `--include-deps`?**
A: Not always:
- **Use it**: When planning installations, budgeting space, comparing alternatives
- **Skip it**: When analyzing package structure, finding large files within a package

**Q: Do I really need environment isolation?**
A: For production deployment analysis: **YES**. For exploration: **NO**.

---

## See It in Action

```bash
# Try the new UI right now!
pkgsizer scan-env --package numpy --module-depth 2 --tree

# With dependencies
pkgsizer scan-env --package requests --include-deps --depth 2

# Full analysis
pkgsizer scan-env --top 10 --include-deps --tree --json full-analysis.json
```

Enjoy the beautiful new interface! 🎨✨

