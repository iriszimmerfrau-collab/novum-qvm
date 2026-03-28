# Build and publish to PyPI (Windows)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Green
Write-Host "novum-qvm: PyPI Distribution Builder" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check Python
try {
    python --version | Out-Null
} catch {
    Write-Host "Python not found!" -ForegroundColor Red
    exit 1
}

# Check twine
try {
    twine --version | Out-Null
} catch {
    Write-Host "Twine not found! Install with: pip install twine" -ForegroundColor Red
    exit 1
}

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Path "build", "dist", "*.egg-info" -Recurse -ErrorAction SilentlyContinue

# Install build tools
Write-Host "Installing build tools..." -ForegroundColor Yellow
python -m pip install --upgrade build setuptools wheel

# Build distribution
Write-Host ""
Write-Host "Building distribution..." -ForegroundColor Yellow
python -m build

# Check files
Write-Host ""
Write-Host "Build artifacts:" -ForegroundColor Cyan
Get-ChildItem -Path "dist" | Format-List

# Verify with twine
Write-Host ""
Write-Host "Verifying distribution..." -ForegroundColor Yellow
twine check (Get-ChildItem -Path "dist" -File)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Distribution ready in dist/" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To upload to PyPI, run:" -ForegroundColor Cyan
Write-Host "  twine upload dist/*" -ForegroundColor White
Write-Host ""
Write-Host "To upload to TestPyPI first, run:" -ForegroundColor Cyan
Write-Host "  twine upload --repository-url https://test.pypi.org/legacy/ dist/*" -ForegroundColor White
Write-Host ""
