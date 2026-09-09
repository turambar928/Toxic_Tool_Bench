"""Generate camera-ready ToxicBench figures from released result artifacts."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


PUBLIC_ADAPTERS = {
    "autogen_tool_agent": "AutoGen",
    "langgraph_react_full": "LangGraph",
    "pandasai_dataframe": "PandasAI",
    "smolagents_toolcalling": "smolagents",
}
EXPANDED_ADAPTERS = {
    "langgraph_react_full": "LangGraph",
    "smolagents_toolcalling": "smolagents",
    "autogen_tool_agent": "AutoGen",
}

# A single blue palette keeps the paper visually consistent; lightness separates roles.
COLORS = {
    "clean": "#4C93B5",
    "toxic": "#A9D2E5",
    "risk": "#1F5F82",
    "verify": "#6BAAC5",
    "recover": "#78B6D0",
    "exposure": "#3D7FA3",
    "neutral": "#A9C9D8",
    "ink": "#183B50",
    "muted": "#5E7D8D",
    "grid": "#D8E8F0",
    "light": "#F2F8FB",
    "paper": "#FFFFFF",
}

METRIC_CMAPS = {
    "tsr": mpl.colors.LinearSegmentedColormap.from_list("tsr", ["#F2F8FB", "#2F75A3"]),
    "bcr": mpl.colors.LinearSegmentedColormap.from_list("bcr", ["#FFF6F0", "#C65D36"]),
    "vr": mpl.colors.LinearSegmentedColormap.from_list("vr", ["#F0F8F7", "#3E8E7E"]),
    "rr": mpl.colors.LinearSegmentedColormap.from_list("rr", ["#F2F8F2", "#39724B"]),
    "pdr": mpl.colors.LinearSegmentedColormap.from_list("pdr", ["#F5F7F8", "#788991"]),
}


def configure_matplotlib() -> None:
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "axes.titleweight": "semibold",
            "axes.labelcolor": COLORS["ink"],
            "text.color": COLORS["ink"],
            "xtick.color": COLORS["muted"],
            "ytick.color": COLORS["muted"],
            "legend.fontsize": 7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mean(rows: list[dict[str, str]], key: str) -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def format_rate(value: float) -> str:
    rounded = np.floor(value * 100.0 + 0.5) / 100.0
    return f"{rounded:.2f}"


def style_axes(ax: mpl.axes.Axes, *, xgrid: bool = False) -> None:
    ax.set_facecolor(COLORS["paper"])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(COLORS["grid"])
    ax.tick_params(length=0, labelsize=7.5)
    ax.grid(axis="x" if xgrid else "y", color=COLORS["grid"], linewidth=0.55)
    ax.set_axisbelow(True)


def panel_label(ax: mpl.axes.Axes, label: str) -> None:
    ax.text(-0.12, 1.03, f"({label})", transform=ax.transAxes, fontsize=8.5,
            weight="bold", va="bottom", ha="left")


def draw_metric_matrix(
    ax: mpl.axes.Axes,
    values: np.ndarray,
    row_labels: list[str],
    column_labels: list[str],
    metric_types: list[str],
) -> None:
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]
            color = METRIC_CMAPS[metric_types[j]](value)
            ax.add_patch(mpl.patches.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=color,
                                               edgecolor="white", linewidth=0.7))
            ax.text(j, i, format_rate(value), ha="center", va="center", fontsize=7.2,
                    color="white" if value >= 0.72 else COLORS["ink"])
    ax.set_xlim(-0.5, values.shape[1] - 0.5)
    ax.set_ylim(values.shape[0] - 0.5, -0.5)
    ax.set_xticks(np.arange(len(column_labels)), column_labels)
    ax.set_yticks(np.arange(len(row_labels)), row_labels)
    ax.tick_params(length=0, labelsize=7.4)
    for spine in ax.spines.values():
        spine.set_visible(False)


def save_figure(fig: mpl.figure.Figure, output: Path, preview_dir: Path | None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    if preview_dir is not None:
        preview_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(preview_dir / f"{output.stem}.png", dpi=300)
    plt.close(fig)


def short_model(model: str) -> str:
    return {
        "gpt-5.4-mini": "GPT",
        "claude-sonnet-4-6": "Claude",
        "Qwen3.6-35B-A3B-no-thinking": "Qwen",
    }[model]


def plot_cross_agent_model(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    cross_model: list[dict[str, str]] = []
    for path, suite in (
        ("public_cross_model_numerical_summary.csv", "Numerical"),
        ("public_cross_model_semantic_schema_summary.csv", "Semantic/schema"),
    ):
        cross_model.extend({**row, "suite": suite} for row in read_csv(results_dir / path))
    model_order = ["gpt-5.4-mini", "claude-sonnet-4-6", "Qwen3.6-35B-A3B-no-thinking"]
    cross_model.sort(key=lambda row: (["Numerical", "Semantic/schema"].index(row["suite"]), model_order.index(row["model"])))

    columns = ["clean_tsr", "poisoned_tsr", "toxic_bcr", "poison_delivery_rate"]
    column_labels = [r"Clean TSR $\uparrow$", r"Poisoned TSR $\uparrow$", r"BCR $\downarrow$", "PDR"]
    labels = [f"{'Num.' if row['suite'] == 'Numerical' else 'Sem.'} / {short_model(row['model'])}" for row in cross_model]
    matrix = np.array([[float(row[key]) for key in columns] for row in cross_model])
    fig, ax = plt.subplots(figsize=(7.0, 2.95))
    draw_metric_matrix(ax, matrix, labels, column_labels, ["tsr", "tsr", "bcr", "pdr"])
    ax.axvline(2.5, color=COLORS["ink"], linewidth=0.8)
    ax.set_title("Cross-model results", pad=8)
    fig.subplots_adjust(left=0.20, right=0.91, top=0.87, bottom=0.16)
    save_figure(fig, output_dir / "fig_cross_agent_model.pdf", preview_dir)



def plot_operator_profile(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    numerical = {row["poison_type"]: row for row in read_csv(results_dir / "public_poison_type_summary.csv")}
    semantic_raw = [
        row for row in read_csv(results_dir / "semantic_schema_cross_model_poison_summary.csv")
        if row["adapter"] in PUBLIC_ADAPTERS
    ]
    semantic: dict[str, dict[str, float]] = {}
    for poison_type in sorted({row["poison_type"] for row in semantic_raw}):
        subset = [row for row in semantic_raw if row["poison_type"] == poison_type]
        semantic[poison_type] = {key: mean(subset, key) for key in ("toxic_tsr", "bcr", "vr", "rr", "poison_delivery_rate")}

    order = [
        ("aggregate_scale", "Aggregate scale", "Numerical"),
        ("rank_swap", "Rank swap", "Numerical"),
        ("sign_flip", "Sign flip", "Numerical"),
        ("label_swap", "Label swap", "Semantic/schema"),
        ("treatment_control_flip", "Treatment/control", "Semantic/schema"),
        ("stale_metadata", "Stale metadata", "Semantic/schema"),
        ("column_semantic_swap", "Column swap", "Semantic/schema"),
        ("biased_retrieval", "Biased retrieval", "Semantic/schema"),
    ]
    metrics = [
        ("toxic_tsr", r"Poisoned TSR $\uparrow$"),
        ("bcr", r"BCR $\downarrow$"),
        ("vr", "VR"),
        ("rr", "RR"),
        ("poison_delivery_rate", "PDR"),
    ]
    matrix = []
    for key, _, family in order:
        source = numerical[key] if family == "Numerical" else semantic[key]
        matrix.append([float(source[metric]) for metric, _ in metrics])
    values = np.asarray(matrix)

    fig, ax = plt.subplots(figsize=(7.0, 3.05))
    draw_metric_matrix(
        ax, values, [label for _, label, _ in order], [label for _, label in metrics],
        ["tsr", "bcr", "vr", "rr", "pdr"],
    )
    ax.axvline(1.5, color=COLORS["ink"], linewidth=0.8)
    ax.axvline(3.5, color=COLORS["ink"], linewidth=0.8)
    ax.set_title("Operator profiles", pad=8)
    fig.subplots_adjust(left=0.20, right=0.99, top=0.87, bottom=0.15)
    save_figure(fig, output_dir / "fig_operator_profile.pdf", preview_dir)


def plot_guard_tradeoff(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    ablation = {row["adapter"]: row for row in read_csv(results_dir / "langgraph_guarded_ablation_summary.csv")}
    overhead_rows = read_csv(results_dir / "langgraph_guarded_overhead_summary.csv")
    events: dict[str, list[float]] = defaultdict(list)
    for row in overhead_rows:
        if row["env"] == "toxic":
            events[row["adapter"]].append(float(row["mean_tool_events"]))
    variants = ["Base", "Caution only", "Expectation only", "Verification only", "Full guard", "Light guard"]
    labels = ["Base", "Caution", "Expectation", "Verify", "Full", "Light"]
    variant_colors = ["#DCEEF5", "#B9DCEC", "#91C4DB", "#68A9C7", "#3E83A8", "#1F5F82"]

    fig, axes = plt.subplots(1, 3, figsize=(7.12, 2.55), gridspec_kw={"width_ratios": [1.16, 1.0, 1.0]})

    ax = axes[0]
    style_axes(ax)
    x = np.arange(len(variants))
    toxic_tsr = np.array([float(ablation[v]["poisoned_tsr"]) for v in variants])
    bcr = np.array([float(ablation[v]["bcr"]) for v in variants])
    ax.scatter(x - 0.12, toxic_tsr, color=COLORS["clean"], s=25, label="Poisoned TSR", zorder=3)
    ax.scatter(x + 0.12, bcr, color=COLORS["risk"], marker="D", s=22, label="BCR", zorder=3)
    ax.set_xticks(x, labels, rotation=28, ha="right")
    ax.set_ylim(-0.03, 1.03)
    ax.set_ylabel("Rate")
    ax.set_title("Defense ablation", pad=7)
    ax.legend(frameon=False, loc="lower right", handlelength=1.0)
    panel_label(ax, "a")

    ax = axes[1]
    style_axes(ax)
    cost = {row["adapter"]: row for row in read_csv(results_dir / "guard_cost_latency_distribution.csv")}
    keys = ["LangGraph base", "LangGraph full guard", "LangGraph light guard", "AutoGen verification-only", "AutoGen guarded"]
    names = ["LG base", "LG full", "LG light", "AG verify", "AG guard"]
    means = np.array([float(cost[key]["mean_elapsed_seconds"]) for key in keys])
    p50 = np.array([float(cost[key]["p50_elapsed_seconds"]) for key in keys])
    p90 = np.array([float(cost[key]["p90_elapsed_seconds"]) for key in keys])
    x = np.arange(len(keys))
    ax.hlines(x, p50, p90, color=COLORS["muted"], linewidth=2.0, zorder=2)
    ax.scatter(means, x, color=COLORS["clean"], s=25, zorder=3, label="Mean")
    ax.scatter(p50, x, facecolor="white", edgecolor=COLORS["ink"], s=22, zorder=3, label="p50")
    ax.scatter(p90, x, color=COLORS["ink"], s=20, zorder=3, label="p90")
    ax.set_yticks(x, names)
    ax.invert_yaxis()
    ax.set_xlim(0, max(35, float(p90.max()) + 3))
    ax.set_ylim(-0.5, len(keys) - 0.5)
    ax.set_xlabel("Seconds / task")
    ax.set_title("Measured latency", pad=7)
    panel_label(ax, "b")

    ax = axes[2]
    style_axes(ax)
    stress = read_csv(results_dir / "iclr2027_semantic_guard_multiroute_stress_strict_summary.csv")
    p = np.array([float(row["adapter"].split("=")[1]) for row in stress])
    tsr = np.array([float(row["poisoned_tsr"]) for row in stress])
    bcr = np.array([np.nan if int(row["n_exposed"]) == 0 else float(row["bcr"]) for row in stress])
    rr = np.array([np.nan if int(row["n_exposed"]) == 0 else float(row["rr"]) for row in stress])
    ax.plot(p, tsr, color=COLORS["clean"], marker="o", linewidth=1.4, markersize=4, label="Poisoned TSR")
    ax.plot(p, bcr, color=COLORS["risk"], marker="D", linewidth=1.4, markersize=3.8, label="BCR")
    ax.plot(p, rr, color=COLORS["verify"], marker="s", linewidth=1.4, markersize=3.8, label="RR")
    ax.set_xticks(p, [f"{value:g}" for value in p])
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("Poison probability $p$\n(eligible observations)")
    ax.set_title("Route-corruption stress test", pad=7)
    ax.legend(frameon=False, loc="lower left", handlelength=1.0)
    panel_label(ax, "c")

    fig.subplots_adjust(left=0.07, right=0.995, top=0.84, bottom=0.31, wspace=0.42)
    save_figure(fig, output_dir / "fig_guard_tradeoff.pdf", preview_dir)


def plot_severity(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    rows = [
        row for row in read_csv(results_dir / "iclr2027_gpt_expanded_cross_agent_combined_severity_summary.csv")
        if row["adapter"] in EXPANDED_ADAPTERS
    ]
    operators = sorted({row["poison_type"] for row in rows})
    severities = ["obvious", "plausible", "subtle"]
    matrix = np.full((len(operators), len(severities)), np.nan)
    counts = np.zeros((len(operators), len(severities)), dtype=int)
    for i, operator in enumerate(operators):
        for j, severity in enumerate(severities):
            group = [row for row in rows if row["poison_type"] == operator and row["severity"] == severity]
            if group:
                counts[i, j] = sum(int(row["n_exposed"]) for row in group)
                if counts[i, j] > 0:
                    matrix[i, j] = mean(group, "bcr")
    pretty = {
        "aggregate_scale": "Aggregate scale", "biased_retrieval": "Biased retrieval", "column_semantic_swap": "Column swap",
        "denominator_swap": "Denominator swap", "label_swap": "Label swap", "missing_filter": "Missing filter",
        "rank_swap": "Rank swap", "ratio_inversion": "Ratio inversion", "sign_flip": "Sign flip",
        "stale_metadata": "Stale metadata", "treatment_control_flip": "Treatment/control", "unit_conversion": "Unit conversion",
    }
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    cmap = mpl.colors.LinearSegmentedColormap.from_list("severity", ["#F7FBFD", "#A9D2E5", "#1F5F82"])
    cmap.set_bad("#E9EDF0")
    im = ax.imshow(np.ma.masked_invalid(matrix), cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(3), [name.capitalize() for name in severities])
    ax.set_yticks(np.arange(len(operators)), [pretty.get(name, name.replace("_", " ").title()) for name in operators])
    ax.tick_params(length=0, labelsize=8)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if not np.isnan(matrix[i, j]):
                color = "white" if matrix[i, j] >= 0.58 else COLORS["ink"]
                ax.text(j, i, f"{format_rate(matrix[i, j])}\n$n={counts[i, j]}$", ha="center", va="center",
                        fontsize=6.2, color=color, linespacing=1.05)
            else:
                ax.text(j, i, "N/A", ha="center", va="center", fontsize=6.5, color=COLORS["muted"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.025)
    cbar.set_label("BCR", fontsize=8)
    cbar.ax.tick_params(length=0, labelsize=7)
    cbar.outline.set_visible(False)
    ax.set_title("Blind compliance by severity", pad=8)
    fig.subplots_adjust(left=0.23, right=0.94, top=0.89, bottom=0.12)
    save_figure(fig, output_dir / "fig_severity_heatmap.pdf", preview_dir)


def plot_guard_suite_breakdown(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    rows = read_csv(results_dir / "langgraph_guarded_ablation_suite_summary.csv")
    variants = ["Base", "Caution only", "Expectation only", "Verification only", "Full guard", "Light guard"]
    labels = ["Base", "Caution", "Expectation", "Verify", "Full", "Light"]
    suites = ["numerical", "semantic_schema"]
    fig, axes = plt.subplots(1, 2, figsize=(6.35, 2.55), sharey=True)
    y = np.arange(len(variants))
    for ax, metric, title in zip(axes, ["poisoned_tsr", "bcr"], ["Poisoned task success", "Blind compliance"]):
        style_axes(ax, xgrid=True)
        suite_colors = {"numerical": "#2F75A3", "semantic_schema": "#A9D2E5"}
        for i, suite in enumerate(suites):
            values = [float(next(row[metric] for row in rows if row["suite"] == suite and row["adapter"] == variant)) for variant in variants]
            offset = (i - 0.5) * 0.25
            ax.scatter(values, y + offset, s=24, color=suite_colors[suite], edgecolor=COLORS["ink"], linewidth=0.35,
                       label="Numerical" if suite == "numerical" else "Semantic/schema", zorder=3)
            for yi, value in zip(y + offset, values):
                ax.annotate(format_rate(value), (value, yi), xytext=(5, -5 if i == 0 else 5),
                            textcoords="offset points", va="center", fontsize=6.8,
                            color=COLORS["ink"] if value < 0.2 else COLORS["muted"])
        ax.set_xlim(-0.03, 1.03)
        ax.set_xlabel("Rate")
        ax.set_title(title, pad=7)
        ax.set_yticks(y, labels)
    axes[0].invert_yaxis()
    handles = [Line2D([], [], marker="o", linestyle="none", color="#2F75A3", label="Numerical"),
               Line2D([], [], marker="o", linestyle="none", color="#A9D2E5", label="Semantic/schema")]
    fig.legend(handles=handles, frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 0.005))
    panel_label(axes[0], "a")
    panel_label(axes[1], "b")
    fig.subplots_adjust(left=0.14, right=0.99, top=0.84, bottom=0.27, wspace=0.22)
    save_figure(fig, output_dir / "fig_guard_suite_breakdown.pdf", preview_dir)


def plot_capability_gap(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    """Show paired clean/toxic performance and the resulting degradation."""
    rows = [
        row for row in read_csv(results_dir / "iclr2027_gpt_expanded_cross_agent_combined_summary.csv")
        if row["adapter"] in EXPANDED_ADAPTERS
    ]
    rows.sort(key=lambda row: list(EXPANDED_ADAPTERS).index(row["adapter"]))
    labels = [EXPANDED_ADAPTERS[row["adapter"]] for row in rows]
    clean = np.array([float(row["clean_tsr"]) for row in rows])
    toxic = np.array([float(row["poisoned_tsr"]) for row in rows])
    gap = clean - toxic

    fig, ax = plt.subplots(figsize=(7.0, 2.35))
    style_axes(ax, xgrid=True)
    y = np.arange(len(labels))
    ax.hlines(y, toxic, clean, color="#9FB7C2", linewidth=2.0, zorder=1)
    ax.scatter(clean, y, facecolor="white", edgecolor="#4B5E67", linewidth=1.5, s=32, zorder=3, label="Clean TSR")
    ax.scatter(toxic, y, color=COLORS["clean"], s=28, zorder=3, label="Poisoned TSR")
    for yi, clean_value, toxic_value, gap_value in zip(y, clean, toxic, gap):
        ax.text(clean_value + 0.018, yi, f"{format_rate(clean_value)}   $\Delta$ = {format_rate(gap_value)}", va="center", fontsize=7)
        ax.text(toxic_value - 0.018, yi, format_rate(toxic_value), va="center", ha="right", fontsize=7, color=COLORS["clean"])
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0.45, 1.05)
    ax.set_xlabel("Task success rate")
    ax.set_title("")
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2,
              handlelength=1.0, columnspacing=0.8)
    fig.subplots_adjust(left=0.18, right=0.99, top=0.87, bottom=0.20)
    save_figure(fig, output_dir / "fig_capability_gap.pdf", preview_dir)


def plot_defense_frontier(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    """Plot poisoned-task success versus latency with an explicit Pareto frontier."""
    ablation = {row["adapter"]: row for row in read_csv(results_dir / "langgraph_guarded_ablation_summary.csv")}
    overhead_rows = read_csv(results_dir / "langgraph_guarded_overhead_summary.csv")
    toxic_latency: dict[str, list[float]] = defaultdict(list)
    for row in overhead_rows:
        if row["env"] == "toxic":
            toxic_latency[row["adapter"]].append(float(row["mean_seconds"]))
    variants = ["Base", "Caution only", "Expectation only", "Verification only", "Full guard", "Light guard"]
    labels = ["Base", "Caution", "Expectation", "Verify", "Full", "Light"]
    latency = np.array([np.mean(toxic_latency[name]) for name in variants])
    tsr = np.array([float(ablation[name]["poisoned_tsr"]) for name in variants])

    frontier = []
    for i in range(len(variants)):
        dominated = any(
            latency[j] <= latency[i] and tsr[j] >= tsr[i]
            and (latency[j] < latency[i] or tsr[j] > tsr[i])
            for j in range(len(variants))
        )
        if not dominated:
            frontier.append(i)
    frontier.sort(key=lambda i: latency[i])

    fig, ax = plt.subplots(figsize=(3.25, 2.65))
    style_axes(ax)
    ax.plot(latency[frontier], tsr[frontier], color=COLORS["clean"], linestyle=(0, (2, 2)),
            linewidth=1.1, label="Pareto frontier", zorder=1)
    for i, label in enumerate(labels):
        is_frontier = i in frontier
        ax.scatter(latency[i], tsr[i], s=34, color=COLORS["clean"] if is_frontier else COLORS["neutral"],
                   edgecolor=COLORS["ink"], linewidth=0.45, zorder=3)
        ax.annotate(label, (latency[i], tsr[i]), xytext=(4, 5 if i % 2 else -10),
                    textcoords="offset points", fontsize=6.5,
                    color=COLORS["ink"] if is_frontier else COLORS["muted"])
    ax.set_xlabel("Toxic-run latency (s)")
    ax.set_ylabel("Poisoned TSR")
    ax.set_xlim(max(0, float(latency.min()) - 2), float(latency.max()) + 2)
    ax.set_ylim(0.55, 1.02)
    ax.set_title("Robustness--cost frontier", pad=8)
    ax.legend(frameon=False, loc="lower right", fontsize=6.5, handlelength=1.4)
    ax.grid(axis="both", color=COLORS["grid"], linewidth=0.55)
    fig.subplots_adjust(left=0.17, right=0.98, top=0.86, bottom=0.18)
    save_figure(fig, output_dir / "fig_defense_frontier.pdf", preview_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("toxictool_bench/results"))
    parser.add_argument("--output-dir", type=Path, default=Path("figures"))
    parser.add_argument("--preview-dir", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_matplotlib()
    plot_cross_agent_model(args.results_dir, args.output_dir, args.preview_dir)
    plot_operator_profile(args.results_dir, args.output_dir, args.preview_dir)
    plot_severity(args.results_dir, args.output_dir, args.preview_dir)
    plot_capability_gap(args.results_dir, args.output_dir, args.preview_dir)
    plot_defense_frontier(args.results_dir, args.output_dir, args.preview_dir)


if __name__ == "__main__":
    main()
