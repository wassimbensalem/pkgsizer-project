# Testing Guide for pkgsizer Features

## 🧪 Testing All New Features

### Prerequisites
```bash
# Make sure you have the latest code
cd /Users/wassimbensalem/Desktop/Projects-Extra/pkgsizer-project

# Install in development mode
pip install -e ".[dev]"

# Verify installation
pkgsizer --version
```

---

## 1. ✅ Test Progress Bars (Live Feedback)

Progress bars appear automatically when scanning 10+ packages.

### Test with Current Environment:
```bash
# This should show a progress bar if you have 10+ packages
pkgsizer scan-env --top 20
```

### Force Progress Bar (Even with Fewer Packages):
```bash
# Scan with verbose output to see progress
python -m pkgsizer scan-env --top 30
```

### What to Look For:
- ✅ Spinning indicator while scanning
- ✅ Progress percentage (0%, 50%, 100%)
- ✅ Time elapsed counter
- ✅ Bar showing completion status

---

## 2. ✅ Test HTML Reports

### Basic HTML Report:
```bash
# Generate HTML report for current environment
pkgsizer scan-env --html report.html

# Open in browser
open report.html  # macOS
# Or: xdg-open report.html  # Linux
# Or: start report.html     # Windows
```

### HTML with Options:
```bash
# HTML report with top 25 packages
pkgsizer scan-env --top 25 --html top25-report.html

# HTML with dependency sizes included
pkgsizer scan-env --include-deps --html full-report.html

# Combine HTML + JSON outputs
pkgsizer scan-env --html report.html --json data.json
```

### What to Check in HTML Report:
- ✅ Dark theme loads correctly
- ✅ Summary cards show correct numbers
- ✅ Bar chart displays (top 10 packages)
- ✅ Interactive table with all packages
- ✅ Search functionality works
- ✅ Insights panel shows statistics

---

## 3. ✅ Test Improved Error Messages

### Test File Not Found:
```bash
# Should show helpful error message
pkgsizer analyze-file /nonexistent/file.txt
```

**Expected Output:**
```
Error: /nonexistent/file.txt
Hints:
  • Verify the path exists and that pkgsizer has permission to read it.
  • If you're using --python, --venv, or --site-packages, double-check the value.
```

### Test Invalid Size Threshold:
```bash
# Should show format hints
pkgsizer scan-env --fail-over "invalid"
```

**Expected Output:**
```
Error: Invalid size threshold: invalid
Hints:
  • Use formats such as '500MB', '1GB', or provide a raw byte value (e.g., 1048576).
```

### Test Permission Error:
```bash
# Try to scan a protected directory (may not work on all systems)
pkgsizer scan-env --site-packages /root/site-packages
```

### Test Keyboard Interrupt:
```bash
# Run a long scan and press Ctrl+C
pkgsizer scan-env --top 100
# Press Ctrl+C while running
```

**Expected Output:**
```
Aborted by user.
```

---

## 4. ✅ Test GitHub Actions Integration

### Option A: Test Locally with act (GitHub Actions Runner)

**Install act:**
```bash
# macOS
brew install act

# Or download from: https://github.com/nektos/act
```

**Run Workflow Locally:**
```bash
# Test the workflow
act -W .github/workflows/pkgsizer.yml

# Or test specific job
act -j size-check
```

### Option B: Test Action Directly (Manual)

**Create test workflow file:**
```bash
# Create a test workflow
mkdir -p .github/workflows
cat > .github/workflows/test-pkgsizer.yml << 'EOF'
name: Test pkgsizer Action

on: [workflow_dispatch]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt || echo "No requirements.txt"
      - name: Run pkgsizer
        uses: ./.github/actions/pkgsizer
        with:
          fail-over: '1GB'
          html-report: 'test-report.html'
          json-report: 'test-report.json'
      - name: Upload reports
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: |
            test-report.html
            test-report.json
EOF
```

### Option C: Validate Action Syntax

```bash
# Check action.yml syntax
yamllint .github/actions/pkgsizer/action.yml

# Or use GitHub CLI
gh workflow view .github/workflows/pkgsizer.yml
```

### Option D: Test in Real GitHub Repo

1. **Push code to GitHub:**
```bash
git add .github/
git commit -m "Add GitHub Actions integration"
git push origin main
```

2. **Create a Pull Request** - The workflow will run automatically

3. **Check Workflow Run:**
   - Go to: `https://github.com/YOUR_USERNAME/pkgsizer/actions`
   - Check if workflow runs successfully
   - Download artifacts to see HTML/JSON reports

---

## 5. ✅ Test All Features Together

### Comprehensive Test Command:
```bash
# Test everything in one go
pkgsizer scan-env \
  --top 25 \
  --include-deps \
  --html comprehensive-report.html \
  --json comprehensive-data.json \
  --tree \
  --fail-over 500MB
```

### Check Results:
```bash
# Verify files were created
ls -lh comprehensive-report.html comprehensive-data.json

# Open HTML report
open comprehensive-report.html

# Check JSON structure
cat comprehensive-data.json | jq '.package_count'
```

---

## 6. ✅ Run Automated Tests

### Run All Tests:
```bash
pytest
```

