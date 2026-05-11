"""
Step 7: Multiple Comparison Correction (FDR)

Family 정의:

  Primary family (가설 직접 검증):
    - music_onset_age → primary brain features (global eff, clustering, modularity)
    - primary brain features → episodic_memory
    - music_onset_age → episodic_memory

  Secondary family (탐색):
    - secondary cognitive outcomes
    - 추가 network-level features

각 family 내에서 Benjamini-Hochberg FDR (q < 0.05).

Output:
  - outputs/fdr_corrected_results.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "outputs"

# Primary로 다룰 graph metrics
PRIMARY_BRAIN_FEATURES = ["global_efficiency", "clustering_coef", "modularity"]
PRIMARY_OUTCOME = "episodic_memory"


def bh_fdr(pvals: np.ndarray, alpha: float = 0.05) -> tuple:
    """Benjamini-Hochberg. NaN은 그대로 둠."""
    pvals = np.asarray(pvals, dtype=float)
    mask = ~np.isnan(pvals)
    qvals = np.full_like(pvals, np.nan)
    if mask.sum() == 0:
        return qvals, np.zeros_like(pvals, dtype=bool)
    rej, q, _, _ = multipletests(pvals[mask], alpha=alpha, method="fdr_bh")
    qvals[mask] = q
    reject = np.zeros_like(pvals, dtype=bool)
    reject[mask] = rej
    return qvals, reject


def main():
    print("=" * 70)
    print("Step 7: FDR Correction")
    print("=" * 70)

    # Load
    bb = pd.read_csv(OUTPUT_DIR / "glm_brain_behavior.csv")
    mb = pd.read_csv(OUTPUT_DIR / "glm_music_behavior.csv")
    mbr = pd.read_csv(OUTPUT_DIR / "glm_music_brain.csv")

    all_results = []

    # ---- Primary family ----
    # 1) Brain → episodic_memory (primary brain features만)
    p1 = bb[(bb["outcome"] == PRIMARY_OUTCOME)
            & (bb["predictor"].isin(PRIMARY_BRAIN_FEATURES))].copy()
    p1["family"] = "primary_brain_to_episodic"

    # 2) music_onset_age → episodic_memory
    p2 = mb[(mb["outcome"] == PRIMARY_OUTCOME)
            & (mb["predictor"] == "music_onset_age")].copy()
    p2["family"] = "primary_music_to_episodic"

    # 3) music_onset_age → primary brain features
    p3 = mbr[(mbr["outcome"].isin(PRIMARY_BRAIN_FEATURES))
             & (mbr["predictor"] == "music_onset_age")].copy()
    p3["family"] = "primary_music_to_brain"

    primary = pd.concat([p1, p2, p3], ignore_index=True)
    if len(primary):
        qvals, reject = bh_fdr(primary["p"].values, alpha=0.05)
        primary["q_fdr"] = qvals
        primary["reject_fdr05"] = reject
        all_results.append(primary)
        print(f"\nPrimary family: {len(primary)} tests, "
              f"survives FDR q<.05: {reject.sum()}")
        print(primary[["family", "outcome", "predictor", "beta", "p", "q_fdr",
                       "reject_fdr05"]].to_string(index=False))

    # ---- Secondary family: secondary outcomes ----
    secondary_outcomes = ["working_memory", "cognitive_flexibility",
                          "inhibition", "processing_speed"]
    s1 = bb[(bb["outcome"].isin(secondary_outcomes))
            & (bb["predictor"].isin(PRIMARY_BRAIN_FEATURES))].copy()
    s1["family"] = "secondary_brain_to_cog"
    s2 = mb[(mb["outcome"].isin(secondary_outcomes))
            & (mb["predictor"] == "music_onset_age")].copy()
    s2["family"] = "secondary_music_to_cog"
    secondary = pd.concat([s1, s2], ignore_index=True)
    if len(secondary):
        qvals, reject = bh_fdr(secondary["p"].values, alpha=0.05)
        secondary["q_fdr"] = qvals
        secondary["reject_fdr05"] = reject
        all_results.append(secondary)
        print(f"\nSecondary family (cognitive outcomes): {len(secondary)} tests, "
              f"survives FDR: {reject.sum()}")

    # ---- Exploratory family: network-level FC ----
    net_rows = []
    for tbl, label in [(bb, "brain_to_episodic"), (mbr, "music_to_brain")]:
        rows = tbl[tbl["outcome"].astype(str).str.startswith(("within_", "between_")) |
                   tbl["predictor"].astype(str).str.startswith(("within_", "between_"))].copy()
        if len(rows):
            rows["family"] = f"exploratory_network_{label}"
            net_rows.append(rows)
    if net_rows:
        exploratory = pd.concat(net_rows, ignore_index=True)
        qvals, reject = bh_fdr(exploratory["p"].values, alpha=0.05)
        exploratory["q_fdr"] = qvals
        exploratory["reject_fdr05"] = reject
        all_results.append(exploratory)
        print(f"\nExploratory family (network FC): {len(exploratory)} tests, "
              f"survives FDR: {reject.sum()}")

    # Save
    combined = pd.concat(all_results, ignore_index=True)
    out = OUTPUT_DIR / "fdr_corrected_results.csv"
    combined.to_csv(out, index=False)
    print(f"\n저장: {out}")
    print("\nStep 7 완료.")


if __name__ == "__main__":
    main()
