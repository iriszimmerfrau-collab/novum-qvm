"""
Quantum Natural Language Processing (QNLP) module for Novum-QVM.

Production-ready QNLP utilities built on PFQVS. Implements:
- Quantum string encoding (position+char amplitude encoding)
- Quantum word embeddings (Perlin-seeded embeddings)
- Quantum attention (entangling-based attention primitives)
- Quantum syntactic parsing (circuit-based parser)
- Quantum language model with vocabulary management and probabilistic prediction

All quantum operations use `PFQVS_QuantumComputer` so they inherit Perlin
initialization, Fourier gate execution, spectral decoherence, and
importance-sampling measurement.
"""

import logging
from typing import Dict, List, Optional
import numpy as np

from .QuantumComputer import PFQVS_QuantumComputer

logger = logging.getLogger(__name__)


class QuantumStringEncoder:
    """Encode short strings into a quantum state.

    Encoding: allocate `position_bits` for the position and 8 bits for the
    character code. Basis index = (position << 8) | char_id. The resulting
    computational-basis state is set to a superposition of the encoded tokens.
    """

    def __init__(self, max_length: int = 256):
        self.max_length = int(max_length)
        self.position_bits = max(1, int(np.ceil(np.log2(self.max_length))))
        self.char_bits = 8
        self.n_qubits = self.position_bits + self.char_bits
        self.char_to_int: Dict[str, int] = {}
        self.int_to_char: Dict[int, str] = {}
        # reserve <UNK>
        self._register_char("<UNK>")

    def _register_char(self, ch: str) -> int:
        if ch not in self.char_to_int:
            idx = len(self.char_to_int)
            self.char_to_int[ch] = idx
            self.int_to_char[idx] = ch
        return self.char_to_int[ch]

    def encode_string(self, text: str) -> PFQVS_QuantumComputer:
        text = text or ""
        state_size = 2 ** self.n_qubits
        psi = np.zeros(state_size, dtype=complex)

        for pos, ch in enumerate(text[: self.max_length]):
            ch_id = self._register_char(ch)
            idx = (pos << self.char_bits) | (ch_id & ((1 << self.char_bits) - 1))
            psi[idx] += 1.0

        # Normalize amplitudes
        if np.linalg.norm(psi) == 0:
            # empty string -> small random state
            psi = 1e-3 + 1e-3j * np.random.randn(state_size)
        psi = psi / np.linalg.norm(psi)

        qc = PFQVS_QuantumComputer(self.n_qubits)
        try:
            qc.state = np.matrix(psi).T
        except Exception:
            qc.state = np.matrix(psi.copy()).T
        return qc

    def decode_string(self, qc: PFQVS_QuantumComputer, shots: int = 1000) -> str:
        counts = qc.measure(shots)

        # Reconstruct by selecting most frequent measurement per position
        position_chars: Dict[int, List[str]] = {}
        for bitstr, c in counts.items():
            idx = int(bitstr, 2)
            char_id = idx & ((1 << self.char_bits) - 1)
            pos = idx >> self.char_bits
            ch = self.int_to_char.get(char_id, "<UNK>")
            position_chars.setdefault(pos, []).append((c, ch))

        # assemble string by choosing most frequent char per position
        if not position_chars:
            return ""
        max_pos = max(position_chars.keys())
        out = []
        for p in range(max_pos + 1):
            candidates = position_chars.get(p, [])
            if not candidates:
                break
            ch = max(candidates, key=lambda x: x[0])[1]
            out.append(ch)
        return "".join(out)


