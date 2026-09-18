"""Losslessly embed unchanged PNG figures in PDF; this does not vectorize text.

Uses the actual ICLR template text width (5.5 in = 396 pt). Source PNGs are
read-only. Decoded PDF image samples must exactly equal the source RGB samples.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (BooleanObject, DecodedStreamObject, DictionaryObject,
                            EncodedStreamObject, NameObject, NumberObject)

ROOT = Path(__file__).resolve().parents[1]
WIDTH_PT = 396.0


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rgb_png_stream(png, size):
    """Return original lossless IDAT bytes for noninterlaced 8-bit RGB PNG."""
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Not a PNG")
    position, chunks, valid = 8, [], False
    while position < len(png):
        length = int.from_bytes(png[position:position+4],"big")
        kind = png[position+4:position+8]
        data = png[position+8:position+8+length]
        if kind == b"IHDR":
            dimensions=(int.from_bytes(data[:4],"big"),int.from_bytes(data[4:8],"big"))
            valid=dimensions==size and data[8:]==b"\x08\x02\x00\x00\x00"
        if kind == b"IDAT":chunks.append(data)
        position += length+12
        if kind == b"IEND":break
    if not valid or not chunks:
        raise ValueError("Need noninterlaced 8-bit RGB PNG")
    return b"".join(chunks)


def validate(source, destination, width_pt=WIDTH_PT):
    with Image.open(source) as im:
        if "A" in im.getbands() and im.getchannel("A").getextrema() != (255,255):
            raise ValueError("Nonopaque alpha needs a separately verified transparency workflow")
        original = im.convert("RGB")
    reader = PdfReader(destination)
    if len(reader.pages) != 1:
        raise ValueError("Expected one tightly sized page")
    page = reader.pages[0]
    images = list(page.images)
    if len(images) != 1:
        raise ValueError("Expected exactly one embedded raster image")
    extracted = images[0].image.convert("RGB")
    if extracted.size != original.size or extracted.tobytes() != original.tobytes():
        raise ValueError("Embedded pixels differ from the original PNG")
    xobjects = page["/Resources"]["/XObject"].get_object()
    image_objects = [obj.get_object() for obj in xobjects.values()
                     if obj.get_object().get("/Subtype") == "/Image"]
    filters = [str(obj.get("/Filter")) for obj in image_objects]
    if any("DCTDecode" in f or "JPXDecode" in f for f in filters):
        raise ValueError("Lossy image encoding is not permitted")
    width, height = original.size
    expected_height = width_pt * height / width
    if abs(float(page.mediabox.width)-width_pt) > .001 or abs(float(page.mediabox.height)-expected_height) > .001:
        raise ValueError("PDF dimensions or aspect ratio changed")
    if page.extract_text().strip():
        raise ValueError("Unexpected text overlay")
    return {"source":source.name,"pdf":destination.name,"source_sha256":sha(source.read_bytes()),
            "pdf_sha256":sha(destination.read_bytes()),"width_pixels":width,"height_pixels":height,
            "page_width_points":width_pt,"page_height_points":expected_height,
            "effective_dpi_at_paper_width":width/(width_pt/72),"image_filters":filters,
            "rgb_pixels_identical":True,"rgb_pixel_sha256":sha(original.tobytes()),
            "font_or_layout_changed":False,"vectorized":False}


def export(source, destination, width_pt=WIDTH_PT, replace=False):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("Source and destination must differ")
    if destination.exists() and not replace:
        raise FileExistsError("PDF exists; use --replace only to regenerate the derived PDF")
    original_hash = sha(source.read_bytes())
    with Image.open(source) as im:
        if "A" in im.getbands() and im.getchannel("A").getextrema() != (255,255):
            raise ValueError("Unexpected transparency; refusing to flatten or alter appearance")
        rgb = im.convert("RGB")
    width, height = rgb.size
    destination.parent.mkdir(parents=True,exist_ok=True)
    # PDF's PNG predictor permits reusing PNG's efficiently compressed IDAT
    # bytes. For opaque RGBA, create an RGB PNG in memory without altering any
    # color samples. Never recompress using JPEG or inflate into raw-row Flate.
    try:
        compressed = rgb_png_stream(source.read_bytes(),rgb.size)
    except ValueError:
        buffer=io.BytesIO()
        rgb.save(buffer,format="PNG",compress_level=9)
        compressed=rgb_png_stream(buffer.getvalue(),rgb.size)
    writer=PdfWriter()
    page=writer.add_blank_page(width=width_pt,height=width_pt*height/width)
    image=EncodedStreamObject()
    image._data=compressed
    for key,value in {"/Type":NameObject("/XObject"),"/Subtype":NameObject("/Image"),
        "/Width":NumberObject(width),"/Height":NumberObject(height),
        "/BitsPerComponent":NumberObject(8),"/ColorSpace":NameObject("/DeviceRGB"),
        "/Filter":NameObject("/FlateDecode"),"/Interpolate":BooleanObject(False),
        "/DecodeParms":DictionaryObject({NameObject("/Predictor"):NumberObject(15),
            NameObject("/Colors"):NumberObject(3),NameObject("/BitsPerComponent"):NumberObject(8),
            NameObject("/Columns"):NumberObject(width)})}.items():
        image[NameObject(key)]=value
    page[NameObject("/Resources")]=DictionaryObject({NameObject("/XObject"):
        DictionaryObject({NameObject("/Figure"):writer._add_object(image)})})
    drawing=DecodedStreamObject()
    drawing.set_data(f"q\n{width_pt:.8f} 0 0 {width_pt*height/width:.8f} 0 0 cm\n/Figure Do\nQ\n".encode())
    page[NameObject("/Contents")]=writer._add_object(drawing)
    writer.add_metadata({"/Title":source.stem+" — unchanged original-resolution figure",
        "/Author":"","/Subject":"Lossless PNG-predictor raster embedding; original typography/layout retained; not a vector PDF."})
    with destination.open("wb" if replace else "xb") as handle:
        writer.write(handle)
    if sha(source.read_bytes()) != original_hash:
        raise ValueError("Source changed during export")
    return validate(source,destination,width_pt)


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--replace",action="store_true")
    p.add_argument("--verify-only",action="store_true")
    args=p.parse_args()
    records=[]
    for name in ["figure1","figure2"]:
        source=ROOT/"figures"/(name+".png")
        target=ROOT/"figures"/(name+".pdf")
        records.append(validate(source,target) if args.verify_only else export(source,target,replace=args.replace))
    if not args.verify_only:
        (ROOT/"figures/figure_pdf_export.json").write_text(json.dumps(records,indent=2)+"\n")
    print(json.dumps(records,indent=2))
