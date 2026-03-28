#!/usr/bin/env python3
"""
Stress evaluation script for Novum-QVM QNLP and PFQVS components.

Tests robustness under extreme conditions:
- Large quantum states
- Long text inputs
- High-dimensional embeddings
- Complex attention mechanisms
- Performance benchmarks
- Memory usage analysis
"""

import sys
import os
import time
import tracemalloc
import numpy as np

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not available, memory monitoring disabled")

sys.path.insert(0, os.path.dirname(__file__))

from novum_qvm import (
    PFQVS_QuantumComputer,
    QuantumStringEncoder,
    QuantumWordEmbeddings,
    QuantumAttention,
    QuantumSyntacticParser,
    QuantumLanguageModel
)

def get_memory_usage():
    """Get current memory usage in MB."""
    if not HAS_PSUTIL:
        return 0.0
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def stress_test_pfqvs():
    """Stress test PFQVS with large qubit counts."""
    print("=== PFQVS Stress Test ===")

    max_qubits = 12  # Reduced for feasibility
    results = []

    for n_qubits in range(5, max_qubits + 1, 5):
        try:
            start_time = time.time()
            start_mem = get_memory_usage()

            qc = PFQVS_QuantumComputer(n_qubits)

            # Apply multiple gates
            for i in range(min(5, n_qubits)):  # Reduced number of gates
                qc.apply_gate('H', i % n_qubits)
                if i + 1 < n_qubits:
                    qc.apply_gate('CNOT', i, i + 1)

            # Measure
            counts = qc.measure(100)  # Reduced samples

            end_time = time.time()
            end_mem = get_memory_usage()

            results.append({
                'qubits': n_qubits,
                'time': end_time - start_time,
                'memory': end_mem - start_mem,
                'state_norm': abs(np.linalg.norm(qc.state) - 1.0)
            })

            print(f"✓ {n_qubits} qubits: {end_time - start_time:.2f}s, {end_mem - start_mem:.1f}MB")

        except Exception as e:
            print(f"✗ {n_qubits} qubits failed: {e}")
            break

    return results

def stress_test_string_encoding():
    """Stress test quantum string encoding with long texts."""
    print("\n=== String Encoding Stress Test ===")

    encoder = QuantumStringEncoder(max_length=10000)

    test_texts = [
        "Short text",
        "A" * 100,
        "A" * 1000,
        "A" * 5000,
        "Mixed text with various characters: !@#$%^&*()_+-=[]{}|;:,.<>?",
        "Unicode: 你好世界 🌍🚀",
    ]

    results = []
    for text in test_texts:
        try:
            start_time = time.time()
            qc = encoder.encode_string(text)
            end_time = time.time()

            results.append({
                'length': len(text),
                'qubits': qc.n_qubits,
                'time': end_time - start_time
            })

            print(f"✓ Encoded {len(text)} chars in {end_time - start_time:.3f}s ({qc.n_qubits} qubits)")

        except Exception as e:
            print(f"✗ Failed encoding {len(text)} chars: {e}")

    return results

def stress_test_embeddings():
    """Stress test word embeddings with many words."""
    print("\n=== Word Embeddings Stress Test ===")

    embeddings = QuantumWordEmbeddings(embedding_dim=20)

    # Generate many words
    words = [f"word_{i}" for i in range(50)]  # Reduced

    results = []
    start_time = time.time()
    for word in words:
        emb = embeddings.get_embedding(word)

    end_time = time.time()

    # Test similarities
    sim_start = time.time()
    similarities = []
    for i in range(5):  # Reduced
        for j in range(i+1, 10):
            sim = embeddings.similarity(words[i], words[j])
            similarities.append(sim)

    sim_end = time.time()

    results.append({
        'words_processed': len(words),
        'embedding_time': end_time - start_time,
        'similarity_time': sim_end - sim_start,
        'avg_similarity': sum(similarities) / len(similarities)
    })

    print(f"✓ Processed {len(words)} words in {end_time - start_time:.2f}s")
    print(f"✓ Computed {len(similarities)} similarities in {sim_end - sim_start:.2f}s")

    return results

