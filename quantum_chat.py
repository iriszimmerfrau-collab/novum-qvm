#!/usr/bin/env python3
"""
Interactive Quantum NLP Chat - Dual Dataset (Puffin + human_chat.txt).

Features:
- Trains on BOTH Puffin dataset AND human_chat.txt dataset
- Maximum vocabulary size (10000 words)
- 12-qubit quantum embeddings for richer representations
- Order-2 (trigram) transition patterns for coherent text generation
- Fallback to order-1 (bigram) transitions when trigrams unavailable
- Uses all available examples from both datasets (~4500 total)
- Caches the model for instant reuse
- Interactive terminal chat interface
"""

import sys
import os
import time
import pickle

sys.path.insert(0, os.path.dirname(__file__))

from novum_qvm import QuantumLanguageModel

try:
    from datasets import load_dataset
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "datasets", "-q"])
    from datasets import load_dataset


MODEL_CACHE = "quantum_dual_dataset_model.pkl"


def load_puffin_dataset(num_examples=None):
    """Load Puffin dataset - load ALL examples if num_examples is None."""
    print("Loading Puffin dataset...")
    dataset = load_dataset("LDJnr/Puffin", split="train")
    if num_examples is not None:
        dataset = dataset.select(range(min(num_examples, len(dataset))))
    print(f"  ✓ Puffin: {len(dataset)} examples")
    return dataset


def load_human_chat_dataset(num_examples=None):
    """Load human_chat.txt dataset - load ALL examples if num_examples is None."""
    print("Loading human_chat.txt dataset...")
    dataset = load_dataset("athirababu0988/human_chat.txt", split="train")
    if num_examples is not None:
        dataset = dataset.select(range(min(num_examples, len(dataset))))
    print(f"  ✓ human_chat.txt: {len(dataset)} examples")
    return dataset
def load_gpt5_chat_dataset(num_examples=None):
    """Load GPT-5 chat dataset - load ALL examples if num_examples is None."""
    print("Loading GPT-5 chat dataset...")
    dataset = load_dataset("ytz20/LMSYS-Chat-GPT-5-Chat-Response", split="train")
    if num_examples is not None:
        dataset = dataset.select(range(min(num_examples, len(dataset))))
    print(f"  ✓ GPT-5 chat: {len(dataset)} examples")
    return dataset

def extract_puffin_text(dataset):
    """Extract conversation text from Puffin dataset."""
    all_text = []
    for i, example in enumerate(dataset):
        if 'conversations' in example and example['conversations']:
            for turn in example['conversations']:
                if isinstance(turn, dict) and 'value' in turn:
                    value = turn['value']
                    if value:
                        all_text.append(str(value))
        
        if (i + 1) % 500 == 0:
            print(f"    Puffin progress: {i + 1}/{len(dataset)} examples", end='\r')
    
    print()  # newline
    return ' '.join(all_text)


def extract_human_chat_text(dataset):
    """Extract text from human_chat.txt dataset."""
    all_text = []
    for i, example in enumerate(dataset):
        # human_chat.txt has 'text' field
        if 'text' in example and example['text']:
            text = example['text']
            if text:
                all_text.append(str(text))
        
        if (i + 1) % 500 == 0:
            print(f"    human_chat.txt progress: {i + 1}/{len(dataset)} examples", end='\r')
    
    print()  # newline
    return ' '.join(all_text)


def train_model(vocab_size=250000, embedding_qubits=16):
    """Train a new quantum model on BOTH Puffin AND human_chat.txt datasets."""
    print("\n" + "=" * 70)
    print("TRAINING QUANTUM MODEL ON DUAL DATASETS")
    print("(Puffin + human_chat.txt with maximum vocabulary)")
    print("=" * 70)
    
    # Load both datasets with ALL examples
    print(f"\nLoading both datasets...")
    puffin_dataset = load_puffin_dataset()  # Load all Puffin examples
    human_chat_dataset = load_human_chat_dataset()  # Load all human_chat examples
    
    # Extract text from both
    print(f"\nExtracting text from Puffin...")
    puffin_text = extract_puffin_text(puffin_dataset)
    
    print(f"Extracting text from human_chat.txt...")
    human_chat_text = extract_human_chat_text(human_chat_dataset)
    
    # Combine texts
    print(f"\nCombining datasets...")
    combined_text = puffin_text + " " + human_chat_text
    
    # Statistics
    words = combined_text.lower().split()
    unique_words = len(set(words))
    print(f"\n✓ Combined corpus statistics:")
    print(f"  Puffin examples: {len(puffin_dataset)}")
    print(f"  human_chat.txt examples: {len(human_chat_dataset)}")
    print(f"  Total examples: {len(puffin_dataset) + len(human_chat_dataset)}")
    print(f"  Total characters: {len(combined_text):,}")
    print(f"  Total words: {len(words):,}")
    print(f"  Unique words: {unique_words:,}")
    print(f"  Vocabulary coverage: {min(vocab_size, unique_words):,} / {unique_words:,}")
    
    # Create and train
    print(f"\nTraining quantum model...")
    print(f"  Vocabulary size: {vocab_size}")
    print(f"  Embedding qubits: {embedding_qubits}")
    
    model = QuantumLanguageModel(
        vocab_size=vocab_size,
        embedding_qubits=embedding_qubits,
        context_length=3
    )
    
    start = time.time()
    model.add_training_corpus(combined_text)
    train_time = time.time() - start
    
    print(f"\n✓ Training complete in {train_time:.2f}s")
    print(f"  Vocabulary learned: {len(model.vocab.word_to_idx)}")
    print(f"  Transition patterns: {len(model.transitions)}")
    
    return model


