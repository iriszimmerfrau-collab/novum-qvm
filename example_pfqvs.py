#!/usr/bin/env python3
"""
Example usage of Perlin-Fourier Quantum Virtual Simulation (PFQVS)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from novum_qvm.QuantumComputer import PFQVS_QuantumComputer

def main():
    print("Novum-QVM: Perlin-Fourier Quantum Virtual Simulation Demo")
    print("=" * 60)
    
    # Create a 2-qubit PFQVS simulator
    qc = PFQVS_QuantumComputer(2)
    print(f"Initialized 2-qubit system with Perlin-seeded state")
    print(f"Initial state norm: {np.linalg.norm(qc.state):.6f}")
    
    # Apply gates: H on qubit 0, CNOT from 0 to 1
    gates = [('H', 0), ('CNOT', 0, 1)]
    qc.execute_circuit(gates)
    print("Applied circuit: H(0), CNOT(0,1)")
    print(f"Final state norm: {np.linalg.norm(qc.state):.6f}")
    
    # Measure
    counts = qc.measure(10000)
    print(f"Measurement counts (10,000 shots): {counts}")
    
    # Expected for Bell state: ~50% 00 and 11
    total = sum(counts.values())
    prob_00 = counts.get('00', 0) / total
    prob_11 = counts.get('11', 0) / total
    print(".4f")
    print(".4f")
    
    # Decoherence spectrum
    spectrum = qc.get_decoherence_spectrum()
    print(f"Decoherence power spectrum (first 4 components): {np.abs(spectrum[:4])}")
    
    # Test Grover's search
    print("\nTesting Grover's Search for |11⟩:")
    qc2 = PFQVS_QuantumComputer(2)
    grover_counts = qc2.grovers_search('11')
    print(f"Grover's result: {grover_counts}")
    
    # Test QASM
    print("\nTesting QASM parsing:")
    qc3 = PFQVS_QuantumComputer(2)
    qasm = "h q[0]; cx q[0], q[1];"
    qasm_counts = qc3.parse_qasm(qasm)
    print(f"QASM result: {qasm_counts}")

if __name__ == "__main__":
    main()