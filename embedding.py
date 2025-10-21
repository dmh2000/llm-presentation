# %%
d_model = 128

with open("chapter1.txt", "r", encoding="utf-8") as f:
    text = f.read()


# %%
# tokenize the input text
from torchtext.data.utils import get_tokenizer


def tokenize(text):
    tokenizer = get_tokenizer("basic_english")
    tokens = tokenizer(text)
    return tokens


# %%
# create the vocabulary from the tokens
from collections import Counter
from torchtext.vocab import Vocab


def vocabulary_from_tokens(tokens):
    counter = Counter(tokens)
    vocab = Vocab(counter, min_freq=1)
    return vocab


# %%
# create the embedding layer
import torch
import torch.nn as nn


def get_vectors(text):
    tokens = tokenize(text)
    vocabulary = vocabulary_from_tokens(tokens)

    # initialize vectors with random values
    embedding = nn.Embedding(len(vocabulary), embedding_dim=d_model)
    input_indices = torch.IntTensor([vocabulary[token] for token in tokens])
    vectors = embedding(input_indices)
    return vectors, vocabulary


# %%
