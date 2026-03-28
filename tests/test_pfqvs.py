import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from novum_qvm.QuantumComputer import PFQVS_QuantumComputer
from novum_qvm.qnlp import (
    QuantumStringEncoder,
    QuantumWordEmbeddings,
    QuantumAttention,
    QuantumSyntacticParser,
    QuantumLanguageModel,
)


class TestPFQVS(unittest.TestCase):
    def setUp(self):
        self.qc = PFQVS_QuantumComputer(2)

    def _reset_to_zero(self, qc):
        """Reset state to computational |0...0> basis state."""
        psi = np.zeros(qc.N, dtype=complex)
        psi[0] = 1.0
        qc._set_flat_state(psi)

    def test_initialization(self):
        self.assertEqual(self.qc.n_qubits, 2)
        self.assertEqual(self.qc.N, 4)
        norm = np.linalg.norm(np.array(self.qc.state).flatten())
        self.assertAlmostEqual(norm, 1.0, places=10)

    def test_gate_application(self):
        initial_state = self.qc.state.copy()
        self.qc.apply_gate('H', 0)
        self.assertFalse(np.allclose(self.qc.state, initial_state))
        norm = np.linalg.norm(np.array(self.qc.state).flatten())
        self.assertAlmostEqual(norm, 1.0, places=10)

    def test_bell_state(self):
        # Must start from |00> for H+CNOT to produce a Bell state
        self._reset_to_zero(self.qc)
        self.qc.apply_gate('H', 0)
        self.qc.apply_gate('CNOT', 0, 1)
        counts = self.qc.measure(2000)
        total = sum(counts.values())
        bell_frac = (counts.get('00', 0) + counts.get('11', 0)) / total
        self.assertGreater(bell_frac, 0.85)

    def test_grovers_search(self):
        # Use 3 qubits: N=8, n_iter=2 → ~94% probability for target
        qc = PFQVS_QuantumComputer(3)
        counts = qc.grovers_search('111')
        total = sum(counts.values())
        self.assertGreater(counts.get('111', 0) / total, 0.5)

    def test_deutsch_jozsa(self):
        counts = self.qc.deutsch_jozsa(lambda x: 0)
        self.assertIn('00', counts)
        total = sum(counts.values())
        self.assertGreater(counts.get('00', 0) / total, 0.9)

    def test_qasm_parsing(self):
        # Must start from |00> for the Bell circuit to produce correct output
        self._reset_to_zero(self.qc)
        counts = self.qc.parse_qasm("h q[0]; cx q[0], q[1];")
        total = sum(counts.values())
        bell_frac = (counts.get('00', 0) + counts.get('11', 0)) / total
        self.assertGreater(bell_frac, 0.85)


class TestQNLP(unittest.TestCase):
    def test_string_encoding(self):
        encoder = QuantumStringEncoder()
        qc = encoder.encode_string("test")
        self.assertIsInstance(qc, PFQVS_QuantumComputer)
        self.assertGreater(qc.n_qubits, 0)

    def test_word_embeddings(self):
        embeddings = QuantumWordEmbeddings()
        emb = embeddings.get_embedding("test")
        self.assertIsInstance(emb, PFQVS_QuantumComputer)
        sim = embeddings.similarity("test", "word")
        self.assertIsInstance(sim, float)
        self.assertGreaterEqual(sim, 0.0)
        self.assertLessEqual(sim, 1.0)

    def test_attention(self):
        attention = QuantumAttention(2)
        states = [QuantumWordEmbeddings().get_embedding(w) for w in ["a", "b"]]
        attended = attention.attention_layer(states)
        self.assertIsInstance(attended, PFQVS_QuantumComputer)

    def test_parsing(self):
        parser = QuantumSyntacticParser()
        result = parser.parse_sentence("test sentence")
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_language_generation(self):
        model = QuantumLanguageModel()
        model.add_training_corpus("the quick brown fox jumps over the lazy dog")
        generated = model.generate_text("the quick", max_length=5)
        self.assertIsInstance(generated, str)
        self.assertGreater(len(generated), len("the quick"))


if __name__ == '__main__':
    unittest.main()
