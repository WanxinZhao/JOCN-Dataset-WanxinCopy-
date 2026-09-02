"""Generate manuscript figures directly from the major-revision CSV outputs."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
E1 = ROOT / "MajorRevision" / "E1_semantic_utility" / "utility_results_summary.csv"
E2 = ROOT / "MajorRevision" / "E2_privacy" / "privacy_utility_tradeoff.csv"
PAPER_FIGURES = ROOT.parent / "1-论文正文" / "Figures"


def main() -> None:
    utility = pd.read_csv(E1)
    utility = utility[utility["task"] == "binary"].set_index("method")
    privacy = pd.read_csv(E2).set_index("method")

    labels = ["Majority", "Random", "Optical only", "Raw+optical", "V1+optical", "V2+optical", "V3+optical", "PCA3+optical"]
    methods = ["Majority", "StratifiedRandom", "OpticalOnly", "RawWirelessPlusOptical", "V1PlusOptical", "V2PlusOptical", "V3PlusOptical", "PCA3PlusOptical"]
    colors = ["#9e9e9e", "#bdbdbd", "#90a4ae", "#5c6bc0", "#42a5f5", "#26a69a", "#ef6c00", "#7e57c2"]

    values = utility.loc[methods, "macro_f1_mean"]
    errors = utility.loc[methods, "macro_f1_ci95"]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0), constrained_layout=True)
    axes[0].barh(labels, values, xerr=errors, color=colors, capsize=2)
    axes[0].invert_yaxis()
    axes[0].set_xlim(0.4, 0.68)
    axes[0].set_xlabel("Binary service-risk Macro-F1")
    axes[0].set_title("(a) Utility (mean and 95% CI; 10 seeds)")
    axes[0].grid(axis="x", alpha=0.25)

    for method, marker, color in [("V1", "o", "#42a5f5"), ("V2", "s", "#26a69a"), ("V3", "^", "#ef6c00"), ("PCA3", "D", "#7e57c2")]:
        row = privacy.loc[method]
        axes[1].scatter(row["privacy_leakage"], row["utility"], marker=marker, s=75, color=color, label=method)
        axes[1].annotate(method, (row["privacy_leakage"], row["utility"]), xytext=(5, 4), textcoords="offset points", fontsize=9)
    axes[1].set_xlabel("Strongest CPE-attacker Macro-F1 (lower is better)")
    axes[1].set_ylabel("Binary service-risk Macro-F1 (higher is better)")
    axes[1].set_title("(b) Observed privacy--utility trade-off")
    axes[1].grid(alpha=0.25)
    axes[1].set_xlim(0.205, 0.26)
    axes[1].set_ylim(0.575, 0.655)

    PAPER_FIGURES.mkdir(parents=True, exist_ok=True)
    output = PAPER_FIGURES / "semantic_module_revision_results.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(output)


if __name__ == "__main__":
    main()