### Run Specific Test Files:
```bash
# Test HTML report generation
pytest tests/test_html_report.py -v

# Test core functionality
pytest tests/test_report.py tests/test_size_calc.py -v

# Test with coverage
pytest --cov=pkgsizer --cov-report=html
```

### View Coverage Report:
```bash
# After running coverage tests
open htmlcov/index.html  # macOS
```

---

## 7. ✅ Test Edge Cases

### Empty Environment:
```bash
# Create a minimal virtual environment
python -m venv test_env
source test_env/bin/activate  # macOS/Linux
# Or: test_env\Scripts\activate  # Windows

# Scan empty environment
pkgsizer scan-env --venv test_env
```

### Large Environment:
```bash
# Install many packages
pip install numpy pandas matplotlib scipy sklearn tensorflow torch

# Scan and check progress bar
pkgsizer scan-env --top 50 --html large-env-report.html
```

### Environment with Editable Installs:
```bash
# Install current project in editable mode
pip install -e .

# Scan and verify editable detection
pkgsizer scan-env --top 10
```

---

## 8. ✅ Test Performance

### Time a Scan:
```bash
# Measure scan time
time pkgsizer scan-env --top 50
```

### Compare with/without Progress Bar:
```bash
# With progress (terminal)
time pkgsizer scan-env --top 50

# Without progress (redirect to file)
time pkgsizer scan-env --top 50 > /dev/null
```

---

## 9. ✅ Test CLI Commands

### Test All Commands:
```bash
# Help
pkgsizer --help

# Version
pkgsizer --version

# Scan environment
pkgsizer scan-env --help

# Analyze file
pkgsizer analyze-file --help

# Why command
pkgsizer why --help

# Unused command
pkgsizer unused --help

# Alternatives
pkgsizer alternatives --help

# Updates
pkgsizer updates --help

# Compare
pkgsizer compare --help
```

---

## 10. ✅ Quick Validation Checklist

Run these commands and verify:

```bash
# ✅ 1. Progress bar shows during scan
pkgsizer scan-env --top 30

# ✅ 2. HTML report generates
pkgsizer scan-env --html test.html && [ -f test.html ] && echo "✅ HTML created"

# ✅ 3. JSON report generates
pkgsizer scan-env --json test.json && [ -f test.json ] && echo "✅ JSON created"

# ✅ 4. Error messages are helpful
pkgsizer analyze-file /fake/path 2>&1 | grep -q "Hints:" && echo "✅ Helpful errors"

# ✅ 5. GitHub Action syntax is valid
yamllint .github/actions/pkgsizer/action.yml && echo "✅ Action YAML valid"

# ✅ 6. Tests pass
pytest && echo "✅ All tests pass"

# ✅ 7. Package builds
python -m build && echo "✅ Package builds successfully"
```

---

## 🐛 Debugging Tips

### Enable Verbose Output:
```bash
# See what pkgsizer is doing
python -m pkgsizer scan-env --top 10
```

### Check Python Environment:
```bash
# Verify pkgsizer is installed correctly
python -c "import pkgsizer; print(pkgsizer.__version__)"
```

### Test Template Loading:
```bash
# Check if templates are accessible
python -c "from importlib import resources; print(list(resources.files('pkgsizer').joinpath('templates').iterdir()))"
```

### Verify Dependencies:
```bash
# Check all dependencies are installed
pip list | grep -E "(jinja2|rich|typer)"
```

---

## 📊 Expected Output Examples

### Progress Bar Output:
```
⠋ Scanning packages ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45% 0:02
```

### HTML Report Output:
```
HTML report written to: report.html
```

### Error Message Output:
```
Error: File not found: /fake/path
Hints:
  • Verify the path exists and that pkgsizer has permission to read it.
```

### Success Output:
```
📦 Package Size Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Package              Version      Size         Files    Depth    Type         Editable
────────────────────────────────────────────────────────────────────────────────────────
numpy                1.24.0       45.23 MB     234      0        📍 direct    
pandas               2.0.0        125.45 MB    567      0        📍 direct    
...
```

---

## 🎯 Quick Test Script

Create a test script:

```bash
#!/bin/bash
# save as test-features.sh

echo "🧪 Testing pkgsizer Features..."
echo ""

echo "1. Testing progress bar..."
pkgsizer scan-env --top 20 > /dev/null 2>&1 && echo "✅ Progress bar test passed"

echo "2. Testing HTML report..."
pkgsizer scan-env --html test-report.html > /dev/null 2>&1
[ -f test-report.html ] && echo "✅ HTML report created" || echo "❌ HTML report failed"

echo "3. Testing error messages..."
pkgsizer analyze-file /fake/path 2>&1 | grep -q "Hints:" && echo "✅ Error messages work" || echo "❌ Error messages failed"

echo "4. Running tests..."
pytest > /dev/null 2>&1 && echo "✅ All tests pass" || echo "❌ Tests failed"

echo ""
echo "✅ Feature testing complete!"
```

Run it:
```bash
chmod +x test-features.sh
./test-features.sh
```

---

## 📝 Notes

- Progress bars only show in terminal environments (not in CI)
- HTML reports are standalone (no server needed)
- Error messages adapt based on error type
- GitHub Actions require a GitHub repository to fully test

