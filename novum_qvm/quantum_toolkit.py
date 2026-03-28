"""
Quantum toolkit for model creation, training, persistence and evaluation.

This is a minimal, functional toolkit intended as a foundation for building
more advanced training loops and persistence mechanisms for quantum models.
"""

import os
import json
import pickle
from typing import Dict, Any

from .qnlp import QuantumLanguageModel


class ModelPersistence:
    @staticmethod
    def save(model: QuantumLanguageModel, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Save metadata + serialized model via pickle
        meta = {
            "model_type": model.__class__.__name__,
            "vocab_size": model.vocab.vocab_size,
            "context_length": model.context_length,
        }
        with open(path + ".meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f)
        with open(path + ".pkl", "wb") as f:
            pickle.dump(model, f)

    @staticmethod
    def load(path: str) -> QuantumLanguageModel:
        with open(path + ".pkl", "rb") as f:
            model = pickle.load(f)
        return model


class QuantumToolkit:
    def __init__(self):
        self.models: Dict[str, QuantumLanguageModel] = {}

    def create_language_model(self, name: str, vocab_size: int = 1000, embedding_qubits: int = 10) -> QuantumLanguageModel:
        model = QuantumLanguageModel(vocab_size=vocab_size, embedding_qubits=embedding_qubits)
        self.models[name] = model
        return model

    def save_model(self, name: str, path: str) -> None:
        model = self.models.get(name)
        if model is None:
            raise ValueError("Unknown model")
        ModelPersistence.save(model, path)

    def load_model(self, name: str, path: str) -> QuantumLanguageModel:
        model = ModelPersistence.load(path)
        self.models[name] = model
        return model
