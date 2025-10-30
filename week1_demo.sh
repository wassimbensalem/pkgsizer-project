#!/bin/bash
#
# Week 1 Features Demo Script
# This script demonstrates all three critical features from Week 1
#

set -e

echo "🚀 pkgsizer Week 1 Features Demo"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Demo 1: Fixed tree structure
echo -e "${CYAN}📦 Demo 1: Fixed Tree Structure${NC}"
echo "Command: pkgsizer scan-env --package rich --depth 2 --include-deps"
echo ""
pkgsizer scan-env --package rich --depth 2 --include-deps
echo ""
echo "✅ Tree structure now properly shows parent-child relationships!"
echo ""
read -p "Press Enter to continue..."
echo ""

# Demo 2: Why command
echo -e "${CYAN}🔍 Demo 2: Why Command${NC}"
echo "Let's find out why 'rich' is installed..."
echo "Command: pkgsizer why rich"
echo ""
pkgsizer why rich
echo ""
echo "✅ Now you know all dependency paths to 'rich'!"
echo ""
read -p "Press Enter to continue..."
echo ""

# Demo 3: Why command with JSON
echo -e "${CYAN}📄 Demo 2b: Why Command with JSON Output${NC}"
echo "Command: pkgsizer why rich --json /tmp/why-rich.json"
echo ""
pkgsizer why rich --json /tmp/why-rich.json
echo ""
echo "JSON output saved to /tmp/why-rich.json"
echo "Preview:"
cat /tmp/why-rich.json | head -20
echo "..."
echo ""
read -p "Press Enter to continue..."
echo ""

# Demo 4: Unused command (without code path)
echo -e "${CYAN}🗑️  Demo 3a: Unused Command (No Code Scan)${NC}"
echo "Command: pkgsizer unused"
echo ""
pkgsizer unused | head -30
echo ""
echo "⚠️  Without a code path, it just lists all packages"
echo ""
read -p "Press Enter to continue..."
echo ""

# Demo 5: Unused command (with code path)
echo -e "${CYAN}🗑️  Demo 3b: Unused Command (With Code Scan)${NC}"
echo "Let's scan the pkgsizer package itself for unused dependencies"
echo "Command: pkgsizer unused ./pkgsizer"
echo ""
pkgsizer unused ./pkgsizer | head -60
echo ""
echo "✅ Found packages that aren't imported in the code!"
echo ""
read -p "Press Enter to continue..."
echo ""

# Demo 6: Create test directory for unused detection
echo -e "${CYAN}🧪 Demo 3c: Unused Command (Custom Test)${NC}"
echo "Creating test code that only imports 'typer' and 'rich'..."
mkdir -p /tmp/test_pkgsizer
cat > /tmp/test_pkgsizer/main.py <<EOF
# Simple test file
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def hello(name: str):
    console.print(f"Hello {name}!")

if __name__ == "__main__":
    app()
EOF

echo ""
echo "Command: pkgsizer unused /tmp/test_pkgsizer"
echo ""
pkgsizer unused /tmp/test_pkgsizer | head -40
echo "..."
echo ""
echo "✅ Correctly identified that most packages are unused!"
echo ""

# Cleanup
rm -rf /tmp/test_pkgsizer
rm -f /tmp/why-rich.json

echo ""
echo "=================================="
echo -e "${GREEN}✅ Week 1 Demo Complete!${NC}"
echo ""
echo "Summary of Features:"
echo "  1. ✅ Fixed tree structure for dependency visualization"
echo "  2. ✅ 'pkgsizer why' - trace dependency paths"
echo "  3. ✅ 'pkgsizer unused' - find unused dependencies"
echo ""
echo "Next: Week 2 features (alternative packages, update checker, etc.)"
echo ""

