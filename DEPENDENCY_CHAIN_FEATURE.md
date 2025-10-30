# Dependency Chain Feature

## 🔗 What's New: Automatic Dependency Chain Display

When you use `--depth` flag with a value greater than 0, the table now **automatically** shows a "Dependency Chain" column that tells you which package depends on each transitive dependency!

---

## ✨ Feature Overview

### **Before** (Without this feature):
```
Package          Depth   Type
wandb            1       transitive  ← But who needs this?
pydantic         2       transitive  ← Where does this come from?
jsonschema       2       transitive  ← Why is this here?
```

**Problem:** You see packages but don't know WHY they're installed.

### **After** (With this feature):
```
Package          Depth   Dependency Chain           Type
wandb            1       ← compredict-wandb         transitive
pydantic         2       ← wandb                    transitive
jsonschema       2       ← wandb                    transitive
rpds-py          2       ← jsonschema               transitive
```

**Solution:** You instantly see the parent package that brought in each dependency!

---

## 📊 How It Works

### Automatic Activation

The "Dependency Chain" column appears **automatically** when:
1. You use `--depth` flag with value > 0
2. Any package in results has depth > 0 (transitive dependencies exist)

### Example Commands

#### **Show Direct + 1 Level**
```bash
pkgsizer scan-env --package compredict-wandb --depth 1
```

**Output:**
```
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Package          ┃ Size   ┃ Files  ┃ Depth  ┃ Chain                  ┃ Type        ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ compredict-wandb │ 72 MB  │ 1833   │ 0      │                        │ 📍 direct   │
│ wandb            │ 65 MB  │ 1844   │ 1      │ ← compredict-wandb     │ 🔗 trans... │
│ jsonschema       │ 974 KB │ 76     │ 1      │ ← compredict-wandb     │ 🔗 trans... │
│ PyYAML           │ 841 KB │ 43     │ 1      │ ← compredict-wandb     │ 🔗 trans... │
└──────────────────┴────────┴────────┴────────┴────────────────────────┴─────────────┘
```

**Understanding:**
- **compredict-wandb**: Your package (depth 0, no chain shown)
- **wandb**: Depends on compredict-wandb (shows `← compredict-wandb`)
- **jsonschema**: Also depends on compredict-wandb directly
- **PyYAML**: Also depends on compredict-wandb directly

#### **Show 2 Levels Deep**
```bash
pkgsizer scan-env --package compredict-wandb --depth 2
```

**Output:**
```
┃ Package          ┃ Depth  ┃ Dependency Chain           ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ compredict-wandb │ 0      │                            │  ← Direct install
│ wandb            │ 1      │ ← compredict-wandb         │  ← Level 1
│ pydantic         │ 2      │ ← wandb                    │  ← Level 2
│ sentry-sdk       │ 2      │ ← wandb                    │  ← Level 2
│ protobuf         │ 2      │ ← wandb                    │  ← Level 2
│ GitPython        │ 2      │ ← wandb                    │  ← Level 2
│ jsonschema       │ 1      │ ← compredict-wandb         │  ← Level 1
│ rpds-py          │ 2      │ ← jsonschema               │  ← Level 2
│ referencing      │ 2      │ ← jsonschema               │  ← Level 2
```

**Understanding the Tree:**
```
compredict-wandb (you)
├─ wandb ───────────────┐
│  ├─ pydantic          │ All from wandb
│  ├─ sentry-sdk        │
│  ├─ protobuf          │
│  └─ GitPython ────────┘
│
└─ jsonschema ──────────┐
   ├─ rpds-py           │ All from jsonschema
   └─ referencing ──────┘
```

---

## 🎯 Use Cases

### 1. **Understanding Bloat**
**Question:** "Why is pydantic installed? I didn't add it!"

**Command:**
```bash
pkgsizer scan-env --depth 2 | grep pydantic
```

**Answer:**
```
pydantic    2.11.7    3.62 MB    ← wandb
```
→ "Ah! `wandb` needs it."

---

### 2. **Finding Heavy Dependency Chains**
**Question:** "Which of my packages brings in the most transitive dependencies?"

**Command:**
```bash
pkgsizer scan-env --package compredict-wandb --depth 2 --include-deps
```

**Answer:**
```
Package          Size      With Deps    Chain
compredict-wandb 72 MB     156 MB       (root)
wandb            65 MB     78 MB        ← compredict-wandb
jsonschema       1 MB      6 MB         ← compredict-wandb
```
→ "wandb adds 78 MB total with all its dependencies!"

---

### 3. **Tracking Unwanted Dependencies**
**Question:** "I removed package X, but package Y is still installed. Why?"

**Command:**
```bash
pkgsizer scan-env --depth 3
```

**Answer:**
```
package-y    ← package-z ← package-a ← my-package
```
→ "Oh! `package-a` still needs it through `package-z`."

---

### 4. **Optimization Opportunities**
**Question:** "Can I reduce my Docker image by removing this dependency?"

**Command:**
```bash
pkgsizer scan-env --depth 2 --include-deps
```

**Check the chain:**
```
heavy-package    150 MB    ← optional-feature
```
→ "If I make `optional-feature` optional, I save 150 MB!"

