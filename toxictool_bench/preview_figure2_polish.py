"""Light palette/alignment polish of the original Figure 2; preview only."""
import json
import re
import xml.etree.ElementTree as ET

from pypdf import PdfReader

from rebuild_vector_figures import ROOT, NS, cairo, Rsvg, digest, figure2, render


OUT = ROOT / "paper/previews/figure2_polish_20260926"
PALETTE = {
    "#4264ce": "#5974BC", "#4162cf": "#5974BC",
    "#713cc2": "#805DAE", "#c73532": "#BC5B57",
    "#b1262d": "#A84D52", "#c77d32": "#B48649",
    "#4d965c": "#648F70", "#4f995d": "#648F70",
    "#2b794b": "#477B5C", "#54a36a": "#739A7C",
    "#263650": "#3B4A63", "#535e73": "#657083",
    "#dbe1e8": "#E8EBF0",
}


def move_text(root, value, **attrs):
    elements = [e for e in root.findall(f"{{{NS}}}text") if e.text == value]
    assert len(elements) == 1, (value, len(elements))
    for name, value in attrs.items():
        elements[0].set(name.replace("_", "-"), str(value))


def move_icon(root, old, new):
    elements = [e for e in root.findall(f"{{{NS}}}g") if e.get("transform") == old]
    assert len(elements) == 1, (old, len(elements))
    elements[0].set("transform", new)


def move_shape(root, tag, match, **attrs):
    elements = [e for e in root.findall(f"{{{NS}}}{tag}")
                if all(e.get(k) == str(v) for k, v in match.items())]
    assert len(elements) == 1, (tag, match, len(elements))
    for name, value in attrs.items():
        elements[0].set(name.replace("_", "-"), str(value))


def replace_arrow(s, old_points, new_points, color, width=3, head=10):
    old_path = "M " + " L ".join(f"{x} {y}" for x, y in old_points)
    children = list(s.root)
    matches = [i for i, e in enumerate(children)
               if e.tag == f"{{{NS}}}path" and e.get("d") == old_path]
    assert len(matches) == 1, old_path
    index = matches[0]
    assert children[index + 1].tag == f"{{{NS}}}polygon"
    s.root.remove(children[index])
    s.root.remove(children[index + 1])
    s.arrow(new_points, color, width, head)
    list(s.root)[-2].set("class", "protocol-aligned-arrow")


