"""Asset regression checks; rendering dependencies are not needed to run these."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "figures"
NS = "{http://www.w3.org/2000/svg}"
ORIGINALS = {
    "figure1.png": "038c3a40d10a2e4937ba34865fa9bece0c304c449eb7b5e716cf7ae17e568b67",
    "figure2.png": "59df196e8dfdb386a6fddb641f958b80d29e21956cd2d1111e9ea3a2176801c9",
    "figure1.pdf": "e9247c32841f7c0e917c674e020f58d39ef4d98b5624b7a52643695fc92b2528",
    "figure2.pdf": "e642898b08a9693cf8d80067572dfd578dea888f46a28d25cd521cc73569078a",
}


def test_original_raster_versions_unchanged():
    for name, expected in ORIGINALS.items():
        assert hashlib.sha256((FIG / name).read_bytes()).hexdigest() == expected


@pytest.mark.parametrize("number", [1, 2])
def test_svg_contains_editable_text_and_native_shapes_only(number):
    root = ET.parse(FIG / f"figure{number}_vector.svg").getroot()
    assert root.tag == NS + "svg"
    assert len(list(root.iter(NS + "text"))) > 40
    assert len(list(root.iter(NS + "path"))) > 10
    for element in root.iter():
        assert element.tag not in {NS + "image", NS + "foreignObject", NS + "filter"}
        assert not any(key.endswith("href") for key in element.attrib)


@pytest.mark.parametrize("number", [1, 2])
def test_pdf_is_vector_with_embedded_selectable_text(number):
    reader = PdfReader(FIG / f"figure{number}_vector.pdf")
    assert len(reader.pages) == 1
    page = reader.pages[0]
    assert not list(page.images)
    assert float(page.mediabox.width) == pytest.approx(396)
    assert float(page.mediabox.height) == pytest.approx(396 * 3072 / 5504, abs=0.001)
    text = " ".join(page.extract_text().split())
    required = (
        ["Store A", "Store B", "$450,000", "$230,000", "$310,000",
         "csv_tool(query)", "No Modification", "Swap Store Labels"]
        if number == 1 else
        ["34", "24", "11 CSV datasets", "17 datasets", "120 tasks", "13 tasks",
         "TSR", "PAR / VPA", "BCR", "ADR", "VR", "RR", "Source Data Unchanged",
         "Route 2 answer selected", "Returns a second answer"]
    )
    for phrase in required:
        assert phrase in text
    fonts = page["/Resources"]["/Font"].get_object()
    assert fonts
    for reference in fonts.values():
        font = reference.get_object()
        descendants = font.get("/DescendantFonts", [font])
        for descendant in descendants:
            descriptor = descendant.get_object()["/FontDescriptor"].get_object()
            assert any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3"))


def test_manifest_matches_delivered_assets():
    manifest = json.loads((FIG / "vector_rebuild_manifest.json").read_text())
    for name, expected in manifest["preserved_original_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
    for figure in manifest["figures"]:
        for kind in ("svg", "pdf"):
            assert hashlib.sha256((FIG / figure[kind]).read_bytes()).hexdigest() == figure[kind + "_sha256"]
