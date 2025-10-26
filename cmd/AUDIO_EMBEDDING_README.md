# Audio Embedding for PowerPoint

This guide explains how to programmatically embed MP3 audio files into PowerPoint slides using Python.

## Overview

The `embed_audio.py` script allows you to automatically embed MP3 audio files into PowerPoint presentations. It works by:

1. Extracting the PPTX file (which is a ZIP archive containing XML files)
2. Copying MP3 files to the `ppt/media/` directory
3. Adding relationship entries in slide `.rels` files
4. Ensuring content types are registered
5. Repackaging everything back into a PPTX file

## Requirements

- Python 3.6+
- No external dependencies required (uses standard library only)

## File Naming Convention

Audio files should be named to match slide numbers:

- `audio-1.mp3` → Embedded in Slide 1
- `audio-2.mp3` → Embedded in Slide 2
- `audio-3.mp3` → Embedded in Slide 3
- etc.

Alternative format also supported: `audio1.mp3`, `audio2.mp3`, etc.

## Usage

### Basic Usage

```bash
python embed_audio.py <input.pptx> <audio_directory>
```

This will create `input_with_audio.pptx` with the embedded audio files.

### Specify Output File

```bash
python embed_audio.py <input.pptx> <audio_directory> <output.pptx>
```

### Examples

```bash
# Example 1: Basic usage
python cmd/embed_audio.py presentation.pptx ./audio/

# Example 2: With custom output
python cmd/embed_audio.py presentation.pptx ./audio/ presentation_final.pptx

# Example 3: Using the unzipped media files from x/ppt/media
# First, rename the media files to match the audio naming convention
cd x/ppt/media
cp media1.mp3 audio-1.mp3
cp media2.mp3 audio-2.mp3
# ... etc
cd ../../..
python cmd/embed_audio.py some_presentation.pptx x/ppt/media/
```

## How It Works

### 1. PPTX File Structure

A PPTX file is actually a ZIP archive with this structure:

```
presentation.pptx
├── [Content_Types].xml          # Registers file types (including audio/mpeg for MP3)
├── _rels/                        # Root relationships
├── ppt/
│   ├── media/                   # Where audio/image files are stored
│   │   ├── media1.mp3
│   │   ├── media2.mp3
│   │   └── ...
│   ├── slides/                  # Slide content
│   │   ├── slide1.xml
│   │   ├── slide2.xml
│   │   └── _rels/               # Slide relationships (links to media)
│   │       ├── slide1.xml.rels
│   │       ├── slide2.xml.rels
│   │       └── ...
│   └── presentation.xml
└── docProps/
```

### 2. Audio Embedding Process

For each slide with audio, the script:

**a) Copies the MP3 file** to `ppt/media/mediaN.mp3`

**b) Adds two relationship entries** to `ppt/slides/_rels/slideN.xml.rels`:

```xml
<!-- OpenXML standard audio relationship -->
<Relationship Id="rId2"
              Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio"
              Target="../media/media1.mp3"/>

<!-- Microsoft Office media extension -->
<Relationship Id="rId1"
              Type="http://schemas.microsoft.com/office/2007/relationships/media"
              Target="../media/media1.mp3"/>
```

**c) Ensures MP3 content type** is registered in `[Content_Types].xml`:

```xml
<Default Extension="mp3" ContentType="audio/mpeg"/>
```

### 3. Why Two Relationships?

PowerPoint requires **two** relationship entries per audio file:
- **OpenXML standard** (`officeDocument/2006/relationships/audio`): For compatibility
- **Microsoft extension** (`office/2007/relationships/media`): For PowerPoint-specific features

### 4. Visual Audio Icon (Optional)

The current script embeds audio **without** a visual icon on the slide. The audio is embedded and will be present in the file, but won't show a visible speaker icon.

To add a visible audio control, you would need to modify the slide XML (`slideN.xml`) to include a `<p:pic>` element with:
- Audio file reference
- Visual icon image (speaker icon)
- Position and size information

## Complete Workflow Example

Here's a complete workflow from markdown to PowerPoint with audio:

```bash
# Step 1: Convert markdown to PowerPoint
python cmd/md_to_pptx.py slides.md notes.md
# Output: slides.pptx

# Step 2: Generate audio from notes
python cmd/convert-notes.py notes.md -o ./audio/
# Output: ./audio/audio-1.mp3, audio-2.mp3, etc.

# Step 3: Embed audio into PowerPoint
python cmd/embed_audio.py slides.pptx ./audio/ slides_with_audio.pptx
# Output: slides_with_audio.pptx
```

## Troubleshooting

### "Slide N does not exist"
- Make sure your PPTX file has enough slides for the audio files
- Check that slide numbers match your audio file names

### "Audio file not found"
- Verify the audio directory path is correct
- Check that audio files follow the naming convention: `audio-1.mp3`, `audio-2.mp3`, etc.

### "Could not extract slide number"
- Ensure audio files are named correctly: `audio-1.mp3` or `audio1.mp3`
- Remove any non-numeric characters from the filename

### Audio embedded but not playing
- PowerPoint may require you to enable audio playback
- Check PowerPoint's "Playback" settings for the audio
- The audio is embedded as a relationship but may not have a visible trigger

## Technical Details

### XML Namespaces

The script uses these XML namespaces:

- `p`: PresentationML (slides, shapes)
- `a`: DrawingML (graphics, audio)
- `r`: Relationships (links between files)
- `p14`: PowerPoint 2010 extensions

### Relationship IDs

Each relationship in a `.rels` file has a unique ID (`rId1`, `rId2`, etc.). The script automatically:
- Scans existing relationships
- Assigns the next available ID
- Ensures no conflicts

## Limitations

1. **No visual audio icon**: The script embeds audio but doesn't add a visible speaker icon to slides
2. **No auto-play configuration**: You'll need to configure playback settings in PowerPoint
3. **MP3 only**: Currently only supports MP3 format (could be extended to WAV, M4A, etc.)
4. **One audio per slide**: Designed for one audio file per slide

## Extending the Script

To add visual audio icons, you would need to modify the `add_audio_to_slide()` function to:

1. Add a speaker icon image to `ppt/media/`
2. Create a `<p:pic>` element in the slide XML with:
   - Reference to the audio file (`a:audioFile`)
   - Reference to the icon image (`a:blip`)
   - Position and size (`p:spPr`)
   - Click action (`a:hlinkClick` with `ppaction://media`)

See the existing slide XML in your unzipped PPTX for examples.

## License

This script is provided as-is for educational and practical use.
