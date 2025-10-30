# 📦 Publishing Guide for pkgsizer

Complete guide to publish pkgsizer to PyPI and GitHub.

---

## 📋 Pre-Publication Checklist

### ✅ Code Ready
- [x] All features implemented
- [x] Code optimized (caching, parallelization)
- [x] No linter errors
- [x] Tests passing
- [x] Documentation complete

### ✅ Package Configuration
- [x] `pyproject.toml` configured
- [x] Version number set (0.3.0)
- [x] Dependencies listed
- [x] README.md written
- [x] LICENSE file present

---

## 🐙 Part 1: GitHub Setup

### Step 1: Create GitHub Repository

```bash
# On GitHub.com:
# 1. Go to https://github.com/new
# 2. Repository name: pkgsizer
# 3. Description: "Python package size analyzer and dependency manager"
# 4. Public repository
# 5. Don't initialize with README (we have one)
# 6. Click "Create repository"
```

### Step 2: Initialize Git Repository

```bash
cd /Users/wassimbensalem/pkgsizer-project

# Initialize git
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# OS
.DS_Store
Thumbs.db

# pkgsizer specific
.pkgsizer/

# Temporary files
*.tmp
*.bak
EOF

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: pkgsizer v0.3.0

Features:
- scan-env: Scan Python environment for package sizes
- analyze-file: Analyze dependency files
- why: Trace dependency paths
- unused: Find unused dependencies
- alternatives: Suggest better alternatives
- updates: Check for outdated packages
- compare: Compare two environments

Complete with documentation and optimizations."

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/pkgsizer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Create Release on GitHub

```bash
# Tag the release
git tag -a v0.3.0 -m "Release v0.3.0

Week 1 & 2 Features Complete:
- 6 major features implemented
- 7 commands available
- Full documentation
- Performance optimizations
- Production ready"

# Push tags
git push origin v0.3.0
```

Then on GitHub:
1. Go to your repository
2. Click "Releases"
3. Click "Draft a new release"
4. Select tag v0.3.0
5. Title: "v0.3.0 - Week 1 & 2 Complete"
6. Description: Copy from CHANGELOG.md
7. Click "Publish release"

---

## 📦 Part 2: PyPI Publishing

### Step 1: Prepare Package

```bash
cd /Users/wassimbensalem/pkgsizer-project

# Install build tools
pip install --upgrade build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
python -m build

# This creates:
# dist/pkgsizer-0.3.0-py3-none-any.whl
# dist/pkgsizer-0.3.0.tar.gz
```

### Step 2: Test on TestPyPI (Recommended)

```bash
# Register on TestPyPI first: https://test.pypi.org/account/register/

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# You'll be prompted for:
# Username: YOUR_TESTPYPI_USERNAME
# Password: YOUR_TESTPYPI_PASSWORD (or token)

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ pkgsizer

# Test the package
pkgsizer --help
pkgsizer scan-env --top 5

# If everything works, proceed to real PyPI
```

### Step 3: Publish to PyPI

```bash
# Register on PyPI: https://pypi.org/account/register/

