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

# Restrained, colorblind-safe palette. Blue denotes capability, vermilion risk,
# and green evidence-based recovery throughout the paper.
COLORS = {
    "clean": "#32658A",
    "toxic": "#D07A4A",
    "risk": "#B9473E",
    "verify": "#2F7D6D",
    "recover": "#5A78A8",
    "exposure": "#8064A2",
    "neutral": "#7B858E",
    "ink": "#202A32",
    "muted": "#66727C",
    "grid": "#D9DEE2",
    "light": "#F3F5F6",
    "paper": "#FFFFFF",
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
    ax.text(-0.14, 1.09, label, transform=ax.transAxes, fontsize=9, weight="bold")


def save_figure(fig: mpl.figure.Figure, output: Path, preview_dir: Path | None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight", pad_inches=0.03)
    if preview_dir is not None:
        preview_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(preview_dir / f"{output.stem}.png", dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def short_model(model: str) -> str:
    return {
        "gpt-5.4-mini": "GPT",
        "claude-sonnet-4-6": "Claude",
        "Qwen3.6-35B-A3B-no-thinking": "Qwen",
    }[model]


def plot_cross_agent_model(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    expanded = [
        row
        for row in read_csv(results_dir / "iclr2027_gpt_expanded_cross_agent_combined_summary.csv")
        if row["adapter"] in EXPANDED_ADAPTERS
    ]
    expanded.sort(key=lambda row: list(EXPANDED_ADAPTERS).index(row["adapter"]))

    cross_model: list[dict[str, str]] = []
    for path, suite in (
        ("public_cross_model_numerical_summary.csv", "Numerical"),
        ("public_cross_model_semantic_schema_summary.csv", "Semantic/schema"),
    ):
        cross_model.extend({**row, "suite": suite} for row in read_csv(results_dir / path))
    model_order = ["gpt-5.4-mini", "claude-sonnet-4-6", "Qwen3.6-35B-A3B-no-thinking"]
    cross_model.sort(key=lambda row: (["Numerical", "Semantic/schema"].index(row["suite"]), model_order.index(row["model"])))

    fig, axes = plt.subplots(1, 3, figsize=(7.12, 2.45), gridspec_kw={"width_ratios": [1.08, 1.25, 1.25]})

    ax = axes[0]
    style_axes(ax, xgrid=True)
    y = np.arange(len(expanded))
    clean = np.array([float(row["clean_tsr"]) for row in expanded])
    toxic = np.array([float(row["poisoned_tsr"]) for row in expanded])
    for i in range(len(expanded)):
        ax.plot([toxic[i], clean[i]], [i, i], color=COLORS["grid"], linewidth=2.4, zorder=1)
    ax.scatter(clean, y, color=COLORS["clean"], s=34, zorder=3)
    ax.scatter(toxic, y, color=COLORS["toxic"], s=34, zorder=3)
    ax.set_yticks(y, [EXPANDED_ADAPTERS[row["adapter"]] for row in expanded])
    ax.invert_yaxis()
    ax.set_xlim(0.45, 1.01)
    ax.set_xlabel("Task success rate")
    ax.set_title("Expanded GPT-only (120)", pad=7)
    panel_label(ax, "a")

    ax = axes[1]
    style_axes(ax, xgrid=True)
    y = np.arange(len(cross_model))
    clean = np.array([float(row["clean_tsr"]) for row in cross_model])
    toxic = np.array([float(row["poisoned_tsr"]) for row in cross_model])
    for i in range(len(cross_model)):
        ax.plot([toxic[i], clean[i]], [i, i], color=COLORS["grid"], linewidth=2.2, zorder=1)
    ax.scatter(clean, y, color=COLORS["clean"], s=29, zorder=3)
    ax.scatter(toxic, y, color=COLORS["toxic"], s=29, zorder=3)
    labels = [f"{'Num.' if row['suite'] == 'Numerical' else 'Sem.'} / {short_model(row['model'])}" for row in cross_model]
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0.42, 1.02)
    ax.set_xlabel("Task success rate")
    ax.set_title("Cross-model mean", pad=7)
    panel_label(ax, "b")

    ax = axes[2]
    style_axes(ax, xgrid=True)
    bcr = np.array([float(row["toxic_bcr"]) for row in cross_model])
    pdr = np.array([float(row["poison_delivery_rate"]) for row in cross_model])
    for i in range(len(cross_model)):
        ax.plot([bcr[i], pdr[i]], [i, i], color=COLORS["grid"], linewidth=2.2, zorder=1)
    ax.scatter(bcr, y, marker="D", color=COLORS["risk"], s=27, zorder=3)
    ax.scatter(pdr, y, marker="o", facecolor=COLORS["paper"], edgecolor=COLORS["exposure"], linewidth=1.3, s=30, zorder=3)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.02)
    ax.set_xlabel("Rate")
    ax.set_title("Risk conditional on exposure", pad=7)
    panel_label(ax, "c")

    handles = [
        Line2D([], [], marker="o", linestyle="none", color=COLORS["clean"], label="Clean TSR"),
        Line2D([], [], marker="o", linestyle="none", color=COLORS["toxic"], label="Poisoned TSR"),
        Line2D([], [], marker="D", linestyle="none", color=COLORS["risk"], label="BCR"),
        Line2D([], [], marker="o", linestyle="none", markerfacecolor="white", markeredgecolor=COLORS["exposure"], label="PDR"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.01), handletextpad=0.35, columnspacing=1.15)
    fig.subplots_adjust(left=0.10, right=0.99, top=0.84, bottom=0.25, wspace=0.58)
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
        ("toxic_tsr", "Poisoned\nTSR"),
        ("bcr", "BCR"),
        ("vr", "VR"),
        ("rr", "RR"),
        ("poison_delivery_rate", "PDR"),
    ]
    matrix = []
    for key, _, family in order:
        source = numerical[key] if family == "Numerical" else semantic[key]
        matrix.append([float(source[metric]) for metric, _ in metrics])
    values = np.asarray(matrix)

    fig, ax = plt.subplots(figsize=(7.12, 3.15))
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "toxicbench_rates", ["#F5F6F7", "#D9E1E5", "#83A9B5", "#265F78"]
    )
    im = ax.imshow(values, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(metrics)), [label for _, label in metrics])
    ax.set_yticks(np.arange(len(order)), [label for _, label, _ in order])
    ax.tick_params(length=0, labelsize=8)
    ax.tick_params(axis="x", pad=5)
    ax.axhline(2.5, color=COLORS["paper"], linewidth=3.0)
    ax.text(-0.19, 0.78, "Numerical", transform=ax.transAxes, rotation=90, va="center", ha="center", fontsize=7, color=COLORS["muted"])
    ax.text(-0.19, 0.31, "Semantic / schema", transform=ax.transAxes, rotation=90, va="center", ha="center", fontsize=7, color=COLORS["muted"])
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            color = "white" if values[i, j] >= 0.58 else COLORS["ink"]
            ax.text(j, i, format_rate(values[i, j]), ha="center", va="center", fontsize=7.4, color=color)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax, fraction=0.024, pad=0.025)
    cbar.set_label("Rate", fontsize=8)
    cbar.ax.tick_params(length=0, labelsize=7)
    cbar.outline.set_visible(False)
    ax.set_title("Failure and recovery profiles by poisoning operator", pad=9)
    fig.subplots_adjust(left=0.25, right=0.94, top=0.88, bottom=0.14)
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
    variant_colors = [COLORS["neutral"], COLORS["toxic"], COLORS["toxic"], COLORS["verify"], COLORS["clean"], COLORS["recover"]]

    fig, axes = plt.subplots(1, 3, figsize=(7.12, 2.55), gridspec_kw={"width_ratios": [1.16, 1.0, 1.0]})

    ax = axes[0]
    style_axes(ax)
    x = np.arange(len(variants))
    toxic_tsr = np.array([float(ablation[v]["poisoned_tsr"]) for v in variants])
    bcr = np.array([float(ablation[v]["bcr"]) for v in variants])
    ax.plot(x, toxic_tsr, color=COLORS["clean"], linewidth=1.4, marker="o", markersize=4, label="Poisoned TSR")
    ax.plot(x, bcr, color=COLORS["risk"], linewidth=1.4, marker="D", markersize=3.8, label="BCR")
    ax.set_xticks(x, labels, rotation=38, ha="right")
    ax.set_ylim(-0.03, 1.03)
    ax.set_ylabel("Rate")
    ax.set_title("Defense ablation", pad=7)
    ax.legend(
        frameon=True, facecolor="white", edgecolor="none", framealpha=0.92,
        loc="center left", bbox_to_anchor=(0.0, 0.56), handlelength=1.2,
    )
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
    ax.bar(x, means, color=[COLORS["neutral"], COLORS["clean"], COLORS["recover"], COLORS["verify"], COLORS["verify"]], width=0.62)
    ax.vlines(x, p50, p90, color=COLORS["ink"], linewidth=1.5, zorder=3)
    ax.scatter(x, p50, facecolor="white", edgecolor=COLORS["ink"], s=13, zorder=4)
    ax.scatter(x, p90, color=COLORS["ink"], s=11, zorder=4)
    ax.set_xticks(x, names, rotation=38, ha="right")
    ax.set_ylim(0, 34)
    ax.set_ylabel("Seconds / task")
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
    ax.legend(
        frameon=True, facecolor="white", edgecolor="none", framealpha=0.92,
        loc="upper right", handlelength=1.2,
    )
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
    for i, operator in enumerate(operators):
        for j, severity in enumerate(severities):
            group = [row for row in rows if row["poison_type"] == operator and row["severity"] == severity]
            if group:
                matrix[i, j] = mean(group, "bcr")
    pretty = {
        "aggregate_scale": "Aggregate scale", "biased_retrieval": "Biased retrieval", "column_semantic_swap": "Column swap",
        "denominator_swap": "Denominator swap", "label_swap": "Label swap", "missing_filter": "Missing filter",
        "rank_swap": "Rank swap", "ratio_inversion": "Ratio inversion", "sign_flip": "Sign flip",
        "stale_metadata": "Stale metadata", "treatment_control_flip": "Treatment/control", "unit_conversion": "Unit conversion",
    }
    fig, ax = plt.subplots(figsize=(7.12, 3.0))
    cmap = mpl.colors.LinearSegmentedColormap.from_list("severity", ["#F5F6F7", "#E7C7B6", "#B9473E"])
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(3), [name.capitalize() for name in severities])
    ax.set_yticks(np.arange(len(operators)), [pretty.get(name, name.replace("_", " ").title()) for name in operators])
    ax.tick_params(length=0, labelsize=8)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if not np.isnan(matrix[i, j]):
                color = "white" if matrix[i, j] >= 0.58 else COLORS["ink"]
                ax.text(j, i, format_rate(matrix[i, j]), ha="center", va="center", fontsize=7.2, color=color)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.025)
    cbar.set_label("BCR", fontsize=8)
    cbar.ax.tick_params(length=0, labelsize=7)
    cbar.outline.set_visible(False)
    ax.set_title("Blind compliance by operator and annotated severity", pad=8)
    fig.subplots_adjust(left=0.23, right=0.94, top=0.89, bottom=0.12)
    save_figure(fig, output_dir / "fig_severity_heatmap.pdf", preview_dir)