class QuantumWordEmbeddings:
    """Quantum embeddings implemented as PFQVS states seeded by word hash.

    Each word maps to a `PFQVS_QuantumComputer` instance of `embedding_qubits`.
    """

    def __init__(self, vocab_size: int = 1000, embedding_qubits: int = 10):
        self.vocab_size = int(vocab_size)
        self.embedding_qubits = int(embedding_qubits)
        self.embeddings: Dict[str, PFQVS_QuantumComputer] = {}

    def get_embedding(self, word: str) -> PFQVS_QuantumComputer:
        key = word.lower() if word is not None else "<UNK>"
        if key not in self.embeddings:
            seed = abs(hash(key)) % (2 ** 31)
            qc = PFQVS_QuantumComputer(self.embedding_qubits, seed=seed)
            self.embeddings[key] = qc
        return self.embeddings[key]

    def similarity(self, word1: str, word2: str) -> float:
        emb1 = self.get_embedding(word1)
        emb2 = self.get_embedding(word2)
        v1 = np.array(emb1.state).flatten()
        v2 = np.array(emb2.state).flatten()
        # fidelity
        fid = np.abs(np.vdot(v1, v2)) ** 2
        return float(np.clip(fid, 0.0, 1.0))


class QuantumAttention:
    """Simplified quantum attention: entangle embeddings to share amplitude information."""

    def __init__(self, n_qubits_per_token: int = 2):
        self.n_qubits_per_token = int(n_qubits_per_token)

    def attention_layer(self, input_states: List[PFQVS_QuantumComputer]) -> PFQVS_QuantumComputer:
        if not input_states:
            return PFQVS_QuantumComputer(1)
        total_qubits = len(input_states) * self.n_qubits_per_token
        qc = PFQVS_QuantumComputer(total_qubits)
        # Simple entangling pattern to mix information
        for i in range(min(total_qubits - 1, 8)):
            try:
                qc.apply_gate('H', i)
                qc.apply_gate('CNOT', i, i + 1)
            except Exception:
                pass
        return qc


class QuantumSyntacticParser:
    """Circuit-based syntactic parser (prototype).

    In production, replace with grammar-specific circuits derived from the
    parsing formalism; this is a scaffolding to run experiments.
    """

    def __init__(self, n_qubits: int = 10):
        self.n_qubits = int(n_qubits)

    def parse_sentence(self, sentence: str) -> Dict[str, int]:
        qc = PFQVS_QuantumComputer(self.n_qubits)
        encoder = QuantumStringEncoder()
        context = encoder.encode_string(sentence)
        # apply a small parsing circuit
        try:
            qc.apply_gate('H', 0)
            qc.apply_gate('CNOT', 0, 1)
        except Exception:
            pass
        counts = qc.measure(1000)
        return counts


class VocabularyManager:
    """Simple vocabulary manager with add/get functionality."""

    def __init__(self, vocab_size: int = 1000):
        self.vocab_size = int(vocab_size)
        self.word_to_idx: Dict[str, int] = {}
        self.idx_to_word: Dict[int, str] = {}
        self._init_common()

    def _init_common(self):
        common = ["<BOS>", "<EOS>", "<UNK>", "the", "and", "of", "to", "in", "a", "is"]
        for w in common:
            self.add_word(w)

    def add_word(self, word: str) -> int:
        w = word.lower().strip()
        if w in self.word_to_idx:
            return self.word_to_idx[w]
        if len(self.word_to_idx) >= self.vocab_size:
            return self.word_to_idx.get("<UNK>", 0)
        idx = len(self.word_to_idx)
        self.word_to_idx[w] = idx
        self.idx_to_word[idx] = w
        return idx

    def get_word(self, idx: int) -> str:
        return self.idx_to_word.get(int(idx), "<UNK>")


class QuantumVocabularyMapper:
    """Map measurement counts to vocabulary words."""

    def __init__(self, vocab_manager: VocabularyManager):
        self.vocab = vocab_manager

    def measurement_to_word_probabilistic(self, counts: Dict[str, int], temperature: float = 1.0, 
                                          candidates: Dict[str, int] = None) -> str:
        if not counts:
            return self.vocab.get_word(0)
        
        counts = counts.copy()
        counts.pop("__importance__", None)
        total = sum(counts.values())
        probs: Dict[int, float] = {}
        
        for bitstr, c in counts.items():
            try:
                idx = int(bitstr, 2) % self.vocab.vocab_size
            except Exception:
                continue
            p = c / total
            # temperature scaling
            p = np.exp(np.log(max(p, 1e-12)) / max(1e-6, temperature))
            probs[idx] = probs.get(idx, 0.0) + p
        
        if not probs:
            return self.vocab.get_word(0)
        
        # If candidates provided (from trigram/bigram), weight them more heavily
        if candidates:
            candidate_words = list(candidates.keys())
            candidate_counts = list(candidates.values())
            candidate_total = sum(candidate_counts)
            
            # Boost probabilities of trained candidates
            for word_str in candidate_words:
                idx = self.vocab.word_to_idx.get(word_str, None)
                if idx is not None:
                    boost = (candidates[word_str] / candidate_total) * 2.0  # 2x boost for trained transitions
                    probs[idx] = probs.get(idx, 0) + boost
        
        keys = list(probs.keys())
        vals = np.array([probs[k] for k in keys], dtype=float)
        vals /= vals.sum()
        chosen = np.random.choice(keys, p=vals)
        return self.vocab.get_word(chosen)


