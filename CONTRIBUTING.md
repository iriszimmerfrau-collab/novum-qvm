# Contributing to novum-qvm

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- pip and virtual environment setup

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/novum-qvm.git
cd novum-qvm

# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## Development Workflow

1. **Create a branch** from `develop` for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit frequently:
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

3. **Write or update tests** for your changes:
   ```bash
   pytest tests/ -v
   ```

4. **Run linting** to check code style:
   ```bash
   flake8 novum_qvm
   ```

5. **Format code** for consistency:
   ```bash
   black novum_qvm
   ```

6. **Push to your fork** and create a pull request (PR)

## Pull Request Process

1. Update `README.md` if needed
2. Update docstrings and comments
3. Ensure all tests pass
4. Add your changes to the PR description
5. Request review from maintainers

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=novum_qvm

# Run specific test file
pytest tests/test_algorithm.py -v
```

## Code Style

- Follow PEP 8
- Use `black` for formatting
- Use type hints where applicable
- Write descriptive docstrings

Example:
```python
def measure(self, shots: int = 1000) -> Dict[str, int]:
    """
    Measure quantum state with importance sampling.
    
    Args:
        shots: Number of measurement repetitions
        
    Returns:
        Dictionary of measurement outcomes and frequencies
    """
```

## Reporting Issues

Use the [Bug Report](../../issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBUG%5D+) template and include:
- Python version
- novum-qvm version
- OS and environment
- Steps to reproduce
- Error messages/logs

## Feature Requests

Use the [Feature Request](../../issues/new?assignees=&labels=enhancement&template=feature_request.md&title=%5BFEATURE%5D+) template and include:
- Clear description
- Use case/motivation
- Proposed solution
- Example code if applicable

## Git Commit Messages

Use clear, descriptive commit messages:
- ✅ Good: "Add trigram transitions for improved coherence"
- ❌ Avoid: "fix stuff", "update", "test"

Format:
```
[Type] Brief description

Optional longer explanation of changes.
- Mention specific files if helpful
- Reference related issues #123
```

Types:
- `[FEATURE]`: New feature
- `[BUG]`: Bug fix
- `[DOCS]`: Documentation
- `[REFACTOR]`: Code refactoring
- `[TESTS]`: Test updates

## Release Process

1. Update version in `setup.py` and `pyproject.toml`
2. Update `CHANGELOG.md` (create if not exists)
3. Create PR, get approval
4. Merge to `main`
5. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
6. Push tag: `git push origin vX.Y.Z`
7. GitHub Actions automatically publishes to PyPI

## Questions?

- Check [GitHub Issues](../../issues)
- Read [documentation](../../wiki)
- Open an issue with your question

---

**Thank you for contributing to novum-qvm!** 🚀
