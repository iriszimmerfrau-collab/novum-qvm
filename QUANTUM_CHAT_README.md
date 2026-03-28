#!/usr/bin/env python3
"""
QUANTUM NLP INTERACTIVE CHAT - README

A terminal-based chat interface for quantum language models trained on 
the Puffin dataset. The model is trained once and cached for reuse.

QUICK START:
============
    python quantum_chat.py

FEATURES:
=========
✓ First run: Trains on Puffin (500 examples, 345K words)
✓ Saves model cache to puffin_model.pkl
✓ Subsequent runs: Loads from cache (instant startup)
✓ Interactive chat interface  
✓ Configurable temperature and max length
✓ Force retrain option

INTERACTIVE COMMANDS:
====================
    prompt text         → Generate text from prompt
    temp <value>        → Set temperature (0.5-1.5, default 0.8)
    length <value>      → Set max length (5-30, default 15)
    filter on/off       → Toggle control token filtering (default: on)
    retrain             → Force retraining on fresh Puffin data
    quit / exit         → Exit chat

EXAMPLE SESSION:
================

$ python quantum_chat.py

======================================================================
QUANTUM NLP CHAT - Puffin-Trained
======================================================================
Loading model from cache...
✓ Model loaded from cache

======================================================================
QUANTUM NLP CHAT - Interactive Mode
======================================================================

Commands:
  - Type any prompt to generate text
  - 'retrain' to train on fresh data  
  - 'quit' or 'exit' to close chat
  - 'temp <value>' to set temperature (0.5-1.5)
  - 'length <value>' to set max length (5-30)

----------------------------------------------------------------------

You: how does quantum work
Quantum: how does quantum work is <eos> <bos> <eos> i <eos> a <eos> i <eos> is

You: explain the algorithm
Quantum: explain the algorithm <eos> <bos> a is <eos> <bos> <eos> is <eos> a <eos>

You: temp 1.2
Temperature set to 1.2

You: what is machine learning
Quantum: what is machine learning a <eos> <eos> i <eos> i <bos> <bos> a <eos>

You: length 20
Max length set to 20

You: the quantum computing
Quantum: the quantum computing is <eos> <bos> <eos> i a <eos> <eos> <eos> is <eos> 
         a <eos> <bos> <eos> <eos> that a be <eos> of <eos>

You: quit
Exiting chat...

TECHNICAL DETAILS:
=================

Model Architecture:
  - Vocabulary: 800 words (from Puffin dataset)
  - Embedding Qubits: 4 (PFQVS quantum embeddings)
  - Context Length: 3 words
  - Measurement Shots: 500 per prediction

Puffin Dataset:
  - Source: https://huggingface.co/datasets/LDJnr/Puffin
  - 3,000 multi-turn conversations
  - Topics: Coding, Math, Physics, Biology, Chemistry, Q&A
  - Training data: 500 examples (345K words)

Quantum Operations:
  - Each word maps to a PFQVS quantum state (4 qubits)
  - Predictions use Hadamard gates + measurement
  - Temperature scaling for output diversity
  
Cache File:
  - puffin_model.pkl (cached model for instant loading)
  - Delete to force retraining

PERFORMANCE:
===========
✓ Training time: ~1 minute (first run)
✓ Chat response time: 50-100ms per generation
✓ Memory: ~50MB (model + embeddings cache)

OUTPUT QUALITY & FILTERING:
==========================
By default, the chat applies control token filtering to improve readability.

Without filtering:
  "what is a is <bos> <eos> <eos> <eos> <eos> center <unk> is <bos>"

With filtering:
  "what is a is center"

Use 'filter off' to see raw quantum output with control tokens.
Tips: Lower temperature = more focused, Higher = more varied.

TROUBLESHOOTING:

REQUIREMENTS:
=============
- Python 3.7+
- novum_qvm (in local directory)
- datasets (auto-installed if missing)
- numpy

FILES:
======
quantum_chat.py              ← Main interactive chat script
puffin_model.pkl             ← Cached model (auto-generated)
train_on_puffin.py           ← Training script (for custom training)
train_puffin_enhanced.py     ← Enhanced training (larger dataset)
verify_quantum_model.py      ← Verification tests
train_qnlp_model.py          ← QNLP HTML document training

For more information, see the main project README.md
"""

# This file is documentation. To run the chat:
# python quantum_chat.py
