#!/bin/bash
# Validation script for pkgsizer

set -e

echo "================================================"
echo "pkgsizer Validation Script"
echo "================================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
python3 --version
echo ""

# Check if we're in the right directory
echo "2. Checking project structure..."
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Please run from project root."
    exit 1
fi
echo "✓ Project structure OK"
echo ""

# Validate Python syntax
echo "3. Validating Python syntax..."
for f in pkgsizer/*.py pkgsizer/file_parsers/*.py; do
    python3 -m py_compile "$f" 2>&1 > /dev/null && echo "  ✓ $f" || (echo "  ✗ $f" && exit 1)
done
echo ""

# Check imports
echo "4. Checking imports..."
python3 -c "import pkgsizer; print(f'  ✓ pkgsizer version {pkgsizer.__version__}')" || exit 1
python3 -c "from pkgsizer.cli import app; print('  ✓ CLI module')" || exit 1
python3 -c "from pkgsizer.scanner import scan_environment; print('  ✓ Scanner module')" || exit 1
python3 -c "from pkgsizer.report import format_size; print('  ✓ Report module')" || exit 1
echo ""

# List files
echo "5. Project files:"
echo ""
echo "Python modules:"
find pkgsizer -name "*.py" | wc -l | xargs echo "  Main package:"
find tests -name "*.py" | wc -l | xargs echo "  Tests:"
echo ""
echo "Documentation:"
ls -1 *.md | sed 's/^/  /'
echo ""

# Show size
echo "6. Project size:"
du -sh . | sed 's/^/  Total: /'
du -sh pkgsizer/ | sed 's/^/  Package: /'
echo ""

echo "================================================"
echo "✓ All validations passed!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Install: pip install -e ."
echo "  2. Test: pkgsizer --help"
echo "  3. Try: pkgsizer scan-env --top 10"
echo ""

