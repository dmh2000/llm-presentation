---
marp: true
theme: default
paginate: true
---

# LLM Inference Pipeline

Understanding the complete flow from text to predictions

---

## Tokenize Input Context

**Converting text to numbers**

- Text → numerical tokens via predefined vocabulary
- Vocabulary: 32k-100k+ tokens (BPE, WordPiece, SentencePiece)
- Each word/subword → unique integer ID
- Example: "running" → ["run", "##ning"] → [5432, 7821]
- Deterministic and reversible process

---

## Embeddings

**From tokens to dense vectors**

- Token ID → high-dimensional vector (1024, 2048+ dims)
- Learned lookup table mapping IDs to vectors
- Captures semantic meaning in continuous space
- Similar words → similar vectors
- Embedding dimension = model's information capacity

---

## Positional Encoding

**Teaching transformers about order**

- Transformers process tokens in parallel → no inherent order
- Adds position information to embeddings
- Original: sinusoidal functions (sin/cos)
- Modern: learned positional embeddings
- Combined representation: semantic + positional info
- "dog bites man" ≠ "man bites dog"

---

## Transformer Blocks

**Stacked layers for hierarchical learning**

- Multiple identical blocks stacked sequentially
- GPT-3: 96 layers, GPT-4: even more
- Each block: attention + feedforward + normalization
- Progressive abstraction through layers:
  - Early: syntax, simple patterns
  - Middle: semantic relationships
  - Late: complex reasoning, task-specific features
- Data is processed in chunks of batch size (B), sequence length (T) and vector size (d-model)
  - (B,T,d-model) tensor
---

### Transformer 1: Multi-Head Self-Attention

**The core innovation**

- Each token attends to all other tokens
- Q (Query), K (Key), V (Value) projections
- Attention score = dot(Q, K) → softmax → weight V
- Multiple heads (8-16) learn different relationships
- Enables context understanding
- Example: "it was too tired" → "it" refers to "animal"

---

### Transformer 2: Feedforward Neural Network

**Position-wise transformations**

- Two-layer fully connected network
- Dimension expansion (often 4x): 768 → 3072 → 768
- Non-linear activation (ReLU/GELU)
- Operates independently on each token
- Attention: inter-token relationships
- Feedforward: token-specific processing

---

### Transformer 3: Layer Normalization

**Stabilizing deep networks**

- Normalizes activations: zero mean, unit variance
- Applied before/after attention and feedforward
- Prevents covariate shift
- Combined with residual connections
- Pattern: LayerNorm(input + Sublayer(input))
- Enables training 100+ layer networks

---

## Output Projection

**Back to vocabulary space**

- Final hidden state → vocabulary space
- Linear transformation: hidden_dim → vocab_size
- Example: 1024 → 50,000 dimensions
- Produces logits (unnormalized scores)
- Higher logit = higher confidence
- Often shares weights with input embeddings

---

## Softmax

**Converting scores to probabilities**

- Logits → probability distribution
- Formula: P(token_i) = exp(logit_i) / Σ(exp(logit_j))
- All probabilities ∈ [0,1] and sum to 1.0
- Temperature scaling controls randomness:
  - temp < 1: sharper (deterministic)
  - temp > 1: flatter (random)

---

## Next-Token Sampling

**Selecting the output**

**Strategies:**
- Greedy (argmax): highest probability token
- Top-k: sample from k most probable
- Top-p (nucleus): sample from cumulative probability p
- Beam search: maintain multiple candidates

**Trade-offs:**
- Greedy: fast, deterministic, can be repetitive
- Stochastic: creative, diverse output

---

## Detokenization

**Numbers back to text**

- Token ID → text string (reverse vocabulary lookup)
- Handle subword pieces (concatenate, remove markers)
- Remove special tokens (padding, separators)
- Autoregressive loop:
  1. Generate token
  2. Append to sequence
  3. Repeat until stop condition
- Final output: human-readable text

---

# Summary

**Complete Pipeline:**
Text → Tokens → Embeddings → +Position → Transformer Blocks → Logits → Probabilities → Sample → Text

**Key Insights:**
- Transformers = Attention + Feedforward + Normalization
- Depth enables hierarchical learning
- Sampling strategy affects output quality
