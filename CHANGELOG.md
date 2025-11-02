# Changelog

All notable changes to pkgsizer will be documented in this file.

## [Unreleased]

_No unreleased changes yet._

## [0.1.2] - 2025-10-31

### 🆕 Added
- **Interactive HTML reports**: `pkgsizer scan-env --html report.html` now generates a shareable HTML dashboard with charts, searchable tables, and summary insights.
- **GitHub Action**: Composite action (`.github/actions/pkgsizer`) for CI/CD workflows, plus an example workflow for quick adoption.
- **GitLab CI/CD template**: Added `.gitlab-ci.yml` for quick integration into GitLab pipelines.
- **SEO landing page**: New `docs/index.html` optimized for search engines and GitHub Pages.
- **Optional extras**: `pkgsizer[html]`, `pkgsizer[yaml]`, and `pkgsizer[all]` extras reduce default install size while keeping advanced features available.
- **README examples**: Additional GitHub/GitLab snippets and quick-start commands.

### ✨ Improved
- **Live progress bars**: Long-running scans now show progress feedback in the terminal when 10+ packages are processed.
- **Error messaging**: CLI commands provide actionable hints for common issues like missing paths, optional dependencies, or invalid thresholds.
- **Keyword metadata**: Added GitHub/GitLab/CLI keywords to improve PyPI and search engine discoverability.

## [0.3.0] - 2025-10-30 - Week 2 Features

### 🆕 Added
- **`pkgsizer alternatives [package]` command**: Suggest lighter or better alternatives
  - Database of 24 popular packages with alternatives
  - Shows size expectations (smaller, similar, larger)
  - Checks if alternatives are already installed
  - Actual size comparisons for installed alternatives
  - `--list-all` flag to browse the alternatives database
  - JSON output support

- **`pkgsizer updates [packages]` command**: Check for outdated packages
  - Fetches latest versions from PyPI
  - Compares with installed versions using semantic versioning
  - Shows current package sizes
  - Provides pip upgrade commands
  - `--all` flag to check all packages
  - JSON output support

- **`pkgsizer compare env1 env2` command**: Compare two environments
  - Shows packages in common with version differences
  - Lists unique packages in each environment
  - Calculates total size differences
  - Smart path resolution (handles venv and site-packages)
  - Custom environment names
  - JSON output support

### 📊 Statistics
- **Lines of Code Added**: ~1000
- **New Modules**: 3 (`alternatives.py`, `updates.py`, `compare.py`)
- **Alternatives Database**: 24 packages, 45 alternatives
- **Performance**: < 1s for alternatives, 0.5s/pkg for updates

---

## [0.2.0] - 2025-10-30 - Week 1 Features

### 🆕 Added
- **`pkgsizer why <package>` command**: Trace why a package is installed
  - Shows all dependency paths from root packages to target
  - Displays package size, version, and depth
  - Provides removal safety advice
  - Supports JSON output for automation
  - Fast performance (< 1 second for typical environments)

- **`pkgsizer unused [code_path]` command**: Find unused dependencies
  - AST-based code scanning for accurate import detection
  - Calculates wasted disk space
  - Provides removal recommendations
  - Supports JSON output
  - Excludes common directories (`__pycache__`, `.git`, `venv`, etc.)

### 🔧 Fixed
- **Tree structure display**: Now properly shows parent-child relationships
  - Implemented `_traverse_tree_order()` for correct DFS traversal
  - Tree prefixes (`└─ `) now correctly indicate hierarchy
  - Packages displayed in proper parent-before-children order

### 📚 Documentation
- Added `WEEK1_FEATURES.md` - Comprehensive feature documentation
- Added `WEEK1_COMPLETE.md` - Implementation summary
- Added `QUICK_REFERENCE.md` - Command quick reference guide
- Added `week1_demo.sh` - Interactive demo script
- Updated `README.md` with new features
- Created `CHANGELOG.md` (this file)

### 🎯 Performance
- `why` command: < 1s for environments with < 500 packages
- `unused` command: 2-30s depending on codebase size
- Added caching for package size calculations
- Limited path finding to prevent infinite loops (max 20 paths, max depth 10)

### 📊 Statistics
- **Lines of Code Added**: ~500
- **New Files**: 6
- **Modified Files**: 3
- **Test Coverage**: Manual testing complete

---

## [0.1.0] - 2025-10-29 - Initial Release

### 🆕 Added
- **`pkgsizer scan-env` command**: Scan Python environment for package sizes
  - Measure on-disk sizes of installed packages
  - Show dependency trees with configurable depth
  - Enumerate subpackages to specified depth
  - Support for editable installs
  - Beautiful Rich terminal output
  - JSON export

- **`pkgsizer analyze-file` command**: Analyze dependency files
  - Support for `requirements.txt`
  - Support for Poetry (`pyproject.toml`, `poetry.lock`)
  - Support for uv (`uv.lock`)
  - Support for Conda (`environment.yml`)
  - Support for Pipfile

### ✨ Core Features
- Inode-based deduplication for accurate size calculation
- Configurable exclusion patterns
- Editable install detection and marking
- Symlink handling (follow or skip)
- Multiple output formats (table, tree, JSON)
- Environment auto-detection (venv, pyenv, conda)

### 📚 Documentation
- Comprehensive README with examples
- Implementation guide (`IMPLEMENTATION.md`)
- Quick start guide (`QUICKSTART.md`)
- Project summary (`PROJECT_SUMMARY.md`)
- Command explanations (`COMMAND_EXPLANATION.md`)
- Feature analysis (`DEEP_FEATURE_ANALYSIS.md`)

### 🎯 Performance
- Fast scanning with parallel file I/O where possible
- Efficient memory usage with streaming
- Typical scan time: 1-5 seconds for 100 packages

---

## Roadmap

### Week 2 (Upcoming)
- [ ] Alternative package suggestions
- [ ] Dependency update checker
- [ ] Environment comparison tool

### Week 3 (Upcoming)
- [ ] Virtual environment creator/tester
- [ ] License checker
- [ ] Security audit integration

### Week 4+ (Future)
- [ ] Web dashboard
- [ ] CI/CD GitHub Action
- [ ] Rust optimization for core operations
- [ ] Package similarity detection

---

## Version History Summary

| Version | Date | Key Features |
|---------|------|-------------|
| 0.2.0 | 2025-10-30 | `why`, `unused` commands, tree fix |
| 0.1.0 | 2025-10-29 | Initial release, `scan-env`, `analyze-file` |

---

## Contributing

See [CONTRIBUTING.md] for development guidelines.

## License

MIT License - see [LICENSE] for details.

