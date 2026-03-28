"""
Novum-QVM: Quantum Virtual Machine with PFQVS and QNLP capabilities.
"""

from .QuantumComputer import PFQVS_QuantumComputer
from .functions import perlin, get_environmental_seed
from .qnlp import (
    QuantumStringEncoder,
    QuantumWordEmbeddings,
    QuantumAttention,
    QuantumSyntacticParser,
    QuantumLanguageModel,
)
from .quantum_toolkit import ModelPersistence, QuantumToolkit

__version__ = "1.2.0"

__all__ = [
    "PFQVS_QuantumComputer",
    "perlin",
    "get_environmental_seed",
    "QuantumStringEncoder",
    "QuantumWordEmbeddings",
    "QuantumAttention",
    "QuantumSyntacticParser",
    "QuantumLanguageModel",
    "ModelPersistence",
    "QuantumToolkit",
    "__version__",
]
