# %%
# load the model encoder data
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.distributions as dist
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from torchtext.data.utils import get_tokenizer
import torch
import torch.nn as nn
import numpy as np
import embedding
from embedding import d_model

num_heads = 8  # number of attention heads
d_ff = 128  # dimension of feedforward network
num_layers = 6  # ff network layers

with open("chapter1.txt", "r", encoding="utf-8") as f:
    text = f.read()
vectors, vocabulary = embedding.get_vectors(text)

encoder_output = torch.load("encoded_vector.pth", weights_only=False)


# %%
decoder_layer = nn.TransformerDecoderLayer(
    d_model=d_model, nhead=num_heads, batch_first=True
)
decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)


def greedy_decode(
    encoder_output,
    tgt_embeddings,
    decoder,
    start_token_id,
    d_model,
    max_length,
    vocab_size,
):
    final_linear = nn.Linear(d_model, vocab_size)
    tgt_tokens = torch.full((1, 1), start_token_id)  # initialize with <SOS>
    generated = [tgt_tokens]  # store token indices step-by-step

    for step in range(max_length):
        tgt_embedded = tgt_embeddings(tgt_tokens)  # [batch_size, cur_length, d_model]
        tgt_mask = torch.nn.Transformer.generate_square_subsequent_mask(
            tgt_embedded.shape[1]
        )
        out = decoder(tgt=tgt_embedded, memory=encoder_output, tgt_mask=tgt_mask)

        # Project to vocab and get next token
        logits = final_linear(
            out[:, -1, :]
        )  # [batch_size, vocab_size]; use last token's output
        next_token = torch.argmax(logits, dim=-1, keepdim=True)  # [batch_size, 1]

        tgt_tokens = torch.cat(
            [tgt_tokens, next_token], dim=1
        )  # append new token to the input
        generated.append(next_token)

        # You may want to stop if '<EOS>' is generated for all batch samples
        if next_token.item() == vocabulary["<EOS>"]:
            break

    return tgt_tokens


# %%
vocab_size = vocabulary.__len__()
tgt_embeddings = nn.Embedding(vocab_size, d_model)


target_string = "<SOS> aunt em was <EOS>"
target_tokens = embedding.tokenize(target_string)
token_ids = [vocabulary[token] for token in target_tokens]
t = torch.tensor(token_ids).unsqueeze(0)

emb = nn.Embedding(vocab_size, embedding_dim=d_model)
tgt_embedding = emb(t)


start_token_id = vocabulary["<SOS>"]
result = greedy_decode(
    encoder_output,
    tgt_embeddings,
    decoder,
    start_token_id,
    d_model,
    max_length=100,
    vocab_size=vocab_size,
)


print(target_string)
for tokens in result[0:]:
    for token in tokens:
        print(vocabulary.itos[token.item()], end=" ")
