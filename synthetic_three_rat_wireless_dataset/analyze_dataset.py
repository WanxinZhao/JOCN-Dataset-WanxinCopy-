#!/usr/bin/env python3
"""Scientific, run-aware analysis of the synthetic three-RAT dataset."""

from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ANALYSIS = ROOT / "analysis"
FIGURES = ANALYSIS / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

BRANCHES = ["NR", "WiFi80211ax", "LiFi"]
METRICS = [
    "throughput_mbps",
    "mean_delay_ms",
    "mean_jitter_ms",
    "FlowMonitor_reported_loss_ratio",
]
LOADS = [2.0, 5.0, 10.0, 20.0]
SPEEDS = [0.5, 3.0]
FOVS = [40.0, 70.0]
SEEDS = [1, 2, 3]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else float("nan")


def std(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def fmt(value: float, digits: int = 6) -> str:
    if not math.isfinite(value):
        return "NA"
    return f"{value:.{digits}g}"


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_fallback_svgs(run_rows: list[dict[str, object]], physical_rows: list[dict[str, object]]) -> list[str]:
    """Write dependency-free SVG candidates when raster plotting is unavailable."""
    colours = {"NR": "#1f77b4", "WiFi80211ax": "#ff7f0e", "LiFi": "#2ca02c"}
    labels = {"NR": "5G NR", "WiFi80211ax": "Wi-Fi 802.11ax", "LiFi": "LiFi/OWC"}

    def line_chart(filename: str, metric: str, title: str, ylabel: str) -> None:
        width, height = 760, 460
        left, right, top, bottom = 75, 25, 45, 65
        chart_w, chart_h = width - left - right, height - top - bottom
        series: dict[str, list[float]] = {}
        errors: dict[str, list[float]] = {}
        for branch in BRANCHES:
            values_by_load: list[list[float]] = []
            for load in LOADS:
                seed_values = []
                for seed in SEEDS:
                    seed_rows = [row for row in run_rows if row["branch"] == branch and row["offered_load_mbps"] == load and row["seed"] == seed]
                    seed_values.append(mean([float(row[metric]) for row in seed_rows]))
                values_by_load.append(seed_values)
            series[branch] = [mean(values) for values in values_by_load]
            errors[branch] = [std(values) for values in values_by_load]
        finite_values = [value for values in series.values() for value in values if math.isfinite(value)]
        ymax = max(finite_values) * 1.12 if finite_values and max(finite_values) > 0 else 1.0

        def xcoord(value: float) -> float:
            return left + (value - min(LOADS)) / (max(LOADS) - min(LOADS)) * chart_w

        def ycoord(value: float) -> float:
            return top + chart_h - value / ymax * chart_h

        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', f'<text x="{width/2:.1f}" y="24" text-anchor="middle" font-family="sans-serif" font-size="17">{title}</text>']
        for tick in range(6):
            value = ymax * tick / 5
            y = ycoord(value)
            parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+chart_w}" y2="{y:.1f}" stroke="#dddddd"/>')
            parts.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="11">{value:.3g}</text>')
        parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+chart_h}" stroke="black"/><line x1="{left}" y1="{top+chart_h}" x2="{left+chart_w}" y2="{top+chart_h}" stroke="black"/>')
        for load in LOADS:
            x = xcoord(load)
            parts.append(f'<line x1="{x:.1f}" y1="{top+chart_h}" x2="{x:.1f}" y2="{top+chart_h+5}" stroke="black"/>')
            parts.append(f'<text x="{x:.1f}" y="{top+chart_h+21}" text-anchor="middle" font-family="sans-serif" font-size="11">{load:g}</text>')
        for branch in BRANCHES:
            points = " ".join(f"{xcoord(load):.1f},{ycoord(value):.1f}" for load, value in zip(LOADS, series[branch]))
            parts.append(f'<polyline points="{points}" fill="none" stroke="{colours[branch]}" stroke-width="2.5"/>')
            for load, value, error in zip(LOADS, series[branch], errors[branch]):
                x = xcoord(load)
                y = ycoord(value)
                y_low = ycoord(max(0.0, value - error))
                y_high = ycoord(value + error)
                parts.append(f'<line x1="{x:.1f}" y1="{y_low:.1f}" x2="{x:.1f}" y2="{y_high:.1f}" stroke="{colours[branch]}"/><line x1="{x-4:.1f}" y1="{y_low:.1f}" x2="{x+4:.1f}" y2="{y_low:.1f}" stroke="{colours[branch]}"/><line x1="{x-4:.1f}" y1="{y_high:.1f}" x2="{x+4:.1f}" y2="{y_high:.1f}" stroke="{colours[branch]}"/>')
                parts.append(f'<circle cx="{xcoord(load):.1f}" cy="{ycoord(value):.1f}" r="4" fill="{colours[branch]}"/>')
        for index, branch in enumerate(BRANCHES):
            x = left + 25 + index * 170
            parts.append(f'<line x1="{x}" y1="{height-25}" x2="{x+22}" y2="{height-25}" stroke="{colours[branch]}" stroke-width="3"/><text x="{x+28}" y="{height-21}" font-family="sans-serif" font-size="11">{labels[branch]}</text>')
        parts.append(f'<text x="{width/2:.1f}" y="{height-5}" text-anchor="middle" font-family="sans-serif" font-size="12">Offered load (Mbps)</text><text transform="translate(16 {height/2}) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="12">{ylabel}</text></svg>')
        (FIGURES / filename).write_text("".join(parts), encoding="utf-8")

    line_chart("throughput_vs_offered_load.svg", "throughput_mbps", "Synthetic three-RAT wireless throughput", "Throughput (Mbps)")
    line_chart("delay_vs_offered_load.svg", "mean_delay_ms", "Synthetic three-RAT wireless delay", "Mean delay (ms)")

    # For the FOV figure, average CPEs and nuisance load/speed cells within
    # each seed, then show mean +/- SD across the three seeds.
    by_fov_seed: dict[tuple[float, int], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in physical_rows:
        by_fov_seed[(float(row["lifi_fov_deg"]), int(row["seed"]))]["in_fov_fraction"].append(float(row["in_fov_fraction"]))
    for row in run_rows:
        if row["branch"] == "LiFi":
            by_fov_seed[(float(row["lifi_fov_deg"]), int(row["seed"]))]["rx_packet_fraction"].append(float(row["rx_packet_fraction"]))
    fov_values: dict[str, dict[float, tuple[float, float]]] = {"in_fov_fraction": {}, "rx_packet_fraction": {}}
    for metric in fov_values:
        for fov in FOVS:
            seed_values = [mean(by_fov_seed[(fov, seed)][metric]) for seed in SEEDS]
            fov_values[metric][fov] = (mean(seed_values), std(seed_values))
    width, height = 700, 430
    margins = (70, 20, 45, 70)
    chart_w, chart_h = width - margins[0] - margins[1], height - margins[2] - margins[3]
    titles = [("in_fov_fraction", "In-FOV fraction"), ("rx_packet_fraction", "Received-packet fraction")]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/><text x="350" y="24" text-anchor="middle" font-family="sans-serif" font-size="17">LiFi/OWC FOV response</text>']
    panel_w = chart_w / 2
    for panel, (metric, title) in enumerate(titles):
        x0 = margins[0] + panel * panel_w
        y0 = margins[2]
        h = chart_h
        ymax = 1.0
        parts.append(f'<text x="{x0+panel_w/2:.1f}" y="{y0-10}" text-anchor="middle" font-family="sans-serif" font-size="13">{title}</text><line x1="{x0:.1f}" y1="{y0}" x2="{x0:.1f}" y2="{y0+h}" stroke="black"/><line x1="{x0:.1f}" y1="{y0+h}" x2="{x0+panel_w-20:.1f}" y2="{y0+h}" stroke="black"/>')
        for idx, fov in enumerate(FOVS):
            value, error = fov_values[metric][fov]
            bar_w = 42
            x = x0 + 48 + idx * 100
            bar_h = value / ymax * (h - 10)
            ybar = y0 + h - bar_h
            yerr_low = y0 + h - min(1.0, max(0.0, value - error)) * (h - 10)
            yerr_high = y0 + h - min(1.0, value + error) * (h - 10)
            parts.append(f'<rect x="{x:.1f}" y="{ybar:.1f}" width="{bar_w}" height="{bar_h:.1f}" fill="#2ca02c"/><line x1="{x+bar_w/2:.1f}" y1="{yerr_low:.1f}" x2="{x+bar_w/2:.1f}" y2="{yerr_high:.1f}" stroke="black"/><line x1="{x+bar_w/2-5:.1f}" y1="{yerr_low:.1f}" x2="{x+bar_w/2+5:.1f}" y2="{yerr_low:.1f}" stroke="black"/><line x1="{x+bar_w/2-5:.1f}" y1="{yerr_high:.1f}" x2="{x+bar_w/2+5:.1f}" y2="{yerr_high:.1f}" stroke="black"/><text x="{x+bar_w/2:.1f}" y="{y0+h+18}" text-anchor="middle" font-family="sans-serif" font-size="11">{int(fov)}°</text>')
        parts.append(f'<text x="{x0+4:.1f}" y="{y0+h+35}" font-family="sans-serif" font-size="10">mean ± SD, 3 seeds</text>')
    parts.append('</svg>')
    (FIGURES / "lifi_fov_physical_response.svg").write_text("".join(parts), encoding="utf-8")
    return ["throughput_vs_offered_load.svg", "delay_vs_offered_load.svg", "lifi_fov_physical_response.svg"]


def optionally_plot(run_rows: list[dict[str, object]], physical_rows: list[dict[str, object]]) -> list[str]:
    """Create only the three requested compact figures when matplotlib exists."""
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception as exc:
        return write_fallback_svgs(run_rows, physical_rows)

    messages: list[str] = []
    colours = {"NR": "#1f77b4", "WiFi80211ax": "#ff7f0e", "LiFi": "#2ca02c"}
    labels = {"NR": "5G NR", "WiFi80211ax": "Wi-Fi 802.11ax", "LiFi": "LiFi/OWC"}

    def grouped(metric: str, branch: str, load: float | None = None, fov: float | None = None) -> tuple[list[float], list[float], list[float]]:
        values: dict[float, list[float]] = defaultdict(list)
        for row in run_rows:
            if row["branch"] != branch:
                continue
            if load is not None and row["offered_load_mbps"] != load:
                continue
            if fov is not None and row["lifi_fov_deg"] != fov:
                continue
            values[row["offered_load_mbps"]].append(row[metric])
        x = sorted(values)
        return x, [mean(values[k]) for k in x], [std(values[k]) for k in x]

    plt.figure(figsize=(7, 4.5))
    for branch in BRANCHES:
        x, y, e = grouped("throughput_mbps", branch)
        plt.errorbar(x, y, yerr=e, marker="o", capsize=3, label=labels[branch], color=colours[branch])
    plt.xlabel("Offered load (Mbps)")
    plt.ylabel("Throughput (Mbps)")
    plt.title("Synthetic three-RAT wireless throughput")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "throughput_vs_offered_load.png", dpi=180)
    plt.close()
    messages.append("throughput_vs_offered_load.png")

    plt.figure(figsize=(7, 4.5))
    for branch in BRANCHES:
        x, y, e = grouped("mean_delay_ms", branch)
        plt.errorbar(x, y, yerr=e, marker="o", capsize=3, label=labels[branch], color=colours[branch])
    plt.xlabel("Offered load (Mbps)")
    plt.ylabel("Mean delay (ms)")
    plt.title("Synthetic three-RAT wireless delay")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "delay_vs_offered_load.png", dpi=180)
    plt.close()
    messages.append("delay_vs_offered_load.png")

    pgroup: dict[float, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in physical_rows:
        pgroup[row["lifi_fov_deg"]]["in_fov_fraction"].append(row["in_fov_fraction"])
        pgroup[row["lifi_fov_deg"]]["SNR_mean"].append(row["SNR_mean"])
        pgroup[row["lifi_fov_deg"]]["PER_mean"].append(row["PER_mean"])
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.5))
    for fov in FOVS:
        axes[0].bar(str(int(fov)), mean(pgroup[fov]["in_fov_fraction"]), label=f"{int(fov)}°")
        axes[1].bar(str(int(fov)), mean(pgroup[fov]["SNR_mean"]), label=f"{int(fov)}°")
        axes[2].bar(str(int(fov)), mean(pgroup[fov]["PER_mean"]), label=f"{int(fov)}°")
    axes[0].set_ylabel("In-FOV fraction")
    axes[1].set_ylabel("Mean SNR")
    axes[2].set_ylabel("Mean PER")
    for axis, title in zip(axes, ["Optical geometry", "Electrical quality", "Packet error"]):
        axis.set_title(title)
        axis.set_xlabel("Receiver FOV")
        axis.grid(axis="y", alpha=0.25)
    fig.suptitle("LiFi/OWC physical response")
    fig.tight_layout()
    fig.savefig(FIGURES / "lifi_fov_physical_response.png", dpi=180)
    plt.close(fig)
    messages.append("lifi_fov_physical_response.png")
    return messages


