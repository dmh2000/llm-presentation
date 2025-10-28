
import argparse
import zipfile
import os
import shutil
import tempfile
import xml.etree.ElementTree as ET

def get_next_rid(rels_tree):
    """Gets the next available relationship ID."""
    rids = [int(r.attrib['Id'][3:]) for r in rels_tree.getroot()]
    return f"rId{max(rids) + 1 if rids else 1}"

def get_next_spid(slide_tree):
    """Gets the next available shape ID."""
    spids = [int(sp.attrib['id']) for sp in slide_tree.findall('.//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr')]
    return str(max(spids) + 1 if spids else 1)

def update_content_types(temp_dir, extensions_needed):
    """Updates [Content_Types].xml to include required media extensions."""
    content_types_path = os.path.join(temp_dir, '[Content_Types].xml')

    # Parse the content types file
    ET.register_namespace('', 'http://schemas.openxmlformats.org/package/2006/content-types')
    tree = ET.parse(content_types_path)
    root = tree.getroot()

    # Map extensions to their content types
    content_type_map = {
        'mp3': 'audio/mpeg',
        'png': 'image/png',
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg'
    }

    # Get existing extensions
    existing_extensions = {elem.attrib['Extension'] for elem in root.findall('{http://schemas.openxmlformats.org/package/2006/content-types}Default')}

    # Add missing content types
    for ext in extensions_needed:
        if ext not in existing_extensions and ext in content_type_map:
            ET.SubElement(root, '{http://schemas.openxmlformats.org/package/2006/content-types}Default',
                         Extension=ext, ContentType=content_type_map[ext])

    # Write back with proper formatting
    tree.write(content_types_path, xml_declaration=True, encoding='UTF-8', method='xml')

def embed_audio(slide_number, pptx_path, mp3_path, icon_path='audio_icon.png'):
    """Embeds an MP3 file into a specific slide of a PowerPoint presentation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Unzip the presentation
        with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Add media files
        media_dir = os.path.join(temp_dir, 'ppt', 'media')
        os.makedirs(media_dir, exist_ok=True)
        
        mp3_filename = os.path.basename(mp3_path)
        shutil.copy(mp3_path, os.path.join(media_dir, mp3_filename))

        icon_filename = os.path.basename(icon_path)
        shutil.copy(icon_path, os.path.join(media_dir, icon_filename))

        # Update slide relationships
        rels_path = os.path.join(temp_dir, 'ppt', 'slides', '_rels', f'slide{slide_number}.xml.rels')

        # Register namespace to avoid auto-generated prefixes
        ET.register_namespace('', 'http://schemas.openxmlformats.org/package/2006/relationships')
        rels_tree = ET.parse(rels_path)
        rels_root = rels_tree.getroot()

        rid_media = get_next_rid(rels_tree)
        ET.SubElement(rels_root, 'Relationship', Id=rid_media, Type='http://schemas.microsoft.com/office/2007/relationships/media', Target=f'../media/{mp3_filename}')

        rid_audio = get_next_rid(rels_tree)
        ET.SubElement(rels_root, 'Relationship', Id=rid_audio, Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio', Target=f'../media/{mp3_filename}')

        rid_image = get_next_rid(rels_tree)
        ET.SubElement(rels_root, 'Relationship', Id=rid_image, Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/image', Target=f'../media/{icon_filename}')

        rels_tree.write(rels_path, xml_declaration=True, encoding="UTF-8", method='xml')

        # Update slide content
        slide_path = os.path.join(temp_dir, 'ppt', 'slides', f'slide{slide_number}.xml')
        slide_tree = ET.parse(slide_path)
        slide_root = slide_tree.getroot()
        
        spid = get_next_spid(slide_tree)

        pic_xml = f"""
<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
    <p:nvPicPr>
        <p:cNvPr id="{spid}" name="audio-{slide_number}">
            <a:hlinkClick r:id="" action="ppaction://media"/>
        </p:cNvPr>
        <p:cNvPicPr>
            <a:picLocks noChangeAspect="1"/>
        </p:cNvPicPr>
        <p:nvPr>
            <a:audioFile r:link="{rid_audio}"/>
            <p:extLst>
                <p:ext uri="{{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}}">
                    <p14:media xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" r:embed="{rid_media}"/>
                </p:ext>
            </p:extLst>
        </p:nvPr>
    </p:nvPicPr>
    <p:blipFill>
        <a:blip r:embed="{rid_image}"/>
        <a:stretch>
            <a:fillRect/>
        </a:stretch>
    </p:blipFill>
    <p:spPr>
        <a:xfrm>
            <a:off x="5943600" y="3276600"/>
            <a:ext cx="304800" cy="304800"/>
        </a:xfrm>
        <a:prstGeom prst="rect">
            <a:avLst/>
        </a:prstGeom>
    </p:spPr>
