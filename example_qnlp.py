#!/usr/bin/env python3
"""
Example script demonstrating Quantum Natural Language Processing (QNLP) with PFQVS.

This script showcases:
- Quantum string encoding
- Quantum word embeddings
- Quantum attention
- Quantum syntactic parsing
- Quantum language generation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from novum_qvm import (
    QuantumStringEncoder,
    QuantumWordEmbeddings,
    QuantumAttention,
    QuantumSyntacticParser,
    QuantumLanguageModel
)

def demo_string_encoding():
    """Demonstrate quantum string encoding."""
    print("=== Quantum String Encoding Demo ===")
    encoder = QuantumStringEncoder()
    text = "Hello, quantum world!"
    qc = encoder.encode_string(text)
    print(f"Encoded '{text}' into quantum state with {qc.n_qubits} qubits")
    # Decode (simplified)
    decoded = encoder.decode_string(qc)
    print(f"Decoded back: '{decoded}'")

def demo_word_embeddings():
    """Demonstrate quantum word embeddings."""
    print("\n=== Quantum Word Embeddings Demo ===")
    embeddings = QuantumWordEmbeddings()
    
    words = ["quantum", "classical", "computer", "algorithm"]
    for word in words:
        emb = embeddings.get_embedding(word)
        print(f"Embedding for '{word}': {emb.n_qubits}-qubit state")
    
    # Similarity
    sim = embeddings.similarity("quantum", "classical")
    print(f"Similarity between 'quantum' and 'classical': {abs(sim):.3f}")

def demo_attention():
    """Demonstrate quantum attention."""
    print("\n=== Quantum Attention Demo ===")
    attention = QuantumAttention(n_qubits_per_token=2)
    
    # Create some input states (simplified)
    input_states = [QuantumWordEmbeddings().get_embedding(w) for w in ["the", "quick", "brown", "fox"]]
    
    attended = attention.attention_layer(input_states)
    print(f"Applied attention to {len(input_states)} words, resulting in {attended.n_qubits}-qubit entangled state")

def demo_parsing():
    """Demonstrate quantum syntactic parsing."""
    print("\n=== Quantum Syntactic Parsing Demo ===")
    parser = QuantumSyntacticParser()
    
    sentence = "The cat sat on the mat."
    parse_result = parser.parse_sentence(sentence)
    print(f"Parsed '{sentence}' with quantum circuit")
    print(f"Parse distribution: {dict(list(parse_result.items())[:5])}...")

def demo_language_generation():
    """Demonstrate quantum language generation."""
    print("\n=== Quantum Language Generation Demo ===")
    model = QuantumLanguageModel()
    
    prompt = "The quantum"
    generated = model.generate_text(prompt, max_length=10)
    print(f"Generated text from prompt '{prompt}': '{generated}'")

if __name__ == "__main__":
    print("Novum-QVM QNLP Demo")
    print("=" * 50)
    
    demo_string_encoding()
    demo_word_embeddings()
    demo_attention()
    demo_parsing()
    demo_language_generation()
    
    print("\nDemo completed!")