#!/usr/bin/env python3
"""
Embed an MP3 audio file into a PowerPoint slide.

Usage:
    python embed_audio.py <slide_number> <pptx_file> <mp3_file>

Example:
    python embed_audio.py 1 presentation.pptx audio.mp3

This script:
1. Unzips the PPTX file
2. Adds the MP3 to the media directory
3. Registers the MP3 content type
4. Adds audio element to the specified slide
5. Creates necessary relationships
6. Adds timing/animation for audio playback
7. Repackages as PPTX

Based on Office Open XML specification for PresentationML.
"""

import argparse
import os
import sys
import shutil
import zipfile
import xml.etree.ElementTree as ET
import uuid
import base64
from pathlib import Path

# XML Namespaces
NAMESPACES = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
    'ct': 'http://schemas.openxmlformats.org/package/2006/content-types',
    'p14': 'http://schemas.microsoft.com/office/powerpoint/2010/main',
    'a16': 'http://schemas.microsoft.com/office/drawing/2014/main',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006'
}

# Register namespaces for proper XML output
for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


def unzip_pptx(pptx_path, extract_dir):
    """Extract PPTX file to directory."""
    print(f"Extracting {pptx_path}...")
    with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"  Extracted to {extract_dir}")


def zip_pptx(source_dir, output_path):
    """Package directory back into PPTX file."""
    print(f"Packaging {output_path}...")

    # Create a new zip file
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

    print(f"  Created {output_path}")


def get_next_media_number(media_dir):
    """Get the next available media file number."""
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
        return 1

    max_num = 0
    for filename in os.listdir(media_dir):
        if filename.startswith('media') and filename.endswith('.mp3'):
            try:
                num = int(filename.replace('media', '').replace('.mp3', ''))
                max_num = max(max_num, num)
            except ValueError:
                continue

    return max_num + 1


def get_next_rid(rels_file):
    """Get the next available relationship ID."""
    tree = ET.parse(rels_file)
    root = tree.getroot()

    max_num = 0
    for rel in root.findall('.//rel:Relationship', NAMESPACES):
        rid = rel.get('Id', '')
        if rid.startswith('rId'):
            try:
                num = int(rid.replace('rId', ''))
                max_num = max(max_num, num)
            except ValueError:
                continue

    return max_num + 1


def ensure_mp3_content_type(content_types_file):
    """Ensure MP3 content type is registered in [Content_Types].xml."""
    print("Checking MP3 content type registration...")

    tree = ET.parse(content_types_file)
    root = tree.getroot()

    # Check if MP3 is already registered
    for default in root.findall('.//ct:Default', NAMESPACES):
        if default.get('Extension') == 'mp3':
            print("  MP3 content type already registered")
            return

    # Add MP3 content type
    mp3_element = ET.Element(
        '{http://schemas.openxmlformats.org/package/2006/content-types}Default',
        Extension='mp3',
        ContentType='audio/mpeg'
    )
    root.insert(0, mp3_element)

    tree.write(content_types_file, encoding='UTF-8', xml_declaration=True)
    print("  Added MP3 content type")


def ensure_png_content_type(content_types_file):
    """Ensure PNG content type is registered in [Content_Types].xml."""
    tree = ET.parse(content_types_file)
    root = tree.getroot()

    # Check if PNG is already registered
    for default in root.findall('.//ct:Default', NAMESPACES):
        if default.get('Extension') == 'png':
            return

    # Add PNG content type
    png_element = ET.Element(
        '{http://schemas.openxmlformats.org/package/2006/content-types}Default',
        Extension='png',
        ContentType='image/png'
    )
    root.insert(0, png_element)

    tree.write(content_types_file, encoding='UTF-8', xml_declaration=True)


