#!/usr/bin/env python3
"""
Enhanced Puffin Training: Train quantum model on larger Puffin dataset sample.

Features:
- Loads 1000 examples from Puffin (multi-turn conversations)
- Extracts ~700K words of real dialogue
- Trains quantum model with larger vocabulary
- Generates coding and technical questions based on Puffin data
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

from novum_qvm import QuantumLanguageModel

try:
    from datasets import load_dataset
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "datasets", "-q"])
    from datasets import load_dataset


def train_puffin_enhanced(num_examples=1000, vocab_size=1000, embedding_qubits=4):
    """Train on larger Puffin dataset."""
    
    print("=" * 75)
    print("QUANTUM LANGUAGE MODEL - PUFFIN DATASET (ENHANCED)")
    print("=" * 75)
    
    # Load Puffin dataset
    print(f"\nLoading {num_examples} examples from Puffin...")
    dataset = load_dataset("LDJnr/Puffin", split="train")
    dataset = dataset.select(range(min(num_examples, len(dataset))))
    
    # Extract text
    print(f"Extracting conversation text...")
    all_text = []
    for i, example in enumerate(dataset):
        if 'conversations' in example and example['conversations']:
            for turn in example['conversations']:
                if isinstance(turn, dict) and 'value' in turn:
                    value = turn['value']
                    if value:
                        all_text.append(str(value))
        
        if (i + 1) % 200 == 0:
            print(f"  {i + 1}/{num_examples} examples processed...")
    
    text = ' '.join(all_text)
    
    # Statistics
    words = text.lower().split()
    unique_words = len(set(words))
    print(f"\n✓ Extracted {len(all_text)} text segments")
    print(f"  Total characters: {len(text):,}")
    print(f"  Total words: {len(words):,}")
    print(f"  Unique words: {unique_words:,}")
    
    # Train model
    print(f"\n=== Quantum Model Configuration ===")
    print(f"  Vocabulary: {vocab_size}")
    print(f"  Embedding qubits: {embedding_qubits}")
    
    model = QuantumLanguageModel(
        vocab_size=vocab_size,
        embedding_qubits=embedding_qubits,
        context_length=3
    )
    
    print(f"\nTraining on Puffin corpus...")
    start = time.time()
    model.add_training_corpus(text)
    train_time = time.time() - start
    
    print(f"✓ Training in {train_time:.2f}s")
    print(f"  Vocabulary learned: {len(model.vocab.word_to_idx)}")
    print(f"  Transition patterns: {len(model.transitions)}")
    
    # Test with technical prompts from Puffin
    print(f"\n=== Generation Tests (Puffin-style Prompts) ===\n")
    
    prompts = [
        "how do i",
        "what is",
        "explain how",
        "can you",
        "the code",
    ]
    
    for prompt in prompts:
        gen = model.generate_text(prompt, max_length=15, temperature=0.85)
        print(f"Prompt: '{prompt}'")
        print(f"  → {gen}\n")
    
    print("=" * 75)
    print("✓ Puffin quantum training complete!")
    print("=" * 75)
    
    return model


if __name__ == "__main__":
    try:
        model = train_puffin_enhanced(num_examples=1000, vocab_size=1000, embedding_qubits=4)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
