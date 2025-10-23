# %% [markdown]
# project gutenberg wizard of oz

# %%
from embedding import d_model

# %%
import embedding

with open("chapter1.txt", "r", encoding="utf-8") as f:
    text = f.read()

vectors, vocabulary = embedding.get_vectors(text)

# %% [markdown]
#

# %%
import math
import torch
import torch.nn as nn


# add positional encoding using sin/cos altorihms
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # Shape: (1, max_len, d_model)
        self.register_buffer("pe", pe)

    def forward(self, x):
        # x shape: (batch_size, seq_len, d_model)
        seq_len = x.size(1)
        x = x + self.pe[:, :seq_len]
        return x


# %%
# add positional encoding in batch mode
batch_size, seq_len, d_model = 64, 32, d_model
size = vectors.shape[0]

# add batch dimension for compatibility with positional encoding
vectors = vectors.unsqueeze(0)

# add positional encoding
pos_encoder = PositionalEncoding(d_model, max_len=size)
x = pos_encoder(vectors)


# %%
import torch.nn.functional as F


# ENCODING


class TransformerBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        # one pass of self-attention
        self.attn = nn.MultiheadAttention(
            d_model, num_heads, dropout=dropout, batch_first=True
        )
        # normalized feedforward network
        self.norm1 = nn.LayerNorm(d_model)

        # execute the feedforward network  in sequence
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),  # linear transformation input
            nn.ReLU(),  # Rectified Linear Unit
            nn.Dropout(dropout),  # Dropout (to prevent overfitting)
            nn.Linear(d_ff, d_model),  # linear transformation output
        )
        self.norm2 = nn.LayerNorm(d_model)

    def forward(self, x, mask=None):
        # Multi-head attention + residual + norm
        attn_out, _ = self.attn(x, x, x, key_padding_mask=mask)
        x = self.norm1(x + attn_out)
        # Feedforward network + residual + norm
        ff_out = self.ff(x)
        x = self.norm2(x + ff_out)
        return x


class StackedTransformerEncoder(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, num_layers, dropout=0.1):
        super().__init__()
        self.layers = nn.ModuleList(
            [
                TransformerBlock(d_model, num_heads, d_ff, dropout)
                for _ in range(num_layers)
            ]
        )

    def forward(self, x, mask=None):
        for layer in self.layers:
            x = layer(x, mask)
        return x


# %%
num_heads = 8  # number of attention heads
d_ff = 128  # dimension of feedforward network
num_layers = 4  # number of transformer blocks

mask = None  # can be a boolean mask tensor with shape [batch_size, seq_len]
encoder = StackedTransformerEncoder(d_model, num_heads, d_ff, num_layers)
encoded = encoder(x, mask)

# output is the updated  token vectors


# %%
# save the model
torch.save(encoded, "encoded_vector.pth")
