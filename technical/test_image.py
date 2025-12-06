import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

models_to_test = [
    "nano-banana-pro-preview",
    "gemini-3-pro-image-preview",
    "imagen-4.0-generate-001",
    "gemini-2.5-flash-image"
]

prompt = "A small red circle."

for model in models_to_test:
    print(f"Testing model: {model}")
    try:
        response = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1)
        )
        print(f"Success with {model}!")
        # If successful, we can break or just log it.
    except Exception as e:
        print(f"Failed with {model}: {e}")