def plot_guard_suite_breakdown(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    rows = read_csv(results_dir / "langgraph_guarded_ablation_suite_summary.csv")
    variants = ["Base", "Caution only", "Expectation only", "Verification only", "Full guard", "Light guard"]
    labels = ["Base", "Caution", "Expectation", "Verify", "Full", "Light"]
    suites = ["numerical", "semantic_schema"]
    fig, axes = plt.subplots(1, 2, figsize=(7.12, 2.55), sharey=True)
    y = np.arange(len(variants))
    for ax, metric, title in zip(axes, ["poisoned_tsr", "bcr"], ["Poisoned task success", "Blind compliance"]):
        style_axes(ax, xgrid=True)
        for i, suite in enumerate(suites):
            values = [float(next(row[metric] for row in rows if row["suite"] == suite and row["adapter"] == variant)) for variant in variants]
            offset = (i - 0.5) * 0.28
            ax.scatter(values, y + offset, marker="o" if i == 0 else "s", s=28,
                       color=COLORS["clean"] if i == 0 else COLORS["verify"],
                       label="Numerical" if suite == "numerical" else "Semantic/schema", zorder=3)
        ax.set_xlim(-0.03, 1.03)
        ax.set_xlabel("Rate")
        ax.set_title(title, pad=7)
        ax.set_yticks(y, labels)
    axes[0].invert_yaxis()
    handles = [
        Line2D([], [], marker="o", linestyle="none", color=COLORS["clean"], label="Numerical"),
        Line2D([], [], marker="s", linestyle="none", color=COLORS["verify"], label="Semantic/schema"),
    ]
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

    fig, axes = plt.subplots(1, 2, figsize=(7.12, 2.45), gridspec_kw={"width_ratios": [1.18, 1.0]})
    ax = axes[0]
    style_axes(ax, xgrid=True)
    x = np.arange(len(labels))
    width = 0.34
    ax.bar(x - width / 2, clean, width, color=COLORS["clean"], label="Clean TSR")
    ax.bar(x + width / 2, toxic, width, color=COLORS["toxic"], label="Poisoned TSR")
    for values, offset in ((clean, -width / 2), (toxic, width / 2)):
        for i, value in enumerate(values):
            ax.text(i + offset, value + 0.018, format_rate(value), ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x, labels)
    ax.set_ylim(0.45, 1.04)
    ax.set_ylabel("Task success rate")
    ax.set_title("Paired performance", pad=7)
    ax.legend(frameon=False, loc="lower left", ncol=2, handlelength=1.0)
    panel_label(ax, "a")

    ax = axes[1]
    style_axes(ax, xgrid=True)
    colors = [COLORS["risk"] if value >= 0.3 else COLORS["recover"] for value in gap]
    bars = ax.barh(x, gap, color=colors, height=0.48)
    ax.set_yticks(x, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, max(0.4, float(gap.max()) + 0.08))
    ax.set_xlabel("Clean TSR - poisoned TSR")
    ax.set_title("Performance degradation", pad=7)
    for bar, value in zip(bars, gap):
        ax.text(value + 0.012, bar.get_y() + bar.get_height() / 2, format_rate(value), va="center", fontsize=7)
    panel_label(ax, "b")
    fig.subplots_adjust(left=0.11, right=0.99, top=0.84, bottom=0.18, wspace=0.48)
    save_figure(fig, output_dir / "fig_capability_gap.pdf", preview_dir)


def plot_defense_frontier(results_dir: Path, output_dir: Path, preview_dir: Path | None) -> None:
    """Plot robustness versus measured latency, with BCR as marker size."""
    ablation = {row["adapter"]: row for row in read_csv(results_dir / "langgraph_guarded_ablation_summary.csv")}
    overhead_rows = read_csv(results_dir / "langgraph_guarded_overhead_summary.csv")
    toxic_latency: dict[str, list[float]] = defaultdict(list)
    for row in overhead_rows:
        if row["env"] == "toxic":
            toxic_latency[row["adapter"]].append(float(row["mean_seconds"]))
    variants = ["Base", "Caution only", "Expectation only", "Verification only", "Full guard", "Light guard"]
    labels = ["Base", "Caution", "Expectation", "Verify", "Full", "Light"]
    colors = [COLORS["neutral"], COLORS["toxic"], COLORS["toxic"], COLORS["verify"], COLORS["clean"], COLORS["recover"]]
    latency = np.array([np.mean(toxic_latency[name]) for name in variants])
    tsr = np.array([float(ablation[name]["poisoned_tsr"]) for name in variants])
    bcr = np.array([float(ablation[name]["bcr"]) for name in variants])

    fig, ax = plt.subplots(figsize=(3.65, 2.8))
    style_axes(ax)
    label_offsets = {
        "Base": (5, -10),
        "Caution": (5, 5),
        "Expectation": (5, 8),
        "Verify": (5, -13),
        "Full": (5, 7),
        "Light": (5, -15),
    }
    for x, y, size, color, label in zip(latency, tsr, bcr, colors, labels):
        ax.scatter(x, y, s=70 + 220 * size, color=color, edgecolor="white", linewidth=0.8, label=label, zorder=3)
        ax.annotate(label, (x, y), xytext=label_offsets[label], textcoords="offset points", fontsize=7)
    ax.set_xlabel("Toxic-run latency (s)")
    ax.set_ylabel("Poisoned TSR")
    ax.set_xlim(0, max(45, float(latency.max()) + 4))
    ax.set_ylim(0.55, 1.02)
    ax.set_title("Robustness--cost frontier", pad=8)
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
    plot_guard_tradeoff(args.results_dir, args.output_dir, args.preview_dir)
    plot_severity(args.results_dir, args.output_dir, args.preview_dir)
    plot_guard_suite_breakdown(args.results_dir, args.output_dir, args.preview_dir)
    plot_capability_gap(args.results_dir, args.output_dir, args.preview_dir)
    plot_defense_frontier(args.results_dir, args.output_dir, args.preview_dir)


if __name__ == "__main__":
    main()
