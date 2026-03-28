# PyPI & GitHub Setup Guide

## Overview

This document describes how to complete the PyPI and GitHub setup for publishing `novum-qvm` to PyPI and setting up your GitHub repository for CI/CD.

## Prerequisites

- Python 3.8+
- GitHub account (for repository)
- PyPI account (for package publishing)
- Git installed locally

## Step 1: Prepare Your GitHub Account

### Create a GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click **New** to create a new repository
3. Repository name: `novum-qvm`
4. Description: "Perlin-Fourier Quantum Virtual Simulation (PFQVS)"
5. Make it **Public** for open-source
6. Click **Create repository**

### Clone and Set Remote

```bash
git clone https://github.com/yourusername/novum-qvm.git
cd novum-qvm
git add .
git commit -m "Initial commit: PFQVS quantum simulator with QNLP"
git push -u origin main
```

## Step 2: Update Package URLs

Replace `yourusername` in these files with your actual GitHub username:

- **setup.py**: Line with `https://github.com/yourusername/novum-qvm`
- **pyproject.toml**: Lines with `https://github.com/yourusername/novum-qvm`

## Step 3: Set Up PyPI Credentials

### Create PyPI Account

1. Go to [pypi.org](https://pypi.org)
2. Click **Register** and create account
3. Verify email
4. Set up two-factor authentication (recommended)

### Create PyPI Token

1. In PyPI, go to **Account Settings** → **API tokens**
2. Click **Add API token**
3. Name: `novum-qvm-ci`
4. Scope: **Entire account** (or just this project)
5. Copy the token (starts with `pypi-`)

### Add GitHub Secret

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
3. Name: `PYPI_TOKEN`
4. Value: Paste your PyPI token
5. Click **Add secret**

## Step 4: Build and Test Distribution

### Test Locally

```bash
# On Linux/macOS
bash build_dist.sh

# On Windows PowerShell
.\build_dist.ps1
```

This will:
- Install build tools
- Build wheel (.whl) and source (.tar.gz) distributions
- Verify with twine
- Output artifacts to `dist/`

### Test on TestPyPI First

```bash
twine upload --repository testpypi dist/*
# You'll be prompted for credentials (use __token__ as username)
```

Then test installation:
```bash
pip install -i https://test.pypi.org/simple/ novum-qvm==1.1.0
```

## Step 5: Tag Release and Push to GitHub

```bash
# Create annotated tag
git tag -a v1.1.0 -m "Release version 1.1.0"

# Push tag to GitHub
git push origin v1.1.0
```

This automatically triggers the GitHub Actions workflow to:
- Run tests on Python 3.8-3.11
- Run tests on Windows, macOS, Linux
- If all pass, publish to PyPI

## Step 6: Publish to PyPI

### Automatic (Recommended)

Once you push a tag like `v1.1.0`, GitHub Actions automatically builds and publishes.

### Manual

```bash
twine upload dist/*
```

You'll be prompted:
- Username: `__token__`
- Password: Your PyPI token

## Post-Release Checklist

- [ ] Verify package on [pypi.org/project/novum-qvm](https://pypi.org/project/novum-qvm)
- [ ] Test installation: `pip install novum-qvm`
- [ ] Create GitHub release page with release notes
- [ ] Announce on your social media/forums

## Project Structure

```
novum-qvm/
├── .github/
│   └── workflows/
│       └── publish.yml          # CI/CD workflows
├── novum_qvm/                   # Main package
│   ├── QuantumComputer.py
│   ├── qnlp.py
│   ├── functions.py
│   ├── quantum_toolkit.py
│   └── __init__.py
├── tests/                       # Test suite
├── setup.py                     # Build configuration
├── pyproject.toml               # Project metadata
├── README.md                    # Overview
├── LICENSE                      # MIT License
├── MANIFEST.in                  # Package files
├── .gitignore                   # Git ignore rules
├── build_dist.sh               # Build script (Linux/macOS)
└── build_dist.ps1              # Build script (Windows)
```

## Troubleshooting

### "Package already exists" on PyPI

- Increment version number in `setup.py` and `pyproject.toml`
- Create new tag like `v1.1.1`
- Push and re-run workflow

### GitHub Actions failing

1. Check workflow logs: **Actions** tab in GitHub
2. Common issues:
   - Python syntax errors: Fix and re-push
   - Missing dependencies: Add to `install_requires` in setup.py
   - PYPI_TOKEN not set: Add to repository secrets

### Installation issues

- Try on fresh venv: `python -m venv test_env && source test_env/bin/activate && pip install novum-qvm`
- Check for conflicts with existing packages
- Read installation error messages carefully

## Next Steps

1. **Documentation**: Add full API docs in `/docs` directory
2. **Examples**: Add example scripts in `/examples` directory
3. **Community**: Set up discussions/issues templates on GitHub
4. **CI/CD**: Add code coverage tracking with Codecov
5. **Releases**: Automate changelog generation

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [PyPI Help](https://pypi.org/help/)
- [GitHub Actions](https://docs.github.com/actions)
- [twine Documentation](https://twine.readthedocs.io/)
