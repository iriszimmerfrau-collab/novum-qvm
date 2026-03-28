#!/usr/bin/env python3
from novum_qvm import PFQVS_QuantumComputer
import numpy as np

print('=== Debugging Bell State ===\n')

# Create 2-qubit system
qc = PFQVS_QuantumComputer(2)
print('Initial state:')
state = np.array(qc.state).flatten()
print(f'  |00>: {abs(state[0]):.4f}')
print(f'  |01>: {abs(state[1]):.4f}')
print(f'  |10>: {abs(state[2]):.4f}')
print(f'  |11>: {abs(state[3]):.4f}')
print(f'  Norm: {np.linalg.norm(state):.6f}')

# Apply H to qubit 0
print('\nAfter H on qubit 0:')
qc.apply_gate('H', 0)
state = np.array(qc.state).flatten()
print(f'  |00>: {abs(state[0]):.4f}')
print(f'  |01>: {abs(state[1]):.4f}')
print(f'  |10>: {abs(state[2]):.4f}')
print(f'  |11>: {abs(state[3]):.4f}')
print(f'  Norm: {np.linalg.norm(state):.6f}')

# Apply CNOT(0, 1)
print('\nAfter CNOT(0, 1):')
qc.apply_gate('CNOT', 0, 1)
state = np.array(qc.state).flatten()
print(f'  |00>: {abs(state[0]):.4f}')
print(f'  |01>: {abs(state[1]):.4f}')
print(f'  |10>: {abs(state[2]):.4f}')
print(f'  |11>: {abs(state[3]):.4f}')
print(f'  Norm: {np.linalg.norm(state):.6f}')

print('\nExpected Bell state (|00> + |11>)/sqrt(2):')
print(f'  |00>: 0.7071')
print(f'  |11>: 0.7071')
