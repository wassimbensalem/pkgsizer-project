# 💡 How the Alternatives System Works

## Overview

The `alternatives` command suggests lighter or better alternative packages. Here's exactly how it works:

---

## Is it Hardcoded? YES ✅

**The alternatives database is currently hardcoded** in `pkgsizer/alternatives.py`.

### Why Hardcoded?

**Pros:**
- ✅ **Fast:** Instant lookup, no network calls
- ✅ **Reliable:** Always available offline
- ✅ **Curated:** Quality-controlled suggestions
- ✅ **Simple:** Easy to understand and maintain
- ✅ **No dependencies:** No external APIs needed

**Cons:**
- ❌ **Limited:** Only 24 packages covered
- ❌ **Static:** Requires code updates to add more
- ❌ **Opinionated:** Reflects maintainer's choices

---

## Database Structure

Located in: `pkgsizer/alternatives.py`

```python
ALTERNATIVES_DB = {
    "requests": [
        {
            "name": "httpx",
            "reason": "Modern, async support, HTTP/2",
            "size_diff": "similar"
        },
        {
            "name": "urllib3",
            "reason": "Lower-level, fewer dependencies",
            "size_diff": "smaller"
        },
    ],
    "pandas": [
        {
            "name": "polars",
            "reason": "Much faster, better memory usage",
            "size_diff": "smaller"
        },
    ],
    # ... 22 more packages
}
```

### Fields Explained:

1. **`name`** (str): Alternative package name
2. **`reason`** (str): Why use this alternative
3. **`size_diff`** (str): Expected size difference
   - `"much_smaller"` - Significantly smaller
   - `"smaller"` - Somewhat smaller
   - `"similar"` - Similar size
   - `"larger"` - Larger (but worth it for features)

---

## How It Works (Step by Step)

### 1. User Query
```bash
pkgsizer alternatives requests
```

### 2. Lookup Process
```python
# 1. Get alternatives from database
alternatives = ALTERNATIVES_DB.get("requests", [])
# Returns: [{"name": "httpx", ...}, {"name": "urllib3", ...}]

# 2. Check if alternatives are installed
for alt in alternatives:
    alt_name = alt["name"].lower()
    alt["installed"] = alt_name in distributions
    
    # 3. If installed, calculate actual size
    if alt["installed"]:
        alt["actual_size"] = calculate_size(alt_name)
        alt["size_comparison"] = alt_size - current_size
```

### 3. Display Results
- Show current package size
- List each alternative with:
  - Name and reason
  - Size expectation (icon)
  - Installation status
  - Actual size comparison if installed

### 4. Provide Recommendations
- Suggest installing alternatives that aren't installed yet
- Show actual savings if alternative is already installed

---

## Current Database Coverage

### 24 Packages with Alternatives:

**Web Frameworks:**
- `django` → fastapi, flask
- `flask` → fastapi, bottle

**HTTP Clients:**
- `requests` → httpx, urllib3

**Data Processing:**
- `pandas` → polars, dask
- `numpy` → jax

**CLI:**
- `click` → typer, argparse

**Testing:**
- `pytest` → unittest
- `nose` → pytest, unittest

**Database:**
- `sqlalchemy` → peewee, sqlite3

**JSON:**
- `simplejson` → json, ujson, orjson

**Date/Time:**
- `arrow` → pendulum, python-dateutil

**Image Processing:**
- `pillow` → opencv-python, imageio

**Plotting:**
- `matplotlib` → plotly, seaborn

**Parsing:**
- `beautifulsoup4` → selectolax, pyquery

**Task Queues:**
- `celery` → rq, dramatiq

**Validation:**
- `cerberus` → pydantic, marshmallow

**And more...**

Total: **24 packages → 45 alternatives**

---

## Limitations

### 1. Coverage
- Only 24 packages out of 400,000+ on PyPI
- Focused on popular packages

### 2. Opinions
- Suggestions reflect maintainer's experience
- May not fit all use cases

### 3. Context-Free
- Doesn't know your specific requirements
- Can't assess compatibility with your code

### 4. Size Estimates
- "smaller" vs "larger" are rough estimates
- Actual sizes shown only if both installed

---

## Future Enhancements

### Short Term (Feasible):

**1. Expand Database (Manual Curation)**
```python
# Add more packages based on:
- GitHub stars
- PyPI download stats
- Community requests
- Domain-specific packages (ML, web, data)
```

**2. External Database File**
```python
# Move to JSON/YAML for easier updates
alternatives.json:
{
  "requests": [
    {"name": "httpx", "reason": "...", "size_diff": "similar"}
  ]
}

# Benefits:
- Non-code updates
- Community contributions easier
- Version-specific alternatives
```

**3. User Contributions**
```python
# Allow users to submit alternatives
pkgsizer alternatives --suggest requests httpx "Modern, async support"

# Stores in local database
~/.pkgsizer/user_alternatives.json
```

### Long Term (Advanced):

