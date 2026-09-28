"""Keep every original table value and its denominator in the integrated plots."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import plot_table_conversion_previews as plots


@pytest.fixture(autouse=True)
def plotting_style():
    plots.configure_style()
    yield
    plots.plt.close("all")


def test_defense_preserves_all_original_fields():
    data = plots.load_data()
    fields = ["clean_tsr", "poisoned_tsr", "bcr", "par", "vpa", "vr", "rr", "exposed"]
    expected = [
        [.99, .89, .09, .09, .00, .46, .44, 99],
        [.99, 1., .00, .00, .00, .98, .98, 101],
        [.92, .90, .00, .01, .01, .97, .86, 101],
        [.98, .97, .00, .00, .00, .97, .94, 104],
    ]
    np.testing.assert_allclose([[r[f] for f in fields] for r in data["defense"]], expected)
    fig = plots.defense_figure(data)
    for ax, keys in zip(fig.axes, [("clean_tsr", "poisoned_tsr"), ("bcr", "par", "vpa"), ("vr", "rr")]):
        actual = [p.get_y() + p.get_height() for p in ax.patches]
        np.testing.assert_allclose(actual, [r[k] for k in keys for r in data["defense"]])
    for row, tick in zip(data["defense"], fig.axes[2].get_xticklabels()):
        assert f"n={row['exposed']}" in tick.get_text()
    assert len(fig.axes[1].texts) == 12  # Includes explicit zero labels.
    assert fig.axes[0].get_ylim()[0] == .8
    assert fig.axes[1].get_ylim()[0] == fig.axes[2].get_ylim()[0] == 0


def test_human_preserves_all_24_counts_and_separates_conditions():
    data = plots.load_data()
    fig = plots.human_figure(data)
    core = [r for r in data["human"] if r["setting"] == "Core"]
    repeated = [r for r in data["human"] if r["setting"].startswith("Repeated")]
    cross = next(r for r in data["human"] if r["setting"] == "Cross-model")
    expected = [
        [r[k] for k in ("clean_auto", "clean_human") for r in core],
        [r[k] for k in ("poison_auto", "poison_human") for r in core],
        [r[k] for k in ("poison_auto", "poison_human") for r in repeated],
        [cross[k] for k in ("clean_auto", "poison_auto", "clean_human", "poison_human")],
    ]
    assert sum(map(len, expected)) == 24
    for ax, counts in zip(fig.axes, expected):
        assert [t.get_text() for t in ax.texts] == [f"{a}/{b}" for a, b in counts]
        np.testing.assert_allclose([p.get_y() + p.get_height() for p in ax.patches], [a/b for a, b in counts])
    assert [ax.get_ylim()[0] for ax in fig.axes] == [.75, .75, 0, 0]


def test_paper_defense_labels_are_horizontal_and_do_not_touch():
    fig = plots.defense_figure(plots.load_data())
    plots.style_paper_figure(fig, plots.defense_figure)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        assert all(text.get_rotation() == 0 for text in ax.texts)
        boxes = [text.get_window_extent(renderer).padded(1) for text in ax.texts]
        for i, box in enumerate(boxes):
            assert not any(box.overlaps(other) for other in boxes[i + 1:])


def test_evidence_keeps_zero_outcomes_and_48_completion_denominator():
    fig = plots.evidence_figure(plots.load_data())
    labels = [t.get_text() for t in fig.axes[0].texts]
    assert labels[:8] == ["48/48", "100.0% correct", "47/48", "97.9% correct",
                           "0/48", "0.0% correct", "0/48", "0.0% correct"]
    assert not fig.axes[0].images  # Heatmap cells are vector rectangles.
    assert fig.axes[1].get_xlim() == (0, 1)


def test_paper_evidence_is_compact_with_legible_nonoverlapping_labels():
    fig = plots.evidence_figure(plots.load_data())
    plots.style_paper_figure(fig, plots.evidence_figure)
    assert fig.get_figheight() <= 2.0
    assert not fig.texts  # Setup and sample-size notes are in the caption.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ax = fig.axes[0]
    assert max(text.get_fontsize() for text in ax.texts) <= 11
    boxes = [text.get_window_extent(renderer).padded(1) for text in ax.texts]
    for i, box in enumerate(boxes):
        assert not any(box.overlaps(other) for other in boxes[i + 1:])
        assert ax.get_window_extent(renderer).contains(*box.get_points()[0])
        assert ax.get_window_extent(renderer).contains(*box.get_points()[1])


def test_manuscript_uses_three_pdf_figures_and_retains_detailed_evidence_table():
    for name, filename in [("05_experiments.tex", "fig_defense_comparison.pdf"),
                           ("09_revision_validation.tex", "fig_human_method_comparison.pdf"),
                           ("11_matched_evidence_controls.tex", "fig_evidence_control.pdf")]:
        text = (plots.ROOT / "sections" / name).read_text()
        assert f"figures/{filename}" in text
        assert (plots.ROOT / "figures" / filename).is_file()
    evidence = (plots.ROOT / "sections/11_matched_evidence_controls.tex").read_text()
    assert r"\input{output/evidence_controls_v4/results}" in evidence
    assert not any(r"\ref{tab:langgraph-guarded}" in p.read_text()
                   for p in (plots.ROOT / "sections").glob("*.tex"))
