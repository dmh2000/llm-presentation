#!/usr/bin/env python3
# %%
# Inference script for trained LLM model
import torch
import torch.nn as nn
import argparse
import sys
import embedding
from train import TransformerLM


# %%
def load_model_and_vocab(model_path="final_model.pth"):
    """Load the trained model and vocabulary"""
    # Load vocabulary from original text
    with open("chapter1.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    vectors, vocabulary = embedding.get_vectors(text)
    vocab_size = len(vocabulary)
    
    # Model parameters (should match training)
    d_model = embedding.d_model
    num_heads = 8
    d_ff = 128
    num_layers = 4
    
    # Initialize model
    model = TransformerLM(vocab_size, d_model, num_heads, d_ff, num_layers)
    
    # Load trained weights
    try:
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
        print(f"Model loaded from {model_path}")
    except FileNotFoundError:
        print(f"Warning: Model file {model_path} not found. Using untrained model.")
    
    model.eval()
    return model, vocabulary


# %%
def generate_text(model, vocabulary, prompt, max_length=100, temperature=1.0):
    """Generate text using the trained model"""
    model.eval()
    
    # Since vocabulary doesn't have special tokens, use indices as fallbacks
    vocab_dict = vocabulary.get_stoi() if hasattr(vocabulary, 'get_stoi') else vocabulary.stoi
    vocab_size = len(vocab_dict)
    
    # Use arbitrary tokens as start/end markers
    sos_token = 0  # First token in vocabulary
    eos_token = 1  # Second token in vocabulary
    
    # Tokenize input prompt
    prompt_tokens = embedding.tokenize(prompt.lower())
    
    # Convert to token IDs, handle unknown tokens
    prompt_ids = []
    for token in prompt_tokens:
        if token in vocab_dict:
            prompt_ids.append(vocabulary[token])
        else:
            # Use a random token from vocabulary as fallback
            prompt_ids.append(0)
    
    # Ensure we have at least one token for source
    if not prompt_ids:
        prompt_ids = [0]
    
    # Create input tensors
    src = torch.tensor([prompt_ids])  # Source sequence [batch_size, seq_len]
    tgt = torch.tensor([[sos_token]])  # Start with SOS token [batch_size, 1]
    
    generated_tokens = [sos_token]
    
    with torch.no_grad():
        for step in range(max_length):
            # Forward pass
            logits = model(src, tgt)
            
            # Get probabilities for next token
            next_token_logits = logits[0, -1, :] / temperature
            probs = torch.softmax(next_token_logits, dim=-1)
            
            # Sample next token (greedy or sampling)
            if temperature == 0.0:
                next_token = torch.argmax(probs)
            else:
                next_token = torch.multinomial(probs, 1)
            
            next_token_id = next_token.item()
            generated_tokens.append(next_token_id)
            
            # Stop if EOS token is generated or if we hit vocabulary boundary
            if next_token_id == eos_token or next_token_id >= vocab_size:
                break
            
            # Append to target sequence - fix tensor dimensions
            next_token_tensor = torch.tensor([[next_token_id]])  # [batch_size, 1]
            tgt = torch.cat([tgt, next_token_tensor], dim=1)
    
    return generated_tokens


# %%
def tokens_to_text(tokens, vocabulary):
    """Convert token IDs back to text"""
    words = []
    for token_id in tokens:
        if hasattr(vocabulary, 'get_itos'):
            # torchtext >= 0.9.0
            if token_id < len(vocabulary.get_itos()):
                word = vocabulary.get_itos()[token_id]
            else:
                word = "<unk>"
        else:
            # older torchtext versions
            if hasattr(vocabulary, 'itos') and token_id < len(vocabulary.itos):
                word = vocabulary.itos[token_id]
            else:
                word = "<unk>"
        
        # Skip special tokens in output
        if word not in ["<SOS>", "<EOS>", "<unk>"]:
            words.append(word)
    
    return " ".join(words)


# %%
def main():
    parser = argparse.ArgumentParser(description="Generate text using trained LLM")
    parser.add_argument("prompt", nargs="?", default="dorothy", 
                       help="Input prompt for text generation")
    parser.add_argument("--model", default="final_model.pth",
                       help="Path to trained model file")
    parser.add_argument("--max-length", type=int, default=50,
                       help="Maximum length of generated text")
    parser.add_argument("--temperature", type=float, default=0.8,
                       help="Sampling temperature (0.0 = greedy, higher = more random)")
    
    args = parser.parse_args()
    
    # If no prompt provided and not from command line args, read from stdin
    if len(sys.argv) == 1:
        print("Enter a prompt (or 'quit' to exit):")
        prompt = input("> ").strip()
        if prompt.lower() == 'quit':
            return
    else:
        prompt = args.prompt
    
    print(f"Loading model and generating text for prompt: '{prompt}'")
    print(f"Max length: {args.max_length}, Temperature: {args.temperature}")
    print("-" * 50)
    
    # Load model and vocabulary
    model, vocabulary = load_model_and_vocab(args.model)
    
    # Generate text
    generated_tokens = generate_text(
        model, vocabulary, prompt, 
        max_length=args.max_length, 
        temperature=args.temperature
    )
    
    # Convert back to text
    generated_text = tokens_to_text(generated_tokens, vocabulary)
    
    # Output results
    print(f"Prompt: {prompt}")
    print(f"Generated: {generated_text}")


# %%
if __name__ == "__main__":
    main()