**4. Dynamic Size Calculation**
```python
# Instead of "smaller"/"larger" estimates:
- Fetch package sizes from PyPI
- Calculate actual size differences
- Update database periodically
```

**5. ML-Based Suggestions**
```python
# Analyze package usage patterns:
- Import similarity
- API compatibility
- Community adoption
- Performance benchmarks
```

**6. Context-Aware Suggestions**
```python
# Consider:
- Python version
- OS platform
- Existing dependencies
- Use case (web/ML/data/CLI)
```

**7. Integration with Package Registries**
```python
# Query external APIs:
- PyPI alternatives metadata
- GitHub "Alternatives to X"
- libraries.io
- awesome-python lists
```

---

## Adding New Alternatives (Current Method)

### Step 1: Edit `pkgsizer/alternatives.py`

```python
ALTERNATIVES_DB = {
    # ... existing entries ...
    
    "your-package": [
        {
            "name": "alternative-1",
            "reason": "Why it's better",
            "size_diff": "smaller",  # or "similar", "larger", "much_smaller"
        },
        {
            "name": "alternative-2",
            "reason": "Another option",
            "size_diff": "similar",
        },
    ],
}
```

### Step 2: Verify Size Expectations

```bash
# Install both packages
pip install your-package alternative-1

# Compare sizes
pkgsizer alternatives your-package
```

### Step 3: Test

```bash
# Verify it works
pkgsizer alternatives your-package
pkgsizer alternatives --list-all
```

---

## Why This Approach Works

### For Most Users:
1. **Fast & Reliable:** Instant suggestions, no network needed
2. **Quality:** Curated by someone who tested them
3. **Simple:** Easy to understand and use
4. **Actionable:** Direct pip install commands

### For The Project:
1. **Low Maintenance:** No external dependencies
2. **Predictable:** No API rate limits or outages
3. **Extensible:** Easy to add more entries
4. **Portable:** Works anywhere Python runs

---

## Comparison with Other Approaches

### Hardcoded (Current) vs Dynamic:

| Aspect | Hardcoded | Dynamic (API) |
|--------|-----------|---------------|
| Speed | ⚡ Instant | 🐌 Slower (network) |
| Offline | ✅ Works | ❌ Requires internet |
| Coverage | ❌ Limited (24) | ✅ Unlimited |
| Quality | ✅ Curated | ❓ Variable |
| Maintenance | 🔄 Manual updates | ✅ Auto-updated |
| Dependencies | ✅ None | ❌ External APIs |
| Reliability | ✅ Always works | ❓ API dependent |

### Recommendation:

**Hybrid Approach (Future):**
```python
# 1. Check local hardcoded database (fast)
alternatives = ALTERNATIVES_DB.get(package)

# 2. If not found, check user database
if not alternatives:
    alternatives = load_user_alternatives(package)

# 3. If not found, optionally query API
if not alternatives and --online flag:
    alternatives = fetch_from_api(package)
```

---

## Example: Real-World Usage

### Scenario: Optimizing Data Pipeline

```bash
# 1. Check what's installed
$ pkgsizer scan-env --top 10

# Result: pandas is 67MB

# 2. Look for alternatives
$ pkgsizer alternatives pandas

# Output:
# Alternative: polars
# Reason: Much faster, better memory usage
# Size: ⬇️⬇️ Much smaller
# Status: ○ Not installed

# 3. Install and test
$ pip install polars

# 4. Benchmark
$ python benchmark.py
# Result: 2x faster, 30% less memory

# 5. Verify size
$ pkgsizer alternatives pandas

# Output:
# Alternative: polars
# Status: ✓ Installed (35MB) (-32MB savings!)
```

---

## Contributing Alternatives

**Want to add alternatives? Two ways:**

### 1. Submit a Pull Request
```bash
# Edit pkgsizer/alternatives.py
# Add your suggestions
# Submit PR with reasoning
```

### 2. Open an Issue
```markdown
Package: requests
Alternatives:
  - httpx: Modern, async support, HTTP/2
  - urllib3: Lower-level, fewer dependencies

Reasoning: [explain why]
Size comparison: [if known]
```

---

## Summary

### Current State:
- ✅ **24 packages covered**
- ✅ **45 alternatives catalogued**
- ✅ **Fast, reliable, offline**
- ✅ **Easy to use**
- ❌ **Limited coverage**
- ❌ **Manual updates needed**

### Future Vision:
- 📈 **100+ packages covered**
- 🌐 **Optional online lookups**
- 👥 **Community contributions**
- 🤖 **ML-powered suggestions**
- 📊 **Dynamic size calculations**

### For Now:
The hardcoded approach works well for the most common packages. It's a pragmatic solution that delivers value without complexity.

---

**Bottom Line:** Yes, it's hardcoded, but that's a feature, not a bug! It provides fast, reliable, curated suggestions for the packages that matter most. Future enhancements can add dynamic lookups while keeping the core database as a fast fallback. 🚀

