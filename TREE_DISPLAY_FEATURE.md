# Tree Display Feature - Improved!

## 🌳 What's New: Tree Structure in Table

Instead of a separate "Dependency Chain" column, packages are now displayed with **tree-style indentation** directly in the table - much clearer and more intuitive!

---

## ✨ Before vs After

### **OLD Approach** (Separate Column):
```
┃ Package       ┃ Depth ┃ Dependency Chain    ┃
┃ my-package    ┃ 0     ┃                     ┃
┃ wandb         ┃ 1     ┃ ← my-package        ┃
┃ pydantic      ┃ 2     ┃ ← wandb             ┃
┃ sentry-sdk    ┃ 2     ┃ ← wandb             ┃
```
**Problem:** Have to read two columns to understand relationship

### **NEW Approach** (Tree Structure):
```
┃ Package              ┃ Depth ┃ From         ┃
┃ my-package           ┃ 0     ┃              ┃
┃   └─ wandb           ┃ 1     ┃ my-package   ┃
┃     └─ pydantic      ┃ 2     ┃ wandb        ┃
┃     └─ sentry-sdk    ┃ 2     ┃ wandb        ┃
```
**Solution:** Visual tree structure shows relationships at a glance! ✨

---

## 📊 Real Example

### Command:
```bash
pkgsizer scan-env --package compredict-wandb --depth 2 --include-deps
```

### Output:
```
📦 Package Size Analysis
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Package                     ┃ Version ┃    Size ┃ W/Deps  ┃ Files ┃ Depth ┃ From         ┃ Type     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ compredict-wandb            │ 0.3.1   │  72 MB  │ 156 MB  │ 1833  │ 0     │              │ 📍 direct│
│   └─ wandb                  │ 0.22.2  │  65 MB  │  78 MB  │ 1844  │ 1     │ compredict.. │ 🔗 trans.│
│     └─ pydantic             │ 2.11.7  │ 3.6 MB  │ 3.6 MB  │  216  │ 2     │ wandb        │ 🔗 trans.│
│     └─ sentry-sdk           │ 2.30.0  │ 2.6 MB  │ 2.6 MB  │  298  │ 2     │ wandb        │ 🔗 trans.│
│     └─ protobuf             │ 4.25.8  │ 2.0 MB  │ 2.0 MB  │  102  │ 2     │ wandb        │ 🔗 trans.│
│     └─ GitPython            │ 3.1.44  │ 1.4 MB  │ 1.4 MB  │   82  │ 2     │ wandb        │ 🔗 trans.│
│     └─ click                │ 8.2.1   │ 822 KB  │ 822 KB  │   38  │ 2     │ wandb        │ 🔗 trans.│
│   └─ jsonschema             │ 4.24.0  │ 974 KB  │ 5.6 MB  │   76  │ 1     │ compredict.. │ 🔗 trans.│
│     └─ rpds-py              │ 0.25.1  │ 952 KB  │ 952 KB  │   10  │ 2     │ jsonschema   │ 🔗 trans.│
│     └─ referencing          │ 0.36.2  │ 278 KB  │ 1.6 MB  │   33  │ 2     │ jsonschema   │ 🔗 trans.│
│   └─ PyYAML                 │ 6.0.2   │ 841 KB  │ 841 KB  │   43  │ 1     │ compredict.. │ 🔗 trans.│
└─────────────────────────────┴─────────┴─────────┴─────────┴───────┴───────┴──────────────┴──────────┘
```

---

## 🎯 What You Can See Instantly

### Visual Tree Structure:
```
compredict-wandb (root)
├─ wandb (level 1)
│  ├─ pydantic (level 2)
│  ├─ sentry-sdk (level 2)
│  ├─ protobuf (level 2)
│  ├─ GitPython (level 2)
│  └─ click (level 2)
├─ jsonschema (level 1)
│  ├─ rpds-py (level 2)
│  └─ referencing (level 2)
└─ PyYAML (level 1)
```

### Key Insights:
- ✅ **wandb brings 5 dependencies** (clearly grouped under it)
- ✅ **jsonschema brings 2 dependencies** (visually nested)
- ✅ **PyYAML has no dependencies** (no children)
- ✅ **Total structure** is immediately clear

---

## 📝 Column Explanations

### **Package** (with tree structure)
- **Root level** (depth 0): No indentation
- **Level 1** (depth 1): `  └─ package-name`
- **Level 2** (depth 2): `    └─ package-name`
- Shows visual hierarchy at a glance

### **From** (parent package)
- Shows which package directly depends on this one
- Replaces the old "Dependency Chain" column
- Shorter, clearer header