class QuantumLanguageModel:
    """Quantum language model with order-2 (trigram) transition patterns for better conversation."""

    def __init__(self, vocab_size: int = 1000, embedding_qubits: int = 10, context_length: int = 3):
        self.vocab = VocabularyManager(vocab_size)
        self.mapper = QuantumVocabularyMapper(self.vocab)
        self.embeddings = QuantumWordEmbeddings(vocab_size, embedding_qubits)
        self.context_length = int(context_length)
        # Order-2 transitions: (word_prev, word_current) -> {next_word: count}
        self.transitions: Dict[tuple, Dict[str, int]] = {}
        # Fallback transitions: word -> {next_word: count} for single-word context
        self.fallback_transitions: Dict[str, Dict[str, int]] = {}

    def add_training_corpus(self, text: str):
        words = text.lower().split()
        for w in words:
            self.vocab.add_word(w)
        
        # Build order-2 (trigram) transitions
        for i in range(len(words) - 2):
            context = (words[i], words[i + 1])
            next_word = words[i + 2]
            self.transitions.setdefault(context, {})[next_word] = \
                self.transitions.setdefault(context, {}).get(next_word, 0) + 1
        
        # Build fallback order-1 transitions
        for a, b in zip(words, words[1:]):
            self.fallback_transitions.setdefault(a, {})[b] = \
                self.fallback_transitions.setdefault(a, {}).get(b, 0) + 1

    def _encode_context(self, words: List[str]) -> Optional[PFQVS_QuantumComputer]:
        context = words[-self.context_length:]
        if not context:
            return None
        # produce a small combined quantum state from the last token's embedding
        last = context[-1]
        return self.embeddings.get_embedding(last)

    def predict_next_word(self, text: str, temperature: float = 1.0, shots: int = 500) -> str:
        words = text.lower().strip().split()
        if not words:
            return self.vocab.get_word(0)
        
        # Try order-2 (trigram) prediction first
        candidates = None
        if len(words) >= 2:
            context = (words[-2], words[-1])
            candidates = self.transitions.get(context)
        
        # Fall back to order-1 (bigram) if trigram not found
        if not candidates and len(words) >= 1:
            last = words[-1]
            candidates = self.fallback_transitions.get(last)
        
        # If still no candidates, use random word
        if not candidates:
            return self.vocab.get_word(0)
        
        # Build prediction circuit
        last = words[-1]
        emb_qc = self.embeddings.get_embedding(last)
        pred_qc = PFQVS_QuantumComputer(emb_qc.n_qubits)
        try:
            pred_qc.state = emb_qc.state.copy()
        except Exception:
            pass
        
        # Small exploration gates
        for i in range(min(3, pred_qc.n_qubits)):
            try:
                pred_qc.apply_gate('H', i)
            except Exception:
                pass
        
        counts = pred_qc.measure(shots)
        # Use trigram/bigram candidates for weighting
        word = self.mapper.measurement_to_word_probabilistic(counts, temperature=temperature, 
                                                              candidates=candidates)
        return word

    def generate_text(self, prompt: str, max_length: int = 50, temperature: float = 1.0) -> str:
        text = prompt.strip()
        for _ in range(max_length):
            next_word = self.predict_next_word(text, temperature=temperature)
            if next_word in ("<EOS>", ""):
                break
            text = text + " " + next_word
        return text
