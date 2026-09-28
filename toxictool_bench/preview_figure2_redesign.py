"""Create a standalone, editable Figure 2 proposal without replacing paper assets."""
import json

from pypdf import PdfReader

from rebuild_vector_figures import SVG, NS, ROOT, cairo, Rsvg, digest, render


OUT = ROOT / "paper/previews/figure2_redesign_20260926"
INK = "#293141"
MUTED = "#646B79"
ACCENT = "#6462A3"
LINE = "#D9DCE4"
PAPER = "#F7F8FB"
LAVENDER = "#F2F1F8"
CORAL = "#B96560"
BLUSH = "#FCF2F0"
WIDTH, HEIGHT = 2000, 1180


def text(s, x, y, value, size=36, color=INK, bold=False, anchor="start", width=None):
    return s.text(x, y, value, size, color, bold, anchor, width)


def box(s, x, y, w, h, fill=PAPER, stroke=LINE):
    return s.rect(x, y, w, h, fill, stroke, r=12, sw=2)


def diagram():
    s = SVG("ToxicBench: paired evaluation and the Generic Guard protocol")
    s.root.set("width", str(WIDTH))
    s.root.set("height", str(HEIGHT))
    s.root.set("viewBox", f"0 0 {WIDTH} {HEIGHT}")
    s.root.find(f"{{{NS}}}rect").set("height", str(HEIGHT))

    # A compact task strip; detailed suite sizes remain in the paper.
    text(s, 24, 49, "Numerical tasks", 42, bold=True)
    text(s, 1040, 49, "Semantic / schema tasks", 42, bold=True)
    s.line(995, 24, 995, 192, LINE, 2)
    for y, value in zip([103, 147, 191], [
        "Examples: Aggregate scale · Sign flip · Rank swap",
        "Ratio inversion · Denominator swap",
        "Omitted filter",
    ]):
        text(s, 24, y, value, 34)
    for y, value in zip([103, 147, 191], [
        "Examples: Label swap · Treatment/control flip",
        "Column-semantic swap · Stale metadata",
        "Biased retrieval",
    ]):
        text(s, 1040, y, value, 34)
    s.line(24, 228, 1976, 228, LINE, 2)

    text(s, 24, 290, "Paired evaluation", 44, bold=True)
    text(s, 1976, 290, "Same task, model, and budget limits", 32, MUTED, anchor="end")

    # The diagram follows observation flow, not a claim that agents never
    # initiate tool calls. Follow-up access to unchanged sources is explicit.
    box(s, 24, 376, 300, 366, LAVENDER)
    text(s, 174, 426, "Shared task", 39, bold=True, anchor="middle")
    text(s, 174, 481, "Same query", 34, anchor="middle")
    text(s, 174, 524, "Fixed source tables", 31, anchor="middle")
    s.rect(78, 557, 192, 87, "#FFFFFF", LINE, r=4, sw=2)
    s.rect(79, 558, 190, 25, "#E4E3EE", "none", r=0)
    for y in (583, 613):
        s.line(78, y, 270, y, LINE, 2)
    for x in (142, 206):
        s.line(x, 557, x, 644, LINE, 2)
    text(s, 174, 703, "Source unchanged", 30, MUTED, anchor="middle")

    s.path("M 324 559 L 355 559 L 355 449", MUTED, sw=2.5)
    s.path("M 355 559 L 355 663", MUTED, sw=2.5)
    for center in (449, 663):
        s.arrow([(355, center), (395, center)], MUTED, 2.5, 10)

    for top, label, is_poisoned in [(376, "Clean run", False), (590, "Poisoned run", True)]:
        center = top + 73
        text(s, 395, top - 23, label, 32, MUTED, bold=True)
        box(s, 395, top, 290, 146)
        text(s, 540, top + 47, "Tool executes", 36, bold=True, anchor="middle")
        text(s, 540, top + 102, "o = f(x)", 38, ACCENT, anchor="middle")
        s.arrow([(685, center), (762, center)], MUTED, 2.5, 11)

        box(s, 762, top, 358, 146,
            BLUSH if is_poisoned else PAPER, CORAL if is_poisoned else LINE)
        text(s, 941, top + 47,
             "Modify the return" if is_poisoned else "Return unchanged",
             36, CORAL if is_poisoned else INK, True, "middle")
        text(s, 941, top + 102,
             "Silent output proxy" if is_poisoned else "Original observation",
             32, MUTED, anchor="middle")
        s.arrow([(1120, center), (1195, center)],
                CORAL if is_poisoned else MUTED, 2.5, 11)

        box(s, 1195, top, 315, 146)
        text(s, 1352.5, top + 41, "Agent response", 36, bold=True, anchor="middle")
        text(s, 1352.5, top + 85, "Checks, if any", 32, anchor="middle")
        text(s, 1352.5, top + 123, "& final answer", 32, anchor="middle")
        s.arrow([(1510, center), (1580, center)], MUTED, 2.5, 11)

    box(s, 1580, 337, 396, 432, LAVENDER)
    text(s, 1610, 383, "Score the trace", 36, bold=True)
    text(s, 1610, 446, "All runs", 32, MUTED)
    text(s, 1610, 497, "TSR", 42, ACCENT, True)
    s.line(1610, 527, 1946, 527, LINE, 2)
    text(s, 1610, 580, "Exposed runs", 32, MUTED)
    text(s, 1610, 634, "PAR · BCR · VPA", 34, ACCENT, True)
    text(s, 1610, 685, "ADR · VR · RR", 34, ACCENT, True)
    text(s, 24, 825,
         "Follow-up checks use the same sources; returned evidence may also be corrupted.",
         32, MUTED)
    s.line(24, 866, 1976, 866, LINE, 2)

    text(s, 24, 928, "Generic Guard", 44, bold=True)
    text(s, 1976, 928, "Two routes; the second answer is returned", 32, MUTED, anchor="end")
    stages = [
        (24, "Expectation prompt", ["Applied to both routes"]),
        (536, "Primary route", ["Agent + tool calls", "Produces the first answer"]),
        (1048, "Verification route", ["Checks the first answer", "with additional tool evidence"]),
        (1560, "Return route 2", ["Use the second answer"]),
    ]
    for number, (x, title, details) in enumerate(stages, 1):
        s.circle(x + 20, 994, 20, LAVENDER, LINE, sw=1.5)
        text(s, x + 20, 1005, str(number), 30, ACCENT, True, "middle")
        text(s, x + 53, 1006, title, 34, bold=True)
        for i, detail in enumerate(details):
            text(s, x, 1066 + 43 * i, detail, 30, MUTED)
        if number < 4:
            s.arrow([(x + 457, 1040), (x + 492, 1040)], ACCENT, 2.5, 10)
    return s


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    originals = [ROOT / "paper/figures/figure2_vector.pdf", ROOT / "paper/figures/figure2_vector.svg"]
    arxiv_figure = ROOT / "paper/exports/ARXIV_OVERLEAF_20260925/figures/figure2_vector.pdf"
    if arxiv_figure.is_file():
        originals.append(arxiv_figure)
    before = {str(path): digest(path) for path in originals}
    s = diagram()
    svg = OUT / "figure2_redesign.svg"
    pdf = svg.with_suffix(".pdf")
    s.write(svg)
    render(svg, pdf)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    viewport = Rsvg.Rectangle()
    viewport.x = viewport.y = 0
    viewport.width, viewport.height = WIDTH, HEIGHT
    Rsvg.Handle.new_from_file(str(svg)).render_document(cairo.Context(surface), viewport)
    surface.write_to_png(str(svg.with_suffix(".png")))

    page = PdfReader(pdf).pages[0]
    assert not list(page.images)
    extracted = " ".join(page.extract_text().split())
    for phrase in ["TSR", "PAR", "BCR", "VPA", "ADR", "VR", "RR", "Source unchanged",
                   "Return route 2", "Same query", "Tool executes", "Modify the return"]:
        assert phrase in extracted, phrase
    for item in s.texts:
        assert 0 <= item["left"] < item["right"] <= WIDTH, item
        assert 0 < item["baseline"] < HEIGHT, item
    # Exact font-metric bounds also catch side-by-side labels touching.
    for i, first in enumerate(s.texts):
        for second in s.texts[i + 1:]:
            x_overlap = min(first["right"], second["right"]) - max(first["left"], second["left"])
            y_overlap = min(first["baseline"], second["baseline"]) - max(
                first["baseline"] - first["font_size"], second["baseline"] - second["font_size"])
            assert not (x_overlap > 0 and y_overlap > 0), (first["text"], second["text"])
    assert before == {str(path): digest(path) for path in originals}
    print(json.dumps({"preview": str(pdf), "vector_only": True,
                      "originals_unchanged": True, "text_items": len(s.texts)}, indent=2))


if __name__ == "__main__":
    main()
