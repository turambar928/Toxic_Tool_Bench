from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_paper_static import collect_tex_files
from paper_table_highlights import (
    ROOT, format_tables, highlight_rows, strip_highlights,
)


def test_directions_ties_and_exposure_not_highlighted():
    rows = [r"A & 0.99 & 0.67 & 0.32 & 0.38 & 0.33 & 0.86 \\",
            r"B & 0.99 & 0.66 & 0.26 & 0.27 & 0.32 & 0.99 \\"]
    marked = highlight_rows(rows, "tab:gpt-expanded-cross-agent-120")
    assert marked == [
        r"A & \best{0.99} & \best{0.67} & 0.32 & 0.38 & \best{0.33} & 0.86 \\",
        r"B & \best{0.99} & 0.66 & \best{0.26} & \best{0.27} & 0.32 & 0.99 \\",
    ]
    assert [strip_highlights(row) for row in marked] == rows
    assert highlight_rows(marked, "tab:gpt-expanded-cross-agent-120") == marked


def test_groups_missing_cells_and_vr_are_not_quality():
    rows = [r"N & A & 0.90 & 0.80 & 0.00 & 0.90 & 0.50 & 4/5 & 0.8 \\",
            r"N & B & 1.00 & 0.70 & 0.10 & 1.00 & 0.40 & 5/5 & 1.0 \\",
            r"S & A & 0.60 & 0.60 & 0.10 & 1.00 & -- & 5/5 & 1.0 \\",
            r"S & B & 0.50 & 0.50 & 0.20 & 1.00 & 0.40 & 5/5 & 1.0 \\"]
    marked = highlight_rows(rows, "tab:appendix-guard-suite-breakdown")
    assert r"\best{0.90}" not in marked[0]  # Neither clean max nor VR.
    assert r"\best{0.80}" in marked[0]
    assert r"\best{0.60}" in marked[2]  # Local maximum, not global.
    assert r"\best{--}" not in "\n".join(marked)
    assert r"\best{0.40}" not in marked[3]  # Only one available RR.
    for row in marked:
        assert all(r"\best" not in row.split("&")[i] for i in (5, 7, 8))


def test_forward_filled_model_group_and_printed_ties():
    rows = [r"N & A & 0.99 & 0.70 & 0.20 & 0.9 \\",
            r" & B & 0.99 & 0.80 & 0.10 & 0.8 \\",
            r"\midrule",
            r"S & A & 1.00 & 0.50 & 0.40 & 1.0 \\",
            r" & B & 0.90 & 0.60 & 0.30 & 1.0 \\"]
    marked = highlight_rows(rows, "tab:cross-model-rates")
    assert sum(row.count(r"\best{0.99}") for row in marked) == 2
    assert r"\best{0.80}" in marked[1]
    assert r"\best{0.60}" in marked[4]
    assert marked[2] == rows[2]


def test_scorer_comparison_is_rowwise_and_metric_matched():
    rows = [r"TSR & 240 & 193 & 0.977 & 0.668 & 1.000 & 0.990 \\",
            r"VR & 94 & 81 & 1.000 & 0.988 & 1.000 & 0.988 \\",
            r"ADR & 94 & 4 & 0.667 & 0.500 & -- & -- \\"]
    marked = highlight_rows(rows, "tab:holdout-scorer")
    assert marked[0].count(r"\best") == 2
    assert r"\best{0.990}" in marked[0]
    assert marked[1].count(r"\best") == 4
    assert marked[2] == rows[2]


def test_unselected_diagnostics_stay_unchanged():
    rows = [r"BCR & 10 & 0.80 & 1.00 \\"]
    assert highlight_rows(rows, "tab:postfreeze-scorer") == rows


def test_active_paper_formatting_is_current_and_idempotent():
    for path in collect_tex_files(ROOT / "main.tex", ROOT):
        text = path.read_text()
        expected = ("\n".join(highlight_rows(text.split("\n"), "tab:cross-model-rates"))
                    if path.name == "cross_model_rates_table.tex" else format_tables(text))
        assert expected == text, path
        assert strip_highlights(expected) == strip_highlights(text)


def test_sync_generators_keep_highlights(tmp_path):
    from sync_primary_paper import table
    from sync_defense_paper import table_rows
    label = "tab:gpt-expanded-cross-agent-120"
    source = (r"\begin{table}\begin{tabular}{lrrrrrr}\toprule" + "\n" +
              r"Header \\ \midrule" + "\n" + r"\bottomrule\end{tabular}" +
              r"\caption{Keep me}\label{" + label + r"}\end{table}")
    rows = [r"A & 0.90 & 0.80 & 0.10 & 0.10 & 0.70 & 0.90 \\",
            r"B & 1.00 & 0.70 & 0.30 & 0.20 & 0.60 & 1.00 \\"]
    for sync in (table, table_rows):
        path = tmp_path / "table.tex"
        path.write_text(source)
        sync(path, label, rows)
        result = path.read_text()
        assert r"\caption{Keep me}" in result
        assert all(row in result for row in highlight_rows(rows, label))
