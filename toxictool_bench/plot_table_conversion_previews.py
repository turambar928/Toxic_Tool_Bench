"""Standalone vector previews; never edits manuscript or existing figures."""
from pathlib import Path
import argparse
import hashlib
import json
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Patch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper/previews/table_figure_previews_20260921_v6"
PRIMARY = "#54A88D"
SECONDARY = "#ADD5A2"
DEFENSE_PRIMARY = "#9785D3"
DEFENSE_SECONDARY = "#E4AEC8"
INK = "#253448"
MUTED = "#657080"
GRID = "#E3E7EC"
CMAP = LinearSegmentedColormap.from_list("evidence_coral", ["#FFF6E9", "#F4C697", "#DD816E"])


def read_rows(path):
    rows = []
    for line in path.read_text().splitlines():
        if "&" in line and line.rstrip().endswith(r"\\"):
            rows.append([v.strip() for v in line.strip()[:-2].split("&")])
    return rows


def load_data():
    defense_path = ROOT / "paper/figures/defense_comparison_data.tex"
    text = defense_path.read_text()
    table = next(t for t in re.findall(r"\\begin\{table\}(.*?)\\end\{table\}", text, re.S)
                 if r"\label{tab:langgraph-guarded}" in t)
    defense = []
    for line in table.splitlines():
        if re.match(r"^(Base|Double-pass|Verification only|Generic guard) &", line):
            cells = [v.strip() for v in line.strip()[:-2].split("&")]
            defense.append({"method": cells[0].replace("Verification only", "Verification-only")
                            .replace("Generic guard", "Generic Guard"),
                            **dict(zip(["clean_tsr", "poisoned_tsr", "bcr", "par", "vpa", "vr", "rr"],
                                       map(float, cells[1:8]))),
                            "exposed": int(cells[8])})
    assert len(defense) == 4
    evidence_path = ROOT / "output/evidence_controls_v4/results.tex"
    evidence = []
    for row in read_rows(evidence_path):
        if row[0] in ("Primary", "Retry", "Verify"):
            pairs = [[int(n) for n in s.split("/")] for s in row[2:]]
            evidence.append({"policy": row[0], "evidence": row[1], "source_counts": pairs,
                             "correct": sum(p[0] for p in pairs), "total": sum(p[1] for p in pairs)})
    assert len(evidence) == 7
    human_path = ROOT / "output/human_validation_20260920/method_comparison.tex"
    human = []
    for row in read_rows(human_path):
        if row[0] in ("Core", "Repeated, $p=1$", "Cross-model"):
            counts = [None if s == "--" else [int(n) for n in s.split("/")] for s in row[2:]]
            human.append({"setting": row[0], "method": row[1],
                          **dict(zip(["clean_auto", "clean_human", "poison_auto", "poison_human"], counts))})
    assert len(human) == 7
    for r in human:
        for key in ("clean_auto", "clean_human", "poison_auto", "poison_human"):
            if r[key] is not None:
                assert 0 <= r[key][0] <= r[key][1]
    return {"defense": defense, "evidence": evidence, "human": human,
            "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in [defense_path, evidence_path, human_path]}}


def style_axis(ax, labels):
    positions = np.arange(4) if len(labels) == 4 else np.linspace(.5, 2.5, len(labels))
    ax.set_xlim(-.65, 3.65)
    ax.set_ylim(0, 1.16)
    ax.set_yticks([0, .25, .5, .75, 1], ["0", ".25", ".50", ".75", "1.00"])
    ax.set_xticks(positions, labels)
    ax.yaxis.grid(True, color=GRID, linewidth=.6)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0, pad=6, labelsize=10)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return positions


def method_label(name):
    return name.replace("Double-pass", "Double-\npass").replace("Verification-only", "Verification-\nonly").replace("Generic Guard", "Generic\nGuard")


