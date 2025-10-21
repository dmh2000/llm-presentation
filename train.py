# %%
# Training loop and loss function for LLM
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import embedding
from encoder import StackedTransformerEncoder, PositionalEncoding


# %%
# Dataset class for text data
class TextDataset(Dataset):
    def __init__(self, text, vocabulary, seq_length=50):
        self.tokens = embedding.tokenize(text)
        self.token_ids = [vocabulary[token] for token in self.tokens]
        self.seq_length = seq_length
        self.vocabulary = vocabulary

    def __len__(self):
        return len(self.token_ids) - self.seq_length

    def __getitem__(self, idx):
        src = torch.tensor(self.token_ids[idx : idx + self.seq_length])
        tgt_input = torch.tensor(self.token_ids[idx : idx + self.seq_length])
        tgt_output = torch.tensor(self.token_ids[idx + 1 : idx + self.seq_length + 1])
        return src, tgt_input, tgt_output


# %%
# Complete transformer model combining encoder-decoder
class TransformerLM(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, d_ff, num_layers):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        self.encoder = StackedTransformerEncoder(d_model, num_heads, d_ff, num_layers)

        decoder_layer = nn.TransformerDecoderLayer(d_model, num_heads, batch_first=True)
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers)
        self.output_projection = nn.Linear(d_model, vocab_size)

    def forward(self, src, tgt):
        # Encode
        src_emb = self.pos_encoder(self.embedding(src))
        memory = self.encoder(src_emb)

        # Decode
        tgt_emb = self.pos_encoder(self.embedding(tgt))
        tgt_mask = nn.Transformer.generate_square_subsequent_mask(tgt.size(1))
        output = self.decoder(tgt_emb, memory, tgt_mask=tgt_mask)

        return self.output_projection(output)


# %%
# Training function
def train_model(model, dataloader, num_epochs=10, learning_rate=0.0001):
    # Use unknown token as padding token if available, otherwise use 0
    pad_idx = 0  # Default padding index
    criterion = nn.CrossEntropyLoss(ignore_index=pad_idx)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    model.train()
    for epoch in range(num_epochs):
        total_loss = 0
        num_batches = 0

        for batch_idx, (src, tgt_input, tgt_output) in enumerate(dataloader):
            optimizer.zero_grad()

            # Forward pass
            logits = model(src, tgt_input)

            # Reshape for loss calculation
            loss = criterion(
                logits.reshape(-1, model.vocab_size), tgt_output.reshape(-1)
            )

            # Backward pass
            loss.backward()

            # Gradient clipping to prevent exploding gradients
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

            if batch_idx % 100 == 0:
                print(f"Epoch {epoch+1}, Batch {batch_idx}, Loss: {loss.item():.4f}")

        avg_loss = total_loss / num_batches
        print(f"Epoch {epoch+1} completed, Average Loss: {avg_loss:.4f}")

        # Save model checkpoint
        if (epoch + 1) % 5 == 0:
            torch.save(model.state_dict(), f"model_checkpoint_epoch_{epoch+1}.pth")


# %%
# Main training setup
if __name__ == "__main__":
    # Load data
    with open("chapter1.txt", "r", encoding="utf-8") as f:
        text = f.read()

    vectors, vocabulary = embedding.get_vectors(text)
    vocab_size = len(vocabulary)

    # Model parameters
    d_model = embedding.d_model
    num_heads = 8
    d_ff = 128
    num_layers = 4
    seq_length = 32
    batch_size = 16

    # Create dataset and dataloader
    dataset = TextDataset(text, vocabulary, seq_length=seq_length)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    model = TransformerLM(vocab_size, d_model, num_heads, d_ff, num_layers)

    print(
        f"Model initialized with {sum(p.numel() for p in model.parameters())} parameters"
    )
    print(f"Training on {len(dataset)} sequences")

    # Train the model
    train_model(model, dataloader, num_epochs=60, learning_rate=0.0001)

    # Save final model
    torch.save(model.state_dict(), "final_model.pth")
    print("Training completed and model saved!")
