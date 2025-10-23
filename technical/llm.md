## tokenize input context

Tokenization is the first step in LLM inference, where input text is converted into numerical tokens that the model can process. The tokenizer uses a predefined vocabulary (typically 32k-100k+ tokens) built during training using algorithms like Byte Pair Encoding (BPE), WordPiece, or SentencePiece. Each word or subword unit is mapped to a unique integer ID from this vocabulary. For example, "running" might be split into ["run", "##ning"] and mapped to token IDs [5432, 7821]. This representation allows the model to handle unknown words through subword decomposition and maintains a manageable vocabulary size. The tokenization process is deterministic and reversible, enabling detokenization after inference.

---
## create embeddings

Each token ID is converted into a dense vector representation called an embedding. The embedding layer is essentially a learned lookup table where each token ID maps to a high-dimensional vector (typically 1024, 2048, or larger dimensions depending on the model). For instance, token ID 5432 might map to a 1024-dimensional vector of floating-point numbers. These embeddings are learned during training and capture semantic meaning - similar words have similar embedding vectors in the high-dimensional space. This continuous vector representation enables the model to perform mathematical operations and learn relationships between tokens. The embedding dimension determines the model's capacity to represent information and remains consistent throughout the network.

---
## positional encoding

Since transformers process all tokens in parallel (unlike RNNs which process sequentially), they have no inherent understanding of token order. Positional encoding adds information about each token's position in the sequence to its embedding. The original Transformer paper used sinusoidal functions (sin and cos of different frequencies) to generate position-dependent patterns, while modern models like GPT use learned positional embeddings. These positional encodings are added element-wise to the token embeddings, creating a combined representation that contains both semantic (what the token means) and positional (where it appears) information. This allows the model to distinguish between "dog bites man" and "man bites dog" - same tokens, different meanings based on position.

---
## transformer blocks (repeated layers)

A transformer model consists of multiple identical transformer blocks stacked sequentially (GPT-3 has 96 layers, GPT-4 reportedly has even more). Each block contains the same architecture: multi-head self-attention followed by a feedforward network, with layer normalization and residual connections around each component. The output of one block becomes the input to the next block. As data flows through these stacked layers, the model builds increasingly abstract representations - early layers might capture syntax and simple patterns, middle layers learn semantic relationships, and later layers handle complex reasoning and task-specific features. This depth allows the model to learn hierarchical representations similar to how deep CNNs learn visual features. During inference, the input must pass through all these layers sequentially, which is why deeper models are slower despite being more capable.

---
### multihead self-attention

The attention mechanism is the core innovation of transformers, allowing each token to "attend to" or gather information from all other tokens in the sequence. Each token's embedding is projected into three vectors: Query (Q), Key (K), and Value (V) using learned weight matrices. The attention score between tokens is computed as the dot product of queries and keys, scaled and normalized with softmax, then used to weight the value vectors. Multi-head attention runs this process in parallel across multiple "heads" (typically 8-16), each learning different aspects of relationships - one head might focus on syntax, another on semantic relationships. The outputs from all heads are concatenated and projected back to the original dimension. This mechanism enables the model to understand context: in "The animal didn't cross the street because it was too tired", attention helps determine that "it" refers to "animal" not "street".

---
### feedforward neural network

After the attention mechanism, each token's representation passes through a position-wise feedforward neural network. This is a simple two-layer fully connected network with a non-linear activation function (typically ReLU or GELU) in between. The first layer expands the dimension (often by 4x - so 768 dimensions becomes 3072), applies the activation, then the second layer projects back down to the original dimension. This network operates independently on each token position, providing additional transformational capacity beyond what attention provides. While attention lets tokens interact with each other, the feedforward network allows each token to be processed through a learned non-linear transformation. This combination of attention (for inter-token relationships) and feedforward (for token-specific processing) gives transformers their representational power.

---
### layer normalization

Layer normalization is applied within each transformer block to stabilize training and improve convergence. It normalizes the activations across the feature dimension for each token independently, ensuring they have zero mean and unit variance. This is typically applied before or after (depending on architecture variant) both the attention and feedforward sublayers. LayerNorm prevents the internal covariate shift problem where the distribution of inputs to each layer changes during training. It also acts as a regularizer and helps with gradient flow through very deep networks. Modern transformers use residual connections (skip connections) around each sublayer combined with layer normalization - the pattern is typically: output = LayerNorm(input + Sublayer(input)). This combination enables training very deep networks (100+ layers) without vanishing or exploding gradients.

---
## output projection layer

After the final transformer block, the model needs to convert the high-dimensional hidden state representation back to vocabulary space to predict the next token. The output projection layer (also called the language modeling head) is a linear transformation that projects from the model's hidden dimension (e.g., 768 or 1024) to the vocabulary size (e.g., 50,000 or 100,000). For autoregressive generation, only the last token's representation is used for this projection. This produces a vector of logits (unnormalized scores) with one value for each token in the vocabulary. Higher logit values indicate the model's higher confidence that the corresponding token should come next. In many models, this projection layer shares weights with the input embedding layer (weight tying), which reduces parameters and improves performance.

---
## compute output probability using softmax

The softmax function converts the raw logits from the output projection layer into a proper probability distribution over the vocabulary. It exponentiates each logit value and normalizes by the sum of all exponentiated values, ensuring all probabilities are between 0 and 1 and sum to 1.0. The formula is: P(token_i) = exp(logit_i) / Σ(exp(logit_j)) for all j in vocabulary. Softmax emphasizes larger values - a logit of 5.0 gets much higher probability than a logit of 2.0. Temperature scaling is often applied before softmax to control randomness: dividing logits by temperature < 1 makes the distribution sharper (more deterministic), while temperature > 1 makes it flatter (more random). This probability distribution represents the model's belief about which token should come next in the sequence.

---
## next-token sampling

Once we have the probability distribution from softmax, we need to select which token to actually generate. The simplest approach is greedy decoding using argmax - selecting the token with the highest probability. However, this isn't always used in practice. Alternative sampling strategies include: Top-k sampling (randomly sample from the k most probable tokens), Top-p/nucleus sampling (sample from the smallest set of tokens whose cumulative probability exceeds p), and beam search (maintain multiple candidate sequences and pick the overall most probable). Greedy argmax is deterministic and fast but can lead to repetitive or boring outputs. Stochastic sampling methods introduce controlled randomness that often produces more creative and diverse text. The choice of sampling strategy significantly impacts the quality and variety of generated text.

---
## detokenization

The final step converts the selected token ID back into human-readable text. The detokenizer uses the same vocabulary mapping as the tokenizer but in reverse - mapping integer IDs back to their corresponding text strings. For subword tokenizers, this involves concatenating the pieces and handling special characters (like removing "##" prefixes in WordPiece or merging byte pairs in BPE). The detokenizer also handles special tokens (like padding or separation tokens) that should be removed from the final output. For autoregressive generation, this process repeats: the newly generated token is appended to the input sequence, and the entire inference process runs again to generate the next token. This continues until a stop condition is met (end-of-sequence token, maximum length, or user interruption). The accumulated detokenized tokens form the final generated text output.
