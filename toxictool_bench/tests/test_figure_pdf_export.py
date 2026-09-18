import sys
from pathlib import Path

from PIL import Image
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from export_figure_pdfs import export, validate


def test_lossless_pdf_preserves_pixels_and_geometry(tmp_path):
    source=tmp_path/"input.png"
    image=Image.new("RGB",(127,61))
    image.putdata([((i*17)%256,(i*41)%256,(i*67)%256) for i in range(127*61)])
    image.save(source)
    data=source.read_bytes()
    record=export(source,tmp_path/"figure.pdf",396)
    assert record["rgb_pixels_identical"] and not record["vectorized"]
    assert record["width_pixels"]==127 and record["height_pixels"]==61
    assert source.read_bytes()==data
    assert validate(source,tmp_path/"figure.pdf")==record
    with pytest.raises(FileExistsError):export(source,tmp_path/"figure.pdf")


def test_opaque_alpha_does_not_change_appearance(tmp_path):
    source=tmp_path/"rgba.png"
    Image.new("RGBA",(11,7),(30,80,120,255)).save(source)
    assert export(source,tmp_path/"rgba.pdf")["rgb_pixels_identical"]


def test_transparency_is_not_silently_flattened(tmp_path):
    source=tmp_path/"transparent.png"
    Image.new("RGBA",(11,7),(30,80,120,120)).save(source)
    with pytest.raises(ValueError,match="transparency"):
        export(source,tmp_path/"transparent.pdf")
    assert not (tmp_path/"transparent.pdf").exists()