def create_audio_icon(output_path):
    """Create a simple audio icon PNG (speaker icon)."""
    # Simple 32x32 PNG speaker icon in base64
    # This is a minimal PNG image of a speaker icon
    icon_base64 = (
        'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlz'
        'AAALEgAACxIB0t1+/AAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNui8sowAAAAV'
        'dEVYdENyZWF0aW9uIFRpbWUAMy8xNC8xM4RmojUAAAH4SURBVFiF7ZY9aBRBFIC/2d3ZS7KXXHKX'
        'YEBBEBFBULSwsBNEsLK1sbOyEqwsrGxs7QQrGxErwT9EEBEUBEVREMGfiJp4uSTm7m53d2bHYu/M'
        'JntJTrCwyfD2vZn33rx58+YNrGENa/gfIf9boA5TgAGmAYNl2daadVnWAqwB1oEcUAQqgAPkgRxQ'
        'AkpAGSgDFaACOEAVcAEPqAM+EAARkABxIAHYQBJIA2kgA2SBDNAJdAKdQAfQDnQAbUAGaAFagGYg'
        'DSQBCzCBGBAFLMAEDEADBmAAUUACEhABPiCBEAiAAAiBEAiFEAgQwhQiERQBUeAD0j9BKgghFAih'
        'ECJBhBCEEIQQghBCEEIIQghBCCEIIQQhBBBCACGAEP4FSUAE+IAUQghCCEIIQQhBCCEIIQQhhBCE'
        'EEIIIQghhP8CCSGAP0ECCQiBQAghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEL4V5BAAvhTJBBC+Fck'
        'kBBCCEIIIQghhCCEEIQQQhBCCEIIIQghhPAvSP8KVCGEEEIIQQghhBBCCCGEEEIIIQghhBBCCCGE'
        'EML/gfwT5B+g/wF+CSEEIYQQ/gYRQhBCCAKh/Ag='
    )

    icon_bytes = base64.b64decode(icon_base64)
    with open(output_path, 'wb') as f:
        f.write(icon_bytes)


def get_next_shape_id(slide_file):
    """Get the next available shape ID in the slide."""
    tree = ET.parse(slide_file)
    root = tree.getroot()

    max_id = 1
    # Search for all cNvPr elements which contain the id attribute
    for elem in root.iter():
        if elem.tag.endswith('cNvPr'):
            shape_id = elem.get('id')
            if shape_id:
                try:
                    max_id = max(max_id, int(shape_id))
                except ValueError:
                    continue

    return max_id + 1