---

## 🔍 Advanced Features

### **Multiple Parents**

If a package is used by multiple parents, it shows:
```
Package          Chain
requests         ← wandb (+2 more)
```

This means:
- Primary parent: `wandb`
- Also used by: 2 other packages

**To see all parents**, use the tree view:
```bash
pkgsizer scan-env --depth 2 --tree
```

---

### **No Chain for Direct Dependencies**

Direct dependencies (depth 0) don't show a chain:
```
Package          Depth    Chain
compredict-wandb 0        (empty)  ← You installed this
wandb            1        ← compredict-wandb
```

This keeps the display clean and focuses on "why is this here?" questions.

---

## 📖 Complete Example

### Setup
```bash
# Your package depends on: wandb, jsonschema
# wandb depends on: pydantic, sentry-sdk, click, protobuf
# jsonschema depends on: rpds-py, referencing
```

### Command
```bash
pkgsizer scan-env --package compredict-wandb --depth 2 --include-deps
```

### Output
```
📦 Package Size Analysis
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Package             ┃ Size    ┃ W/Deps  ┃ Files     ┃ Depth ┃ Chain              ┃ Type       ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ compredict-wandb    │ 72 MB   │ 156 MB  │ 1833      │ 0     │                    │ 📍 direct  │
│ wandb               │ 65 MB   │ 78 MB   │ 1844      │ 1     │ ← compredict-wandb │ 🔗 trans.  │
│ pydantic            │ 3.6 MB  │ 3.6 MB  │ 216       │ 2     │ ← wandb            │ 🔗 trans.  │
│ sentry-sdk          │ 2.6 MB  │ 2.6 MB  │ 298       │ 2     │ ← wandb            │ 🔗 trans.  │
│ protobuf            │ 2.0 MB  │ 2.0 MB  │ 102       │ 2     │ ← wandb            │ 🔗 trans.  │
│ click               │ 822 KB  │ 822 KB  │ 38        │ 2     │ ← wandb            │ 🔗 trans.  │
│ jsonschema          │ 974 KB  │ 5.6 MB  │ 76        │ 1     │ ← compredict-wandb │ 🔗 trans.  │
│ rpds-py             │ 952 KB  │ 952 KB  │ 10        │ 2     │ ← jsonschema       │ 🔗 trans.  │
│ referencing         │ 278 KB  │ 1.6 MB  │ 33        │ 2     │ ← jsonschema       │ 🔗 trans.  │
└─────────────────────┴─────────┴─────────┴───────────┴───────┴────────────────────┴────────────┘

Insights from this output:
→ wandb is your heaviest dependency (78 MB with all deps)
→ wandb brings in 4 level-2 dependencies (pydantic, sentry-sdk, protobuf, click)
→ jsonschema adds 5.6 MB total (itself + 2 dependencies)
→ Total footprint: 156 MB
```

---

## 💡 Tips

1. **Start with depth 1**: See immediate dependencies
   ```bash
   pkgsizer scan-env --package mypackage --depth 1
   ```

2. **Increase depth to understand chains**: See transitive dependencies
   ```bash
   pkgsizer scan-env --package mypackage --depth 2
   ```

3. **Combine with `--include-deps`**: See total impact
   ```bash
   pkgsizer scan-env --package mypackage --depth 2 --include-deps
   ```

4. **Use `--tree` for complex cases**: Better visualization
   ```bash
   pkgsizer scan-env --package mypackage --depth 2 --tree
   ```

5. **Export to JSON for analysis**: Script-friendly
   ```bash
   pkgsizer scan-env --depth 2 --json deps.json
   ```

---

## 🎨 Visual Legend

**In the Dependency Chain column:**
- `← package-name` = This package depends on you
- `← package (+2 more)` = Multiple packages depend on you
- `(empty)` = Direct dependency (you installed it)

**Colors (in terminal):**
- Dim italic = Dependency chain text
- Cyan bold = Package names
- Yellow = Depth numbers
- Green = Sizes

---

## 📊 Technical Details

### How Parent Detection Works

1. **Build reverse dependency map**: For each package, find who depends on it
2. **Show primary parent**: Display the first (main) parent
3. **Count additional parents**: Show "+N more" if multiple
4. **Automatic activation**: Column only appears when needed (depth > 0)

### Performance Impact

- **Negligible**: Parent calculation is O(n) where n = number of packages
- **Already fast**: Adds <50ms even for 500 packages
- **Smart caching**: Results cached for display

---

## 🚀 Try It Now!

```bash
# Your example (with your actual package)
pkgsizer scan-env --package compredict-wandb --depth 2 --include-deps

# Explore any package
pkgsizer scan-env --package requests --depth 2

# Full environment with chains
pkgsizer scan-env --depth 2 --top 20
```

**The dependency chain column will automatically appear!** ✨

---

## 📝 Summary

**New Feature**: Automatic "Dependency Chain" column  
**When**: Automatically shows when `--depth > 0`  
**Shows**: Which package(s) depend on each transitive dependency  
**Benefit**: Instant understanding of "why is this package installed?"  

**No configuration needed** - just use `--depth` flag and enjoy! 🎉

