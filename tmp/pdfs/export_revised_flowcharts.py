"""Wrap the reviewed, unchanged PNGs in tightly sized PDF pages."""
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "flowchart_revision_20260912"

for stem, title in [
    ("figure1_silent_tool_poisoning_v2", "Silent tool poisoning: observation-boundary example"),
    ("figure2_evaluation_and_verification_v2", "ToxicBench: paired evaluation and Guarded Verification"),
]:
    source = OUT / f"{stem}.png"
    destination = OUT / f"{stem}.pdf"
    with Image.open(source) as im:
        width_px, height_px = im.size
        width_pt = 468.0
        height_pt = width_pt * height_px / width_px
        page = canvas.Canvas(str(destination), pagesize=(width_pt, height_pt))
        page.setTitle(title)
        page.setAuthor("")
        page.setSubject("Reviewed raster figure embedded at original resolution; not a vector PDF")
        page.drawImage(ImageReader(im), 0, 0, width_pt, height_pt)
        page.showPage()
        page.save()
    reader = PdfReader(str(destination))
    assert len(reader.pages) == 1
    assert abs(float(reader.pages[0].mediabox.width) - width_pt) < 0.01
    print(f"{destination.name}: {width_px} x {height_px} px; {width_pt:.1f} x {height_pt:.1f} pt")