def paired_bars(ax, labels, first, second, count_labels=False, colors=None, baseline=0.0, separation=.22):
    positions = style_axis(ax, labels)
    if baseline:
        ax.set_ylim(baseline, 1.04)
        ticks = np.linspace(baseline, 1, 6)
        ax.set_yticks(ticks, [f"{t:.2f}" for t in ticks])
        for shift in (-.012, .012):
            ax.plot([-.016, .016], [shift - .014, shift + .014],
                    transform=ax.transAxes, color=MUTED, lw=1.1, clip_on=False)
    first_color, second_color = colors or (PRIMARY, SECONDARY)
    for offset, values, color in [(-separation, first, first_color), (separation, second, second_color)]:
        for i, value in enumerate(values):
            score = value[0] / value[1] if count_labels else value
            x = positions[i] + offset
            assert score >= baseline
            ax.bar(x, score - baseline, bottom=baseline, width=.34, color=color, zorder=3)
            label = f"{value[0]}/{value[1]}" if count_labels else f"{score:.2f}"
            ax.text(x, score + (.007 if baseline else .027), label, ha="center", va="bottom", fontsize=9, color=INK)


def defense_figure(data):
    rows = data["defense"]
    fig, axes = plt.subplots(1, 3, figsize=(11.8, 4.5),
                             gridspec_kw={"wspace": .27, "width_ratios": [1, 1.3, 1.05]})
    fig.subplots_adjust(left=.045, right=.985, top=.73, bottom=.30)
    labels = [method_label(r["method"]) for r in rows]
    paired_bars(axes[0], labels, [r["clean_tsr"] for r in rows], [r["poisoned_tsr"] for r in rows],
                colors=(DEFENSE_PRIMARY, DEFENSE_SECONDARY), baseline=.80, separation=.25)
    axes[0].set_yticks([.80, .85, .90, .95, 1], ["0.80", "0.85", "0.90", "0.95", "1.00"])
    axes[0].set_title("Task success", loc="left", pad=40, fontsize=13)
    axes[0].legend(handles=[Patch(color=DEFENSE_PRIMARY, label="Clean TSR"),
                            Patch(color=DEFENSE_SECONDARY, label="Poisoned TSR")],
                   loc="lower left", bbox_to_anchor=(-.02, 1.02), ncol=2, frameon=False,
                   fontsize=9.5, handlelength=1.1, columnspacing=1)

    positions = style_axis(axes[1], labels)
    axes[1].set_ylim(0, .118)
    ticks = [0, .02, .04, .06, .08, .10]
    axes[1].set_yticks(ticks, [f"{v:.2f}" for v in ticks])
    adoption_colors = [DEFENSE_PRIMARY, DEFENSE_SECONDARY, "#ADBCD8"]
    for offset, metric, color in zip([-.36, 0, .36], ["bcr", "par", "vpa"], adoption_colors):
        for i, row in enumerate(rows):
            value = row[metric]
            axes[1].bar(positions[i] + offset, value, width=.26, color=color, zorder=3)
            axes[1].text(positions[i] + offset, value + .003, "0" if value == 0 else f"{value:.2f}",
                         ha="center", va="bottom", color=INK, fontsize=8)
    axes[1].set_title("Poison adoption", loc="left", pad=40, fontsize=13)
    axes[1].legend(handles=[Patch(color=c, label=m) for c, m in zip(adoption_colors, ["BCR", "PAR", "VPA"])],
                   loc="lower left", bbox_to_anchor=(-.02, 1.02), ncol=3, frameon=False,
                   fontsize=9.5, handlelength=1.1, columnspacing=1)
    exposed_labels = [f"{method_label(r['method'])}\nn={r['exposed']}" for r in rows]
    paired_bars(axes[2], exposed_labels, [r["vr"] for r in rows], [r["rr"] for r in rows],
                colors=(DEFENSE_PRIMARY, DEFENSE_SECONDARY), separation=.25)
    axes[2].set_title("Checking and recovery", loc="left", pad=40, fontsize=13)
    axes[2].legend(handles=[Patch(color=DEFENSE_PRIMARY, label="Checks (VR)"), Patch(color=DEFENSE_SECONDARY, label="Recovery (RR)")],
                   loc="lower left", bbox_to_anchor=(-.02, 1.02), ncol=2, frameon=False,
                   fontsize=10, handlelength=1.2, columnspacing=1.2)
    fig.text(.045, .105, "TSR: all 118 tasks. BCR, PAR, VPA, VR and RR: exposed runs (n shown at right).",
             fontsize=10, color=MUTED)
    fig.text(.045, .05, "TSR axis starts at 0.80; adoption uses a separate scale. Zero labels denote 0.00, not missing values. Historical injector; frozen scoring.",
             fontsize=9, color=MUTED)
    return fig