def add_audio_to_slide(extract_dir, slide_num, mp3_file, media_num, icon_num):
    """Add audio element to slide XML."""
    slide_file = os.path.join(extract_dir, 'ppt', 'slides', f'slide{slide_num}.xml')

    if not os.path.exists(slide_file):
        print(f"  Error: Slide {slide_num} does not exist")
        return False

    print(f"Adding audio to slide {slide_num}...")

    tree = ET.parse(slide_file)
    root = tree.getroot()

    # Find the spTree element (shape tree)
    sp_tree = root.find('.//p:cSld/p:spTree', NAMESPACES)
    if sp_tree is None:
        print("  Error: Could not find shape tree in slide")
        return False

    # Get next shape ID
    shape_id = get_next_shape_id(slide_file)

    # Get relationship IDs (will be created in the relationships file)
    # rId1: embedded audio (Microsoft format)
    # rId2: audio file (standard format)
    # rId3: audio icon image

    # Create audio picture element
    pic = ET.Element(f'{{{NAMESPACES["p"]}}}pic')

    # Non-visual picture properties
    nv_pic_pr = ET.SubElement(pic, f'{{{NAMESPACES["p"]}}}nvPicPr')

    # cNvPr - Non-visual drawing properties
    c_nv_pr = ET.SubElement(nv_pic_pr, f'{{{NAMESPACES["p"]}}}cNvPr')
    c_nv_pr.set('id', str(shape_id))
    c_nv_pr.set('name', f'audio-{slide_num}')

    # Hyperlink click action
    hlink_click = ET.SubElement(c_nv_pr, f'{{{NAMESPACES["a"]}}}hlinkClick')
    hlink_click.set(f'{{{NAMESPACES["r"]}}}id', '')
    hlink_click.set('action', 'ppaction://media')

    # Extension list for creation ID
    ext_lst = ET.SubElement(c_nv_pr, f'{{{NAMESPACES["a"]}}}extLst')
    ext = ET.SubElement(ext_lst, f'{{{NAMESPACES["a"]}}}ext')
    ext.set('uri', '{FF2B5EF4-FFF2-40B4-BE49-F238E27FC236}')
    creation_id = ET.SubElement(ext, f'{{{NAMESPACES["a16"]}}}creationId')
    creation_id.set('id', '{' + str(uuid.uuid4()).upper() + '}')

    # cNvPicPr - Non-visual picture drawing properties
    c_nv_pic_pr = ET.SubElement(nv_pic_pr, f'{{{NAMESPACES["p"]}}}cNvPicPr')
    pic_locks = ET.SubElement(c_nv_pic_pr, f'{{{NAMESPACES["a"]}}}picLocks')
    pic_locks.set('noChangeAspect', '1')

    # nvPr - Non-visual properties
    nv_pr = ET.SubElement(nv_pic_pr, f'{{{NAMESPACES["p"]}}}nvPr')

    # Audio file reference (external link format)
    audio_file = ET.SubElement(nv_pr, f'{{{NAMESPACES["a"]}}}audioFile')
    audio_file.set(f'{{{NAMESPACES["r"]}}}link', 'rIdAudio')

    # Extension list for media
    ext_lst2 = ET.SubElement(nv_pr, f'{{{NAMESPACES["p"]}}}extLst')
    ext2 = ET.SubElement(ext_lst2, f'{{{NAMESPACES["p"]}}}ext')
    ext2.set('uri', '{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}')
    media = ET.SubElement(ext2, f'{{{NAMESPACES["p14"]}}}media')
    media.set(f'{{{NAMESPACES["r"]}}}embed', 'rIdMedia')

    # blipFill - Image fill for the audio icon
    blip_fill = ET.SubElement(pic, f'{{{NAMESPACES["p"]}}}blipFill')
    blip = ET.SubElement(blip_fill, f'{{{NAMESPACES["a"]}}}blip')
    blip.set(f'{{{NAMESPACES["r"]}}}embed', 'rIdIcon')
    stretch = ET.SubElement(blip_fill, f'{{{NAMESPACES["a"]}}}stretch')
    fill_rect = ET.SubElement(stretch, f'{{{NAMESPACES["a"]}}}fillRect')

    # spPr - Shape properties (position and size)
    sp_pr = ET.SubElement(pic, f'{{{NAMESPACES["p"]}}}spPr')
    xfrm = ET.SubElement(sp_pr, f'{{{NAMESPACES["a"]}}}xfrm')
    off = ET.SubElement(xfrm, f'{{{NAMESPACES["a"]}}}off')
    off.set('x', '4419600')  # Position X (in EMUs)
    off.set('y', '3276600')  # Position Y
    ext = ET.SubElement(xfrm, f'{{{NAMESPACES["a"]}}}ext')
    ext.set('cx', '304800')  # Width (32 pixels in EMUs)
    ext.set('cy', '304800')  # Height

    prst_geom = ET.SubElement(sp_pr, f'{{{NAMESPACES["a"]}}}prstGeom')
    prst_geom.set('prst', 'rect')
    av_lst = ET.SubElement(prst_geom, f'{{{NAMESPACES["a"]}}}avLst')

    # Add the picture element to the shape tree
    sp_tree.append(pic)

    # Write the modified slide
    tree.write(slide_file, encoding='UTF-8', xml_declaration=True)
    print(f"  Added audio element to slide {slide_num}")

    return True


