import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from novum_qvm.QuantumComputer import PFQVS_QuantumComputer
from novum_qvm.qnlp import (
    QuantumStringEncoder,
    QuantumWordEmbeddings,
    QuantumAttention,
    QuantumSyntacticParser,
    QuantumLanguageModel
)
import numpy as np

class TestPFQVS(unittest.TestCase):
    def setUp(self):
        self.qc = PFQVS_QuantumComputer(2)
    
    def test_initialization(self):
        self.assertEqual(self.qc.n_qubits, 2)
        self.assertEqual(len(self.qc.state), 4)
        self.assertAlmostEqual(np.linalg.norm(self.qc.state), 1.0)
    
    def test_gate_application(self):
        initial_state = self.qc.state.copy()
        self.qc.apply_gate('H', 0)
        self.assertNotEqual(np.allclose(self.qc.state, initial_state), True)
        self.assertAlmostEqual(np.linalg.norm(self.qc.state), 1.0)
    
    def test_bell_state(self):
        self.qc.apply_gate('H', 0)
        self.qc.apply_gate('CNOT', 0, 1)
        counts = self.qc.measure(1000)
        total = sum(counts.values())
        # Should have high probability for 00 and 11
        self.assertGreater(counts.get('00', 0) / total + counts.get('11', 0) / total, 0.8)
    
    def test_grovers_search(self):
        # For 2 qubits, search for '11'
        counts = self.qc.grovers_search('11')
        # Should find '11' with high probability
        total = sum(counts.values())
        self.assertGreater(counts.get('11', 0) / total, 0.5)
    
    def test_deutsch_jozsa(self):
        # Test with constant function f=0
        f = lambda x: 0
        counts = self.qc.deutsch_jozsa(f)
        # Should measure 00...0
        # Simplified check
        self.assertIn('00', counts)
    
    def test_qasm_parsing(self):
        qasm = "h q[0]; cx q[0], q[1];"
        counts = self.qc.parse_qasm(qasm)
        total = sum(counts.values())
        self.assertGreater(counts.get('00', 0) / total + counts.get('11', 0) / total, 0.8)


class TestQNLP(unittest.TestCase):
    def test_string_encoding(self):
        encoder = QuantumStringEncoder()
        text = "test"
        qc = encoder.encode_string(text)
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
        input_states = [QuantumWordEmbeddings().get_embedding(w) for w in ["a", "b"]]
        attended = attention.attention_layer(input_states)
        self.assertIsInstance(attended, PFQVS_QuantumComputer)
    
    def test_parsing(self):
        parser = QuantumSyntacticParser()
        result = parser.parse_sentence("test sentence")
        self.assertIsInstance(result, dict)
    
    def test_language_generation(self):
        model = QuantumLanguageModel()
        generated = model.generate_text("test", max_length=5)
        self.assertIsInstance(generated, str)
        self.assertGreater(len(generated), len("test"))


if __name__ == '__main__':
    unittest.main()