# Speaker Notes: How Large Language Models Perform Inference

---

## Slide 1: What Is a Decode-Only LLM?

- Modern LLMs like GPT and Llama are "decode-only" transformers — they generate text one token at a time, left to right, like finishing someone's sentence
- "Decode-only" means the model only has one job: predict the next word (token) given everything that came before it
- This is different from encoder-decoder models (like early translation systems) that first read the whole input, then generate output in a separate step
- Think of it like an autocomplete engine — but one that's read a significant fraction of the internet and learned patterns of language, reasoning, and knowledge
- The architecture is a deep stack of transformer blocks, each one refining the model's understanding of what token should come next
- Every output token becomes part of the input for generating the next one — the model "talks to itself" one word at a time

---

## Slide 2: Tokenization — Turning Text into Numbers

- Before the model can do anything, raw text must be converted into tokens — small chunks that are usually words, subwords, or punctuation
- The model doesn't see letters or words the way we do; it works with a fixed vocabulary of ~32K–100K token IDs (integers)
- Common words like "the" are a single token; rare words get split into pieces ("unbelievable" → "un" + "believ" + "able")
- This is a lookup process, not learned — it uses a pre-built dictionary (like BPE) created before training
- Each token ID is then mapped to a high-dimensional vector (the "embedding") — this is where meaning starts to be represented
- Think of tokenization as translating human language into the model's native language of numbers

---

## Slide 3: Embedding and Positional Encoding

- Each token ID is looked up in an embedding table, producing a dense vector (e.g., 4096 numbers) that represents the token's meaning
- These vectors live in a high-dimensional space where similar concepts end up near each other — "king" is near "queen," "cat" is near "dog"
- The model also needs to know *where* each token appears in the sequence — "dog bites man" vs "man bites dog" mean very different things
- Positional encodings are added to each embedding so the model can distinguish token order
- At this point, each token is represented as a rich numerical vector that encodes both *what* the token is and *where* it sits in the sequence
- This combined representation is the input that flows into the transformer layers

---

## Slide 4: Self-Attention — How Tokens Talk to Each Other

- Self-attention is the core mechanism that lets each token "look at" every previous token and decide which ones are relevant
- Imagine reading a sentence and highlighting the words that help you understand the current word — that's what attention does, mathematically
- Each token produces three vectors: a Query ("what am I looking for?"), a Key ("what do I contain?"), and a Value ("what information do I share?")
- Attention scores are computed by comparing each token's Query against all previous tokens' Keys — high scores mean high relevance
- In decode-only models, tokens can only attend to tokens that came *before* them (causal masking) — the model can't peek ahead
- Multi-head attention runs this process multiple times in parallel, letting the model attend to different types of relationships simultaneously (grammar, meaning, context)

---

## Slide 5: Feed-Forward Layers — Where Knowledge Lives

- After attention gathers context, each token passes through a feed-forward network (FFN) — essentially two large matrix multiplications with an activation function in between
- If attention is "thinking about relationships between words," the FFN is "applying stored knowledge" — facts, patterns, and associations learned during training
- These layers are where most of the model's parameters live — they act like a vast compressed database of learned information
- The FFN processes each token independently — it transforms the attention-enriched representation into a deeper, more refined understanding
- Think of it as: attention decides what's relevant, then the FFN interprets what that means based on everything the model learned in training
- Each transformer block pairs one attention layer with one FFN — a typical model stacks 32–80 of these blocks deep

---

## Slide 6: Layer Stacking — Building Understanding Incrementally

- The model processes tokens through dozens of transformer blocks in sequence — each one refines the representation further
- Early layers tend to capture surface-level features: syntax, grammar, simple word relationships
- Middle layers build more abstract understanding: entity recognition, semantic roles, factual associations
- Later layers focus on task-specific reasoning: deciding what the actual next word should be given the full context
- A residual connection around each sub-layer means information can skip ahead — the model doesn't lose early insights as it goes deeper
- Layer normalization keeps the numbers stable as they flow through many layers, preventing signals from exploding or vanishing

---

## Slide 7: Output — From Vectors to Words

- After the final transformer block, each token position has a rich vector representation encoding the model's full understanding
- We only care about the *last* token's vector — that's the one predicting what comes next
- This vector is multiplied by the embedding table (transposed) to produce a score (logit) for every token in the vocabulary
- A softmax function converts these logits into probabilities — "the" might get 12%, "a" might get 8%, "cat" might get 3%, etc.
- A sampling strategy then picks the actual next token: greedy (take the highest), temperature sampling (add randomness), or top-k/top-p (choose from the most likely candidates)
- The chosen token is appended to the sequence, and the whole process repeats — this is the "autoregressive" loop

---

## Slide 8: The KV Cache — Making It Practical

- Naively, generating each new token would require reprocessing the entire sequence from scratch — this gets very expensive as the output grows
- The KV cache stores the Key and Value vectors from all previous tokens in each attention layer, so they don't need to be recomputed
- When generating token #100, only the *new* token needs to go through the full computation — previous tokens' attention contributions are looked up from cache
- This is a classic time-space tradeoff: we use more memory to dramatically reduce computation time
- The KV cache is a major reason LLM inference is memory-bound rather than compute-bound — long sequences need gigabytes of cache
- This is also why long-context models are challenging: the cache grows linearly with sequence length, putting pressure on GPU memory

---

## Slide 9: Prefill vs. Decode — The Two Phases of Inference

- **Prefill phase**: The model processes your entire input prompt in one parallel batch — this is compute-heavy but fast because all tokens are processed simultaneously
- **Decode phase**: The model generates output tokens one at a time in a sequential loop — each token depends on the one before it
- Prefill is like reading a whole page at once; decode is like writing one word at a time — fundamentally different performance profiles
- Time-to-first-token (TTFT) is dominated by prefill; tokens-per-second after that is determined by decode speed
- This is why you see a pause before the response starts streaming, then a steady flow of tokens
- Understanding this split is key to optimizing inference — different hardware and batching strategies target each phase differently

---

## Slide 10: Putting It All Together

- The full pipeline: tokenize → embed → pass through N transformer blocks (attention + FFN each) → project to vocabulary → sample → repeat
- A single forward pass through a large model involves billions of multiply-add operations, yet produces just one token
- A typical response of 200 tokens means 200 sequential forward passes through the entire model
- The magic isn't in any single component — it's in the scale: enough parameters, enough training data, and enough layers to capture the patterns of language
- Key intuition: the model doesn't "understand" in a human sense — it has learned incredibly sophisticated pattern matching over vast amounts of text
- Current research focuses on making this process faster (speculative decoding, quantization, better architectures) while preserving quality