def stress_test_attention():
    """Stress test attention with long sequences."""
    print("\n=== Attention Stress Test ===")

    attention = QuantumAttention(n_qubits=5)

    sequence_lengths = [5, 10, 15]  # Reduced

    results = []
    for length in sequence_lengths:
        try:
            start_time = time.time()

            # Create sequence of embeddings
            embeddings = QuantumWordEmbeddings(embedding_dim=5)
            input_states = [embeddings.get_embedding(f"token_{i}") for i in range(length)]

            attended = attention.attention_layer(input_states)

            end_time = time.time()

            results.append({
                'sequence_length': length,
                'time': end_time - start_time,
                'output_qubits': attended.n_qubits
            })

            print(f"✓ Attention on {length} tokens: {end_time - start_time:.2f}s")

        except Exception as e:
            print(f"✗ Failed attention on {length} tokens: {e}")
            break

    return results

def stress_test_parsing():
    """Stress test syntactic parsing with complex sentences."""
    print("\n=== Parsing Stress Test ===")

    parser = QuantumSyntacticParser(n_qubits=15)

    test_sentences = [
        "The cat sat on the mat.",
        "The quick brown fox jumps over the lazy dog.",
        "In quantum computing, superposition allows particles to exist in multiple states simultaneously.",
        "Natural language processing with quantum algorithms provides new insights into semantic understanding.",
        "A" * 200,  # Very long sentence
    ]

    results = []
    for sentence in test_sentences:
        try:
            start_time = time.time()
            result = parser.parse_sentence(sentence)
            end_time = time.time()

            results.append({
                'sentence_length': len(sentence),
                'time': end_time - start_time,
                'unique_outcomes': len(result)
            })

            print(f"✓ Parsed {len(sentence)} chars in {end_time - start_time:.2f}s")

        except Exception as e:
            print(f"✗ Failed parsing {len(sentence)} chars: {e}")

    return results

def stress_test_generation():
    """Stress test language generation."""
    print("\n=== Generation Stress Test ===")

    model = QuantumLanguageModel()

    prompts = [
        "The",
        "Quantum computing",
        "In the future",
    ]

    lengths = [10, 50, 100]

    results = []
    for prompt in prompts:
        for max_len in lengths:
            try:
                start_time = time.time()
                generated = model.generate_text(prompt, max_length=max_len)
                end_time = time.time()

                results.append({
                    'prompt': prompt,
                    'max_length': max_len,
                    'actual_length': len(generated),
                    'time': end_time - start_time
                })

                print(f"✓ Generated {len(generated)} chars from '{prompt}' in {end_time - start_time:.2f}s")

            except Exception as e:
                print(f"✗ Failed generation from '{prompt}': {e}")

    return results

def main():
    """Run all stress tests."""
    print("Novum-QVM Stress Evaluation")
    print("=" * 50)

    tracemalloc.start()

    all_results = {}

    try:
        all_results['pfqvs'] = stress_test_pfqvs()
        all_results['string_encoding'] = stress_test_string_encoding()
        all_results['embeddings'] = stress_test_embeddings()
        all_results['attention'] = stress_test_attention()
        all_results['parsing'] = stress_test_parsing()
        all_results['generation'] = stress_test_generation()

    except KeyboardInterrupt:
        print("\nStress test interrupted by user")

    except Exception as e:
        print(f"\nUnexpected error during stress testing: {e}")

    finally:
        current, peak = tracemalloc.get_traced_memory()
        print("\nMemory Usage:")
        print(f"Current: {current / 1024 / 1024:.1f} MB")
        print(f"Peak: {peak / 1024 / 1024:.1f} MB")

        tracemalloc.stop()

    print("\nStress evaluation complete!")
    return all_results

if __name__ == "__main__":
    results = main()