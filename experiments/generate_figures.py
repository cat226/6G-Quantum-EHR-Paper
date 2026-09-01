#!/usr/bin/env python3
"""
Pilot figure generation (Task 8.5), reading results/processed/pilot_summary.csv
(produced by experiments/analyze_pilot.py -- itself just
src/metrics/aggregator.summarize_cell() over the raw pilot data). No new
statistics computed here; this is presentation only.

Palette and mark choices follow the project's dataviz method (validated
default palette): categorical hue is assigned by a fixed slot order and
used only where color encodes IDENTITY (which baseline, which device
count); a pure magnitude comparison (Figure 3) uses a single sequential
hue instead, per that method's form table ("compare magnitude -> one
hue"), not five arbitrary series colors.

Per docs/scope_and_claims.md: every timing here is host-measured
(x86-64; see docs/environment_manifest.md), not a claim about any
embedded or IoMT device. Captions state this explicitly rather than
leaving it implicit in an axis label.

Usage:
    python experiments/generate_figures.py \
        --input results/processed/pilot_summary.csv \
        --output paper/figures
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# --- Validated default palette (dataviz skill, references/palette.md) ---
# Categorical slots, fixed order -- never cycled, never reassigned per chart.
BASELINE_COLOR = {
    "B1": "#2a78d6",  # slot 1 blue
    "B2": "#eb6834",  # slot 2 orange
    "B3": "#1baf7a",  # slot 3 aqua
    "B4": "#eda100",  # slot 4 yellow
    "B5": "#e87ba4",  # slot 5 magenta
}
BASELINE_LABEL = {
    "B1": "B1 Classical",
    "B2": "B2 PQC-only",
    "B3": "B3 QKD-only",
    "B4": "B4 Static hybrid",
    "B5": "B5 Adaptive hybrid",
}
# Figure 1 uses EMPHASIS, not five-way categorical: B1/B2/B3(at full
# availability)/B5 sit at the same ~99.7% packet-loss floor, and B3/B4
# trace nearly identical collapse curves to three decimal places (that
# IS the finding -- B3 and B4 fail together, and their success rate is
# indistinguishable from each other). With values that numerically
# coincide, no amount of line style or marker shape recovers visual
# separation -- and treating all five as equally-weighted identity
# buries the paper's actual claim (B4 vs B5) in overlap. The dataviz
# method's form table is explicit for this case: "one series is the
# point, rest are context -> emphasis (highlight one, gray the rest)".
# B4 and B5 are the point (the critical divergence); B1-B3 are context.
EMPHASIS_GRAY = "#b3b2ab"       # de-emphasis hue for context series
B4_ACCENT = "#d03b3b"           # status-critical red -- the failure path
B5_ACCENT = "#2a78d6"           # categorical slot 1 blue -- the resilient path
BASELINE_MARKER = {"B1": "o", "B2": "s", "B3": "^", "B4": "D", "B5": "*"}
BASELINE_LINESTYLE = {"B1": "-", "B2": "--", "B3": ":", "B4": "-.", "B5": "-"}
BASELINE_MARKERSIZE = {"B1": 5, "B2": 5, "B3": 5.5, "B4": 7, "B5": 12}
EMPHASIS_COLOR = {"B1": EMPHASIS_GRAY, "B2": EMPHASIS_GRAY, "B3": EMPHASIS_GRAY,
                   "B4": B4_ACCENT, "B5": B5_ACCENT}
EMPHASIS_ZORDER = {"B1": 2, "B2": 2, "B3": 2, "B4": 4, "B5": 5}
EMPHASIS_ALPHA = {"B1": 0.85, "B2": 0.85, "B3": 0.85, "B4": 1.0, "B5": 1.0}
EMPHASIS_LINEWIDTH = {"B1": 1.5, "B2": 1.5, "B3": 1.5, "B4": 2.6, "B5": 2.6}
DEVICE_COUNT_COLOR = {10: "#2a78d6", 1000: "#eb6834"}  # slots 1, 2 -- identity (device count)
SEQUENTIAL_BLUE = "#2a78d6"  # single hue for pure-magnitude comparisons (Figure 3)

INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"

QKD_ORDER = [0.0, 0.5, 1.0]
QKD_TICK_LABEL = {0.0: "0%", 0.5: "50%", 1.0: "100%"}


def _style_axes(ax):
    ax.set_facecolor(SURFACE)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(AXIS)
        ax.spines[spine].set_linewidth(1.0)
    ax.grid(axis="y", color=GRID, linewidth=1.0, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK_MUTED, labelsize=9)
    ax.xaxis.label.set_color(INK_SECONDARY)
    ax.yaxis.label.set_color(INK_SECONDARY)


def load_summary(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def figure_1_success_rate(rows: list[dict], output_dir: Path) -> None:
    """Successful transmission rate vs QKD availability, per baseline,
    faceted by device count. Categorical color: the baseline IS the
    subject (identity), matching the dataviz method's "tell distinct
    series apart -> categorical" rule."""
    device_counts = sorted({int(r["device_count"]) for r in rows})
    fig, axes = plt.subplots(1, len(device_counts), figsize=(10, 4.2), sharey=True)
    if len(device_counts) == 1:
        axes = [axes]

    for ax, dc in zip(axes, device_counts):
        _style_axes(ax)
        for baseline in ["B1", "B2", "B3", "B4", "B5"]:
            ys = []
            for q in QKD_ORDER:
                match = [
                    r for r in rows
                    if r["baseline"] == baseline
                    and int(r["device_count"]) == dc
                    and abs(float(r["qkd_availability_config"]) - q) < 1e-9
                ]
                ys.append(float(match[0]["successful_transmission_rate"]) if match else float("nan"))
            ax.plot(
                range(len(QKD_ORDER)), ys,
                color=EMPHASIS_COLOR[baseline], linewidth=EMPHASIS_LINEWIDTH[baseline],
                linestyle=BASELINE_LINESTYLE[baseline],
                marker=BASELINE_MARKER[baseline], markersize=BASELINE_MARKERSIZE[baseline],
                markerfacecolor=EMPHASIS_COLOR[baseline],
                markeredgecolor=SURFACE, markeredgewidth=1.0,
                label=BASELINE_LABEL[baseline], zorder=EMPHASIS_ZORDER[baseline],
                alpha=EMPHASIS_ALPHA[baseline],
            )
        ax.set_xticks(range(len(QKD_ORDER)))
        ax.set_xticklabels([QKD_TICK_LABEL[q] for q in QKD_ORDER])
        ax.set_xlabel("Configured QKD availability")
        ax.set_ylim(-0.05, 1.08)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
        ax.set_title(f"{dc:,} devices", color=INK_PRIMARY, fontsize=11, fontweight="normal")

    axes[0].set_ylabel("Successful transmission rate")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles, labels, loc="lower center", ncol=5, frameon=False,
        bbox_to_anchor=(0.5, -0.06), fontsize=9, labelcolor=INK_SECONDARY,
    )
    fig.suptitle(
        "Successful transmission rate vs. QKD availability: B4 vs. B5 (B1-B3 as context)",
        color=INK_PRIMARY, fontsize=12, fontweight="normal", y=1.02,
    )
    fig.text(
        0.5, -0.16,
        "B4 (static hybrid, red) collapses as QKD availability falls; B5 (adaptive hybrid, blue) holds\n"
        "via PQC fallback -- the project's central behavioral claim. B1/B2/B3 (gray) are context: B1 and B2\n"
        "never depend on QKD; B3 collapses with B4 (their curves coincide almost exactly -- not a\n"
        "rendering artifact). All are host-measured (x86-64; see environment manifest).",
        ha="center", fontsize=8, color=INK_MUTED,
    )
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(output_dir / f"fig1_success_rate_vs_qkd_availability.{ext}",
                    dpi=200, bbox_inches="tight")
    plt.close(fig)


