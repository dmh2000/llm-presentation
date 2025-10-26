#!/usr/bin/env python3
"""
Convert slide notes from markdown to MP3 audio files.

This script reads a markdown notes file and converts each slide section
to a separate MP3 file using Google Gemini TTS.
"""

import argparse
import os
import sys
from audio_utils import speak


def parse_notes_sections(notes_file):
    """
    Parse the notes markdown file and extract text for each slide section.

    Args:
        notes_file: Path to the markdown notes file

    Returns:
        list: List of text strings, one for each slide section
    """
    with open(notes_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by slide separator (triple hyphens)
    sections = content.split('---')

    # Remove empty sections
    sections = [s.strip() for s in sections if s.strip()]

    parsed_sections = []
    for section in sections:
        if not section.strip():
            continue

        lines = section.strip().split('\n')
        text_lines = []

        for line in lines:
            # Skip triple hyphens (in case they appear within sections)
            if line.strip() == '---':
                continue
            # Skip the main title (first section header)
            elif line.startswith('# How Language AI Works'):
                continue
            # Skip individual slide titles (## Slide N:)
            elif line.startswith('## Slide'):
                continue
            # Keep all other content
            else:
                text_lines.append(line)

        # Join text lines and clean up
        section_text = '\n'.join(text_lines).strip()

        # Only add non-empty sections
        if section_text:
            parsed_sections.append(section_text)

    return parsed_sections


def convert_notes_to_audio(notes_file, voice="Sadaltager", output_dir="."):
    """
    Convert each section of the notes file to a separate MP3 audio file.

    Args:
        notes_file: Path to the markdown notes file
        voice: Voice name to use for TTS (default: "Sadaltager")
        output_dir: Directory to save the output MP3 files (default: current directory)
    """
    print(f"Reading {notes_file}...")
    sections = parse_notes_sections(notes_file)
    print(f"Found {len(sections)} sections to convert")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Convert each section to audio
    for i, text in enumerate(sections, start=1):
        print(f"\nConverting section {i}/{len(sections)}...")
        print(f"Text length: {len(text)} characters")

        # Generate output filename (without .mp3 extension, speak() adds it)
        output_file = os.path.join(output_dir, f"audio-{i}")

        try:
            # Convert text to speech
            result = speak(voice, text, output_file)
            print(f"Created: {result}")
        except Exception as e:
            print(f"Error converting section {i}: {e}", file=sys.stderr)
            continue

    print(f"\nConversion complete! Generated {len(sections)} audio files.")


def main():
    """Main entry point for the script."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Convert slide notes from markdown to MP3 audio files."
    )
    parser.add_argument(
        "notes_file",
        help="Path to the markdown notes file to convert"
    )
    parser.add_argument(
        "-v", "--voice",
        default="Sadaltager",
        help="Voice name to use for TTS (default: Sadaltager)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Directory to save the output MP3 files (default: current directory)"
    )

    args = parser.parse_args()

    # Check if file exists
    if not os.path.exists(args.notes_file):
        print(f"Error: File '{args.notes_file}' not found", file=sys.stderr)
        sys.exit(1)

    # Convert notes to audio files
    convert_notes_to_audio(args.notes_file, voice=args.voice, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