def evidence_figure(data):
    lookup = {(r["policy"], r["evidence"]): r for r in data["evidence"]}
    counts = [[lookup[(p, e)] for p in ("Retry", "Verify")] for e in ("clean", "full")]
    assert all(r["total"] == 48 for row in counts for r in row)
    fig = plt.figure(figsize=(5.5, 2.0))
    ax = fig.add_axes([.29, .36, .65, .50])
    values = np.array([[r["correct"] / r["total"] for r in row] for row in counts])
    ax.set_xlim(-.5, 1.5)
    ax.set_ylim(1.5, -.5)
    for i in range(2):
        for j in range(2):
            ax.add_patch(Rectangle((j - .5, i - .5), 1, 1, facecolor=CMAP(values[i, j]), edgecolor="none"))
    ax.set_xticks([0, 1], ["Retry", "Review"])
    ax.xaxis.tick_top()
    ax.set_yticks([0, 1], ["Clean evidence", "Fully corrupted\nevidence"])
    ax.tick_params(length=0, pad=6, labelsize=10)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.axhline(.5, color="white", linewidth=3)
    ax.axvline(.5, color="white", linewidth=3)
    for i in range(2):
        for j in range(2):
            row = counts[i][j]
            color = "#392923"
            ax.text(j, i - .15, f"{row['correct']}/{row['total']}", ha="center", va="center", fontsize=11, color=color)
            ax.text(j, i + .22, f"{100 * values[i, j]:.1f}% correct", ha="center", va="center", fontsize=8.5, color=color)
    # Experimental setup belongs in the caption, not an oversized title/arrow.
    cax = fig.add_axes([.455, .20, .32, .035])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0, 1), cmap=CMAP), cax=cax,
                      orientation="horizontal", ticks=[0, .5, 1])
    cb.outline.set_visible(False)
    cb.solids.set_rasterized(False)
    cb.solids.set_edgecolor("face")  # Avoid hairline seams in vector viewers.
    cb.ax.set_xticklabels(["0%", "50%", "100%"])
    cb.ax.tick_params(length=0, labelsize=8, pad=2)
    cb.set_label("Correctness rate", fontsize=8, color=MUTED, labelpad=1)
    fig.text(.5, .025, "Two completions per task and condition; 48 completions are not 48 independent tasks.",
             ha="center", fontsize=8, color=MUTED)
    return fig


def human_figure(data):
    core = [r for r in data["human"] if r["setting"] == "Core"]
    repeated = [r for r in data["human"] if r["setting"].startswith("Repeated")]
    cross = next(r for r in data["human"] if r["setting"] == "Cross-model")
    fig, axes = plt.subplots(2, 2, figsize=(9, 6.5), gridspec_kw={"hspace": .72, "wspace": .30})
    fig.subplots_adjust(left=.075, right=.98, bottom=.14, top=.84)
    for ax, mode, title in [(axes[0, 0], "clean", "Core tasks · clean"),
                            (axes[0, 1], "poison", "Core tasks · poisoned")]:
        paired_bars(ax, [method_label(r["method"]) for r in core], [r[f"{mode}_auto"] for r in core],
                    [r[f"{mode}_human"] for r in core], count_labels=True, baseline=.75)
        ax.set_title(title + " · n=20", loc="left", fontsize=12, pad=14)
    paired_bars(axes[1, 0], [method_label(r["method"]) for r in repeated], [r["poison_auto"] for r in repeated],
                [r["poison_human"] for r in repeated], count_labels=True)
    axes[1, 0].set_title("Repeated poisoning · p=1 · n=10", loc="left", fontsize=12, pad=14)
    paired_bars(axes[1, 1], ["Clean", "Poisoned"], [cross["clean_auto"], cross["poison_auto"]],
                [cross["clean_human"], cross["poison_human"]], count_labels=True)
    axes[1, 1].set_title("Cross-model · AutoGen · n=10", loc="left", fontsize=12, pad=14)
    fig.legend(handles=[Patch(color=PRIMARY, label="Automatic scoring"), Patch(color=SECONDARY, label="Human labels")],
               loc="upper center", bbox_to_anchor=(.54, .98), ncol=2, frameon=False, fontsize=11)
    fig.text(.075, .06, "Top row: axes start at 0.75. Bottom row: axes start at zero.",
             color=MUTED, fontsize=10)
    fig.text(.075, .025, "Task success rate · labels show correct / total. Conditions are shown separately, not pooled.",
             color=MUTED, fontsize=10)
    return fig


