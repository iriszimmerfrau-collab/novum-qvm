#!/usr/bin/env python3
from novum_qvm import PFQVS_QuantumComputer
import numpy as np

print('=== Testing Deutsch-Jozsa Algorithm ===\n')

# Test 1: Constant function f(x) = 0
print('Test 1: Constant function f(x) = 0')
qc = PFQVS_QuantumComputer(2)
f_const = lambda x: 0
counts = qc.deutsch_jozsa(f_const, shots=1000)
z_prob = counts.get('00', 0)
print(f'  Probability of |00>: {z_prob}/1000 = {z_prob/1000:.2%}')
print(f'  Expected: >90% (constant function)')
if z_prob > 900:
    print('  ✓ PASSED')
else:
    print('  ✗ FAILED')

# Test 2: Constant function f(x) = 1
print('\nTest 2: Constant function f(x) = 1')
qc = PFQVS_QuantumComputer(2)
f_const = lambda x: 1
counts = qc.deutsch_jozsa(f_const, shots=1000)
z_prob = counts.get('00', 0)
print(f'  Probability of |00>: {z_prob}/1000 = {z_prob/1000:.2%}')
print(f'  Expected: >90% (constant function)')
if z_prob > 900:
    print('  ✓ PASSED')
else:
    print('  ✗ FAILED')

# Test 3: Balanced function f(x) = x[0] (first bit)
print('\nTest 3: Balanced function f(x) = x[0]')
qc = PFQVS_QuantumComputer(2)
# For 2 qubits: f(0)=0, f(1)=1, f(2)=0, f(3)=1 -> balanced
f_balanced = lambda x: (x >> 1) & 1
counts = qc.deutsch_jozsa(f_balanced, shots=1000)
z_prob = counts.get('00', 0)
print(f'  Probability of |00>: {z_prob}/1000 = {z_prob/1000:.2%}')
print(f'  Expected: <20% (balanced function)')
if z_prob < 200:
    print('  ✓ PASSED')
else:
    print('  ✗ FAILED')

# Test 4: Balanced function f(x) = parity
print('\nTest 4: Balanced function f(x) = x XOR (x>>1)')
qc = PFQVS_QuantumComputer(2)
# For 2 qubits: f(0)=0, f(1)=1, f(2)=1, f(3)=0 -> balanced
f_balanced = lambda x: (x ^ (x >> 1)) & 1
counts = qc.deutsch_jozsa(f_balanced, shots=1000)
z_prob = counts.get('00', 0)
print(f'  Probability of |00>: {z_prob}/1000 = {z_prob/1000:.2%}')
print(f'  Expected: <20% (balanced function)')
if z_prob < 200:
    print('  ✓ PASSED')
else:
    print('  ✗ FAILED')

print('\n=== Summary ===')
print('Deutsch-Jozsa algorithm should distinguish constant from balanced functions.')
print('Constant: |00⟩ probability >90%')
print('Balanced: |00⟩ probability <20%')
