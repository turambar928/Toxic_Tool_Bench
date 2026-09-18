import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plot_paper_figures import (
    configure_matplotlib, cross_model_rows, format_rate, mean,
    operator_profile_data, plot_cross_model_paired, plot_operator_dots, write_profile_tables,
)
import plot_paper_figures as plotting

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "toxictool_bench/results"


def test_operator_values_match_preserved_heatmap():
    order, metrics, values = operator_profile_data(RESULTS)
    assert len(order) == 7 and len(metrics) == 5
    assert "sign_flip" not in {row[0] for row in order}
    expected = [[.50, .62, .21, .22, .68], [.58, .37, .17, .17, .90],
                [.59, .55, .21, .21, .74], [.59, .50, .18, .18, .89],
                [.65, .33, .67, .65, 1], [.96, 0, .46, .46, 1],
                [.69, .22, .44, .35, 1]]
    assert np.array_equal([[float(format_rate(v)) for v in row] for row in values], expected)


def test_exposure_conditioning_unchanged():
    rows = [{"n_exposed": "0", "vr": "0", "toxic_tsr": "1"},
            {"n_exposed": "1", "vr": "0.8", "toxic_tsr": "0.4"}]
    assert mean(rows, "vr") == .8
    assert mean(rows, "toxic_tsr") == .7


def test_native_tables_preserve_all_displayed_rates(tmp_path):
    write_profile_tables(RESULTS, tmp_path)
    operator = (tmp_path / "operator_profile_table.tex").read_text()
    assert "\\toprule" in operator and "\\bottomrule" in operator
    assert "includegraphics" not in operator and "cellcolor" not in operator
    _, _, values = operator_profile_data(RESULTS)
    for row in values:
        assert " & ".join(format_rate(v) for v in row) in operator
    cross = (tmp_path / "cross_model_rates_table.tex").read_text()
    for row in cross_model_rows(RESULTS):
        assert " & ".join(format_rate(float(row[k])) for k in
                           ["clean_tsr", "poisoned_tsr", "toxic_bcr", "poison_delivery_rate"]) in cross


def test_paired_plot_is_vector_and_keeps_all_endpoint_values(tmp_path):
    configure_matplotlib()
    plot_cross_model_paired(RESULTS, tmp_path, None)
    pdf = PdfReader(tmp_path / "fig_cross_model_paired.pdf")
    assert len(pdf.pages) == 1 and not list(pdf.pages[0].images)
    text = pdf.pages[0].extract_text()
    for row in cross_model_rows(RESULTS):
        for key in ["clean_tsr", "poisoned_tsr"]:
            assert format_rate(float(row[key])) in text
    assert "<image" not in (tmp_path / "fig_cross_model_paired.svg").read_text()


def test_operator_dots_preserve_rates_and_shared_scale(tmp_path, monkeypatch):
    configure_matplotlib()
    _, _, values = operator_profile_data(RESULTS)
    original_save = plotting.save_figure
    checked = []

    def inspect_and_save(fig, output, preview):
        assert len(fig.axes) == 3
        for ax in fig.axes:
            assert ax.get_xlim() == fig.axes[0].get_xlim()
            assert ax.get_ylim() == fig.axes[0].get_ylim()
        a, b, c = fig.axes
        for ax, column in [(a, 0), (b, 1)]:
            assert np.array_equal(ax.collections[0].get_offsets()[:, 0], values[:, column])
        assert np.array_equal(c.collections[0].get_offsets()[:, 0], values[:, 2])
        assert np.array_equal(c.collections[1].get_offsets()[:, 0], values[:, 3])
        # Only the family divider is a line; no VR/RR connector is implied.
        assert len(c.lines) == 1
        y = a.collections[0].get_offsets()[:, 1]
        assert y[2] - y[1] > y[1] - y[0]
        checked.append(True)
        original_save(fig, output, preview)

    monkeypatch.setattr(plotting, "save_figure", inspect_and_save)
    plot_operator_dots(RESULTS, tmp_path, None)
    assert checked
    reader = PdfReader(tmp_path / "fig_operator_dots.pdf")
    assert len(reader.pages) == 1 and not list(reader.pages[0].images)
    text = reader.pages[0].extract_text()
    for label in ["Aggregate scale", "Treatment/control", "Biased retrieval", "VR", "RR", "BCR"]:
        assert label in text
    svg = (tmp_path / "fig_operator_dots.svg").read_text()
    assert "<image" not in svg and "<text" in svg