def configure_style():
    plt.rcParams.update({"font.family": "Times New Roman", "font.size": 10, "text.color": INK,
                         "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": INK,
                         "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
                         "axes.unicode_minus": False, "savefig.facecolor": "white"})


def style_paper_figure(fig, builder):
    """Size labels for the manuscript, keeping rates upright and separated."""
    from matplotlib.text import Text
    if builder is defense_figure:
        # Move methodological notes into the LaTeX caption, not tiny image text.
        for note in list(fig.texts):
            note.remove()
        for text in fig.findobj(Text):
            text.set_fontsize(text.get_fontsize() * 1.38)
        for ax in fig.axes:
            labels = [t.get_text().replace("Verification-", "Verify-") for t in ax.get_xticklabels()]
            ax.set_xticks(ax.get_xticks(), labels, fontsize=13)
        # The slightly wider middle panel fits three horizontal rate labels.
        for text in fig.axes[1].texts:
            text.set_rotation(0)
            text.set_fontsize(11.5)
    elif builder is human_figure:
        for note in list(fig.texts):
            note.remove()
        for text in fig.findobj(Text):
            text.set_fontsize(text.get_fontsize() * 1.1)
    else:
        # The manuscript caption already explains the setup and sample size.
        for note in list(fig.texts):
            if "Two completions" in note.get_text():
                note.remove()


def export_paper_figures(only=None):
    """Approved designs with text sized for the paper's 5.5-inch text width."""
    configure_style()
    data = load_data()
    for name, builder in [("fig_defense_comparison", defense_figure),
                          ("fig_human_method_comparison", human_figure),
                          ("fig_evidence_control", evidence_figure)]:
        if only and name != only:
            continue
        fig = builder(data)
        style_paper_figure(fig, builder)
        for ext in ("pdf", "svg"):
            fig.savefig(ROOT / "paper/figures" / f"{name}.{ext}", bbox_inches="tight", pad_inches=.035)
        plt.close(fig)
    (ROOT / "paper/figures/table_conversion_data.json").write_text(json.dumps(data, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", action="store_true", help="Export the three integrated manuscript figures")
    parser.add_argument("--only", choices=["fig_defense_comparison", "fig_human_method_comparison", "fig_evidence_control"],
                        help="With --paper, regenerate just this figure")
    args = parser.parse_args()
    if args.only and not args.paper:
        parser.error("--only requires --paper")
    if args.paper:
        export_paper_figures(args.only)
        print(ROOT / "paper/figures")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    configure_style()
    data = load_data()
    (OUT / "source_data.json").write_text(json.dumps(data, indent=2) + "\n")
    with PdfPages(OUT / "all_three_previews.pdf") as combined:
        for name, builder in [("table3_method_comparison", defense_figure),
                              ("table26_evidence_control", evidence_figure),
                              ("table9_human_comparison", human_figure)]:
            fig = builder(data)
            for ext in ("pdf", "svg", "png"):
                fig.savefig(OUT / f"{name}.{ext}", dpi=200)
            combined.savefig(fig)
            plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