### **Editable** (previously "Edit")
**What it means:** Shows if package is installed in "editable" mode

#### What is Editable Mode?
When you install a package with `pip install -e .`, it's "editable":
- ✅ Changes to source code take effect immediately
- ✅ No need to reinstall after changes
- ✅ Common during development

#### Why It Matters:
- **Editable packages** point to source directory (not copied to site-packages)
- **Size calculation** follows the source location
- **Development vs Production**: Editable in dev, normal in production

#### Display:
- ✏️ = Editable install (development mode)
- (empty) = Normal install (production mode)

**Example:**
```
┃ Package          ┃ Editable ┃
┃ my-app           ┃    ✏️     ┃  ← Development (pip install -e .)
┃ requests         ┃          ┃  ← Normal (pip install requests)
```

---

## 🎨 Visual Guide

### Tree Symbols Explained:
```
package               ← Root (depth 0)
  └─ child1           ← Level 1 (depth 1)
    └─ grandchild1    ← Level 2 (depth 2)
    └─ grandchild2    ← Level 2 (depth 2)
  └─ child2           ← Level 1 (depth 1)
```

### Indentation Pattern:
- **Depth 0**: No spaces
- **Depth 1**: 2 spaces + `└─ `
- **Depth 2**: 4 spaces + `└─ `
- **Depth 3**: 6 spaces + `└─ `

---

## 💡 Use Cases

### 1. **Understand Dependency Impact**
**Question:** "How many dependencies does wandb bring?"

**Look at tree:**
```
└─ wandb
  └─ pydantic
  └─ sentry-sdk
  └─ protobuf
  └─ GitPython
  └─ click
```
**Answer:** 5 dependencies (visually grouped)

---

### 2. **Find Heavy Branches**
**Question:** "Which dependency pulls in the most stuff?"

**Compare branches:**
```
compredict-wandb
├─ wandb ──────┐  
│  └─ (5 deps) │ ← Heavy branch!
│              │
├─ jsonschema ─┐
│  └─ (2 deps) │ ← Light branch
│              │
└─ PyYAML ─────┘  ← No deps (leaf)
```

**Answer:** wandb has the heaviest branch

---

### 3. **Identify Optimization Targets**
**Question:** "What can I make optional?"

**Look for large branches:**
```
my-package
├─ essential-lib (small)
└─ ml-toolkit ─────┐
   └─ torch        │ ← 2 GB!
   └─ tensorflow   │ ← 1.5 GB!
   └─ scikit-learn │
```

**Action:** Make ml-toolkit an optional extra!

---

### 4. **Debug "Why is X installed?"**
**Question:** "Why do I have protobuf?"

**Trace the tree:**
```
my-package
  └─ wandb
    └─ protobuf  ← Here it is!
```

**Answer:** wandb needs it (shown in "From" column too)

---

## 🚀 How to Use

### **Basic Tree View**
```bash
pkgsizer scan-env --package mypackage --depth 2
```
Shows 2 levels of dependencies with tree structure

### **With All Features**
```bash
pkgsizer scan-env --package mypackage --depth 2 --include-deps
```
Tree + cumulative sizes

### **Deep Analysis**
```bash
pkgsizer scan-env --package mypackage --depth 3 --include-deps --tree
```
Tree table + separate tree visualization

---

## 📊 Column Layout

When using `--depth > 0`, you get:

```
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Package (tree)    ┃ Version┃ Size  ┃ W/Deps ┃ Files ┃ Depth ┃ From      ┃ Type     ┃ Editable ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ Wide enough for   │        │       │ Optional│       │       │ Parent    │ Icon +   │ ✏️ or    │
│ tree indentation  │        │       │ with    │       │       │ package   │ word     │ empty    │
│                   │        │       │ --deps  │       │       │           │          │          │
└───────────────────┴────────┴───────┴────────┴───────┴───────┴───────────┴──────────┴──────────┘
```

**Note:** "W/Deps" column only appears with `--include-deps` flag

---

## 🎯 Benefits Over Old Design

| Feature | Old (Chain Column) | New (Tree Structure) |
|---------|-------------------|---------------------|
| **Visual clarity** | Need to read 2 columns | Instant visual hierarchy |
| **Space efficiency** | Extra column needed | Uses existing Package column |
| **Understanding** | Text-based | Visual tree structure |
| **Scalability** | Gets crowded | Natural grouping |
| **Aesthetics** | Functional | Beautiful & intuitive |

---

## 💡 Pro Tips

### 1. **Start with Depth 1**
```bash
pkgsizer scan-env --package mypackage --depth 1
```
See immediate dependencies first

