"""
Novum-QVM: Quantum Virtual Machine with PFQVS and QNLP capabilities.
"""

from .functions import perlin, get_environmental_seed
from .QuantumComputer import PFQVS_QuantumComputer
from .qnlp import (
    QuantumStringEncoder,
    QuantumWordEmbeddings,
    QuantumAttention,
    QuantumSyntacticParser,
    QuantumLanguageModel
)

__version__ = "1.1.0"