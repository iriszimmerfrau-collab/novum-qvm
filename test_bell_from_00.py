#!/usr/bin/env python3
from novum_qvm import PFQVS_QuantumComputer
import numpy as np

print('=== Bell State Test (from |00> basis state) ===\n')

qc = PFQVS_QuantumComputer(2)

# Override state with |00> basis state
state_00 = np.zeros(4, dtype=complex)
state_00[0] = 1.0  # |00>
qc.state = np.matrix(state_00).T

print('Initial state (|00>):')
state = np.array(qc.state).flatten()
for i in range(4):
    print(f'  |{format(i, "02b")}>: {abs(state[i]):.4f}')

# Apply H to qubit 0
qc.apply_gate('H', 0)
print('\nAfter H on qubit 0 (should be (|00>+|10>)/√2):')
state = np.array(qc.state).flatten()
for i in range(4):
    print(f'  |{format(i, "02b")}>: {abs(state[i]):.4f}')

# Apply CNOT(0, 1)
qc.apply_gate('CNOT', 0, 1)
print('\nAfter CNOT(0,1) (should be Bell state (|00>+|11>)/√2):')
state = np.array(qc.state).flatten()
for i in range(4):
    print(f'  |{format(i, "02b")}>: {abs(state[i]):.4f}')

print('\nExpected Bell state:')
print('  |00>: 0.7071')
print('  |11>: 0.7071')

# Check numerically
expected = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)
fidelity = np.abs(np.vdot(state, expected))**2
print(f'\nFidelity with expected Bell state: {fidelity:.4f}')

if fidelity > 0.99:
    print('✓ Bell state test PASSED!')
else:
    print(f'✗ Bell state test FAILED - fidelity too low: {fidelity:.4f}')