</p:pic>
"""
        spTree = slide_root.find('{http://schemas.openxmlformats.org/presentationml/2006/main}cSld/{http://schemas.openxmlformats.org/presentationml/2006/main}spTree')
        spTree.append(ET.fromstring(pic_xml))

        timing_xml = f"""
<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:tnLst>
        <p:par>
            <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
                <p:childTnLst>
                    <p:seq concurrent="1" nextAc="seek">
                        <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
                            <p:childTnLst>
                                <p:par>
                                    <p:cTn id="3" fill="hold">
                                        <p:stCondLst>
                                            <p:cond delay="indefinite"/>
                                        </p:stCondLst>
                                        <p:childTnLst>
                                            <p:par>
                                                <p:cTn id="4" fill="hold">
                                                    <p:stCondLst>
                                                        <p:cond delay="0"/>
                                                    </p:stCondLst>
                                                    <p:childTnLst>
                                                        <p:par>
                                                            <p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="clickEffect">
                                                                <p:stCondLst>
                                                                    <p:cond delay="0"/>
                                                                </p:stCondLst>
                                                                <p:childTnLst>
                                                                    <p:cmd type="call" cmd="playFrom(0.0)">
                                                                        <p:cBhvr>
                                                                            <p:cTn id="6" dur="15072" fill="hold"/>
                                                                            <p:tgtEl>
                                                                                <p:spTgt spid="{spid}"/>
                                                                            </p:tgtEl>
                                                                        </p:cBhvr>
                                                                    </p:cmd>
                                                                </p:childTnLst>
                                                            </p:cTn>
                                                        </p:par>
                                                    </p:childTnLst>
                                                </p:cTn>
                                            </p:par>
                                        </p:childTnLst>
                                    </p:cTn>
                                </p:par>
                            </p:childTnLst>
                        </p:cTn>
                    </p:seq>
                    <p:audio>
                        <p:cMediaNode vol="80000">
                            <p:cTn id="7" fill="hold" display="0">
                                <p:stCondLst>
                                    <p:cond delay="indefinite"/>
                                </p:stCondLst>
                            </p:cTn>
                            <p:tgtEl>
                                <p:spTgt spid="{spid}"/>
                            </p:tgtEl>
                        </p:cMediaNode>
                    </p:audio>
                </p:childTnLst>
            </p:cTn>
        </p:par>
    </p:tnLst>
</p:timing>
"""
        timing_element = ET.fromstring(timing_xml)
        clr_map_ovr = slide_root.find('{http://schemas.openxmlformats.org/presentationml/2006/main}clrMapOvr')
        if clr_map_ovr is not None:
            slide_root.insert(list(slide_root).index(clr_map_ovr) + 1, timing_element)
        else:
            slide_root.append(timing_element)
        slide_tree.write(slide_path, xml_declaration=True, encoding="UTF-8", method='xml')

        # Update [Content_Types].xml to register media file extensions
        mp3_ext = os.path.splitext(mp3_path)[1][1:]  # Get extension without dot
        icon_ext = os.path.splitext(icon_path)[1][1:]  # Get extension without dot
        update_content_types(temp_dir, [mp3_ext, icon_ext])

        # Re-zip the presentation
        shutil.make_archive(pptx_path.replace('.pptx', ''), 'zip', temp_dir)
        os.rename(pptx_path.replace('.pptx', '.zip'), pptx_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Embed an MP3 file in a PowerPoint slide.')
    parser.add_argument('-s', '--slide', type=int, required=True, help='Slide number to embed the MP3 in')
    parser.add_argument('pptx_file', help='PowerPoint file to modify')
    parser.add_argument('mp3_file', help='MP3 file to embed')
    args = parser.parse_args()

    embed_audio(args.slide, args.pptx_file, args.mp3_file)
    print(f"Embedded '{args.mp3_file}' into slide {args.slide} of '{args.pptx_file}'")