def figure_2_b5_latency(rows: list[dict], output_dir: Path) -> None:
    """B5 key-establishment latency (mean, 95% CI) vs QKD availability,
    log-scale, by device count. Only two series here (device count),
    still identity -> categorical, slots 1-2."""
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    _style_axes(ax)

    device_counts = sorted({int(r["device_count"]) for r in rows if r["baseline"] == "B5"})
    x = list(range(len(QKD_ORDER)))
    offsets = [-0.08, 0.08] if len(device_counts) == 2 else [0.0] * len(device_counts)

    for dc, off in zip(device_counts, offsets):
        means, lo, hi = [], [], []
        for q in QKD_ORDER:
            match = [
                r for r in rows
                if r["baseline"] == "B5" and int(r["device_count"]) == dc
                and abs(float(r["qkd_availability_config"]) - q) < 1e-9
            ]
            r = match[0]
            m = float(r["key_establishment_ms_mean"])
            means.append(m)
            lo.append(m - float(r["key_establishment_ms_ci95_low"]))
            hi.append(float(r["key_establishment_ms_ci95_high"]) - m)

        xs = [xi + off for xi in x]
        ax.errorbar(
            xs, means, yerr=[lo, hi], fmt="o-",
            color=DEVICE_COUNT_COLOR[dc], linewidth=2.0, markersize=6,
            markerfacecolor=DEVICE_COUNT_COLOR[dc], markeredgecolor=SURFACE,
            markeredgewidth=1.2, capsize=3, capthick=1.2, elinewidth=1.2,
            label=f"{dc:,} devices", zorder=3,
        )

    ax.set_xticks(x)
    ax.set_xticklabels([QKD_TICK_LABEL[q] for q in QKD_ORDER])
    ax.set_xlabel("Configured QKD availability")
    ax.set_ylabel("Key-establishment latency, mean (ms, log scale)")
    ax.set_yscale("log")
    ax.set_title(
        "B5 (adaptive hybrid) key-establishment latency vs. QKD availability",
        color=INK_PRIMARY, fontsize=11, fontweight="normal",
    )
    ax.legend(frameon=False, fontsize=9, labelcolor=INK_SECONDARY, loc="upper right")
    fig.text(
        0.02, -0.06,
        "Error bars: bootstrap 95% CI. The ~2-order-of-magnitude rise below 100%\n"
        "availability is the controller's bounded wait (wait_timeout_seconds=0.05s in\n"
        "config/pilot.yaml), not increased cryptographic cost. Host-measured (x86-64).",
        ha="left", fontsize=8, color=INK_MUTED,
    )
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(output_dir / f"fig2_b5_latency_vs_qkd_availability.{ext}",
                    dpi=200, bbox_inches="tight")
    plt.close(fig)