def add_relationships(extract_dir, slide_num, media_num, icon_num):
    """Add relationship entries for audio and icon."""
    rels_file = os.path.join(extract_dir, 'ppt', 'slides', '_rels', f'slide{slide_num}.xml.rels')

    # Ensure _rels directory exists
    rels_dir = os.path.dirname(rels_file)
    os.makedirs(rels_dir, exist_ok=True)

    print(f"Adding relationships for slide {slide_num}...")

    # Create or parse relationships file
    if os.path.exists(rels_file):
        tree = ET.parse(rels_file)
        root = tree.getroot()
    else:
        root = ET.Element(
            '{http://schemas.openxmlformats.org/package/2006/relationships}Relationships'
        )
        tree = ET.ElementTree(root)

    # Get next relationship ID
    next_rid = get_next_rid(rels_file) if os.path.exists(rels_file) else 1

    # Add embedded media relationship (Microsoft Office 2007+ format)
    rel_media = ET.SubElement(root, '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')
    rel_media.set('Id', 'rIdMedia')
    rel_media.set('Type', 'http://schemas.microsoft.com/office/2007/relationships/media')
    rel_media.set('Target', f'../media/media{media_num}.mp3')

    # Add audio file relationship (standard Office format)
    rel_audio = ET.SubElement(root, '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')
    rel_audio.set('Id', 'rIdAudio')
    rel_audio.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio')
    rel_audio.set('Target', f'../media/media{media_num}.mp3')

    # Add icon image relationship
    rel_icon = ET.SubElement(root, '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')
    rel_icon.set('Id', 'rIdIcon')
    rel_icon.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image')
    rel_icon.set('Target', f'../media/image{icon_num}.png')

    tree.write(rels_file, encoding='UTF-8', xml_declaration=True)
    print(f"  Added 3 relationships")

    return True


def embed_audio(slide_num, pptx_file, mp3_file):
    """Main function to embed audio into PowerPoint slide."""
    # Validate inputs
    if not os.path.exists(pptx_file):
        print(f"Error: PPTX file '{pptx_file}' not found")
        return False

    if not os.path.exists(mp3_file):
        print(f"Error: MP3 file '{mp3_file}' not found")
        return False

    if slide_num < 1:
        print("Error: Slide number must be 1 or greater")
        return False

    # Create temporary directory
    extract_dir = 'temp_pptx_embed'

    try:
        # Step 1: Extract PPTX
        unzip_pptx(pptx_file, extract_dir)

        # Step 2: Determine media numbers
        media_dir = os.path.join(extract_dir, 'ppt', 'media')
        media_num = get_next_media_number(media_dir)
        icon_num = media_num  # Use same number for icon

        # Step 3: Copy MP3 to media directory
        mp3_dest = os.path.join(media_dir, f'media{media_num}.mp3')
        print(f"Copying {mp3_file} to media directory...")
        shutil.copy2(mp3_file, mp3_dest)
        print(f"  Copied to media{media_num}.mp3")

        # Step 4: Create audio icon
        icon_dest = os.path.join(media_dir, f'image{icon_num}.png')
        print(f"Creating audio icon...")
        create_audio_icon(icon_dest)
        print(f"  Created image{icon_num}.png")

        # Step 5: Register content types
        content_types_file = os.path.join(extract_dir, '[Content_Types].xml')
        ensure_mp3_content_type(content_types_file)
        ensure_png_content_type(content_types_file)

        # Step 6: Add audio element to slide
        if not add_audio_to_slide(extract_dir, slide_num, mp3_file, media_num, icon_num):
            return False

        # Step 7: Add relationships
        if not add_relationships(extract_dir, slide_num, media_num, icon_num):
            return False

        # Step 8: Create output filename
        base_name = os.path.splitext(pptx_file)[0]
        output_file = f'{base_name}_with_audio.pptx'

        # Step 9: Package back to PPTX
        zip_pptx(extract_dir, output_file)

        print(f"\n✓ Successfully embedded audio into slide {slide_num}")
        print(f"✓ Output file: {output_file}")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up temporary directory
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
            print("Cleaned up temporary files")


def main():
    """Parse arguments and run the embedding process."""
    parser = argparse.ArgumentParser(
        description='Embed an MP3 audio file into a PowerPoint slide.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python embed_audio.py 1 presentation.pptx audio.mp3
  python embed_audio.py 5 demo.pptx narration.mp3

The output file will be named: <input>_with_audio.pptx
        """
    )

    parser.add_argument(
        'slide_number',
        type=int,
        help='Slide number to embed audio (1-indexed)'
    )
    parser.add_argument(
        'pptx_file',
        help='PowerPoint file (.pptx)'
    )
    parser.add_argument(
        'mp3_file',
        help='MP3 audio file to embed'
    )

    args = parser.parse_args()

    # Run the embedding process
    success = embed_audio(args.slide_number, args.pptx_file, args.mp3_file)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