def align_protocol_row(s):
    """Use one icon axis, one caption baseline, and measured arrow clearances."""
    root = s.root
    move_text(root, "Same Query and Source Data", x=1000)
    move_text(root, "Paired Task", x=847.5)
    move_text(root, "Poisoned Env.", x=1622)

    # Both inter-panel gaps are 35 units, with centered 22-unit connectors.
    move_shape(root, "rect", {"x": 1250, "y": 413, "width": 739}, x=1255, width=734)
    move_shape(root, "rect", {"x": 1252, "y": 417, "width": 739}, x=1257, width=734)
    replace_arrow(s, [(440, 496), (473, 496)], [(446.5, 500), (468.5, 500)], PALETTE["#54a36a"])
    replace_arrow(s, [(1250, 496), (1223, 496)], [(1248.5, 500), (1226.5, 500)], PALETTE["#b1262d"])

    # Content in all three panels follows the same y=500 center line.
    move_icon(root, "translate(41 449) scale(0.99)", "translate(41 450.5) scale(0.99)")
    move_icon(root, "translate(312 469) scale(0.8)", "translate(312 460) scale(0.8)")
    replace_arrow(s, [(160, 496), (288, 496)], [(160, 500), (288, 500)], PALETTE["#54a36a"], 4, 15)
    move_text(root, "o = f(x)", y=508)
    move_icon(root, "translate(640 466) scale(0.38)", "translate(619 481) scale(0.38)")
    move_icon(root, "translate(685 466) scale(0.48)", "translate(671 476) scale(0.48)")
    query_width = s.font(22).getlength("(query + dataset)") / 10
    move_text(root, "(query + dataset)", x=902-query_width/2, y=508, font_size="22.000")
    move_shape(root, "polygon", {"points": "1003,462 1036,495 1003,528 970,495"},
               points="1003,467 1036,500 1003,533 970,500")
    move_shape(root, "circle", {"cx": 1137, "cy": 495, "r": 27}, cx=1131, cy=500)
    move_text(root, "=", y=510)
    move_text(root, "vC", x=1131, y=509)
    # 44-unit arrows, 12-unit clearance before/after each neighboring node.
    replace_arrow(s, [(948, 495), (973, 495)], [(914, 500), (958, 500)], "#80828b")
    replace_arrow(s, [(1036, 495), (1094, 495)], [(1048, 500), (1092, 500)], "#80828b")

    move_text(root, "o' = P(o; q)", x=1322, y=508, text_anchor="middle", font_size="22.000")
    equation_right = 1322 + s.font(22).getlength("o' = P(o; q)") / 20
    arrow_start = equation_right + 12
    arrow_end = arrow_start + 44
    proxy_x = arrow_end + 12
    replace_arrow(s, [(1410, 496), (1436, 496)],
                  [(arrow_start, 500), (arrow_end, 500)], PALETTE["#b1262d"])
    move_icon(root, "translate(1440 455) scale(0.89)", f"translate({proxy_x} 460) scale(0.8)")
    move_text(root, "Tool-output Proxy", x=proxy_x+40)
    move_shape(root, "rect", {"x": 1630, "y": 478, "width": 336}, x=1606, height=44, width=360)
    move_text(root, "Silent – no error / warning", x=1770, y=507)
    move_icon(root, "translate(1930 485) scale(0.29)", "translate(1930 485.5) scale(0.29)")
    move_text(root, "Source Data Unchanged", x=1786)

    for value in ("Data Agent", "Tool", "Correct output", "compare",
                  "Tool-output Proxy", "Source Data Unchanged"):
        move_text(root, value, y=562)
    move_text(root, "compare", x=1131)
    # Only the central data-flow label moves; the clean panel has another.
    move_shape(root, "text", {"x": 846, "y": 556}, x=902-query_width/2, y=562)
    # Keep both words, but place "Matched Settings" on the shared caption line.
    words = ["Matched", "Settings"]
    widths = [s.font(19).getlength(word) / 10 for word in words]
    x = 1003 - (sum(widths) + 5) / 2
    for word, width in zip(words, widths):
        move_text(root, word, x=x, y=562, font_size="19.000", text_anchor="start")
        x += width + 5


