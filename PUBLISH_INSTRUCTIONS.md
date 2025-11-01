# 🚀 How to Publish pkgsizer

## ✅ Current Status

Everything is ready! Package is built and ready to publish.

---

## 📦 What's Ready

- ✅ Package built: `dist/pkgsizer-0.1.0-py3-none-any.whl` (43K)
- ✅ Source distribution: `dist/pkgsizer-0.1.0.tar.gz` (40K)
- ✅ Git repository initialized
- ✅ All optimizations applied
- ✅ Tested on itself (works perfectly!)

---

## 🚀 Publish to PyPI (3 Simple Steps)

### Step 1: Create PyPI Account
1. Go to https://pypi.org/account/register/
2. Register and verify your email

### Step 2: Create API Token
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "pkgsizer-upload"
4. Click "Create token"
5. **Copy the token** (you'll only see it once!)

### Step 3: Upload Package
```bash
cd /Users/wassimbensalem/pkgsizer-project
python -m twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: `<paste your token>`

Done! Your package will be on PyPI within minutes.

---

## 🧪 Optional: Test First (Recommended)

Test on TestPyPI before publishing to real PyPI:

```bash
# 1. Register on TestPyPI: https://test.pypi.org/account/register/
# 2. Create TestPyPI token: https://test.pypi.org/manage/account/token/

# 3. Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# 4. Test install
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ pkgsizer

# 5. Test it works
pkgsizer --help
pkgsizer scan-env --top 5

# 6. If all works, proceed to real PyPI
python -m twine upload dist/*
```

---

## 🐙 Publish to GitHub

### Create Repository
1. Go to https://github.com/new
2. Name: `pkgsizer`
3. Description: "Python package size analyzer and dependency manager"
4. Public, don't initialize with README
5. Click "Create repository"

### Push Code
```bash
cd /Users/wassimbensalem/pkgsizer-project
git remote add origin https://github.com/wassimbensalem/pkgsizer.git
git branch -M main
git push -u origin main
```

### Create Release
```bash
git tag -a v0.1.0 -m "Initial release v0.1.0"
git push origin v0.1.0
```

Then on GitHub:
1. Go to repository → Releases
2. Click "Draft a new release"
3. Select tag: v0.1.0
4. Title: "v0.1.0 - Initial Release"
5. Copy description from CHANGELOG.md
6. Click "Publish release"

---

## ✅ Verify Publication

After publishing to PyPI:

```bash
# Wait 2-3 minutes, then:
pip install pkgsizer

# Test it
pkgsizer --version
pkgsizer --help
pkgsizer scan-env --top 5
```

Check on PyPI: https://pypi.org/project/pkgsizer/

---

## 💡 Pro Tips

### Save API Token
Create `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

Then uploading is just: `python -m twine upload dist/*`

### Future Updates
When releasing v0.2.0:
```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md
# 3. Commit changes
git add . && git commit -m "Release v0.2.0"

# 4. Build new version
rm -rf dist/
python -m build

# 5. Upload
python -m twine upload dist/*

# 6. Tag and push
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin main --tags
```

---

## 📊 Package Info

**Package tested on itself:**
- Size: 180 KB
- Total with deps: 13.38 MB
- Commands: 7 (scan-env, analyze-file, why, unused, alternatives, updates, compare)
- Status: ✅ Production ready!

---

## 🆘 Troubleshooting

### "Package already exists"
→ You can't re-upload the same version. Increment version in `pyproject.toml`

### "Invalid credentials"
→ Make sure username is `__token__` and password is your full API token

### "HTTPError: 403"
→ Check your API token has correct permissions

### "Package rejected"
→ Check README.md renders correctly (must be valid Markdown)

---

## 🎉 That's It!

Your package is ready to publish. Just run:

```bash
python -m twine upload dist/*
```

And the world can use pkgsizer! 🚀