### 2. **Increase Gradually**
```bash
pkgsizer scan-env --package mypackage --depth 2
```
Add one level when you need more detail

### 3. **Combine with --include-deps**
```bash
pkgsizer scan-env --package mypackage --depth 2 --include-deps
```
See both structure AND cumulative impact

### 4. **Use --tree for Large Hierarchies**
```bash
pkgsizer scan-env --depth 3 --tree
```
Get both table and separate tree view

---

## 🔍 Technical Details

### Tree Rendering Algorithm:
1. Sort packages by depth (0 → 1 → 2 → ...)
2. For each package, calculate indentation: `"  " * depth`
3. Add tree prefix: `"└─ "` for non-root packages
4. Display in Package column with tree structure

### Column Width Adjustment:
- **Without tree**: Package column = 25 chars
- **With tree**: Package column = 35 chars (accommodates indentation)

### "From" Column:
- Shows direct parent (immediate dependency)
- Kept short for space efficiency
- Redundant with tree structure but useful for quick reference

---

## 📖 Complete Example

### Your Exact Use Case:
```bash
pkgsizer scan-env --package compredict-wandb --depth 2 --include-deps
```

### What You'll See:
```
📦 Package Size Analysis
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Package                     ┃ Version ┃    Size ┃ W/Deps  ┃ Files ┃ Depth ┃ From         ┃ Type        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ compredict-wandb            │ 0.3.1   │  72 MB  │ 156 MB  │ 1833  │ 0     │              │ 📍 direct   │ ✏️
│   └─ wandb                  │ 0.22.2  │  65 MB  │  78 MB  │ 1844  │ 1     │ compredict-..│ 🔗 trans.   │
│     └─ pydantic             │ 2.11.7  │ 3.6 MB  │ 3.6 MB  │  216  │ 2     │ wandb        │ 🔗 trans.   │
│     └─ sentry-sdk           │ 2.30.0  │ 2.6 MB  │ 2.6 MB  │  298  │ 2     │ wandb        │ 🔗 trans.   │
│     └─ protobuf             │ 4.25.8  │ 2.0 MB  │ 2.0 MB  │  102  │ 2     │ wandb        │ 🔗 trans.   │
│     └─ GitPython            │ 3.1.44  │ 1.4 MB  │ 1.4 MB  │   82  │ 2     │ wandb        │ 🔗 trans.   │
│     └─ click                │ 8.2.1   │ 822 KB  │ 822 KB  │   38  │ 2     │ wandb        │ 🔗 trans.   │
│   └─ jsonschema             │ 4.24.0  │ 974 KB  │ 5.6 MB  │   76  │ 1     │ compredict-..│ 🔗 trans.   │
│     └─ rpds-py              │ 0.25.1  │ 952 KB  │ 952 KB  │   10  │ 2     │ jsonschema   │ 🔗 trans.   │
│     └─ referencing          │ 0.36.2  │ 278 KB  │ 1.6 MB  │   33  │ 2     │ jsonschema   │ 🔗 trans.   │
│   └─ PyYAML                 │ 6.0.2   │ 841 KB  │ 841 KB  │   43  │ 1     │ compredict-..│ 🔗 trans.   │
└─────────────────────────────┴─────────┴─────────┴─────────┴───────┴───────┴──────────────┴─────────────┘

Insights:
→ wandb is your largest dependency (65 MB + 13 MB of its deps = 78 MB total)
→ wandb brings 5 sub-dependencies (pydantic, sentry-sdk, protobuf, GitPython, click)
→ jsonschema adds 5.6 MB total (974 KB + 4.6 MB of its 2 deps)
→ Total footprint: 156 MB
```

---

## ✅ Summary

**Major Improvements:**

1. ✨ **Tree structure in table** - Visual hierarchy, no separate column needed
2. 📝 **Renamed "From" column** - Shorter, clearer than "Dependency Chain"
3. 🏷️ **"Editable" column** - Full word instead of just "Edit" (clearer)
4. 📐 **Auto-adjusted widths** - Package column wider when showing tree
5. 🎯 **Better spacing** - Tree symbols and indentation for clarity

**Result:** Much clearer visualization of dependency relationships! 🎉

---

## 🚀 Try It Now!

```bash
# Your package with tree structure
pkgsizer scan-env --package compredict-wandb --depth 2 --include-deps

# Any package
pkgsizer scan-env --package requests --depth 2

# Full environment
pkgsizer scan-env --depth 2 --top 20
```

**You'll see beautiful tree structure showing exactly how packages relate!** ✨

