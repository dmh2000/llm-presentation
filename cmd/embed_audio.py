#!/usr/bin/env python3
"""
Embed MP3 audio files into PowerPoint slides programmatically.

This script takes a PPTX file and a directory of MP3 files, then embeds
each MP3 file into the corresponding slide. The PPTX format is essentially
a ZIP file containing XML files, so we manipulate the structure directly.

Usage:
    python embed_audio.py <input.pptx> <audio_dir> [output.pptx]

Example:
    python embed_audio.py presentation.pptx ./audio/ presentation_with_audio.pptx

Audio files should be named: audio-1.mp3, audio-2.mp3, etc. (matching slide numbers)
"""

import os
import sys
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse


# XML namespaces used in PPTX files
NAMESPACES = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p14': 'http://schemas.microsoft.com/office/powerpoint/2010/main',
}

# Relationship types for audio embedding
REL_AUDIO = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio"
REL_MEDIA = "http://schemas.microsoft.com/office/2007/relationships/media"


def register_namespaces():
    """Register XML namespaces to preserve prefixes when writing XML."""
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)
    # Register additional namespaces commonly found in PPTX files
    ET.register_namespace('', 'http://schemas.openxmlformats.org/package/2006/relationships')


def extract_pptx(pptx_path, extract_dir):
    """
    Extract PPTX file to a directory.

    Args:
        pptx_path: Path to the PPTX file
        extract_dir: Directory to extract files to
    """
    print(f"Extracting {pptx_path}...")
    with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted to {extract_dir}")


def package_pptx(extract_dir, output_pptx):
    """
    Package a directory back into a PPTX file.

    Args:
        extract_dir: Directory containing extracted PPTX files
        output_pptx: Path for the output PPTX file
    """
    print(f"Packaging {output_pptx}...")
    with zipfile.ZipFile(output_pptx, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, extract_dir)
                zip_ref.write(file_path, arcname)
    print(f"Created {output_pptx}")


def get_next_media_number(media_dir):
    """
    Get the next available media file number.

    Args:
        media_dir: Path to the ppt/media directory

    Returns:
        int: Next available media number
    """
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
        return 1

    media_files = [f for f in os.listdir(media_dir) if f.startswith('media') and f.endswith('.mp3')]
    if not media_files:
        return 1

    # Extract numbers from filenames like "media1.mp3"
    numbers = []
    for f in media_files:
        try:
            num = int(f.replace('media', '').replace('.mp3', ''))
            numbers.append(num)
        except ValueError:
            continue

    return max(numbers) + 1 if numbers else 1


def get_next_rid(rels_root):
    """
    Get the next available relationship ID.

    Args:
        rels_root: XML root element of a .rels file

    Returns:
        str: Next available rId (e.g., "rId5")
    """
    rels = rels_root.findall('.//Relationship', namespaces={'': 'http://schemas.openxmlformats.org/package/2006/relationships'})

    if not rels:
        return "rId1"

    # Extract numbers from rId attributes
    numbers = []
    for rel in rels:
        rid = rel.get('Id', '')
        if rid.startswith('rId'):
            try:
                num = int(rid.replace('rId', ''))
                numbers.append(num)
            except ValueError:
                continue

    return f"rId{max(numbers) + 1}" if numbers else "rId1"


def add_audio_to_slide(extract_dir, slide_num, audio_file):
    """
    Add audio file to a specific slide.

    Args:
        extract_dir: Directory containing extracted PPTX files
        slide_num: Slide number (1-indexed)
        audio_file: Path to the MP3 audio file to embed

    Returns:
        bool: True if successful, False otherwise
    """
    slide_path = os.path.join(extract_dir, 'ppt', 'slides', f'slide{slide_num}.xml')
    rels_path = os.path.join(extract_dir, 'ppt', 'slides', '_rels', f'slide{slide_num}.xml.rels')
    media_dir = os.path.join(extract_dir, 'ppt', 'media')

    # Check if slide exists
    if not os.path.exists(slide_path):
        print(f"Warning: Slide {slide_num} does not exist, skipping...")
        return False

    # Check if audio file exists
    if not os.path.exists(audio_file):
        print(f"Warning: Audio file {audio_file} not found, skipping slide {slide_num}...")
        return False

    # Create media directory if it doesn't exist
    os.makedirs(media_dir, exist_ok=True)

    # Get next available media number
    media_num = get_next_media_number(media_dir)
    media_filename = f"media{media_num}.mp3"
    media_dest = os.path.join(media_dir, media_filename)

    # Copy audio file to media directory
    shutil.copy2(audio_file, media_dest)
    print(f"  Copied {os.path.basename(audio_file)} to {media_filename}")

    # Create or update relationships file
    os.makedirs(os.path.dirname(rels_path), exist_ok=True)

    if os.path.exists(rels_path):
        # Parse existing relationships
        tree = ET.parse(rels_path)
        rels_root = tree.getroot()
    else:
        # Create new relationships file
        rels_root = ET.Element('Relationships', xmlns='http://schemas.openxmlformats.org/package/2006/relationships')
        tree = ET.ElementTree(rels_root)

    # Get next available rId
    audio_rid = get_next_rid(rels_root)
    media_rid = get_next_rid(rels_root)

    # Ensure they're different
    if audio_rid == media_rid:
        num = int(media_rid.replace('rId', ''))
        media_rid = f"rId{num + 1}"

    # Add audio relationship (OpenXML standard)
    audio_rel = ET.SubElement(rels_root, 'Relationship')
    audio_rel.set('Id', audio_rid)
    audio_rel.set('Type', REL_AUDIO)
    audio_rel.set('Target', f"../media/{media_filename}")

    # Add media relationship (Microsoft Office extension)
    media_rel = ET.SubElement(rels_root, 'Relationship')
    media_rel.set('Id', media_rid)
    media_rel.set('Type', REL_MEDIA)
    media_rel.set('Target', f"../media/{media_filename}")

    # Write relationships file
    tree.write(rels_path, encoding='UTF-8', xml_declaration=True)
    print(f"  Updated relationships: {audio_rid} (audio), {media_rid} (media)")

    # Note: We're not adding visual audio shapes to the slide XML
    # The audio will be embedded but not visible. To make it visible,
    # you would need to add a <p:pic> element to the slide XML.

    return True