def main() -> int:
    app = read_csv(ANALYSIS / "final_application_flow_dataset.csv")
    physical = read_csv(ANALYSIS / "lifi_physical_summary.csv")
    numeric_fields = METRICS + ["tx_packets", "rx_packets", "lost_packets", "rx_bytes"]
    for row in app:
        for field in numeric_fields:
            row[field] = float(row[field])
        for field in ["seed", "CPE", "FlowId"]:
            row[field] = int(row[field])
        for field in ["offered_load_mbps", "mobility_speed_mps", "lifi_fov_deg"]:
            row[field] = float(row[field])
    for row in physical:
        for field in [
            "seed", "CPE", "optical_state_rows", "offered_load_mbps", "mobility_speed_mps", "lifi_fov_deg",
            "in_fov_fraction", "zero_gain_fraction", "distance_mean", "distance_min", "distance_max",
            "H_LOS_mean", "received_power_mean", "SNR_mean", "SNR_min", "BER_mean", "PER_mean",
        ]:
            row[field] = float(row[field])

    # The run is the experimental unit: average the three CPE application
    # rows within each run/branch before any seed-level or factor summary.
    grouped_cpe: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in app:
        grouped_cpe[(str(row["run_id"]), str(row["branch"]))].append(row)
    run_rows: list[dict[str, object]] = []
    for (run_id, branch), rows in sorted(grouped_cpe.items()):
        first = rows[0]
        out: dict[str, object] = {
            "run_id": run_id,
            "seed": first["seed"],
            "offered_load_mbps": first["offered_load_mbps"],
            "mobility_speed_mps": first["mobility_speed_mps"],
            "lifi_fov_deg": first["lifi_fov_deg"],
            "branch": branch,
            "n_cpe": len(rows),
            "rx_packet_fraction": mean([float(row["rx_packets"]) / float(row["tx_packets"]) for row in rows if float(row["tx_packets"]) > 0]),
        }
        for field in METRICS:
            out[field] = mean([float(row[field]) for row in rows])
        for field in ["tx_packets", "rx_packets", "lost_packets", "rx_bytes"]:
            out[f"{field}_mean"] = mean([float(row[field]) for row in rows])
        run_rows.append(out)

    run_fields = ["run_id", "seed", "offered_load_mbps", "mobility_speed_mps", "lifi_fov_deg", "branch", "n_cpe", "rx_packet_fraction"] + METRICS + [f"{field}_mean" for field in ["tx_packets", "rx_packets", "lost_packets", "rx_bytes"]]
    write_csv(ANALYSIS / "run_level_kpi.csv", run_fields, run_rows)

    # Main-effect summaries retain run-level units; paired deltas below are
    # used for the clearest same-configuration comparisons.
    effect_rows: list[dict[str, object]] = []
    for factor, values, field in [
        ("offered_load", LOADS, "offered_load_mbps"),
        ("mobility_speed", SPEEDS, "mobility_speed_mps"),
        ("lifi_fov", FOVS, "lifi_fov_deg"),
    ]:
        for branch in BRANCHES:
            for value in values:
                subset = [row for row in run_rows if row["branch"] == branch and row[field] == value]
                result = {"factor": factor, "level": value, "branch": branch, "n_run_units": len(subset)}
                for metric in METRICS:
                    vals = [float(row[metric]) for row in subset]
                    result[f"{metric}_mean"] = mean(vals)
                    result[f"{metric}_std_across_run_units"] = std(vals)
                effect_rows.append(result)
    effect_fields = ["factor", "level", "branch", "n_run_units"]
    for metric in METRICS:
        effect_fields += [f"{metric}_mean", f"{metric}_std_across_run_units"]
    write_csv(ANALYSIS / "factor_main_effect_summary.csv", effect_fields, effect_rows)

    # Paired contrasts use identical load/speed/FOV/seed except for the
    # factor under test. This avoids treating CPEs as independent replicates.
    keyed = {(row["branch"], row["seed"], row["offered_load_mbps"], row["mobility_speed_mps"], row["lifi_fov_deg"]): row for row in run_rows}
    contrast_rows: list[dict[str, object]] = []

    def add_contrast(factor: str, low_label: str, high_label: str, low_key: str, high_key: str, vary: str, branch_filter: list[str] = BRANCHES) -> None:
        for branch in branch_filter:
            deltas: dict[str, list[float]] = defaultdict(list)
            pairs = 0
            if vary == "offered_load_mbps":
                pair_bases = ((seed, speed, fov) for seed in SEEDS for speed in SPEEDS for fov in FOVS)
                pairs_iter = (({"branch": branch, "seed": seed, "offered_load_mbps": float(low_key), "mobility_speed_mps": speed, "lifi_fov_deg": fov},
                               {"branch": branch, "seed": seed, "offered_load_mbps": float(high_key), "mobility_speed_mps": speed, "lifi_fov_deg": fov})
                              for seed, speed, fov in pair_bases)
            elif vary == "mobility_speed_mps":
                pairs_iter = (({"branch": branch, "seed": seed, "offered_load_mbps": load, "mobility_speed_mps": float(low_key), "lifi_fov_deg": fov},
                               {"branch": branch, "seed": seed, "offered_load_mbps": load, "mobility_speed_mps": float(high_key), "lifi_fov_deg": fov})
                              for seed in SEEDS for load in LOADS for fov in FOVS)
            else:
                pairs_iter = (({"branch": branch, "seed": seed, "offered_load_mbps": load, "mobility_speed_mps": speed, "lifi_fov_deg": float(low_key)},
                               {"branch": branch, "seed": seed, "offered_load_mbps": load, "mobility_speed_mps": speed, "lifi_fov_deg": float(high_key)})
                              for seed in SEEDS for load in LOADS for speed in SPEEDS)
            for low, high in pairs_iter:
                keys = ["branch", "seed", "offered_load_mbps", "mobility_speed_mps", "lifi_fov_deg"]
                low_row = keyed.get(tuple(low[k] for k in keys))
                high_row = keyed.get(tuple(high[k] for k in keys))
                if low_row is None or high_row is None:
                    continue
                pairs += 1
                for metric in METRICS:
                    deltas[metric].append(float(high_row[metric]) - float(low_row[metric]))
            result: dict[str, object] = {"factor": factor, "low_level": low_label, "high_level": high_label, "branch": branch, "n_paired_run_units": pairs}
            for metric in METRICS:
                result[f"{metric}_delta_high_minus_low_mean"] = mean(deltas[metric])
                result[f"{metric}_delta_std"] = std(deltas[metric])
                result[f"{metric}_delta_positive_fraction"] = mean([delta > 0 for delta in deltas[metric]])
            contrast_rows.append(result)

    add_contrast("offered_load", "2", "20", "2", "20", "offered_load_mbps")
    add_contrast("mobility_speed", "0.5", "3.0", "0.5", "3.0", "mobility_speed_mps")
    add_contrast("lifi_fov", "70", "40", "70", "40", "lifi_fov_deg", ["LiFi"])
    contrast_fields = ["factor", "low_level", "high_level", "branch", "n_paired_run_units"]
    for metric in METRICS:
        contrast_fields += [f"{metric}_delta_high_minus_low_mean", f"{metric}_delta_std", f"{metric}_delta_positive_fraction"]
    write_csv(ANALYSIS / "paired_factor_contrasts.csv", contrast_fields, contrast_rows)

    # LiFi physical summaries, with the same CPE-within-run then seed logic.
    physical_grouped: dict[tuple[float, float, float], list[dict[str, object]]] = defaultdict(list)
    for row in physical:
        physical_grouped[(row["offered_load_mbps"], row["mobility_speed_mps"], row["lifi_fov_deg"])].append(row)
    physical_metrics = ["in_fov_fraction", "zero_gain_fraction", "distance_mean", "H_LOS_mean", "received_power_mean", "SNR_mean", "SNR_min", "BER_mean", "PER_mean"]
    physical_grouped_rows: list[dict[str, object]] = []
    for key, rows in sorted(physical_grouped.items()):
        load, speed, fov = key
        by_seed: dict[int, list[dict[str, object]]] = defaultdict(list)
        for row in rows:
            by_seed[int(row["seed"])].append(row)
        seed_rows: list[dict[str, float]] = []
        for seed_rows_raw in by_seed.values():
            seed_rows.append({metric: mean([float(row[metric]) for row in seed_rows_raw]) for metric in physical_metrics})
        result: dict[str, object] = {"offered_load_mbps": load, "mobility_speed_mps": speed, "lifi_fov_deg": fov, "n_seed_runs": len(seed_rows)}
        for metric in physical_metrics:
            vals = [row[metric] for row in seed_rows]
            result[f"{metric}_mean"] = mean(vals)
            result[f"{metric}_std_across_seeds"] = std(vals)
        physical_grouped_rows.append(result)
    physical_grouped_fields = ["offered_load_mbps", "mobility_speed_mps", "lifi_fov_deg", "n_seed_runs"]
    for metric in physical_metrics:
        physical_grouped_fields += [f"{metric}_mean", f"{metric}_std_across_seeds"]
    write_csv(ANALYSIS / "lifi_physical_grouped_summary_recomputed.csv", physical_grouped_fields, physical_grouped_rows)

    # Branch distribution summary establishes nontrivial RAT-dependent
    # variation without turning it into a universal technology ranking.
    branch_rows: list[dict[str, object]] = []
    for branch in BRANCHES:
        subset = [row for row in run_rows if row["branch"] == branch]
        result: dict[str, object] = {"branch": branch, "n_run_units": len(subset)}
        for metric in METRICS:
            vals = [float(row[metric]) for row in subset]
            result[f"{metric}_mean"] = mean(vals)
            result[f"{metric}_std"] = std(vals)
            result[f"{metric}_min"] = min(vals)
            result[f"{metric}_max"] = max(vals)
        branch_rows.append(result)
    branch_fields = ["branch", "n_run_units"]
    for metric in METRICS:
        branch_fields += [f"{metric}_mean", f"{metric}_std", f"{metric}_min", f"{metric}_max"]
    write_csv(ANALYSIS / "branch_variation_summary.csv", branch_fields, branch_rows)

    # Exact paired LiFi FOV physical deltas: wide (70°) vs narrow (40°).
    physical_keyed = {(row["seed"], row["offered_load_mbps"], row["mobility_speed_mps"], row["lifi_fov_deg"], row["CPE"]): row for row in physical}
    optical_delta_rows: list[dict[str, object]] = []
    for metric in physical_metrics:
        deltas = []
        for seed in SEEDS:
            for load in LOADS:
                for speed in SPEEDS:
                    for cpe in [1.0, 2.0, 3.0]:
                        narrow = physical_keyed.get((float(seed), float(load), float(speed), 40.0, cpe))
                        wide = physical_keyed.get((float(seed), float(load), float(speed), 70.0, cpe))
                        if narrow and wide:
                            deltas.append(float(narrow[metric]) - float(wide[metric]))
        optical_delta_rows.append({"metric": metric, "comparison": "40deg_minus_70deg", "n_paired_cpe_runs": len(deltas), "mean_delta": mean(deltas), "std_delta": std(deltas), "positive_fraction": mean([value > 0 for value in deltas])})
    write_csv(ANALYSIS / "lifi_fov_paired_physical_contrasts.csv", ["metric", "comparison", "n_paired_cpe_runs", "mean_delta", "std_delta", "positive_fraction"], optical_delta_rows)

    figure_messages = optionally_plot(run_rows, physical)

    # Human-readable findings use the actual generated values, not fixed
    # claims. The markdown is an analysis artifact, not manuscript text.
    def find_contrast(factor: str, branch: str) -> dict[str, object]:
        return next(row for row in contrast_rows if row["factor"] == factor and row["branch"] == branch)

    lines = [
        "# Scientific analysis of the synthetic three-RAT dataset",
        "",
        "This analysis uses the run as the experimental unit: the three CPE application-flow rows are averaged within each run/branch, and the three seeds are retained as the random-seed replicates for each fixed parameter cell.",
        "",
        "## Coverage",
        "",
        f"- Run-level branch summaries: **{len(run_rows)}** (48 runs × 3 branches).",
        f"- LiFi physical summaries: **{len(physical)}** (48 runs × 3 CPEs).",
        "- Factors: offered load 2/5/10/20 Mbps; mobility 0.5/3.0 m/s; LiFi FOV 40/70°; seeds 1/2/3.",
        "",
        "## Q1 — offered load",
        "",
    ]
    for branch in BRANCHES:
        row = find_contrast("offered_load", branch)
        lines.append(f"- **{branch}:** 20−2 Mbps paired change: throughput {fmt(float(row['throughput_mbps_delta_high_minus_low_mean']))} Mbps, delay {fmt(float(row['mean_delay_ms_delta_high_minus_low_mean']))} ms, jitter {fmt(float(row['mean_jitter_ms_delta_high_minus_low_mean']))} ms, FlowMonitor-reported loss ratio {fmt(float(row['FlowMonitor_reported_loss_ratio_delta_high_minus_low_mean']))}; {row['n_paired_run_units']} paired run units.")
    lines += [
        "",
        "Interpretation: the load response is configuration-specific. These paired changes identify whether the declared workload moves the branch toward a different operating regime, but they do not establish a universal capacity ranking.",
        "",
        "## Q2 — mobility",
        "",
    ]
    for branch in BRANCHES:
        row = find_contrast("mobility_speed", branch)
        lines.append(f"- **{branch}:** 3.0−0.5 m/s paired change: throughput {fmt(float(row['throughput_mbps_delta_high_minus_low_mean']))} Mbps, delay {fmt(float(row['mean_delay_ms_delta_high_minus_low_mean']))} ms, jitter {fmt(float(row['mean_jitter_ms_delta_high_minus_low_mean']))} ms, FlowMonitor-reported loss ratio {fmt(float(row['FlowMonitor_reported_loss_ratio_delta_high_minus_low_mean']))}; {row['n_paired_run_units']} paired run units.")
    lines += [
        "",
        "Interpretation: mobility effects are reported empirically under the selected ns-3 channel and mobility implementation; a small paired effect is not evidence that mobility is universally unimportant.",
        "",
        "## Q3 — LiFi FOV",
        "",
    ]
    narrow = next(row for row in contrast_rows if row["factor"] == "lifi_fov" and row["branch"] == "LiFi")
    lines.append(f"- LiFi 40−70° paired change: throughput {fmt(float(narrow['throughput_mbps_delta_high_minus_low_mean']))} Mbps, delay {fmt(float(narrow['mean_delay_ms_delta_high_minus_low_mean']))} ms, jitter {fmt(float(narrow['mean_jitter_ms_delta_high_minus_low_mean']))} ms, FlowMonitor-reported loss ratio {fmt(float(narrow['FlowMonitor_reported_loss_ratio_delta_high_minus_low_mean']))}; {narrow['n_paired_run_units']} paired run units.")
    lifi_rx_deltas = []
    for seed in SEEDS:
        for load in LOADS:
            for speed in SPEEDS:
                low = keyed[("LiFi", seed, load, speed, 70.0)]
                high = keyed[("LiFi", seed, load, speed, 40.0)]
                lifi_rx_deltas.append(float(high["rx_packet_fraction"]) - float(low["rx_packet_fraction"]))
    lines.append(f"- LiFi received-packet fraction (computed from exported tx/rx counters, 40−70°): mean delta {fmt(mean(lifi_rx_deltas))}; {len(lifi_rx_deltas)} paired run units. FlowMonitor-reported loss ratio is kept separate and is not interpreted as terminal loss.")
    for row in optical_delta_rows:
        lines.append(f"- Optical {row['metric']} (40−70°): mean delta {fmt(float(row['mean_delta']))}; {row['n_paired_cpe_runs']} paired CPE/run observations.")
    lines += [
        "",
        "Interpretation: narrowing the FOV is physically expected to reduce geometric acceptance. The preflight and paired summaries should be read through the LOS/FOV equations, not as a calibrated practical LiFi performance claim.",
        "",
        "## Q4 — RAT-dependent variation",
        "",
        "The branch distribution file reports nonzero ranges and branch-specific means for the run-level KPIs. This establishes that the final dataset contains configuration-dependent RAT variation rather than only a branch label, while not supporting a universal ranking across technologies.",
        "",
        "## Q5 — effectively inert or boundary-sensitive factors",
        "",
        "The complete factor and paired-contrast CSV files should be used to identify small effects. Any apparent invariance is a property of this bounded configuration, seed set, and stock/surrogate model, not a general technology statement. The LiFi physical state is sensitive to FOV through the explicit FOV gate; its packet-access abstraction and uncalibrated parameters remain important limitations.",
        "",
        "## Generated analysis artifacts",
        "",
        "- `run_level_kpi.csv`",
        "- `factor_main_effect_summary.csv`",
        "- `paired_factor_contrasts.csv`",
        "- `branch_variation_summary.csv`",
        "- `lifi_physical_grouped_summary_recomputed.csv`",
        "- `lifi_fov_paired_physical_contrasts.csv`",
        *[f"- `{message}`" for message in figure_messages],
        "",
        "No new ns-3 simulation was run by this analysis script.",
    ]
    (ANALYSIS / "scientific_sweep_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Three-RAT dataset analysis complete")
    print(f"run_level_rows={len(run_rows)} physical_rows={len(physical)}")
    print("; ".join(figure_messages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
