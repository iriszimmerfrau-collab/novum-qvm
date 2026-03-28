import numpy as np
import random
import math
import time
import hashlib
from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from .QuantumComputer import PFQVS_QuantumComputer


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
    t = time.time()
    seed_str = f"{t}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
    return seed

def perlin(x, y, z, seed=None):
    if seed is None:
        seed = get_environmental_seed()
    return perlin_noise(x, y, z, seed)


def _apply_ry(qc: "PFQVS_QuantumComputer", theta: float, target: int):
    """Apply RY(theta) rotation to target qubit in-place using state vector pairs."""
    flat = qc._get_flat_state().copy()
    cos_t = math.cos(theta / 2.0)
    sin_t = math.sin(theta / 2.0)
    step = 1 << (qc.n_qubits - 1 - target)
    for i in range(qc.N):
        if ((i >> (qc.n_qubits - 1 - target)) & 1) == 0:
            j = i | step
            a, b = flat[i], flat[j]
            flat[i] = cos_t * a - sin_t * b
            flat[j] = sin_t * a + cos_t * b
    qc._set_flat_state(flat)


def _qnn_circuit(weights: np.ndarray, x: np.ndarray, n_qubits: int = 2, num_layers: int = 2) -> float:
    """Variational QNN circuit: angle embedding + entangling layers. Returns <Z0>."""
    from .QuantumComputer import PFQVS_QuantumComputer
    qc = PFQVS_QuantumComputer(n_qubits=n_qubits)
    psi = np.zeros(qc.N, dtype=complex)
    psi[0] = 1.0
    qc._set_flat_state(psi)

    # Angle embedding: RY(x[i]) on qubit i
    for i in range(min(n_qubits, len(x))):
        _apply_ry(qc, float(x[i]), i)

    # Variational layers: per-qubit RY rotations + CNOT chain entanglement
    w_idx = 0
    for _ in range(num_layers):
        for q in range(n_qubits):
            _apply_ry(qc, float(weights[w_idx]), q)
            w_idx += 1
        for q in range(n_qubits - 1):
            qc.apply_gate('CNOT', q, q + 1)

    # <Z0>: sum over basis states, +1 if qubit 0 is |0>, -1 if qubit 0 is |1>
    flat = qc._get_flat_state()
    probs = np.abs(flat) ** 2
    exp_z0 = float(np.sum(
        probs[idx] * (1.0 - 2.0 * ((idx >> (n_qubits - 1)) & 1))
        for idx in range(qc.N)
    ))
    return exp_z0


def train_qnn(features, labels, num_layers: int = 2, num_steps: int = 100, stepsize: float = 0.1) -> np.ndarray:
    """Train variational QNN via parameter shift rule gradient descent. Returns weights."""
    features = np.asarray(features, dtype=float)
    labels = np.asarray(labels, dtype=float)
    n_qubits = 2
    n_weights = n_qubits * num_layers
    weights = np.random.uniform(0.0, 2.0 * math.pi, size=n_weights)
    shift = math.pi / 2.0

    for _ in range(num_steps):
        grad = np.zeros_like(weights)
        for x, y in zip(features, labels):
            pred = _qnn_circuit(weights, x, n_qubits, num_layers)
            residual = pred - float(y)
            for i in range(n_weights):
                w_plus = weights.copy(); w_plus[i] += shift
                w_minus = weights.copy(); w_minus[i] -= shift
                grad[i] += residual * (
                    _qnn_circuit(w_plus, x, n_qubits, num_layers) -
                    _qnn_circuit(w_minus, x, n_qubits, num_layers)
                ) / 2.0
        weights -= stepsize * grad / max(1, len(features))

    return weights


def test_qnn(weights: np.ndarray, test_data) -> List[float]:
    """Evaluate trained QNN on test_data. Returns list of <Z0> predictions."""
    weights = np.asarray(weights, dtype=float)
    n_qubits = 2
    num_layers = len(weights) // n_qubits
    return [_qnn_circuit(weights, np.asarray(x, dtype=float), n_qubits, num_layers)
            for x in test_data]


def deutsch(f: Callable[[int], int]) -> str:
    """Determine if f: {0,1} -> {0,1} is constant or balanced via Deutsch-Jozsa."""
    from .QuantumComputer import PFQVS_QuantumComputer
    qc = PFQVS_QuantumComputer(n_qubits=1)
    counts = qc.deutsch_jozsa(f)
    return "Constant" if counts.get('0', 0) >= counts.get('1', 0) else "Balanced"


def custom_quantum_machine_learning(X_train, Y_train, X_test, Y_test, num_qubits, num_layers, num_steps):
    """Train and evaluate a QNN classifier with feature standardization."""
    X_train = np.asarray(X_train, dtype=float)
    X_test = np.asarray(X_test, dtype=float)
    Y_train = np.asarray(Y_train, dtype=float)

    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0)
    std[std == 0.0] = 1.0
    X_train = (X_train - mean) / std
    X_test = (X_test - mean) / std

    weights = train_qnn(X_train, Y_train, num_layers, num_steps)
    return test_qnn(weights, X_test)


def find_substring(string, substring):
    return substring in string


def grover_search(secret_bitstring: str, shots: int = 10000, qubits: int = 128) -> str:
    """Search for secret_bitstring using Grover's algorithm via PFQVS_QuantumComputer."""
    from .QuantumComputer import PFQVS_QuantumComputer
    qc = PFQVS_QuantumComputer(n_qubits=qubits)
    counts = qc.grovers_search(secret_bitstring, shots=shots)
    found = max(counts, key=counts.get)
    if found == secret_bitstring:
        return found
    return (
        'ERROR. Cannot Compute. Try Increasing The Qubits, And Shots. '
        'grover_search(secret_bitstring, shots, qubits) '
        'If the error persists, contact the dev.'
    )
