import os
from google import genai

if "GOOGLE_API_KEY" not in os.environ:
    print("GOOGLE_API_KEY not set")
    exit(1)

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

print("Listing models...")
for model in client.models.list(config={'page_size': 100}):
    print(f"Model: {model.name}")