def figure_3_overhead(rows: list[dict], output_dir: Path) -> None:
    """Communication overhead by baseline -- a pure magnitude comparison,
    so ONE hue (sequential blue), not five categorical colors, per the
    dataviz method's form table."""
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    _style_axes(ax)

    baselines = ["B1", "B2", "B3", "B4", "B5"]
    values = []
    for b in baselines:
        match = [r for r in rows if r["baseline"] == b]
        values.append(float(match[0]["communication_overhead_bytes_mean"]))

    bars = ax.bar(
        range(len(baselines)), values, color=SEQUENTIAL_BLUE, width=0.55,
        zorder=3, edgecolor=SURFACE, linewidth=2,
    )
    ax.set_xticks(range(len(baselines)))
    ax.set_xticklabels([BASELINE_LABEL[b].replace(" ", "\n", 1) for b in baselines], fontsize=8.5)
    ax.set_ylabel("Communication overhead (bytes)")
    ax.set_yscale("log")
    ax.set_title(
        "Key-establishment communication overhead, by baseline",
        color=INK_PRIMARY, fontsize=11, fontweight="normal",
    )
    for rect, v in zip(bars, values):
        ax.text(
            rect.get_x() + rect.get_width() / 2, v * 1.08, f"{v:,.0f}",
            ha="center", va="bottom", fontsize=8.5, color=INK_SECONDARY,
        )
    fig.text(
        0.02, -0.04,
        "Constant across every QKD-availability level and device count (verified in\n"
        "results/processed/pilot_analysis_notes.md); depends only on which primitives a\n"
        "baseline's key establishment uses, not on QKD conditions.",
        ha="left", fontsize=8, color=INK_MUTED,
    )
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(output_dir / f"fig3_overhead_by_baseline.{ext}",
                    dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pilot result figures")
    parser.add_argument("--input", default="results/processed/pilot_summary.csv")
    parser.add_argument("--output", default="paper/figures")
    args = parser.parse_args()

    rows = load_summary(Path(args.input))
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]

    figure_1_success_rate(rows, output_dir)
    figure_2_b5_latency(rows, output_dir)
    figure_3_overhead(rows, output_dir)

    produced = sorted(output_dir.glob("fig*.pdf"))
    print(f"{len(produced)} figures written to {output_dir}/:")
    for p in produced:
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