def polished_figure():
    s = figure2()
    root = s.root
    original_text = [e.text for e in root.iter(f"{{{NS}}}text")]
    for element in root.iter():
        for attr in ("fill", "stroke"):
            color = element.get(attr, "").lower()
            if color in PALETTE:
                element.set(attr, PALETTE[color])

    # Match the two suite-heading sizes without changing their content.
    move_text(root, "Numerical Tasks", font_size="30.000")
    # Equal baseline and size for the three protocol headings.
    move_text(root, "Clean Env.", x=225, y=450, font_size="27.000")
    move_text(root, "Paired Task", y=450, font_size="27.000")
    move_text(root, "Poisoned Env.", x=1620, y=450, font_size="27.000")
    for value in ("Data Agent", "Tool", "Tool-output Proxy"):
        move_text(root, value, y=568)
    align_protocol_row(s)

    # All metric symbols now sit wholly in the card body on one 64-pixel grid;
    # headings are centered in their header strips, not offset by icon widths.
    for i, label in enumerate(["TSR", "PAR / VPA", "BCR", "ADR", "VR", "RR"]):
        x = 9 + i * 332
        old = f"translate({x+12} {657 if i == 5 else 661}) scale({.78 if i == 5 else .66})"
        move_icon(root, old, f"translate({x+12} 694) scale(0.64)")
        move_text(root, label, x=x+160, y=677)

    # The two middle Guard cards keep their matching arrows and content;
    # supporting tool symbols now share the same dimensions and baseline.
    for old, new in [
        ("translate(782 1006) scale(0.69)", "translate(782 1006) scale(0.62)"),
        ("translate(895 1011) scale(0.62)", "translate(895 1006) scale(0.62)"),
        ("translate(1280 1011) scale(0.62)", "translate(1280 1006) scale(0.62)"),
        ("translate(1393 1006) scale(0.69)", "translate(1393 1006) scale(0.62)"),
    ]:
        move_icon(root, old, new)
    move_text(root, "Primary pathway", y=961)
    # Join the visually separated words "Select answer" without changing text.
    answers = [e for e in root.findall(f"{{{NS}}}text")
               if e.text == "answer" and e.get("y") == "965"]
    assert len(answers) == 1
    answers[0].set("x", "1597")
    answers[0].set("text-anchor", "start")

    assert original_text == [e.text for e in root.iter(f"{{{NS}}}text")]
    return s


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    originals = [ROOT / "paper/figures/figure1_vector.pdf", ROOT / "paper/figures/figure2_vector.pdf",
                 ROOT / "paper/figures/figure2_vector.svg"]
    # Local preview PDFs/exports are intentionally absent from a fresh checkout.
    for path in [ROOT / "paper/main.pdf", ROOT / "paper/exports/ARXIV_OVERLEAF_20260925/main.pdf",
                 ROOT / "paper/exports/ARXIV_OVERLEAF_20260925/figures/figure2_vector.pdf"]:
        if path.is_file():
            originals.append(path)
    before = {str(p): digest(p) for p in originals}
    s = polished_figure()
    aligned_arrows = [e for e in s.root.findall(f"{{{NS}}}path")
                      if e.get("class") == "protocol-aligned-arrow"]
    lengths = []
    for arrow in aligned_arrows:
        x1, y1, x2, y2 = map(float, re.findall(r"-?\d+(?:\.\d+)?", arrow.get("d")))
        assert y1 == y2 == 500
        lengths.append(round(abs(x2-x1), 6))
    assert sorted(lengths) == [22, 22, 44, 44, 44, 128]
    texts = {e.text: e for e in s.root.findall(f"{{{NS}}}text")}
    assert all(texts[t].get("y") == "450" for t in ("Clean Env.", "Paired Task", "Poisoned Env."))
    assert all(texts[t].get("y") == "562" for t in (
        "Data Agent", "Tool", "Correct output", "Matched", "Settings", "compare",
        "Tool-output Proxy", "Source Data Unchanged"))
    svg = OUT / "figure2_polished.svg"
    s.write(svg)
    pdf = svg.with_suffix(".pdf")
    render(svg, pdf)
    _, _, width, height = map(float, s.root.get("viewBox").split())
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height + 1))
    viewport = Rsvg.Rectangle()
    viewport.x = viewport.y = 0
    viewport.width, viewport.height = width, height
    Rsvg.Handle.new_from_file(str(svg)).render_document(cairo.Context(surface), viewport)
    surface.write_to_png(str(svg.with_suffix(".png")))
    page = PdfReader(pdf).pages[0]
    assert not list(page.images)
    original = PdfReader(ROOT / "paper/figures/figure2_vector.pdf").pages[0]
    # PDF layout extraction may join words differently; verify the SVG text
    # stream exactly instead, and retain the exact original physical size.
    old_root = ET.parse(ROOT / "paper/figures/figure2_vector.svg").getroot()
    assert [e.text for e in old_root.iter(f"{{{NS}}}text")] == [
        e.text for e in s.root.iter(f"{{{NS}}}text")]
    assert list(page.mediabox) == list(original.mediabox)
    assert s.root.find(f".//{{{NS}}}g[@id='recovery-phoenix']") is not None
    assert before == {str(p): digest(p) for p in originals}
    print(json.dumps({"pdf": str(pdf), "originals_unchanged": True,
                      "all_text_preserved": True, "vector_only": True}, indent=2))


if __name__ == "__main__":
    main()
