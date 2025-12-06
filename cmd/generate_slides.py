import argparse
import os
import re
import sys
import time
from google import genai
from google.genai import types

# Configuration
MODEL_ID = "gemini-2.5-flash-image"  # Fallback to Imagen 4 as Nano Banana Pro (preview) was unavailable
OUTPUT_DIR = "slides"
ASPECT_RATIO = "16:9"


def parse_markdown(file_path):
    """Parses the markdown file into sections with title and content."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)

    sections = []
    current_title = ""
    current_content = []

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("##"):
            # New section found
            if current_title:
                sections.append(
                    {
                        "title": current_title,
                        "content": "\n".join(current_content).strip(),
                    }
                )
            # Remove '#' characters and whitespace
            current_title = stripped_line.lstrip("#").strip()
            current_content = []
        elif stripped_line == "---":
            continue
        else:
            current_content.append(line)

    # Add the last section
    if current_title:
        sections.append(
            {"title": current_title, "content": "\n".join(current_content).strip()}
        )

    return sections


def generate_slide(client, section, index):
    """Generates a slide image for a given section."""
    title = section["title"]
    content = section["content"]

    # Construct a prompt that asks for a slide design
    prompt = (
        f"Create a professional presentation slide.\n"
        f"Title: {title}\n"
        f"Content to summarize and display on slide: {content}\n"
        f"Design Requirements: Light color scheme with colorful graphics that reflect the content. "
        f"The graphics should be technical and relevant (e.g., representing tokens, neural networks, attention mechanisms). "
        f"Ensure text is legible, high-contrast, and organized (use bullet points for the content)."
        f"Ensure the slide is formatted for {ASPECT_RATIO} aspect ratio."
    )

    print(f"Generating slide {index + 1}: {title}...")

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[prompt],  # Pass the prompt as a list prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio=ASPECT_RATIO,
                    # image_size="2K"
                ),
            ),
        )

        safe_title = (
            re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_").lower()
        )
        filename = f"slide_{index + 1:02d}_{safe_title}.png"
        save_path = os.path.join(OUTPUT_DIR, filename)

        for part in response.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = part.as_image()
                image.save(save_path)
                print(f"Saved: {save_path}")
        else:
            print(f"No image generated for section: {title}")

    except Exception as e:
        print(f"Error generating slide for '{title}': {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate slides from a markdown file.")
    parser.add_argument("input_file", help="Path to the input markdown file")
    args = parser.parse_args()

    if "GOOGLE_API_KEY" not in os.environ:
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    sections = parse_markdown(args.input_file)

    if not sections:
        print("No sections found in the markdown file.")
        return

    print(f"Found {len(sections)} sections. Starting generation...")

    for i, section in enumerate(sections):
        generate_slide(client, section, i)
        # Sleep briefly to avoid hitting rate limits too aggressively, if any
        time.sleep(1)

    print("Done.")


if __name__ == "__main__":
    main()
