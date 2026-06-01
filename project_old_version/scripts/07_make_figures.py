"""
Figures: 발표용 그림 6개

Fig1: 개념 모델 (텍스트 박스 다이어그램)
Fig2: 분석 pipeline
Fig3: Music onset group × episodic memory boxplot
Fig4: Partial regression — brain feature vs episodic memory (covariates 통제)
Fig5: Forest plot — 표준화 β with 95% CI
Fig6: Mediation diagram
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Rectangle, FancyBboxPatch
import seaborn as sns
import statsmodels.api as sm

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "outputs"
FIG_DIR = PROJECT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 200,
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


# =============================================================================
# Fig 1: Conceptual model
# =============================================================================

def fig1_conceptual():
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    boxes = [
        (1.0, 1.5, 2.0, 1.0, "Music training\nhistory\n(onset age, duration)", "#E8C9F0"),
        (4.0, 1.5, 2.0, 1.0, "Memory-related\nbrain network\norganization", "#C9E0F0"),
        (7.0, 1.5, 2.0, 1.0, "Episodic memory\nperformance", "#C9F0DC"),
    ]
    for x, y, w, h, txt, color in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                     facecolor=color, edgecolor="black", linewidth=1.2))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=10)

    # Arrows
    arrow_style = dict(arrowstyle="->", color="black", linewidth=1.5, mutation_scale=15)
    ax.add_patch(FancyArrowPatch((3.0, 2.0), (4.0, 2.0), **arrow_style))
    ax.add_patch(FancyArrowPatch((6.0, 2.0), (7.0, 2.0), **arrow_style))
    # 직접 경로
    ax.add_patch(FancyArrowPatch((3.0, 1.7), (7.0, 1.7),
                                  arrowstyle="->", color="gray", linewidth=1.2,
                                  linestyle=":", mutation_scale=15,
                                  connectionstyle="arc3,rad=-0.3"))
    ax.text(5.0, 0.55, "direct path (c')", ha="center", color="gray", fontsize=9, style="italic")

    ax.text(5.0, 3.5, "Conceptual Model: Music Training → Brain Network → Episodic Memory",
            ha="center", fontsize=11, fontweight="bold")

    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig1_conceptual_model.png", bbox_inches="tight")
    plt.close()
    print("  ✓ fig1_conceptual_model.png")


# =============================================================================
# Fig 2: Analysis pipeline
# =============================================================================

def fig2_pipeline():
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 3)
    ax.axis("off")

    steps = [
        (0.2, "Data\nprep", "#FFE0B2"),
        (1.85, "ROI\ntime series\n→ FC matrix", "#FFCC80"),
        (3.7, "Graph\nmetrics", "#FFB74D"),
        (5.55, "GLM\n(brain ↔ behavior)", "#FFA726"),
        (7.4, "FDR\ncorrection", "#FF8A65"),
        (9.25, "Mediation\nanalysis", "#E57373"),
    ]
    for x, txt, color in steps:
        ax.add_patch(FancyBboxPatch((x, 0.8), 1.55, 1.4, boxstyle="round,pad=0.06",
                                     facecolor=color, edgecolor="black"))
        ax.text(x + 0.775, 1.5, txt, ha="center", va="center", fontsize=9.5)

    for i in range(len(steps) - 1):
        x_from = steps[i][0] + 1.55
        x_to = steps[i + 1][0]
        ax.add_patch(FancyArrowPatch((x_from, 1.5), (x_to, 1.5),
                                      arrowstyle="->", linewidth=1.5, mutation_scale=12))

    ax.text(5.5, 2.7, "Analysis Pipeline", ha="center", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig2_analysis_pipeline.png", bbox_inches="tight")
    plt.close()
    print("  ✓ fig2_analysis_pipeline.png")


# =============================================================================
# Fig 3: Music onset group vs episodic memory
# =============================================================================

def fig3_onset_memory(df):
    if "episodic_memory" not in df.columns or "early_onset_group" not in df.columns:
        print("  [skip] fig3: 필요한 컬럼 없음")
        return

    order = ["none", "late", "middle", "early"]
    plot_df = df[df["early_onset_group"].isin(order)].copy()
    if len(plot_df) == 0:
        return

    fig, ax = plt.subplots(figsize=(7, 4.5))
    palette = {"none": "#B0BEC5", "late": "#FFB74D",
               "middle": "#64B5F6", "early": "#81C784"}
    sns.boxplot(data=plot_df, x="early_onset_group", y="episodic_memory",
                order=order, palette=palette, ax=ax, width=0.55,
                showfliers=False)
    sns.stripplot(data=plot_df, x="early_onset_group", y="episodic_memory",
                  order=order, ax=ax, color="black", alpha=0.3, size=2.5, jitter=0.18)

    # n 표시
    for i, g in enumerate(order):
        n = (plot_df["early_onset_group"] == g).sum()
        ax.text(i, ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05,
                f"n={n}", ha="center", fontsize=9, color="gray")

    ax.set_xlabel("Music onset group")
    ax.set_ylabel("Episodic memory (age-corrected)")
    ax.set_title("Episodic memory by music onset age group")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig3_music_onset_memory.png", bbox_inches="tight")
    plt.close()
    print("  ✓ fig3_music_onset_memory.png")


# =============================================================================
# Fig 4: Partial regression — top brain feature vs episodic memory
# =============================================================================

def fig4_partial_regression(df, fdr):
    """가장 강한 brain → episodic memory 효과의 partial regression plot."""
    if fdr is None or "episodic_memory" not in df.columns:
        return
    bb = fdr[fdr["family"] == "primary_brain_to_episodic"].sort_values("p")
    if len(bb) == 0:
        return
    top = bb.iloc[0]
    feat = top["predictor"]
    if feat not in df.columns:
        return

    covars = [c for c in ["age_years", "sex_male", "mean_fd", "matrix_iq"]
              if c in df.columns]
    cols = ["episodic_memory", feat] + covars
    sub = df[cols].dropna().copy()
    if len(sub) < 30:
        return

    # Partial residuals
    res_y = sm.OLS(sub["episodic_memory"],
                   sm.add_constant(sub[covars])).fit().resid
    res_x = sm.OLS(sub[feat],
                   sm.add_constant(sub[covars])).fit().resid

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(res_x, res_y, alpha=0.5, s=22, color="#3F51B5", edgecolor="white", linewidth=0.5)
    # fit line
    slope, intercept = np.polyfit(res_x, res_y, 1)
    xs = np.linspace(res_x.min(), res_x.max(), 50)
    ax.plot(xs, slope * xs + intercept, color="#D32F2F", linewidth=1.6)

    ax.set_xlabel(f"{feat}  (residualized)")
    ax.set_ylabel("Episodic memory (residualized)")
    ax.set_title(f"Partial regression\nβ = {top['beta']:.2f}, p = {top['p']:.3f}, "
                 f"q = {top.get('q_fdr', np.nan):.3f} (n={int(top['n'])})")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig4_partial_regression.png", bbox_inches="tight")
    plt.close()
    print(f"  ✓ fig4_partial_regression.png ({feat})")


# =============================================================================
# Fig 5: Forest plot
# =============================================================================

def fig5_forest(fdr):
    if fdr is None:
        return
    primary = fdr[fdr["family"].astype(str).str.startswith("primary_")].copy()
    if len(primary) == 0:
        return
    primary["label"] = primary["family"].str.replace("primary_", "") + ": " \
                       + primary["predictor"].astype(str) + " → " \
                       + primary["outcome"].astype(str)
    primary = primary.sort_values("beta")

    fig, ax = plt.subplots(figsize=(8, max(3, 0.35 * len(primary) + 1)))
    y = np.arange(len(primary))
    ax.errorbar(primary["beta"], y,
                xerr=[primary["beta"] - primary["ci_low"],
                      primary["ci_high"] - primary["beta"]],
                fmt="o", color="#1565C0", ecolor="#90CAF9",
                capsize=3, markersize=6, linewidth=1.4)
    ax.axvline(0, color="gray", linestyle="--", linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(primary["label"], fontsize=8.5)
    ax.set_xlabel("Standardized β (95% CI)")
    ax.set_title("Forest plot: primary family effects")

    # 유의 표시
    for yi, sig in zip(y, primary["reject_fdr05"]):
        if sig:
            ax.text(ax.get_xlim()[1] * 0.95, yi, "*", fontsize=14, color="#D32F2F",
                    va="center", ha="right")

    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig5_forest_plot.png", bbox_inches="tight")
    plt.close()
    print("  ✓ fig5_forest_plot.png")


# =============================================================================
# Fig 6: Mediation diagram
# =============================================================================

def fig6_mediation():
    med_path = OUTPUT_DIR / "mediation_results.csv"
    if not med_path.exists():
        print("  [skip] fig6: mediation_results.csv 없음")
        return
    med = pd.read_csv(med_path)
    if len(med) == 0:
        return
    # Indirect effect 크기 절댓값 기준 top 1
    med = med.dropna(subset=["indirect_ab"]).copy()
    if len(med) == 0:
        return
    top = med.iloc[med["indirect_ab"].abs().argmax()]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # M box (top)
    ax.add_patch(FancyBboxPatch((4, 3.3), 2, 1, boxstyle="round,pad=0.06",
                                 facecolor="#C9E0F0", edgecolor="black"))
    ax.text(5, 3.8, f"M:\n{top['mediator']}", ha="center", va="center", fontsize=10)

    # X box (left)
    ax.add_patch(FancyBboxPatch((0.5, 1), 2, 1, boxstyle="round,pad=0.06",
                                 facecolor="#E8C9F0", edgecolor="black"))
    ax.text(1.5, 1.5, "X:\nmusic_onset_age", ha="center", va="center", fontsize=10)

    # Y box (right)
    ax.add_patch(FancyBboxPatch((7.5, 1), 2, 1, boxstyle="round,pad=0.06",
                                 facecolor="#C9F0DC", edgecolor="black"))
    ax.text(8.5, 1.5, "Y:\nepisodic_memory", ha="center", va="center", fontsize=10)

    # Arrows
    arrow = dict(arrowstyle="->", linewidth=1.6, mutation_scale=16, color="black")
    ax.add_patch(FancyArrowPatch((2.5, 1.9), (4.0, 3.4), **arrow))
    ax.add_patch(FancyArrowPatch((6.0, 3.4), (7.5, 1.9), **arrow))
    ax.add_patch(FancyArrowPatch((2.5, 1.5), (7.5, 1.5),
                                  arrowstyle="->", linewidth=1.6, mutation_scale=16,
                                  color="gray", linestyle=":"))

    # Labels
    ax.text(3.0, 2.9, f"a = {top['a']:.2f}", fontsize=10, color="#1565C0")
    ax.text(6.8, 2.9, f"b = {top['b']:.2f}", fontsize=10, color="#1565C0")
    ax.text(5.0, 1.2, f"c' (direct) = {top['direct_c_prime']:.2f}",
            ha="center", fontsize=9, color="gray")

    sig_txt = "significant" if top["significant"] else "n.s."
    ax.text(5, 4.7,
            f"Indirect effect a×b = {top['indirect_ab']:.3f}  "
            f"(95% CI [{top['ci_low']:.3f}, {top['ci_high']:.3f}])  •  {sig_txt}",
            ha="center", fontsize=11, fontweight="bold")

    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig6_mediation_diagram.png", bbox_inches="tight")
    plt.close()
    print("  ✓ fig6_mediation_diagram.png")


# =============================================================================
# Main
# =============================================================================

def main():
    print("=" * 70)
    print("Figures: 발표용 그림 생성")
    print("=" * 70)

    sample_path = OUTPUT_DIR / "analysis_sample.csv"
    graph_path = OUTPUT_DIR / "graph_metrics.csv"
    fdr_path = OUTPUT_DIR / "fdr_corrected_results.csv"

    if not sample_path.exists():
        raise FileNotFoundError(f"먼저 step 1을 실행하세요")
    sample = pd.read_csv(sample_path)
    if graph_path.exists():
        graph = pd.read_csv(graph_path)
        df = sample.merge(graph, on="src_subject_id", how="left")
    else:
        df = sample
    fdr = pd.read_csv(fdr_path) if fdr_path.exists() else None

    fig1_conceptual()
    fig2_pipeline()
    fig3_onset_memory(df)
    fig4_partial_regression(df, fdr)
    fig5_forest(fdr)
    fig6_mediation()

    print("\n모든 figure 저장 완료.")


if __name__ == "__main__":
    main()
