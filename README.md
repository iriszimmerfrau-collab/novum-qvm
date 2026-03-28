# Novum-QVM

[![PyPI version](https://badge.fury.io/py/novum-qvm.svg)](https://badge.fury.io/py/novum-qvm)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Tests](https://github.com/iriszimmerfrau-collab/novum-qvm/actions/workflows/publish.yml/badge.svg)](https://github.com/iriszimmerfrau-collab/novum-qvm/actions/workflows/publish.yml)

**Novum-QVM** is a pure-Python quantum circuit simulator built on **Perlin-Fourier Quantum Virtual Simulation (PFQVS)** — a simulation architecture that uses Perlin noise for structured state initialization, O(N) Fourier-domain gate execution, spectral decoherence modeling, and importance-sampled measurement. It requires only NumPy and ships with Grover's search, Deutsch-Jozsa, a QASM parser, a variational QNN trainer, and a full QNLP stack.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [PFQVS Architecture](#pfqvs-architecture)
  - [Layer 1 — Perlin State Initialization](#layer-1--perlin-state-initialization)
  - [Layer 2 — O(N) Fourier-Domain Gate Execution](#layer-2--on-fourier-domain-gate-execution)
  - [Layer 3 — Spectral Decoherence Modeling](#layer-3--spectral-decoherence-modeling)
  - [Layer 4 — Importance-Sampled Measurement](#layer-4--importance-sampled-measurement)
- [Algorithms](#algorithms)
  - [Grover's Search](#grovers-search)
  - [Deutsch-Jozsa](#deutsch-jozsa)
  - [Variational QNN](#variational-qnn)
- [QNLP](#qnlp)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

```bash
pip install novum-qvm
```

**From source:**

```bash
git clone https://github.com/iriszimmerfrau-collab/novum-qvm.git
cd novum-qvm
pip install -e .[dev]
pytest tests/
```

**Only dependency:** `numpy >= 1.22.0`

---

## Quick Start

```python
from novum_qvm import PFQVS_QuantumComputer

# 2-qubit simulator — starts from Perlin-noise state, not |00⟩
# Reset to |00⟩ explicitly before circuits that depend on a clean start
import numpy as np
qc = PFQVS_QuantumComputer(n_qubits=2)
qc._set_flat_state(np.array([1, 0, 0, 0], dtype=complex))

# Apply gates
qc.apply_gate('H', 0)        # Hadamard on qubit 0
qc.apply_gate('CNOT', 0, 1)  # CNOT, control=0, target=1

# Measure (importance-sampled)
counts = qc.measure(shots=1000)
# Bell state: '00' and '11' dominate; exact split varies due to importance sampling
print(counts)

# Grover's search over 3 qubits
qc3 = PFQVS_QuantumComputer(n_qubits=3)
result = qc3.grovers_search('101', shots=2000)
print(result)  # '101' dominates

# Deutsch-Jozsa
qc1 = PFQVS_QuantumComputer(n_qubits=2)
counts = qc1.deutsch_jozsa(lambda x: 0)   # constant → measures '00'
counts = qc1.deutsch_jozsa(lambda x: x&1) # balanced → '00' suppressed

# QASM
qc.parse_qasm("h q[0]; cx q[0], q[1];", shots=500)
```

---

## PFQVS Architecture

Classical quantum simulators store an n-qubit state as a vector of 2ⁿ complex amplitudes and apply gates as dense matrix multiplications — O(N²) per gate, N = 2ⁿ. PFQVS reorganizes this across four layers to reduce cost, add structured noise, and improve sampling efficiency.

---

### Layer 1 — Perlin State Initialization

Standard simulators start from |0…0⟩. PFQVS instead seeds the state with **3D Perlin noise**, giving smooth, correlated amplitudes that better represent a real qubit's thermal or environmental starting state.

**Perlin noise construction:**

For each basis index *i* ∈ {0, …, N−1}, fractional coordinates are computed as:

```
x = i / N,   seed offset z = seed × 0.001
```

The amplitude is:

```
ψᵢ = P(x, 0.1, z) + i·P((x + 0.5) mod 1, 0.2, z)
```

where *P(x, y, z)* is 3D Perlin noise built from a seeded permutation table, trilinear interpolation, and quintic smoothstep blending *f(t) = 6t⁵ − 15t⁴ + 10t³*. The state is normalized:

```
ψ ← ψ / ‖ψ‖₂
```

**Why Perlin over random?** Perlin noise has a 1/f^α power spectrum — the same spectral shape found in charge noise and flux noise in real superconducting qubits. Starting from a Perlin state rather than |0⟩ gives the simulator a physically plausible initial condition and makes subsequent decoherence modeling consistent with the initialization basis.

---

### Layer 2 — O(N) Fourier-Domain Gate Execution

**Single-qubit gates** (H, X, Y, Z) are applied in O(N) time without forming the full 2ⁿ × 2ⁿ Kronecker product. For a target qubit *t*, any basis index *i* can be paired with the index *j = i XOR (1 << (n−1−t))* that differs only in bit *t*. The 2×2 gate matrix is applied to each such pair:

```
For all i where bit t of i is 0:
    j = i | (1 << (n−1−t))
    [ψᵢ', ψⱼ']ᵀ = M · [ψᵢ, ψⱼ]ᵀ
```

This processes each pair exactly once, giving O(N/2) = O(N) operations versus the naive O(N²) full matrix-vector product.

**Gate matrices:**

```
H = (1/√2) [[1,  1],    X = [[0, 1],    Y = [[0, -i],    Z = [[1,  0],
             [1, -1]]        [1, 0]]         [i,  0]]         [0, -1]]
```

**CNOT** is applied as a computational-basis permutation. For each basis index *i*, if the control bit is 1 the target bit is flipped:

```
CNOT|ctrl, tgt⟩ = |ctrl, tgt ⊕ ctrl⟩
```

implemented as a scatter: `new_state[permute(i)] = state[i]` for all i.

---

### Layer 3 — Spectral Decoherence Modeling

Physical qubits lose coherence due to overlapping noise sources at different frequencies. PFQVS models this with **octave-weighted Perlin noise** — each octave maps to a distinct physical channel:

| Octave | Frequency Scale | Physical Analog |
|--------|----------------|-----------------|
| 1 | Low | 1/f charge noise |
| 2–3 | Mid | Thermal fluctuations |
| 4–6 | High | EMI / control crosstalk |

For each amplitude ψᵢ, a damping coefficient is computed:

```
env(i) = Σ_{o=1}^{O}  (1/2ᵒ) · P(x·2ᵒ, 0.1·o, seed·0.001 + t·0.01)

damping(i) = exp(−|env(i)| · dt)

ψᵢ ← ψᵢ · damping(i)
```

The `self.t` counter tracks circuit depth so the noise pattern evolves coherently as the circuit deepens. Call `apply_decoherence(dt, octaves)` manually after gate sequences where noise matters.

---

### Layer 4 — Importance-Sampled Measurement

Naive sampling draws from the raw probability distribution **p** directly. For peaked distributions (e.g. after Grover's), this is fine, but for flat distributions it wastes shots on low-probability outcomes.

PFQVS blends **p** with a spectral importance mask **m** derived from the leading Fourier components of **p**:

```
spectrum = FFT(p)
keep top k = max(1, ⌊|spectrum| · f⌋) components by magnitude
m = IFFT(filtered_spectrum),  m ← max(m − min(m), 0),  m ← m / ‖m‖₁

Q = p + α·m,   Q ← Q / ‖Q‖₁

samples ~ Multinomial(shots, Q)
```

Default parameters: α = 0.5, spectral_fraction = 0.1. The blending ensures that low-probability, high-spectral-weight basis states still receive some sample coverage — useful for variational algorithms (VQE, QAOA) where gradient estimation requires broad support.

---

## Algorithms

### Grover's Search

Grover's algorithm finds a marked element in an unsorted database of N items in O(√N) oracle calls versus O(N) classically.

**Circuit:**

1. Initialize uniform superposition: `ψ = (1/√N) Σ|x⟩`
2. Repeat *k* times:
   - **Oracle** — flip phase of target: `ψ[target] *= −1`
   - **Diffusion** — reflect about mean: `ψ ← 2⟨ψ⟩·**1** − ψ`
3. Measure

**Optimal iteration count** — the amplitude of the target state after *k* iterations is `sin((2k+1)θ)` where `sin²θ = 1/N`. Maximum probability occurs at:

```
k* = round(π/4 · √N)
```

For N=4: sinθ = 1/2, θ = π/6. k=1 gives P = sin²(3·π/6) = sin²(π/2) = **1.0** — one iteration finds the target with certainty. The formula `round(π/4·√4)` = `round(1.57)` = 2 in Python, so the implementation uses k=2 for N=4, which gives P = sin²(5π/6) = 0.25 — a known limitation of using `round` versus `floor` for small N.

For N=8: k*=2, P(target) ≈ 0.945. For N≥16 the rounding error is negligible.

```python
qc = PFQVS_QuantumComputer(n_qubits=4)  # N=16
counts = qc.grovers_search('1010', shots=2000)
```

---

### Deutsch-Jozsa

Given a function f: {0,1}ⁿ → {0,1} promised to be either **constant** (same output for all inputs) or **balanced** (0 for exactly half, 1 for the other half), Deutsch-Jozsa determines which in a single query.

**Circuit:**

1. Start: `ψ = |+…+⟩ = (1/√N) Σ|x⟩`
2. Oracle: `ψ[x] *= (−1)^f(x)` for all x
3. Final Hadamard layer — implemented as FFT:
   ```
   ψ' = FFT(ψ) / √N
   ```
4. Measure

**Why the FFT identifies constant vs. balanced in this setting:**

The n-qubit Hadamard transform H⊗ⁿ has matrix elements `H[y,x] = (1/√N)(−1)^{⟨x,y⟩}` where ⟨x,y⟩ = x·y mod 2 (bitwise dot product). The DFT matrix has elements `W[y,x] = (1/√N) exp(−2πixy/N)`. These are not the same transform — H⊗ⁿ uses real ±1 entries while DFT uses complex roots of unity, and they agree only for n=1.

However, for the specific ±1 phase vectors produced by a Deutsch-Jozsa oracle, the DFT produces the correct classification: a constant oracle gives a flat ±1 vector whose FFT concentrates at index 0, and a balanced oracle (equal numbers of +1 and −1) gives a vector with zero DC component, suppressing index 0. This is not a general equivalence between FFT and H⊗ⁿ — it exploits the particular structure of Deutsch-Jozsa oracle outputs. For arbitrary quantum circuits, H⊗ⁿ must be applied explicitly.

**Result:** constant → measures `|0…0⟩` with high probability; balanced → `|0…0⟩` amplitude is zero.

```python
qc = PFQVS_QuantumComputer(n_qubits=3)

# Constant
qc.deutsch_jozsa(lambda x: 1)   # '000' dominates

# Balanced
qc.deutsch_jozsa(lambda x: x % 2)  # '000' suppressed
```

Or use the convenience wrapper in `novum_qvm.functions`:

```python
from novum_qvm.functions import deutsch
print(deutsch(lambda x: 0))      # 'Constant'
print(deutsch(lambda x: x & 1))  # 'Balanced'
```

---

### Variational QNN

A 2-qubit variational quantum circuit trained with the **parameter shift rule** — an exact gradient method for quantum circuits.

**Circuit structure:**

```
Angle embedding:   RY(xᵢ) on qubit i         ← encodes input features
Variational layer: RY(θᵢ) on each qubit  }
                   CNOT(i, i+1) chain     }  × num_layers
```

**RY rotation gate:**

```
RY(θ) = [[cos(θ/2), −sin(θ/2)],
          [sin(θ/2),  cos(θ/2)]]
```

Applied in O(N) using the same paired-basis-state approach as single-qubit gates.

**Loss function:** MSE between predicted ⟨Z₀⟩ expectation value and target label.

**Parameter shift rule** — exact analytic gradient for a quantum circuit parameter θᵢ:

```
∂L/∂θᵢ = (L(θᵢ + π/2) − L(θᵢ − π/2)) / 2
```

No finite differences, no backpropagation through a classical approximation — this is the exact gradient from two circuit evaluations.

```python
from novum_qvm.functions import train_qnn, test_qnn
import numpy as np

X_train = np.random.uniform(0, np.pi, (20, 2))
Y_train = np.sign(np.sin(X_train[:, 0] - X_train[:, 1]))

weights = train_qnn(X_train, Y_train, num_layers=2, num_steps=80, stepsize=0.1)

X_test = np.random.uniform(0, np.pi, (5, 2))
predictions = test_qnn(weights, X_test)  # list of <Z0> values in [-1, 1]
```

---

## QNLP

The `novum_qvm.qnlp` module implements a quantum natural language processing stack on top of PFQVS.

### String Encoding

Text is encoded into a quantum state via position+character amplitude encoding. For position *p* and character code *c*, the basis index is `(p << 8) | c`. Each character contributes one amplitude unit; the state is normalized across all characters.

```python
from novum_qvm import QuantumStringEncoder

encoder = QuantumStringEncoder(max_length=64)
qc = encoder.encode_string("hello world")
text = encoder.decode_string(qc, shots=2000)
```

### Word Embeddings

Each word maps to a `PFQVS_QuantumComputer` whose Perlin seed is derived from `abs(hash(word)) % 2³¹`. Because the Perlin initialization is seeded, the same word always produces the same state (self-similarity = 1.0), and structurally different seeds produce structurally different Perlin states — so fidelity between distinct words is generally small but nonzero, not trivially high for all pairs. Similarity is quantum fidelity:

```
sim(w₁, w₂) = |⟨ψ₁|ψ₂⟩|²  ∈ [0, 1]
```

This gives a deterministic, hash-driven metric on the word embedding space. It is not learned from a corpus — it is a fixed structural property of the Perlin initialization function applied to word hashes.

```python
from novum_qvm import QuantumWordEmbeddings

emb = QuantumWordEmbeddings(embedding_qubits=10)
print(emb.similarity("quantum", "physics"))   # float in [0,1]
print(emb.similarity("quantum", "quantum"))   # 1.0
```

### Language Model

Trigram (order-2) transition model with bigram fallback. Prediction is driven by the classical n-gram table trained on the corpus; PFQVS contributes a vocabulary-indexed sampling distribution from the word embedding of the last token, which is blended with the transition candidates to introduce structured stochasticity. The language model structure is classical — the quantum component acts as a seeded, embedding-aware random sampler over the candidate set, not as a generative model in its own right.

```python
from novum_qvm import QuantumLanguageModel, QuantumToolkit

model = QuantumLanguageModel(vocab_size=2000, embedding_qubits=10)
model.add_training_corpus(open("corpus.txt").read())

print(model.generate_text("the quick", max_length=20))

# Persist
toolkit = QuantumToolkit()
toolkit.models["my_model"] = model
toolkit.save_model("my_model", "saved/my_model")
model2 = toolkit.load_model("my_model", "saved/my_model")
```

---

## API Reference

### `PFQVS_QuantumComputer`

```python
PFQVS_QuantumComputer(n_qubits: int = 1, seed: int | None = None)
```

| Method | Signature | Description |
|--------|-----------|-------------|
| `apply_gate` | `(gate, *args)` | Apply gate. Gates: `'H'`, `'X'`, `'Y'`, `'Z'`, `'CNOT'`/`'CX'` |
| `measure` | `(shots=1000) → Dict[str,int]` | Importance-sampled measurement counts |
| `measure_importance_sampling` | `(shots, alpha, spectral_fraction) → (counts, diagnostics)` | Full result with diagnostics dict |
| `grovers_search` | `(target: str, shots=1000) → Dict[str,int]` | Grover's algorithm; target is a bitstring e.g. `'101'` |
| `deutsch_jozsa` | `(f: Callable[[int],int], shots=1000) → Dict[str,int]` | Deutsch-Jozsa; `f` maps int → 0 or 1 |
| `apply_decoherence` | `(dt=0.01, octaves=3)` | Apply spectral decoherence in-place |
| `parse_qasm` | `(qasm: str, shots=1000) → Dict[str,int]` | Execute QASM string and measure |
| `_get_flat_state` | `() → np.ndarray` | Raw state vector (complex128, length N) |
| `_set_flat_state` | `(flat: np.ndarray)` | Overwrite and normalize state vector |

**Properties:** `n_qubits`, `N` (= 2ⁿ), `seed`, `t` (circuit depth/time), `state` (column matrix)

### `functions` module

```python
from novum_qvm.functions import (
    train_qnn,        # (features, labels, num_layers, num_steps, stepsize) → weights
    test_qnn,         # (weights, test_data) → List[float]
    custom_quantum_machine_learning,  # (X_train, Y_train, X_test, Y_test, ...) → predictions
    deutsch,          # (f) → 'Constant' | 'Balanced'
    grover_search,    # (secret_bitstring, shots, qubits) → str
    perlin,           # (x, y, z, seed) → float
    get_environmental_seed,  # () → int
)
```

### `QNLP` classes

| Class | Key Methods |
|-------|-------------|
| `QuantumStringEncoder` | `encode_string(text)`, `decode_string(qc, shots)` |
| `QuantumWordEmbeddings` | `get_embedding(word)`, `similarity(w1, w2)` |
| `QuantumAttention` | `attention_layer(input_states)` |
| `QuantumSyntacticParser` | `parse_sentence(sentence)` |
| `QuantumLanguageModel` | `add_training_corpus(text)`, `predict_next_word(text)`, `generate_text(prompt, max_length)` |
| `QuantumToolkit` | `create_language_model(name, ...)`, `save_model(name, path)`, `load_model(name, path)` |
| `ModelPersistence` | `save(model, path)`, `load(path)` |

---

## Contributing

```bash
git clone https://github.com/iriszimmerfrau-collab/novum-qvm.git
cd novum-qvm
pip install -e .[dev]
pytest tests/ -v
```

Pull requests welcome. Please add or update tests for any new functionality and ensure the full suite passes before submitting.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Citation

```bibtex
@software{novum_qvm,
  title  = {Novum-QVM: Perlin-Fourier Quantum Virtual Simulation},
  author = {Alogaili, Amin},
  year   = {2026},
  url    = {https://github.com/iriszimmerfrau-collab/novum-qvm}
}
```
