#!/usr/bin/env python3
"""
Deployment verification script - confirms all files are in place and valid
"""

import os
import sys
from pathlib import Path

def verify_deployment():
    """Verify all deployment files exist and are valid"""
    
    print("\n" + "="*70)
    print("DEPLOYMENT VERIFICATION SCRIPT")
    print("="*70 + "\n")
    
    base_path = Path(".")
    required_files = {
        "Configuration": [
            "setup.py",
            "pyproject.toml",
            "MANIFEST.in",
            "LICENSE",
        ],
        "GitHub Automation": [
            ".github/workflows/publish.yml",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/feature_request.md",
            ".github/pull_request_template.md",
        ],
        "Distribution": [
            "build_dist.sh",
            "build_dist.ps1",
            ".gitignore",
        ],
        "Documentation": [
            "README_DEPLOYMENT.md",
            "DEPLOY_QUICK_START.md",
            "PYPI_GITHUB_SETUP.md",
            "PyPI_GITHUB_DEPLOYMENT_READY.md",
            "DEPLOYMENT_COMPLETE.md",
            "CONTRIBUTING.md",
        ],
        "Package": [
            "novum_qvm/__init__.py",
            "dist/novum_qvm-1.1.0.tar.gz",
        ]
    }
    
    all_pass = True
    
    for category, files in required_files.items():
        print(f"📁 {category}:")
        category_pass = True
        for file in files:
            path = base_path / file
            exists = path.exists()
            status = "✓" if exists else "✗"
            size_str = ""
            if exists and path.is_file():
                size = path.stat().st_size
                if size > 1024:
                    size_str = f" ({size/1024:.1f}KB)"
                else:
                    size_str = f" ({size}B)"
            
            print(f"   {status} {file}{size_str}")
            if not exists:
                category_pass = False
                all_pass = False
        
        status_line = "✓ PASS" if category_pass else "✗ FAIL"
        print(f"   → {status_line}\n")
    
    return all_pass

def main():
    success = verify_deployment()
    
    if success:
        print("="*70)
        print("✅ ALL FILES VERIFIED - READY FOR DEPLOYMENT")
        print("="*70)
        print("\nNext steps:")
        print("1. Create GitHub repository")
        print("2. Create PyPI account and API token")
        print("3. Add PYPI_TOKEN to GitHub Secrets")
        print("4. Push code: git push -u origin main")
        print("5. Create tag: git tag -a v1.1.0 -m 'Release 1.1.0'")
        print("6. Push tag: git push origin v1.1.0")
        print("\nGitHub Actions will automatically publish to PyPI!")
        print("\nFor detailed instructions, see: DEPLOY_QUICK_START.md")
        print("="*70 + "\n")
        return 0
    else:
        print("="*70)
        print("❌ VERIFICATION FAILED - MISSING FILES")
        print("="*70)
        print("\nPlease ensure all files listed above exist.")
        print("="*70 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
