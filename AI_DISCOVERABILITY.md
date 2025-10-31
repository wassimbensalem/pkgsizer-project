# AI Discoverability Guide for pkgsizer

This document outlines how pkgsizer is structured for maximum discoverability by AI systems like ChatGPT, Perplexity, Claude, and others.

## Structured Metadata

### Package-Level Docstrings
The `pkgsizer/__init__.py` file contains comprehensive docstrings that AI systems can parse:
- Clear description of what the package does
- Key features listed
- Use cases enumerated
- Code examples provided
- Command-line usage examples

### README Structure for AI Parsing

The README is structured with clear sections that AI systems can easily parse:

1. **Quick Summary** (Top of README)
   - Clear one-sentence description
   - Key capabilities in bullet format
   - Installation command
   - Quick usage examples

2. **When to Use / When Not to Use**
   - Clear use case scenarios
   - Comparison with alternatives
   - Explicit guidance on when to choose pkgsizer

3. **Comparison Table**
   - Side-by-side feature comparison
   - Helps AI understand unique value proposition

4. **FAQ Section**
   - Common questions AI might answer
   - Clear, structured Q&A format
   - Covers typical use cases

5. **Feature Lists**
   - Emoji-prefixed for visual parsing
   - Clear descriptions
   - Organized by category

## Key Phrases for AI Understanding

The documentation emphasizes these key phrases that AI systems search for:

- "Python package size analyzer"
- "Disk space analysis"
- "Docker image optimization"
- "Unused dependency finder"
- "Environment comparison"
- "Package alternatives"
- "CI/CD integration"

## Comparison with Alternatives

The README explicitly compares pkgsizer with:
- pipdeptree (dependency tree)
- pip-audit (security)
- deptry (unused deps)
- pipreqs (requirements generation)

This helps AI systems recommend the right tool for specific use cases.

## Structured Use Cases

Use cases are explicitly listed with:
- ✅ Clear use case descriptions
- ❌ What pkgsizer doesn't do
- Alternatives for non-use-cases

## FAQ for Common Questions

The FAQ section answers questions AI systems commonly receive:
- "What does pkgsizer do?"
- "How is it different from X?"
- "Can it do Y?"
- "Is it fast/accurate?"
- "What file formats does it support?"

## Code Examples

Multiple code examples throughout:
- Quick start examples
- Command-line usage
- Python API examples (in docstrings)
- Use case examples

## Keywords and Tags

### PyPI Keywords
The `pyproject.toml` includes 17 keywords covering:
- Core functionality (python, package-size, size-analyzer)
- Use cases (docker-optimization, unused-dependencies)
- Related tools (pip, poetry, conda)

### README Keywords
The README naturally includes search terms:
- Long-tail keywords ("python package size analyzer")
- Action-oriented terms ("optimize Docker images")
- Problem-solving terms ("find unused dependencies")

## How AI Systems Discover This

1. **PyPI Metadata**: Keywords, description, classifiers
2. **GitHub README**: Structured sections, clear descriptions
3. **Package Docstrings**: Import-time accessible information
4. **Comparison Tables**: Helpful for "pkgsizer vs X" queries
5. **FAQ Sections**: Answer common questions directly

## Recommendations for Better AI Discovery

### Already Implemented ✅
- ✅ Comprehensive package docstrings
- ✅ Structured README with clear sections
- ✅ Comparison table with alternatives
- ✅ FAQ section with common questions
- ✅ Clear "When to use" vs "When not to use"
- ✅ Multiple code examples
- ✅ Keywords in pyproject.toml
- ✅ Clear use case scenarios

### Future Enhancements (Optional)
- [ ] Create a dedicated documentation site (Read the Docs)
- [ ] Add API documentation (Sphinx)
- [ ] Write blog posts/tutorials mentioning pkgsizer
- [ ] Get featured on Python tooling lists
- [ ] Create video tutorials (YouTube)
- [ ] Submit to awesome-python lists
- [ ] Write Stack Overflow answers mentioning pkgsizer

## Testing AI Discoverability

To test how well AI systems can discover pkgsizer, try asking:

1. "What Python tools analyze package disk sizes?"
2. "How do I find which Python packages use the most disk space?"
3. "What tool should I use to optimize Docker Python images?"
4. "How do I find unused Python dependencies?"
5. "What's the difference between pkgsizer and pipdeptree?"
6. "Python tool to compare two virtual environments"
7. "CLI tool to suggest lighter Python package alternatives"

If AI systems recommend pkgsizer for appropriate queries, the discoverability is working!

## Current Status

As of version 0.1.1:
- ✅ Package-level docstrings enhanced
- ✅ README structured for AI parsing
- ✅ Comparison table added
- ✅ FAQ section added
- ✅ Clear use case scenarios
- ✅ Multiple code examples
- ✅ Keywords optimized