# Upload to PyPI
python -m twine upload dist/*

# You'll be prompted for:
# Username: YOUR_PYPI_USERNAME
# Password: YOUR_PYPI_PASSWORD (or token)

# Or use API token (recommended):
# 1. Go to https://pypi.org/manage/account/token/
# 2. Create API token
# 3. Use __token__ as username and token as password
```

### Step 4: Verify Publication

```bash
# Install from PyPI
pip install pkgsizer

# Verify it works
pkgsizer --version
pkgsizer --help

# Check on PyPI
# https://pypi.org/project/pkgsizer/
```

---

## 🔐 Using API Tokens (Recommended)

### PyPI API Token Setup:

```bash
# 1. Create ~/.pypirc file
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
EOF

# 2. Set permissions
chmod 600 ~/.pypirc

# 3. Now you can upload without entering credentials
python -m twine upload dist/*
```

---

## 📝 Update Package Metadata

### In `pyproject.toml`:

```toml
[project]
name = "pkgsizer"
version = "0.3.0"
description = "Python package size analyzer and dependency manager"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["package", "size", "dependencies", "analyzer", "python"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Systems Administration",
]

[project.urls]
Homepage = "https://github.com/YOUR_USERNAME/pkgsizer"
Documentation = "https://github.com/YOUR_USERNAME/pkgsizer/blob/main/README.md"
Repository = "https://github.com/YOUR_USERNAME/pkgsizer"
Changelog = "https://github.com/YOUR_USERNAME/pkgsizer/blob/main/CHANGELOG.md"
Issues = "https://github.com/YOUR_USERNAME/pkgsizer/issues"
```

---

## 🚀 Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: python -m twine upload dist/*
```

Then add `PYPI_API_TOKEN` to GitHub Secrets:
1. Go to repository Settings
2. Secrets and variables → Actions
3. New repository secret
4. Name: `PYPI_API_TOKEN`
5. Value: Your PyPI API token

---

## 📊 Post-Publication Tasks

### 1. Update README Badge

Add to top of README.md:
```markdown
[![PyPI version](https://badge.fury.io/py/pkgsizer.svg)](https://badge.fury.io/py/pkgsizer)
[![Python versions](https://img.shields.io/pypi/pyversions/pkgsizer.svg)](https://pypi.org/project/pkgsizer/)
[![Downloads](https://pepy.tech/badge/pkgsizer)](https://pepy.tech/project/pkgsizer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

### 2. Announce on Social Media

```markdown
🚀 Just published pkgsizer v0.3.0!

A Python package size analyzer and dependency manager with:
✅ 7 powerful commands
✅ Find unused dependencies
✅ Trace dependency chains
✅ Suggest alternatives
✅ Check for updates
✅ Compare environments

pip install pkgsizer

https://github.com/YOUR_USERNAME/pkgsizer

#Python #DevTools #OpenSource
```

### 3. Submit to Python Package Index

- Already done by publishing to PyPI!
- Package will appear in search results

### 4. Create Documentation Site (Optional)

```bash
# Using GitHub Pages
# Create docs/ folder with documentation
# Enable GitHub Pages in repository settings
# Point to docs/ folder or use gh-pages branch
```

---

## 🔄 Future Updates

### For version 0.4.0:

```bash
# 1. Update version in pyproject.toml
version = "0.4.0"

# 2. Update CHANGELOG.md with new features

# 3. Commit changes
git add .
git commit -m "Release v0.4.0"
git tag -a v0.4.0 -m "Release v0.4.0"
git push origin main --tags

# 4. Build and publish
rm -rf dist/
python -m build
python -m twine upload dist/*
```

---

## 📋 Quick Commands Reference

```bash
# Build
python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Install from source
pip install -e .

# Install from PyPI
pip install pkgsizer

# Uninstall
pip uninstall pkgsizer
```

---

## ✅ Publication Checklist

Before publishing:
- [ ] Version number updated in pyproject.toml
- [ ] CHANGELOG.md updated
- [ ] README.md complete
- [ ] All tests passing
- [ ] Documentation up to date
- [ ] Git repository initialized
- [ ] Code pushed to GitHub
- [ ] GitHub release created
- [ ] PyPI account created
- [ ] Package built successfully
- [ ] Tested on TestPyPI
- [ ] Published to PyPI
- [ ] Installation verified
- [ ] README badges added
- [ ] Announcement posted

---

## 🆘 Troubleshooting

### Issue: "Package already exists"
**Solution:** Increment version number in `pyproject.toml`

### Issue: "Invalid credentials"
**Solution:** Use API token instead of password

### Issue: "README not rendering on PyPI"
**Solution:** Ensure README.md is in correct format and referenced in pyproject.toml

### Issue: "Missing dependencies"
**Solution:** Check all dependencies are listed in pyproject.toml

### Issue: "Build fails"
**Solution:** 
```bash
rm -rf dist/ build/ *.egg-info
python -m build
```

---

## 📚 Resources

- **PyPI Guide:** https://packaging.python.org/tutorials/packaging-projects/
- **Twine Documentation:** https://twine.readthedocs.io/
- **GitHub Releases:** https://docs.github.com/en/repositories/releasing-projects-on-github
- **Semantic Versioning:** https://semver.org/

---

**Ready to publish!** 🚀

Follow the steps above to make pkgsizer available to the world!

