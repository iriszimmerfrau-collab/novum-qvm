#!/usr/bin/env python3
"""
Train Quantum Language Model on the Puffin dataset from Hugging Face.

The Puffin dataset contains:
- 3,000 examples of multi-turn conversations
- Conversations between GPT-4 and real humans
- Average context length > 1,000 tokens
- Average > 10 turns per conversation

This script:
1. Downloads the Puffin dataset from Hugging Face
2. Extracts conversation text
3. Trains the quantum language model
4. Tests text generation
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

from novum_qvm import QuantumLanguageModel

# Try to import datasets library
try:
    from datasets import load_dataset
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False
    print("Warning: datasets library not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "datasets"])
    from datasets import load_dataset
    HAS_DATASETS = True


def load_puffin_dataset(split="train", num_examples=None):
    """Load the Puffin dataset from Hugging Face."""
    print("Loading Puffin dataset from Hugging Face...")
    print("(This may take a minute on first download)")
    
    try:
        dataset = load_dataset("LDJnr/Puffin", split=split)
        
        if num_examples is not None:
            dataset = dataset.select(range(min(num_examples, len(dataset))))
        
        print(f"✓ Loaded {len(dataset)} examples from Puffin")
        return dataset
    except Exception as e:
        print(f"Error loading dataset: {e}")
        raise


def extract_conversation_text(dataset, max_examples=None):
    """Extract and concatenate all conversation text."""
    print("\nExtracting conversation text...")
    
    all_text = []
    
    for i, example in enumerate(dataset):
        if max_examples and i >= max_examples:
            break
        
        # Puffin dataset has 'conversations' field with list of {'from': 'human'/'gpt', 'value': text}
        text_parts = []
        
        if 'conversations' in example and example['conversations']:
            for turn in example['conversations']:
                if isinstance(turn, dict) and 'value' in turn:
                    value = turn['value']
                    if value:
                        text_parts.append(str(value))
        
        if text_parts:
            all_text.append(' '.join(text_parts))
        
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1} examples...")
    
    # Concatenate all text
    combined_text = ' '.join(all_text)
    print(f"✓ Extracted text from {len(all_text)} conversations")
    print(f"  Total text length: {len(combined_text):,} characters")
    print(f"  Approx words: {len(combined_text.split()):,}")
    
    return combined_text


def train_on_puffin(num_examples=500, vocab_size=1000, embedding_qubits=4, context_length=3):
    """Load Puffin dataset and train quantum model."""
    
    print("=" * 70)
    print("QUANTUM LANGUAGE MODEL - PUFFIN DATASET TRAINING")
    print("=" * 70)
    
    # Load dataset
    dataset = load_puffin_dataset(split="train", num_examples=num_examples)
    
    # Extract text
    text = extract_conversation_text(dataset, max_examples=num_examples)
    
    # Print statistics
    words = text.lower().split()
    unique_words = len(set(words))
    print(f"\nText statistics:")
    print(f"  Total words: {len(words):,}")
    print(f"  Unique words: {unique_words:,}")
    print(f"  Vocabulary coverage: {min(vocab_size, unique_words):,} / {unique_words:,}")
    
    # Create and train model
    print(f"\n=== Creating Quantum Language Model ===")
    print(f"  Vocab size: {vocab_size}")
    print(f"  Embedding qubits: {embedding_qubits}")
    print(f"  Context length: {context_length}")
    
    model = QuantumLanguageModel(
        vocab_size=vocab_size,
        embedding_qubits=embedding_qubits,
        context_length=context_length
    )
    
    print(f"\nTraining on Puffin corpus...")
    start_time = time.time()
    model.add_training_corpus(text)
    train_time = time.time() - start_time
    
    vocab_count = len(model.vocab.word_to_idx)
    transitions = len(model.transitions)
    print(f"✓ Training completed in {train_time:.2f}s")
    print(f"  Vocabulary learned: {vocab_count} words")
    print(f"  Transition patterns: {transitions}")
    
    return model, text


def test_generation(model, prompts=None, max_length=15, temperature=0.9):
    """Test text generation on the trained model."""
    
    if prompts is None:
        prompts = [
            "the question",
            "how can",
            "what is",
            "explain the",
            "the answer",
        ]
    
    print(f"\n=== Testing Text Generation ===")
    print(f"Max length: {max_length}, Temperature: {temperature}\n")
    
    for i, prompt in enumerate(prompts, 1):
        print(f"Test {i}: Prompt = '{prompt}'")
        start_time = time.time()
        try:
            generated = model.generate_text(prompt, max_length=max_length, temperature=temperature)
            gen_time = time.time() - start_time
            print(f"  Generated: '{generated}'")
            print(f"  Time: {gen_time:.3f}s\n")
        except Exception as e:
            print(f"  Error: {e}\n")


def main():
    """Main execution."""
    
    # Configuration
    num_examples = 500  # Use first 500 examples for training
    vocab_size = 500
    embedding_qubits = 4
    context_length = 3
    
    try:
        # Train on Puffin
        model, text = train_on_puffin(
            num_examples=num_examples,
            vocab_size=vocab_size,
            embedding_qubits=embedding_qubits,
            context_length=context_length
        )
        
        # Test generation
        test_generation(model, max_length=12, temperature=0.8)
        
        print("\n" + "=" * 70)
        print("✓ Puffin dataset training completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
