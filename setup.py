#!/usr/bin/env python3
"""
Setup file for novum-qvm package distribution on PyPI.
"""

from setuptools import setup, find_packages

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="novum-qvm",
    version="1.1.0",
    author="Amin Alogaili",
    author_email="aminalogai@aol.com",
    description="Perlin-Fourier Quantum Virtual Simulation (PFQVS): Advanced quantum circuit simulator with QNLP support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/novum-qvm",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/novum-qvm/issues",
        "Documentation": "https://github.com/yourusername/novum-qvm/wiki",
        "Source Code": "https://github.com/yourusername/novum-qvm",
    },
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*", "docs", "examples"]),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.22.0",
        "pennylane>=0.25.0",
        "qiskit>=0.39.0",
        "qiskit-aer>=0.11.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "qnlp": [
            "datasets>=2.0.0",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.12",
            "black>=21.0",
            "flake8>=3.9",
        ],
        "ml": [
            "torch>=1.9.0",
            "tensorflow>=2.6.0",
            "PennyLane>=0.25.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="quantum computing simulation PFQVS QNLP quantum-machine-learning",
    include_package_data=True,
    zip_safe=False,
)
