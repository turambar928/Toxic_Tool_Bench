"""Generate publication figures from the public ToxicBench result artifacts.

The script intentionally allowlists adapters that are part of the paper. This
prevents historical internal adapter runs from entering a figure by accident.
PDF is the primary output for Overleaf; ``--preview-dir`` optionally writes
PNG previews for visual inspection.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


PUBLIC_ADAPTERS = {
    "autogen_tool_agent": "AutoGen",
    "langgraph_react_full": "LangGraph ReAct",
    "pandasai_dataframe": "PandasAI",
    "smolagents_toolcalling": "smolagents",
}
EXPANDED_ADAPTERS = {
    "autogen_tool_agent": "AutoGen",
    "langgraph_react_full": "LangGraph ReAct",
    "smolagents_toolcalling": "smolagents",
}

COLORS = {
    "navy": "#1F3A5F",
    "blue": "#557EA8",
    "orange": "#C96F52",
    "teal": "#428985",
    "red": "#A94F4F",
    "gold": "#B08A3E",
    "ink": "#25313C",
    "muted": "#687782",
    "grid": "#D7DEE4",
    "paper": "#FFFFFF",
}

mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "axes.titleweight": "semibold",
    "axes.labelweight": "regular",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mean(rows: list[dict[str, str]], key: str) -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def style_axes(ax: mpl.axes.Axes) -> None:
    ax.set_facecolor(COLORS["paper"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS["grid"])
    ax.spines["bottom"].set_color(COLORS["grid"])
    ax.tick_params(colors=COLORS["ink"], labelsize=8, length=0)
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.6, alpha=0.8)
    ax.set_axisbelow(True)


def save_figure(fig: mpl.figure.Figure, output: Path, preview_dir: Path | None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight", pad_inches=0.04)
    if preview_dir is not None:
        preview_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(preview_dir / (output.stem + ".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_cross_agent_model(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    expanded = [
        row
        for row in read_csv(results_dir / "iclr2027_gpt_expanded_cross_agent_combined_summary.csv")
        if row["adapter"] in EXPANDED_ADAPTERS
    ]
    expanded.sort(key=lambda row: list(EXPANDED_ADAPTERS).index(row["adapter"]))
    models: list[dict[str, str]] = []
    for path, suite in [
        ("public_cross_model_numerical_summary.csv", "Numerical"),
        ("public_cross_model_semantic_schema_summary.csv", "Semantic/schema"),
    ]:
        models.extend({**row, "suite": suite} for row in read_csv(results_dir / path))
    model_order = ["gpt-5.4-mini", "claude-sonnet-4-6", "Qwen3.6-35B-A3B-no-thinking"]
    suite_order = ["Numerical", "Semantic/schema"]
    models.sort(key=lambda row: (suite_order.index(row["suite"]), model_order.index(row["model"])))

    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.65), gridspec_kw={"width_ratios": [1.05, 1.35, 1.25]})
    ax = axes[0]
    style_axes(ax)
    x = np.arange(len(expanded))
    width = 0.34
    clean = [float(row["clean_tsr"]) for row in expanded]
    poisoned = [float(row["poisoned_tsr"]) for row in expanded]
    ax.bar(x - width / 2, clean, width, color=COLORS["blue"], label="Clean TSR")
    ax.bar(x + width / 2, poisoned, width, color=COLORS["orange"], label="Poisoned TSR")
    # Keep adapter labels short enough for the compact three-panel layout.
    ax.set_xticks(x, ["Auto\nGen", "Lang\nGraph", "smol.\nagents"])
    ax.tick_params(axis="x", labelsize=7, pad=3)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Task success rate", fontsize=8)
    ax.set_title("Expanded GPT-only evaluation", fontsize=8.5, weight="semibold", pad=8)
    for i, value in enumerate(poisoned):
        ax.text(i + width / 2, value + 0.025, f"{value:.2f}", ha="center", fontsize=7, color=COLORS["ink"])
    ax.text(-0.14, 1.16, "a", transform=ax.transAxes, fontsize=10, weight="bold")

    ax = axes[1]
    style_axes(ax)
    y = np.arange(len(models))
    clean = np.array([float(row["clean_tsr"]) for row in models])
    poisoned = np.array([float(row["poisoned_tsr"]) for row in models])
    for i, row in enumerate(models):
        color = COLORS["navy"] if row["suite"] == "Numerical" else COLORS["teal"]
        ax.plot([poisoned[i], clean[i]], [i, i], color=COLORS["grid"], linewidth=2, zorder=1)
        ax.scatter(clean[i], i, s=30, color=COLORS["blue"], edgecolor="white", linewidth=0.7, zorder=3)
        ax.scatter(poisoned[i], i, s=30, color=COLORS["orange"], edgecolor="white", linewidth=0.7, zorder=3)
    labels = [f"{'Num.' if row['suite'] == 'Numerical' else 'Sem.'} / {row['model'].replace('Qwen3.6-35B-A3B-no-thinking', 'Qwen').replace('claude-sonnet-4-6', 'Claude').replace('gpt-5.4-mini', 'GPT')}" for row in models]
    ax.set_yticks(y, labels)
    ax.set_xlim(0.25, 1.05)
    ax.set_xlabel("TSR", fontsize=8)
    ax.set_title("Paired clean-to-poisoned shift", fontsize=8.5, weight="semibold", pad=8)
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.6)
    ax.grid(axis="y", visible=False)
    ax.text(-0.14, 1.16, "b", transform=ax.transAxes, fontsize=10, weight="bold")

    ax = axes[2]
    style_axes(ax)
    bcr = np.array([float(row["toxic_bcr"]) for row in models])
    ax.barh(y, bcr, color=[COLORS["navy"] if row["suite"] == "Numerical" else COLORS["teal"] for row in models], height=0.58)
    ax.set_yticks(y, [f"{'Sem.' if row['suite'] == 'Semantic/schema' else 'Num.'} / {row['model'].replace('Qwen3.6-35B-A3B-no-thinking', 'Qwen').replace('claude-sonnet-4-6', 'Claude').replace('gpt-5.4-mini', 'GPT')}" for row in models])
    ax.set_xlim(0, 0.85)
    ax.set_xlabel("BCR", fontsize=8)
    ax.set_title("Blind compliance", fontsize=8.5, weight="semibold", pad=8)
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.6)
    ax.grid(axis="y", visible=False)
    ax.text(-0.14, 1.16, "c", transform=ax.transAxes, fontsize=10, weight="bold")
    fig.legend(
        [Patch(facecolor=COLORS["blue"]), Patch(facecolor=COLORS["orange"])],
        ["Clean TSR", "Poisoned TSR"],
        frameon=False, fontsize=7, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 0.005),
        columnspacing=1.2, handlelength=1.2,
    )
    fig.subplots_adjust(wspace=0.72, left=0.08, right=0.99, bottom=0.31, top=0.78)
    save_figure(fig, output_dir / "fig_cross_agent_model.pdf", preview_dir)


def plot_poison_types(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    rows = read_csv(results_dir / "public_poison_type_summary.csv")
    order = ["sign_flip", "aggregate_scale", "rank_swap"]
    rows.sort(key=lambda row: order.index(row["poison_type"]))
    labels = {"sign_flip": "Sign flip", "aggregate_scale": "Aggregate scale", "rank_swap": "Rank swap"}
    metrics = [("bcr", "BCR", COLORS["orange"]), ("vr", "VR", COLORS["teal"]), ("rr", "RR", COLORS["blue"])]
    values = np.array([[float(row[key]) for key, _, _ in metrics] for row in rows])
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.35), gridspec_kw={"width_ratios": [1.4, 1]})
    ax = axes[0]
    style_axes(ax)
    x = np.arange(len(rows))
    width = 0.23
    for j, (_, label, color) in enumerate(metrics):
        ax.bar(x + (j - 1) * width, values[:, j], width, color=color, label=label)
    ax.set_xticks(x, ["Sign\nflip", "Aggregate\nscale", "Rank\nswap"])
    ax.tick_params(axis="x", labelsize=7, pad=3)
    ax.set_ylim(0, 0.72)
    ax.set_ylabel("Rate", fontsize=8)
    ax.set_title("Behavior by numerical poison type", fontsize=8.5, weight="semibold", pad=8)
    ax.legend(frameon=False, fontsize=7, ncol=3, loc="upper left")
    ax.text(-0.08, 1.08, "a", transform=ax.transAxes, fontsize=10, weight="bold")

    ax = axes[1]
    ax.set_facecolor(COLORS["paper"])
    im = ax.imshow(values, cmap=mpl.colors.LinearSegmentedColormap.from_list("paper_heat", ["#F4F7F8", "#B5D5D0", "#3A8D8D"]), vmin=0, vmax=0.72, aspect="auto")
    ax.set_xticks(np.arange(len(metrics)), [label for _, label, _ in metrics])
    ax.set_yticks(np.arange(len(rows)), [labels[row["poison_type"]] for row in rows])
    ax.tick_params(labelsize=8, length=0)
    ax.set_title("Rate profile", fontsize=8.5, weight="semibold", pad=8)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            ax.text(j, i, f"{values[i, j]:.2f}", ha="center", va="center", fontsize=8, color=COLORS["ink"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=7, length=0)
    cbar.outline.set_visible(False)
    ax.text(-0.18, 1.08, "b", transform=ax.transAxes, fontsize=10, weight="bold")
    fig.subplots_adjust(wspace=0.42, left=0.08, right=0.96, bottom=0.29, top=0.82)
    save_figure(fig, output_dir / "fig_poison_type_behavior.pdf", preview_dir)


def plot_guard_tradeoff(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    ablation = {row["adapter"]: row for row in read_csv(results_dir / "langgraph_guarded_ablation_summary.csv")}
    overhead_rows = read_csv(results_dir / "langgraph_guarded_overhead_summary.csv")
    events: dict[str, list[float]] = defaultdict(list)
    for row in overhead_rows:
        if row["env"] == "toxic":
            events[row["adapter"]].append(float(row["mean_tool_events"]))
    variants = ["Base", "Caution only", "Expectation only", "Verification only", "Full guard", "Light guard"]
    colors = [COLORS["muted"], COLORS["gold"], COLORS["gold"], COLORS["teal"], COLORS["navy"], COLORS["blue"]]
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.85), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    style_axes(ax)
    xvals = np.array([np.mean(events[v]) for v in variants])
    yvals = np.array([float(ablation[v]["poisoned_tsr"]) for v in variants])
    bcr = np.array([float(ablation[v]["bcr"]) for v in variants])
    sizes = 85 + 250 * (1 - bcr)
    ax.scatter(xvals, yvals, s=sizes, c=colors, edgecolor="white", linewidth=0.8, zorder=3)
    short_names = {"Base": "B", "Caution only": "C", "Expectation only": "E", "Verification only": "V", "Full guard": "F", "Light guard": "L"}
    for x, y, variant in zip(xvals, yvals, variants):
        ax.text(x, y, short_names[variant], ha="center", va="center", fontsize=7, weight="bold", color="white", zorder=4)
    ax.set_xlabel("Mean poisoned tool events", fontsize=8)
    ax.set_ylabel("Poisoned TSR", fontsize=8)
    ax.set_xlim(1.7, 5.35)
    ax.set_ylim(0.55, 1.01)
    ax.set_title("Robustness versus verification budget", fontsize=8.5, weight="semibold", pad=8)
    handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=6, label=f"{short_names[name]} {name}") for name, color in zip(variants, colors)]
    ax.legend(handles=handles, frameon=False, fontsize=6.2, ncol=3, loc="upper left", bbox_to_anchor=(0.0, -0.22), handletextpad=0.25, columnspacing=0.7)
    ax.text(-0.08, 1.08, "a", transform=ax.transAxes, fontsize=10, weight="bold")

    latency = read_csv(results_dir / "guard_cost_latency_distribution.csv")
    ax = axes[1]
    style_axes(ax)
    names = ["LG\nbase", "LG\nfull", "LG\nlight", "AG\nverify", "AG\nguarded"]
    rows = {row["adapter"]: row for row in latency}
    keys = ["LangGraph base", "LangGraph full guard", "LangGraph light guard", "AutoGen verification-only", "AutoGen guarded"]
    means = [float(rows[k]["mean_elapsed_seconds"]) for k in keys]
    p50 = [float(rows[k]["p50_elapsed_seconds"]) for k in keys]
    p90 = [float(rows[k]["p90_elapsed_seconds"]) for k in keys]
    x = np.arange(len(keys))
    ax.bar(x, means, color=[COLORS["muted"], COLORS["navy"], COLORS["blue"], COLORS["teal"], COLORS["teal"]], width=0.62)
    ax.vlines(x, p50, p90, color=COLORS["ink"], linewidth=2, zorder=3)
    ax.scatter(x, p50, color=COLORS["paper"], edgecolor=COLORS["ink"], s=20, zorder=4, label="P50")
    ax.scatter(x, p90, color=COLORS["ink"], s=18, zorder=4, label="P90")
    ax.set_xticks(x, names, fontsize=7)
    ax.set_ylabel("Wall-clock seconds", fontsize=8)
    ax.set_ylim(0, 36)
    ax.set_title("Latency distribution", fontsize=8.5, weight="semibold", pad=8)
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    ax.text(-0.1, 1.08, "b", transform=ax.transAxes, fontsize=10, weight="bold")
    fig.subplots_adjust(wspace=0.38, left=0.08, right=0.99, bottom=0.36, top=0.82)
    save_figure(fig, output_dir / "fig_guard_tradeoff.pdf", preview_dir)


def plot_severity(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    allowed = set(EXPANDED_ADAPTERS)
    rows = [
        row
        for row in read_csv(results_dir / "iclr2027_gpt_expanded_cross_agent_combined_severity_summary.csv")
        if row["adapter"] in allowed
    ]
    operators = sorted({row["poison_type"] for row in rows})
    severities = ["obvious", "plausible", "subtle"]
    matrix = np.full((len(operators), len(severities)), np.nan)
    for i, operator in enumerate(operators):
        for j, severity in enumerate(severities):
            group = [row for row in rows if row["poison_type"] == operator and row["severity"] == severity]
            if group:
                matrix[i, j] = mean(group, "bcr")
    pretty = {
        "aggregate_scale": "Aggregate scale", "biased_retrieval": "Biased retrieval", "column_semantic_swap": "Column swap",
        "denominator_swap": "Denominator", "label_swap": "Label swap", "missing_filter": "Missing filter",
        "rank_swap": "Rank swap", "ratio_inversion": "Ratio inversion", "sign_flip": "Sign flip",
        "stale_metadata": "Stale metadata", "treatment_control_flip": "Treatment/control", "unit_conversion": "Unit conversion",
    }
    fig, ax = plt.subplots(figsize=(7.15, 3.05))
    im = ax.imshow(matrix, cmap=mpl.colors.LinearSegmentedColormap.from_list("severity_heat", ["#F4F7F8", "#F2C28A", "#B54A4A"]), vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(severities)), [s.capitalize() for s in severities])
    ax.set_yticks(np.arange(len(operators)), [pretty.get(x, x.replace("_", " ").title()) for x in operators])
    ax.tick_params(labelsize=8, length=0)
    ax.set_xlabel("Poison severity", fontsize=8)
    ax.set_title("Blind compliance across poison severity levels", fontsize=9, weight="semibold", pad=9)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if not np.isnan(matrix[i, j]):
                ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", fontsize=7.5, color=COLORS["ink"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("BCR", fontsize=8)
    cbar.ax.tick_params(labelsize=7, length=0)
    cbar.outline.set_visible(False)
    save_figure(fig, output_dir / "fig_severity_heatmap.pdf", preview_dir)


def plot_semantic_types(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    rows = [
        row for row in read_csv(results_dir / "semantic_schema_cross_model_poison_summary.csv")
        if row["adapter"] in PUBLIC_ADAPTERS
    ]
    order = ["biased_retrieval", "column_semantic_swap", "label_swap", "stale_metadata", "treatment_control_flip"]
    labels = {
        "biased_retrieval": "Biased\nretrieval",
        "column_semantic_swap": "Column\nswap",
        "label_swap": "Label\nswap",
        "stale_metadata": "Stale\nmetadata",
        "treatment_control_flip": "Treatment/\ncontrol",
    }
    metrics = [("bcr", "BCR", COLORS["orange"]), ("adr", "ADR", COLORS["gold"]),
               ("vr", "VR", COLORS["teal"]), ("rr", "RR", COLORS["blue"])]
    grouped = []
    for poison_type in order:
        subset = [row for row in rows if row["poison_type"] == poison_type]
        grouped.append([mean(subset, key) if subset else np.nan for key, _, _ in metrics])
    values = np.array(grouped)
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.55), gridspec_kw={"width_ratios": [1.45, 1]})
    ax = axes[0]
    style_axes(ax)
    x = np.arange(len(order))
    width = 0.19
    for j, (_, label, color) in enumerate(metrics):
        ax.bar(x + (j - 1.5) * width, values[:, j], width, color=color, label=label)
    ax.set_xticks(x, [labels[name] for name in order])
    ax.tick_params(axis="x", labelsize=7, pad=3)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Rate", fontsize=8)
    ax.set_title("Behavior by semantic poison type", fontsize=8.5, weight="semibold", pad=8)
    ax.legend(frameon=False, fontsize=7, ncol=4, loc="upper left", columnspacing=0.7, handlelength=1.0)
    ax.text(-0.08, 1.08, "a", transform=ax.transAxes, fontsize=10, weight="bold")

    ax = axes[1]
    cmap = mpl.colors.LinearSegmentedColormap.from_list("semantic_heat", ["#F5F7F8", "#C8DCD9", "#428985"])
    im = ax.imshow(values, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(metrics)), [label for _, label, _ in metrics])
    ax.set_yticks(np.arange(len(order)), [labels[name].replace("\n", " ") for name in order])
    ax.tick_params(labelsize=7, length=0)
    ax.set_title("Rate profile", fontsize=8.5, weight="semibold", pad=8)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            if not np.isnan(values[i, j]):
                ax.text(j, i, f"{values[i, j]:.2f}", ha="center", va="center", fontsize=7, color=COLORS["ink"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Rate", fontsize=8)
    cbar.ax.tick_params(labelsize=7, length=0)
    cbar.outline.set_visible(False)
    ax.text(-0.18, 1.08, "b", transform=ax.transAxes, fontsize=10, weight="bold")
    fig.subplots_adjust(wspace=0.42, left=0.08, right=0.96, bottom=0.28, top=0.82)
    save_figure(fig, output_dir / "fig_semantic_poison_profile.pdf", preview_dir)


def plot_guard_suite_breakdown(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    rows = read_csv(results_dir / "langgraph_guarded_ablation_suite_summary.csv")
    variants = ["Base", "Caution only", "Expectation only", "Verification only", "Full guard", "Light guard"]
    short = ["Base", "Caution", "Expect.", "Verify", "Full", "Light"]
    suites = ["numerical", "semantic/schema"]
    colors = [COLORS["muted"], COLORS["gold"], COLORS["gold"], COLORS["teal"], COLORS["navy"], COLORS["blue"]]
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.65), sharey=True)
    y = np.arange(len(variants))
    for ax, metric, title, xlabel in zip(
        axes, ["poisoned_tsr", "bcr"], ["Poisoned task success", "Blind compliance"], ["Poisoned TSR", "BCR"]
    ):
        style_axes(ax)
        for i, suite in enumerate(suites):
            values = [float(next(row[metric] for row in rows if row["suite"] == suite and row["adapter"] == variant)) for variant in variants]
            offset = (i - 0.5) * 0.30
            ax.barh(y + offset, values, height=0.25, color=COLORS["navy"] if i == 0 else COLORS["teal"], label=suite.title())
        ax.set_xlim(0, 1.05)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.set_title(title, fontsize=8.5, weight="semibold", pad=8)
        ax.grid(axis="x", color=COLORS["grid"], linewidth=0.6)
        ax.grid(axis="y", visible=False)
        ax.set_yticks(y, short)
        ax.invert_yaxis()
        ax.legend(frameon=False, fontsize=7, loc="lower right")
    axes[0].text(-0.12, 1.08, "a", transform=axes[0].transAxes, fontsize=10, weight="bold")
    axes[1].text(-0.12, 1.08, "b", transform=axes[1].transAxes, fontsize=10, weight="bold")
    fig.subplots_adjust(wspace=0.2, left=0.12, right=0.98, bottom=0.18, top=0.82)
    save_figure(fig, output_dir / "fig_guard_suite_breakdown.pdf", preview_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("toxictool_bench/results"))
    parser.add_argument("--output-dir", type=Path, default=Path("figures"))
    parser.add_argument("--preview-dir", type=Path)
    return parser.parse_args()


def configure_matplotlib() -> None:
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Nimbus Roman", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )


def main() -> None:
    args = parse_args()
    configure_matplotlib()
    plot_cross_agent_model(args.results_dir, args.output_dir, args.preview_dir)
    plot_poison_types(args.results_dir, args.output_dir, args.preview_dir)
    plot_guard_tradeoff(args.results_dir, args.output_dir, args.preview_dir)
    plot_severity(args.results_dir, args.output_dir, args.preview_dir)
    plot_semantic_types(args.results_dir, args.output_dir, args.preview_dir)
    plot_guard_suite_breakdown(args.results_dir, args.output_dir, args.preview_dir)


if __name__ == "__main__":
    main()
