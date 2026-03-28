import numpy as np
import random
import math
import time
import hashlib
import pennylane as qml
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, assemble, execute
from sklearn.preprocessing import StandardScaler

# Perlin noise implementation
def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(a, b, t):
    return a + t * (b - a)

def grad(hash, x, y, z):
    h = hash & 15
    u = x if h < 8 else y
    v = y if h < 4 else (x if h == 12 or h == 14 else z)
    return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

def perlin_noise(x, y, z, seed=0):
    # Permutation table
    p = [i for i in range(256)]
    random.seed(seed)
    random.shuffle(p)
    p += p

    X = int(x) & 255
    Y = int(y) & 255
    Z = int(z) & 255

    x -= int(x)
    y -= int(y)
    z -= int(z)

    u = fade(x)
    v = fade(y)
    w = fade(z)

    A = p[X] + Y
    AA = p[A] + Z
    AB = p[A + 1] + Z
    B = p[X + 1] + Y
    BA = p[B] + Z
    BB = p[B + 1] + Z

    return lerp(w, lerp(v, lerp(u, grad(p[AA], x, y, z),
                                   grad(p[BA], x - 1, y, z)),
                          lerp(u, grad(p[AB], x, y - 1, z),
                               grad(p[BB], x - 1, y - 1, z))),
                lerp(v, lerp(u, grad(p[AA + 1], x, y, z - 1),
                             grad(p[BA + 1], x - 1, y, z - 1)),
                     lerp(u, grad(p[AB + 1], x, y - 1, z - 1),
                          grad(p[BB + 1], x - 1, y - 1, z - 1))))

def get_environmental_seed():
    # Use time, and perhaps some 'environmental' factors
    # For simplicity, use current time and some hash
    t = time.time()
    seed_str = f"{t}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
    return seed

def perlin(x, y, z, seed=None):
    if seed is None:
        seed = get_environmental_seed()
    return perlin_noise(x, y, z, seed)

def train_qnn(features, labels, num_layers=2, num_steps=100, stepsize=0.1):
    # Define a quantum circuit
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit(weights, x):
        qml.templates.AngleEmbedding(x, wires=[0, 1])
        qml.templates.BasicEntanglerLayers(weights, wires=[0, 1])
        return qml.expval(qml.PauliZ(0))

    # Define the quantum neural network (QNN) model
    def qnn_classifier(weights, x):
        return circuit(weights, x)

    # Define the cost function
    def cost_fn(weights, features, labels):
        predictions = [qnn_classifier(weights, x) for x in features]
        return np.mean((predictions - labels) ** 2)

    # Initialize the QNN weights
    num_weights = 2 * num_layers
    weights = np.random.random(size=(num_steps, num_weights))

    # Train the QNN       
    opt = qml.GradientDescentOptimizer(stepsize=stepsize)

    for i in range(num_steps):
        weights[i] = opt.step(lambda w: cost_fn(w, features, labels), weights[i])

    return weights[-1]

def test_qnn(weights, test_data):
    # Define a quantum circuit
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit(weights, x):
        qml.templates.AngleEmbedding(x, wires=[0, 1])
        qml.templates.BasicEntanglerLayers(weights, wires=[0, 1])
        return qml.expval(qml.PauliZ(0))

    # Define the quantum neural network (QNN) model
    def qnn_classifier(weights, x):
        return circuit(weights, x)

    # Test the QNN
    predictions = [qnn_classifier(weights, x) for x in test_data]
    return predictions

def deutsch(f):
    # Initialize the quantum computer with 1 qubit
    qc = QuantumCircuit(1, 1)

    # Apply the oracle gate
    if f(0):
        qc.x(0)

    # Apply Hadamard gate
    qc.h(0)

    # Measure qubit and print result
    qc.measure(0, 0)

    # Simulate the circuit using the Aer simulator
    simulator = Aer.get_backend('qasm_simulator')
    job = simulator.run(assemble(qc, shots=1))

    # Get the result of the simulation
    result = job.result()
    counts = result.get_counts()

    # Determine whether f is constant or balanced
    if '0' in counts:
        return "Constant"
    else:
        return "Balanced"

def custom_quantum_machine_learning(X_train, Y_train, X_test, Y_test, num_qubits, num_layers, num_steps):
    # Standardize the features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Train the quantum model
    params = train(X_train, Y_train, num_qubits, num_layers, num_steps)

    # Test the quantum model
    accuracy = test(X_test, Y_test, params, num_qubits)
    return accuracy
def find_substring(string, substring):
    if substring in string:
        return True
    else:
        return False
def grover_search(secret_bitstring, shots=10000, qubits=128):
  qr = QuantumRegister(qubits, name='q')
  cr = ClassicalRegister(qubits, name='c')
  circuit = QuantumCircuit(qr, cr)

  # Apply Hadamard gate on all qubits
  circuit.h(qr)
  print("Step 1: Apply Hadamard gates to all qubits")

  # Build the black-box oracle
  for idx, bit in enumerate(reversed(secret_bitstring)):
    if bit == '1':
      circuit.z(qr[idx])
  print("Step 2: Apply the black-box oracle")

  # Apply Hadamard gate on all qubits again
  circuit.h(qr)
  print("Step 3: Apply Hadamard gates to all qubits")

  # Measure all qubits
  circuit.measure(qr, cr)
  print("Step 4: Measurement")

  # Run the circuit on a simulator and increase the number of shots
  simulator = Aer.get_backend('qasm_simulator')
  result = execute(circuit, backend=simulator, shots=shots).result()
  counts = result.get_counts(circuit)
  print(str(counts))
  # Find the most frequent bitstring
  max_count = 0
  found_bitstring = ''
  for bitstring, count in counts.items():
    if count > max_count:
      max_count = count
      found_bitstring = bitstring
  if found_bitstring == secret_bitstring:
    found_bitstring = secret_bitstring
    return found_bitstring
  else:
    return 'ERROR. Cannot Compute. Try Increasing The Qubits, And Shots. grover_search(secret_bitstring, shots, qubits) If the error persists, contact the dev.'
