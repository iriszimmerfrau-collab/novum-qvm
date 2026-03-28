#!/usr/bin/env python3
"""
Test script: Train and test a Quantum Language Model on HTML document text.

This script:
1. Loads the QNLP HTML document
2. Extracts plain text from HTML
3. Creates a quantum language model
4. Trains the model on the extracted text
5. Tests text generation with various prompts
"""

import sys
import os
import time
import re
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(__file__))

from novum_qvm import QuantumLanguageModel


class HTMLTextExtractor(HTMLParser):
    """Simple HTML to text extractor."""
    
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_script = False
    
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip_script = True
    
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip_script = False
    
    def handle_data(self, data):
        if not self.skip_script:
            text = data.strip()
            if text:
                self.text_parts.append(text)
    
    def get_text(self):
        return ' '.join(self.text_parts)


def load_html_text(filepath):
    """Load and extract text from HTML file."""
    print(f"Loading HTML from {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""
    
    # Extract text
    extractor = HTMLTextExtractor()
    extractor.feed(html_content)
    text = extractor.get_text()
    
    # Clean up: remove extra spaces, normalize
    text = re.sub(r'\s+', ' ', text)
    
    print(f"Extracted {len(text)} characters from HTML")
    print(f"Text preview: {text[:200]}...")
    return text


def train_model(text, vocab_size=500, embedding_qubits=6, context_length=3):
    """Create and train a quantum language model."""
    print("\n=== Creating Quantum Language Model ===")
    print(f"  Vocab size: {vocab_size}")
    print(f"  Embedding qubits: {embedding_qubits}")
    print(f"  Context length: {context_length}")
    
    model = QuantumLanguageModel(
        vocab_size=vocab_size,
        embedding_qubits=embedding_qubits,
        context_length=context_length
    )
    
    print("\nTraining model on corpus...")
    start_time = time.time()
    model.add_training_corpus(text)
    train_time = time.time() - start_time
    
    vocab_count = len(model.vocab.word_to_idx)
    print(f"✓ Training completed in {train_time:.2f}s")
    print(f"  Vocabulary learned: {vocab_count} words")
    print(f"  Transition patterns: {len(model.transitions)}")
    
    return model


def test_generation(model, prompts, max_length=20, temperature=1.0):
    """Test text generation with various prompts."""
    print("\n=== Testing Text Generation ===")
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


def test_prediction(model, test_contexts):
    """Test next-word prediction."""
    print("=== Testing Next-Word Prediction ===\n")
    
    for context in test_contexts:
        print(f"Context: '{context}'")
        try:
            next_word = model.predict_next_word(context, temperature=0.8, shots=300)
            print(f"  Next word (predicted): '{next_word}'\n")
        except Exception as e:
            print(f"  Error: {e}\n")


def main():
    """Main execution."""
    print("Quantum NLP Model Training and Testing")
    print("=" * 60)
    
    # Load HTML file
    html_path = "Quantum Natural Language Processing.html"
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found")
        return
    
    # Extract text
    text = load_html_text(html_path)
    if not text:
        print("Failed to extract text from HTML")
        return
    
    # Train model
    print(f"\nText statistics:")
    words = text.lower().split()
    print(f"  Total words: {len(words)}")
    print(f"  Unique words: {len(set(words))}")
    
    model = train_model(text, vocab_size=300, embedding_qubits=5, context_length=3)
    
    # Test generation with different prompts
    test_prompts = [
        "quantum",
        "quantum computing",
        "natural language",
        "quantum language",
        "the quantum",
    ]
    test_generation(model, test_prompts, max_length=15, temperature=0.9)
    
    # Test next-word prediction
    test_contexts = [
        "quantum",
        "quantum computing",
        "language processing",
        "the cat",
    ]
    test_prediction(model, test_contexts)
    
    print("\n" + "=" * 60)
    print("✓ Training and testing completed successfully!")


if __name__ == "__main__":
    main()
