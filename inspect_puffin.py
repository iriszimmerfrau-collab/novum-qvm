#!/usr/bin/env python3
"""Inspect Puffin dataset structure."""

import sys

try:
    from datasets import load_dataset
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "datasets", "-q"])
    from datasets import load_dataset

print("Loading Puffin dataset...")
dataset = load_dataset("LDJnr/Puffin", split="train")

print(f"Dataset size: {len(dataset)}")
print(f"\nDataset features: {dataset.features}")
print(f"\nFirst example:")
first_example = dataset[0]
for key, value in first_example.items():
    if isinstance(value, str):
        preview = value[:100] if len(value) > 100 else value
        print(f"  {key}: {preview}...")
    else:
        print(f"  {key}: {value}")

print(f"\nSecond example:")
second_example = dataset[1]
for key, value in second_example.items():
    if isinstance(value, str):
        preview = value[:100] if len(value) > 100 else value
        print(f"  {key}: {preview}...")
    else:
        print(f"  {key}: {value}")

print(f"\nKeys in first example: {list(first_example.keys())}")
