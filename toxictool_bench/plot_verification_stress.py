#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt


LABELS = {
    "langgraph_react_verification_only": "Verification-only",
    "langgraph_react_double_pass": "Double-pass",
    "langgraph_react_guarded": "Generic Guard",
}
COLORS = {
    "langgraph_react_verification_only": "#2F75A3",
    "langgraph_react_double_pass": "#D97745",
    "langgraph_react_guarded": "#3E8E7E",
}
MARKERS = {
    "langgraph_react_verification_only": "o",
    "langgraph_react_double_pass": "s",
    "langgraph_react_guarded": "D",
}
SUITES = ["numerical_iclr2027", "semantic_schema_iclr2027", "realistic_extension_iclr2027"]
TITLES = ["Numerical", "Semantic/schema", "Multi-table ($n=13$)"]


def main() -> None:
    source = Path("toxictool_bench/results/verification_stress_summary.csv")
    rows = list(csv.DictReader(source.open(encoding="utf-8")))
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 8,
        "axes.titlesize": 8.5,
        "axes.labelsize": 8,
        "legend.fontsize": 7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.2), sharex=True, sharey=True)
    for column, (ax, suite, title) in enumerate(zip(axes, SUITES, TITLES)):
        for adapter in LABELS:
            selected = sorted(
                (row for row in rows if row["suite"] == suite and row["adapter"] == adapter),
                key=lambda row: float(row["poison_probability"]),
            )
            x = [float(row["poison_probability"]) for row in selected]
            y = [float(row["bcr"]) for row in selected]
            ax.plot(x, y, color=COLORS[adapter], marker=MARKERS[adapter], linewidth=1.35,
                    markersize=4.5, label=LABELS[adapter])
        ax.set_ylim(-0.04, 1.04)
        ax.set_xticks([0.25, 0.50, 0.75, 1.00])
        ax.set_yticks([0.0, 0.5, 1.0])
        ax.grid(axis="y", color="#E5EDF1", linewidth=0.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color("#CADAE2")
        ax.tick_params(length=0, colors="#5E7D8D")
        ax.set_title(title, fontweight="semibold", pad=6)
        ax.text(-0.12, 1.03, f"({chr(97 + column)})", transform=ax.transAxes,
                fontsize=8.5, fontweight="bold", va="bottom")
    axes[0].set_ylabel("Blind compliance rate")
    fig.supxlabel("Verification-route poison probability", fontsize=8, y=0.04)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.02), handlelength=1.8, columnspacing=1.2)
    fig.subplots_adjust(left=0.08, right=0.995, top=0.76, bottom=0.26, wspace=0.18)
    output = Path("figures/verification_stress_curves")
    fig.savefig(output.with_suffix(".pdf"))
    fig.savefig(output.with_suffix(".png"), dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
