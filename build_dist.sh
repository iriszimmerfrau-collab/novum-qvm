#!/bin/bash
# Build and publish to PyPI

set -e

echo "========================================"
echo "novum-qvm: PyPI Distribution Builder"
echo "========================================"
echo ""

# Check for required tools
command -v python &> /dev/null || { echo "Python not found!"; exit 1; }
command -v twine &> /dev/null || { echo "Twine not found! Install with: pip install twine"; exit 1; }

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info 2>/dev/null || true

# Install build tools
echo "Installing build tools..."
python -m pip install --upgrade build setuptools wheel

# Build distribution
echo ""
echo "Building distribution..."
python -m build

# Check files
echo ""
echo "Build artifacts:"
ls -lh dist/

# Verify with twine
echo ""
echo "Verifying distribution..."
twine check dist/*

echo ""
echo "========================================"
echo "✓ Distribution ready in dist/"
echo "========================================"
echo ""
echo "To upload to PyPI, run:"
echo "  twine upload dist/*"
echo ""
echo "To upload to TestPyPI first, run:"
echo "  twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
echo ""
