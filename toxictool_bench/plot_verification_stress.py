#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


LABELS = {
    "langgraph_react_verification_only": "Verification-only",
    "langgraph_react_double_pass": "Double-pass",
    "langgraph_react_guarded": "Generic Guard",
}
COLORS = {
    "langgraph_react_verification_only": "#2C5F8A",
    "langgraph_react_double_pass": "#B06A2B",
    "langgraph_react_guarded": "#2F7659",
}
MARKERS = {
    "langgraph_react_verification_only": "o",
    "langgraph_react_double_pass": "s",
    "langgraph_react_guarded": "D",
}
SUITES = ["numerical_iclr2027", "semantic_schema_iclr2027", "realistic_extension_iclr2027"]
TITLES = ["Numerical", "Semantic/schema", "Multi-table"]
METRICS = [("toxic_tsr", "Poisoned TSR"), ("bcr", "BCR"), ("rr", "RR")]


def main() -> None:
    source = Path("toxictool_bench/results/verification_stress_summary.csv")
    rows = list(csv.DictReader(source.open(encoding="utf-8")))
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["DejaVu Serif"],
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "legend.fontsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
    })
    fig, axes = plt.subplots(3, 3, figsize=(7.0, 6.1), sharex=True, sharey="row")
    for column, (suite, title) in enumerate(zip(SUITES, TITLES)):
        for row_index, (metric, ylabel) in enumerate(METRICS):
            ax = axes[row_index, column]
            for adapter in LABELS:
                selected = sorted(
                    (row for row in rows if row["suite"] == suite and row["adapter"] == adapter),
                    key=lambda row: float(row["poison_probability"]),
                )
                x = [float(row["poison_probability"]) for row in selected]
                y = [float(row[metric]) for row in selected]
                ax.plot(x, y, color=COLORS[adapter], marker=MARKERS[adapter], linewidth=1.6,
                        markersize=4.2, label=LABELS[adapter])
            ax.set_ylim(-0.04, 1.04)
            ax.set_xticks([0.25, 0.50, 0.75, 1.00])
            ax.set_yticks([0.0, 0.5, 1.0])
            ax.grid(axis="y", color="#D6D6D6", linewidth=0.6)
            ax.spines[["top", "right"]].set_visible(False)
            if row_index == 0:
                ax.set_title(title, fontweight="bold")
            if column == 0:
                ax.set_ylabel(ylabel)
            if row_index == 2:
                ax.set_xlabel("Verification-route poison probability")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.955), h_pad=1.0, w_pad=0.8)
    output = Path("figures/verification_stress_curves")
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