def ensure_content_type(extract_dir):
    """
    Ensure MP3 content type is registered in [Content_Types].xml.

    Args:
        extract_dir: Directory containing extracted PPTX files
    """
    content_types_path = os.path.join(extract_dir, '[Content_Types].xml')

    if not os.path.exists(content_types_path):
        print("Warning: [Content_Types].xml not found")
        return

    # Parse content types
    tree = ET.parse(content_types_path)
    root = tree.getroot()

    # Check if MP3 type already exists
    ns = {'ct': 'http://schemas.openxmlformats.org/package/2006/content-types'}
    mp3_defaults = root.findall('.//ct:Default[@Extension="mp3"]', namespaces=ns)

    if not mp3_defaults:
        # Add MP3 default content type
        default = ET.SubElement(root, 'Default')
        default.set('Extension', 'mp3')
        default.set('ContentType', 'audio/mpeg')
        tree.write(content_types_path, encoding='UTF-8', xml_declaration=True)
        print("Added MP3 content type to [Content_Types].xml")
    else:
        print("MP3 content type already registered")


def embed_audio_files(pptx_path, audio_dir, output_pptx=None):
    """
    Embed MP3 audio files into PowerPoint slides.

    Args:
        pptx_path: Path to input PPTX file
        audio_dir: Directory containing MP3 files (named audio-1.mp3, audio-2.mp3, etc.)
        output_pptx: Path to output PPTX file (default: input_with_audio.pptx)
    """
    # Set default output path
    if output_pptx is None:
        base = os.path.splitext(pptx_path)[0]
        output_pptx = f"{base}_with_audio.pptx"

    # Create temporary extraction directory
    extract_dir = "temp_pptx_extract"

    try:
        # Extract PPTX
        extract_pptx(pptx_path, extract_dir)

        # Ensure MP3 content type is registered
        ensure_content_type(extract_dir)

        # Find all audio files in the directory
        audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.mp3')])
        print(f"\nFound {len(audio_files)} audio files in {audio_dir}")

        # Process each audio file
        success_count = 0
        for audio_file in audio_files:
            # Extract slide number from filename (e.g., "audio-1.mp3" -> 1)
            try:
                # Support both "audio-1.mp3" and "audio1.mp3" formats
                basename = os.path.splitext(audio_file)[0]
                slide_num = int(basename.replace('audio-', '').replace('audio', ''))
            except ValueError:
                print(f"Warning: Could not extract slide number from {audio_file}, skipping...")
                continue

            audio_path = os.path.join(audio_dir, audio_file)
            print(f"\nProcessing slide {slide_num}: {audio_file}")

            if add_audio_to_slide(extract_dir, slide_num, audio_path):
                success_count += 1

        print(f"\n✓ Successfully embedded {success_count} audio files")

        # Package back to PPTX
        package_pptx(extract_dir, output_pptx)
        print(f"\n✓ Created {output_pptx}")

    finally:
        # Clean up temporary directory
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
            print(f"Cleaned up temporary files")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Embed MP3 audio files into PowerPoint slides.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python embed_audio.py presentation.pptx ./audio/
  python embed_audio.py input.pptx ./audio/ output.pptx

Audio files should be named: audio-1.mp3, audio-2.mp3, etc. (matching slide numbers)
        """
    )

    parser.add_argument(
        'pptx_file',
        help='Input PowerPoint file (.pptx)'
    )
    parser.add_argument(
        'audio_dir',
        help='Directory containing MP3 audio files'
    )
    parser.add_argument(
        'output_file',
        nargs='?',
        default=None,
        help='Output PowerPoint file (default: input_with_audio.pptx)'
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.pptx_file):
        print(f"Error: PPTX file '{args.pptx_file}' not found", file=sys.stderr)
        sys.exit(1)

    # Validate audio directory
    if not os.path.isdir(args.audio_dir):
        print(f"Error: Audio directory '{args.audio_dir}' not found", file=sys.stderr)
        sys.exit(1)

    # Register XML namespaces
    register_namespaces()

    # Embed audio files
    embed_audio_files(args.pptx_file, args.audio_dir, args.output_file)


if __name__ == '__main__':
    main()
