"""Rebuild the GNPy manuscript figure from the audited unique-configuration CSV."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "MajorRevision" / "E4_gnpy_audit" / "unique_configurations.csv"
OUTPUT = ROOT.parent / "1-论文正文" / "Figures" / "usecase1_revision.png"

DESTINATIONS = ["bradley stoke", "froxfield", "reading", "powergate"]
LABELS = {
    "bradley stoke": "Bradley Stoke\n(23.6 km)",
    "froxfield": "Froxfield\n(118.2 km)",
    "reading": "Reading\n(169.5 km)",
    "powergate": "Powergate\n(246.5 km)",
}
COLORS = {
    "bradley stoke": "#1976d2",
    "froxfield": "#2e7d32",
    "reading": "#ef6c00",
    "powergate": "#c62828",
}


def workflow_panel(ax) -> None:
    ax.set_axis_off()
    boxes = [
        ("User Request", "8 channel slots\nQPSK / 16QAM"),
        ("Scenario Expansion", "4 NDFF paths\n256 occupancy patterns"),
        ("Execution History", "3 launch powers\n8,192 executions"),
        ("Unique Dataset", "6,120 valid\n24 no-signal"),
    ]
    xs = [0.03, 0.275, 0.52, 0.765]
    width, height, y = 0.205, 0.64, 0.22
    for index, ((title, body), x) in enumerate(zip(boxes, xs)):
        box = FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            linewidth=1.2, edgecolor="#333333", facecolor="#f2f5f7",
            transform=ax.transAxes,
        )
        ax.add_patch(box)
        ax.text(x + width / 2, y + 0.46, title, ha="center", va="center", weight="bold", fontsize=10, transform=ax.transAxes)
        ax.text(x + width / 2, y + 0.25, body, ha="center", va="center", fontsize=9, transform=ax.transAxes)
        if index < len(xs) - 1:
            ax.add_patch(FancyArrowPatch(
                (x + width + 0.005, y + height / 2), (xs[index + 1] - 0.005, y + height / 2),
                arrowstyle="-|>", mutation_scale=14, linewidth=1.1, color="#333333",
                transform=ax.transAxes,
            ))
    ax.text(
        0.5, 0.04,
        "Iteration 1: 2,048 executions at -5.5 dBm   |   Iteration 2: 6,144 executions   |   6,144 unique configurations",
        ha="center", va="bottom", fontsize=9, transform=ax.transAxes,
    )
    ax.text(0.002, 0.88, "(a)", ha="left", va="top", fontsize=13, weight="bold", transform=ax.transAxes)


def main() -> None:
    frame = pd.read_csv(DATA, dtype={"channel_pattern": str})
    valid = frame[frame["status"] == "ok"].copy()
    valid["gsnr_db"] = pd.to_numeric(valid["gsnr_db"], errors="coerce")
    valid["channels"] = pd.to_numeric(valid["channels"], errors="coerce")

    fig = plt.figure(figsize=(14.5, 6.2), constrained_layout=True)
    grid = fig.add_gridspec(2, 3, height_ratios=[0.7, 1.6])
    workflow_panel(fig.add_subplot(grid[0, :]))

    # (b) GSNR distributions for the two joint modulation/slot-width configurations.
    ax_b = fig.add_subplot(grid[1, 0])
    positions, data, colors = [], [], []
    for destination_index, destination in enumerate(DESTINATIONS):
        for modulation_index, modulation in enumerate(["QPSK", "16QAM"]):
            subset = valid[
                (valid["destination"] == destination)
                & (valid["modulation"] == modulation)
                & (valid["launch_power_dbm"] == -5.5)
            ]["gsnr_db"].dropna()
            positions.append(destination_index * 3 + modulation_index + 1)
            data.append(subset.to_numpy())
            colors.append("#42b7c8" if modulation == "QPSK" else "#f39c34")
    boxplot = ax_b.boxplot(data, positions=positions, widths=0.72, patch_artist=True, showfliers=False)
    for patch, color in zip(boxplot["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_linewidth(0.9)
    ax_b.set_xticks([1.5, 4.5, 7.5, 10.5], [LABELS[d] for d in DESTINATIONS], fontsize=8)
    ax_b.set_ylabel("GSNR (dB)")
    ax_b.set_title("Joint format/slot configuration, $P_{launch}=-5.5$ dBm", fontsize=9)
    ax_b.grid(axis="y", alpha=0.25)
    ax_b.text(0.01, 0.98, "(b)", transform=ax_b.transAxes, ha="left", va="top", fontsize=13, weight="bold")
    ax_b.plot([], [], color="#42b7c8", linewidth=8, label="QPSK / 37.5 GHz")
    ax_b.plot([], [], color="#f39c34", linewidth=8, label="16QAM / 50 GHz")
    ax_b.legend(fontsize=7, loc="upper right")

    # (c) Mean route sensitivity relative to -5.5 dBm.
    ax_c = fig.add_subplot(grid[1, 1])
    grouped = valid.groupby(["destination", "launch_power_dbm"], as_index=False)["gsnr_db"].mean()
    for destination in DESTINATIONS:
        subset = grouped[grouped["destination"] == destination].sort_values("launch_power_dbm")
        baseline = float(subset.loc[subset["launch_power_dbm"] == -5.5, "gsnr_db"].iloc[0])
        ax_c.plot(
            subset["launch_power_dbm"], subset["gsnr_db"] - baseline,
            marker="o", linewidth=1.6, markersize=3.8,
            color=COLORS[destination], label=LABELS[destination].replace("\n", " "),
        )
    ax_c.axhline(0, color="#777777", linewidth=0.8)
    ax_c.set_xlabel("Launch power (dBm)")
    ax_c.set_ylabel(r"$\Delta$GSNR relative to -5.5 dBm (dB)")
    ax_c.set_xticks([-5.5, -5.0, -4.5])
    ax_c.set_title("Mean over both format/slot configurations", fontsize=9)
    ax_c.grid(alpha=0.25)
    ax_c.legend(fontsize=7, loc="lower left")
    ax_c.text(0.01, 0.98, "(c)", transform=ax_c.transAxes, ha="left", va="top", fontsize=13, weight="bold")

    # (d) QPSK channel-loading trend.
    ax_d = fig.add_subplot(grid[1, 2])
    loading = valid[(valid["modulation"] == "QPSK") & (valid["launch_power_dbm"] == -5.5)]
    loading = loading.groupby(["destination", "channels"], as_index=False)["gsnr_db"].mean()
    for destination in DESTINATIONS:
        subset = loading[loading["destination"] == destination].sort_values("channels")
        ax_d.plot(
            subset["channels"], subset["gsnr_db"], marker="o", linewidth=1.6, markersize=3.8,
            color=COLORS[destination], label=LABELS[destination].replace("\n", " "),
        )
    ax_d.set_xlabel("Number of active WDM channels")
    ax_d.set_ylabel("Mean GSNR (dB)")
    ax_d.set_xticks(range(1, 9))
    ax_d.set_title("QPSK / 37.5 GHz, $P_{launch}=-5.5$ dBm", fontsize=9)
    ax_d.grid(alpha=0.25)
    ax_d.legend(fontsize=7, loc="center right")
    ax_d.text(0.01, 0.98, "(d)", transform=ax_d.transAxes, ha="left", va="top", fontsize=13, weight="bold")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=400, bbox_inches="tight")
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
