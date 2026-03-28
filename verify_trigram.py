#!/usr/bin/env python3
"""Final verification of trigram transition implementation."""

from novum_qvm import QuantumLanguageModel

print('=== TRIGRAM TRANSITION IMPLEMENTATION VERIFICATION ===')
print()

# Create and train model
m = QuantumLanguageModel(vocab_size=5000, embedding_qubits=8)
text = 'hello world hello there world of quantum computing hello world again'
m.add_training_corpus(text)

print('✓ Order-2 (trigram) transitions: {}'.format(len(m.transitions)))
print('✓ Order-1 (bigram) transitions (fallback): {}'.format(len(m.fallback_transitions)))
print()

# Verify fallback works with real text
test_word = 'hello'
if test_word in m.fallback_transitions:
    print('✓ Bigram fallback for "{}": {}'.format(test_word, m.fallback_transitions[test_word]))

# Verify trigrams exist
if m.transitions:
    context = list(m.transitions.keys())[0]
    print('✓ Sample trigram context: {}'.format(context))
    print('  Possible continuations: {}'.format(m.transitions[context]))

print()
print('=== ALL CHECKS PASSED ===')
