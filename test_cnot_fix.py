#!/usr/bin/env python3
from novum_qvm import PFQVS_QuantumComputer
import numpy as np

print('Test 1: Basic initialization')
qc = PFQVS_QuantumComputer(2)
print(f'  State norm: {np.linalg.norm(qc.state):.6f}')

print('\nTest 2: Single qubit gate (H)')
qc.apply_gate('H', 0)
print(f'  State norm after H: {np.linalg.norm(qc.state):.6f}')

print('\nTest 3: Bell state (H + CNOT)')
qc2 = PFQVS_QuantumComputer(2)
qc2.apply_gate('H', 0)
qc2.apply_gate('CNOT', 0, 1)
counts = qc2.measure(1000)
bell_prob = counts.get('00', 0) + counts.get('11', 0)
print(f'  Bell state probability: {bell_prob}/1000')
print(f'  00: {counts.get("00", 0)}, 11: {counts.get("11", 0)}, 01: {counts.get("01", 0)}, 10: {counts.get("10", 0)}')

if bell_prob > 800:
    print('\n✓ Bell state test PASSED!')
    exit(0)
else:
    print(f'\n✗ Bell state test FAILED - probability too low: {bell_prob}/1000')
    exit(1)
