"""Presentation-only extrema for explicitly selected manuscript comparisons.

No rescoring: compare the displayed decimals, preserve ties and numeric text,
and never interpret checking/delivery rates as quality. Run after table syncs;
the primary, defense, and profile generators also call this formatter directly.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HIGHLIGHT = re.compile(r"\\best\{([^{}]*)\}")
NUMBER = re.compile(r"^(\s*)([+-]?\d+(?:\.\d+)?)(\s*(?:\\\\)?\s*)$")
TABLE = re.compile(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", re.S)

# Zero-based columns. Only compare within the stated experimental grouping.
# group=None: whole table; integer: forward-filled column; "prefix": suite
# prefix in the latency table. All ties at the printed precision are shown.
POLICIES = {
    "tab:gpt-expanded-cross-agent-120": ({1: "max", 2: "max", 3: "min", 4: "min", 5: "max"}, None),
    "tab:cross-agent-model-full": ({2: "max", 3: "max", 4: "min", 5: "max", 6: "max", 7: "min"}, 0),
    "tab:appendix-stronger-baselines": ({2: "max", 3: "max", 4: "min", 6: "max"}, 0),
    "tab:appendix-guard-suite-breakdown": ({2: "max", 3: "max", 4: "min", 6: "max"}, 0),
    "tab:appendix-multiroute-stress": ({2: "max", 3: "min", 4: "min", 5: "min", 7: "max"}, 0),
    "tab:appendix-latency-distribution": ({2: "min", 3: "min", 4: "min", 5: "min"}, "prefix"),
    "tab:cross-model-rates": ({2: "max", 3: "max", 4: "min"}, 0),
    "tab:holdout-methods": ({3: "max", 4: "max"}, 0),
}
ROW_PAIRS = {"tab:holdout-scorer": ((3, 5), (4, 6))}


def strip_highlights(text: str) -> str:
    return HIGHLIGHT.sub(r"\1", text)


def highlight_rows(lines: list[str], label: str) -> list[str]:
    """Decorate numeric cells without altering whitespace, values, or headers."""
    if label not in POLICIES and label not in ROW_PAIRS:
        return list(lines)
    plain = [strip_highlights(line) for line in lines]
    directions, group_column = POLICIES.get(label, ({}, None))
    groups = defaultdict(list)
    cells_by_row = {}
    active_group = ""
    selected = set()

    def value(cells, column):
        match = NUMBER.fullmatch(cells[column]) if column < len(cells) else None
        return Decimal(match[2]) if match else None

    for index, line in enumerate(plain):
        if "&" not in line or not line.rstrip().endswith(r"\\"):
            continue
        cells = line.split("&")
        cells_by_row[index] = cells
        if label in ROW_PAIRS:
            for pair in ROW_PAIRS[label]:
                values = [(col, value(cells, col)) for col in pair]
                if all(v is not None for _, v in values):
                    best = max(v for _, v in values)
                    selected.update((index, col) for col, v in values if v == best)
            continue
        # Headers and descriptive rows do not change the forward-filled group.
        if not any(value(cells, col) is not None for col in directions):
            continue
        if isinstance(group_column, int):
            active_group = cells[group_column].strip() or active_group
        elif group_column == "prefix":
            active_group = cells[0].strip().split()[0]
        groups[active_group].append(index)

    for indices in groups.values():
        for column, direction in directions.items():
            values = [(i, value(cells_by_row[i], column)) for i in indices]
            values = [(i, v) for i, v in values if v is not None]
            if len(values) < 2:
                continue  # No comparison for singleton/missing observations.
            best = (max if direction == "max" else min)(v for _, v in values)
            selected.update((i, column) for i, v in values if v == best)
    for index, column in sorted(selected):
        cells = cells_by_row[index]
        match = NUMBER.fullmatch(cells[column])
        cells[column] = match[1] + r"\best{" + match[2] + "}" + match[3]
    result = ["&".join(cells_by_row[i]) if i in cells_by_row else line
              for i, line in enumerate(plain)]
    assert [strip_highlights(line) for line in result] == plain
    return result


def format_tables(text: str) -> str:
    def replace(match):
        block = match.group()
        labels = re.findall(r"\\label\{([^}]+)\}", block)
        selected = [label for label in labels if label in POLICIES or label in ROW_PAIRS]
        if not selected:
            return block
        return "\n".join(highlight_rows(block.split("\n"), selected[0]))
    return TABLE.sub(replace, text)


def main() -> None:
    from check_paper_static import collect_tex_files

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without writing files")
    args = parser.parse_args()
    stale = []
    for path in collect_tex_files(ROOT / "main.tex", ROOT):
        old = path.read_text()
        if path == ROOT / "figures/cross_model_rates_table.tex":
            new = "\n".join(highlight_rows(old.split("\n"), "tab:cross-model-rates"))
        else:
            new = format_tables(old)
        if new != old:
            stale.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(new)
    if args.check and stale:
        raise SystemExit("Highlight formatting is stale: " + ", ".join(stale))
    print("Highlight formatting checked." if args.check else f"Formatted {len(stale)} files.")


if __name__ == "__main__":
    main()
