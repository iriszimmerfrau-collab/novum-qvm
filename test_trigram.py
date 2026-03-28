#!/usr/bin/env python3
"""Test trigram transitions."""

from novum_qvm import QuantumLanguageModel

# Create model
m = QuantumLanguageModel(vocab_size=5000, embedding_qubits=8)

# Train on sample text
sample = 'the cat sat on the mat the dog ran in the park the cat jumped over the fence'
m.add_training_corpus(sample)

print('✓ Model trained on sample text')
print(f'✓ Unique bigrams: {len(m.fallback_transitions)}')
print(f'✓ Unique trigrams: {len(m.transitions)}')
print()
print('Sample trigram transitions:')
for (w1, w2), nexts in list(m.transitions.items())[:5]:
    print(f'  ("{w1}", "{w2}") -> {dict(nexts)}')
print()
print('Sample bigram transitions (fallback):')
for w, nexts in list(m.fallback_transitions.items())[:5]:
    print(f'  "{w}" -> {dict(nexts)}')
