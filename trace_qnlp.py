#!/usr/bin/env python3
from novum_qvm import QuantumStringEncoder, QuantumWordEmbeddings
import time

print("Step 1: Import QuantumStringEncoder...")
t0 = time.time()
print("  Done in {:.3f}s".format(time.time() - t0))

print("\nStep 2: Create encoder...")
t0 = time.time()
encoder = QuantumStringEncoder()
print("  Done in {:.3f}s".format(time.time() - t0))

print("\nStep 3: Encode string...")
t0 = time.time()
qc = encoder.encode_string("test")
print("  Done in {:.3f}s".format(time.time() - t0))

print(f"\nStep 4: Create QuantumWordEmbeddings...")
t0 = time.time()
embeddings = QuantumWordEmbeddings(embedding_qubits=3)
print("  Done in {:.3f}s".format(time.time() - t0))

print(f"\nStep 5: Get embedding...")
t0 = time.time()
emb = embeddings.get_embedding("test")
print("  Done in {:.3f}s".format(time.time() - t0))

print("\n✓ All QNLP steps completed")