def save_model(model, path=MODEL_CACHE):
    """Save model to disk."""
    print(f"\nSaving model to {path}...")
    try:
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        print(f"✓ Model saved")
    except Exception as e:
        print(f"✗ Error saving model: {e}")


def load_model(path=MODEL_CACHE):
    """Load model from disk."""
    if not os.path.exists(path):
        return None
    
    try:
        print(f"Loading model from cache...")
        with open(path, 'rb') as f:
            model = pickle.load(f)
        print(f"✓ Model loaded from cache")
        return model
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return None


def clean_output(text):
    """Remove control tokens from generated text."""
    words = text.split()
    # Filter out special tokens like <bos>, <eos>, <unk>, etc.
    clean_words = [w for w in words if not (w.startswith("<") and w.endswith(">"))]
    return " ".join(clean_words)


def generate_clean(model, prompt, temperature, max_length, min_words=2):
    """Generate text with control token filtering and quality checks.
    
    Retries if response is too short or of poor quality.
    """
    for attempt in range(3):  # Try up to 3 times
        raw = model.generate_text(prompt, max_length=max_length, temperature=temperature)
        response = clean_output(raw)
        
        # Check if response has enough new words (not just echoing prompt)
        new_words = response.replace(prompt, "").strip().split()
        if len(new_words) >= min_words:
            return response
        
        # If response is too short, try again with slightly adjusted temp
        if attempt < 2:
            temperature = temperature * 1.1  # Increase randomness slightly
            continue
    
    # Fallback: return whatever we got
    return clean_output(model.generate_text(prompt, max_length=max_length, temperature=temperature))


def interactive_chat(model):
    """Interactive chat loop."""
    print("\n" + "=" * 70)
    print("QUANTUM NLP CHAT - Interactive Mode")
    print("=" * 70)
    print("\n⚠️  NOTE: This is a demonstration model with intentional limitations.")
    print("   It performs single-word prediction transitions without semantic")
    print("   understanding. For production use, see MODEL_LIMITATIONS.py")
    print("\nCommands:")
    print("  - Type any prompt to generate text")
    print("  - 'retrain' to train on fresh data")
    print("  - 'quit' or 'exit' to close chat")
    print("  - 'temp <value>' to set temperature (0.5-1.5, default 0.8)")
    print("  - 'length <value>' to set max length (5-30, default 15)")
    print("  - 'filter on/off' to toggle control token filtering (default: on)")
    print("\n" + "-" * 70 + "\n")
    
    temperature = 0.8
    max_length = 15
    use_filter = True
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting chat...")
            break
        
        if not user_input:
            continue
        
        # Handle commands
        if user_input.lower() in ('quit', 'exit'):
            print("Exiting chat...")
            break
        
        if user_input.lower() == 'retrain':
            print("Retraining model...")
            model = train_model()
            save_model(model)
            print("Model retrained and saved!")
            continue
        
        if user_input.lower().startswith('temp '):
            try:
                temp_val = float(user_input.split()[1])
                temperature = max(0.5, min(1.5, temp_val))
                print(f"Temperature set to {temperature}")
            except (IndexError, ValueError):
                print("Usage: temp <value> (0.5-1.5)")
            continue
        
        if user_input.lower().startswith('length '):
            try:
                len_val = int(user_input.split()[1])
                max_length = max(5, min(30, len_val))
                print(f"Max length set to {max_length}")
            except (IndexError, ValueError):
                print("Usage: length <value> (5-30)")
            continue
        
        if user_input.lower().startswith('filter '):
            setting = user_input.split()[1].lower()
            if setting in ('on', 'off'):
                use_filter = setting == 'on'
                state = "enabled" if use_filter else "disabled"
                print(f"Control token filtering {state}")
            else:
                print("Usage: filter on/off")
            continue
        
        # Generate response
        print("Quantum: ", end='', flush=True)
        try:
            if use_filter:
                response = generate_clean(model, user_input, temperature, max_length)
            else:
                response = model.generate_text(user_input, max_length=max_length, temperature=temperature)
            print(response)
        except Exception as e:
            print(f"Error generating response: {e}")
        
        print()


def main():
    """Main function."""
    print("=" * 70)
    print("QUANTUM NLP CHAT - Dual Dataset (Puffin + human_chat.txt)")
    print("=" * 70)
    
    # Check for cached model
    model = load_model(MODEL_CACHE)
    
    # If no cached model, train one
    if model is None:
        print("\nNo cached model found.")
        response = input("Train new model? (y/n): ").strip().lower()
        
        if response != 'y':
            print("Exiting...")
            return
        
        model = train_model()  # Uses default: vocab_size=10000, embedding_qubits=12
        save_model(model)
    
    # Start interactive chat
    interactive_chat(model)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
