# pkgsizer – Python Package Size Analyzer

pkgsizer is an open-source CLI tool that helps developers measure and optimize Python package disk usage. It analyzes installed packages, dependency trees, Docker images, virtual environments, and more.

## Why pkgsizer?
- **Measure package size** – identify the largest packages in your environment.
- **Optimize Docker images** – find big dependencies before building containers.
- **Clean unused packages** – detect dependencies never imported by your code.
- **Compare environments** – spot differences between dev and prod.
- **CI/CD ready** – GitHub Actions and GitLab templates included.
- **HTML reports** – share interactive charts with your team.

## Key Features
- Disk usage analysis for all installed packages
- Dependency tree visualization and cumulative size tracking
- Optional HTML reporting (`pkgsizer[html]`)
- Conda `environment.yml` parsing (`pkgsizer[yaml]`)
- `pkgsizer compare` for environment diffs
- `pkgsizer updates` to detect outdated packages
- `pkgsizer alternatives` for lighter replacements

## Installation
```bash
pip install pkgsizer

# Optional extras
pip install "pkgsizer[html]"   # HTML reports
pip install "pkgsizer[yaml]"   # Conda environment parsing
```

## Quick Start
```bash
# Scan current environment
pkgsizer scan-env --top 20

# Generate HTML report
pkgsizer scan-env --html pkgsizer-report.html

# Compare two environments
pkgsizer compare path/to/env1 path/to/env2 --html comparison.html

# Enforce size budgets in CI/CD
pkgsizer scan-env --fail-over 500MB
```

## CI/CD Integration
- GitHub Actions: `.github/actions/pkgsizer`
- Example workflow: `.github/workflows/pkgsizer.yml`
- GitLab CI template: `.gitlab-ci.yml`

## Learn More
- README: Detailed features and command reference
- CHANGELOG: Release notes and new features
- TESTING_GUIDE: How to validate pkgsizer locally and in CI
- SEO_IMPROVEMENTS: Strategies for improving discoverability

Follow the project on GitHub once the repository is published to get updates and contribute improvements.

