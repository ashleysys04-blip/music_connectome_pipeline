"""
Step 8: Exploratory Mediation Analysis

Model:
  Path a:  M = a0 + a1·X + covars     (X → M)
  Path b:  Y = b0 + b1·M + c'·X + covars   (M → Y, X 통제)
  Indirect effect = a1 × b1

  X = music_onset_age
  M = brain network feature (graph metric 또는 network FC)
  Y = episodic_memory

Mediator는 다음 경우에만 검정:
  1) Step 5: music_onset_age → episodic_memory 약하게라도 관계 (p < 0.2)
  2) Step 6: music_onset_age → brain feature 약하게라도 관계 (p < 0.2)
  3) Step 4: brain feature → episodic_memory 약하게라도 관계 (p < 0.2)

(엄격한 mediation은 모든 path가 유의해야 하지만, exploratory이므로
 관습적인 stepwise screening보다는 bootstrap CI에 의존.)

Significance: bootstrap (5000회) percentile CI가 0 포함하지 않으면 유의.

Output:
  - outputs/mediation_results.csv
"""

from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.simplefilter("ignore", category=UserWarning)

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "outputs"

N_BOOTSTRAP = 5000
RANDOM_SEED = 42
SCREENING_P = 0.2  # 약한 관계만이라도 보이는 mediator만 검정

X_VAR = "music_onset_age"
Y_VAR = "episodic_memory"
BASE_COVARS = ["age_years", "sex_male", "mean_fd", "matrix_iq",
               "log_training_duration"]


def fit_simple(df: pd.DataFrame, outcome: str, predictors: list) -> sm.regression.linear_model.RegressionResultsWrapper | None:
    sub = df[[outcome] + predictors].dropna()
    if len(sub) < 30:
        return None
    X = sm.add_constant(sub[predictors])
    y = sub[outcome]
    try:
        return sm.OLS(y, X).fit()
    except Exception:
        return None


def mediation_one(df: pd.DataFrame, mediator: str, covars: list,
                  n_boot: int = N_BOOTSTRAP, seed: int = RANDOM_SEED) -> dict:
    """
    Single mediator test with bootstrap CI for indirect effect a*b.
    """
    cols = [X_VAR, mediator, Y_VAR] + covars
    sub = df[cols].dropna().reset_index(drop=True)
    n = len(sub)
    if n < 30:
        return {"mediator": mediator, "n": n, "a": np.nan, "b": np.nan,
                "indirect_ab": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                "direct_c_prime": np.nan, "total_c": np.nan,
                "prop_mediated": np.nan, "significant": False}

    # Path a: M ~ X + covars
    Xa = sm.add_constant(sub[[X_VAR] + covars])
    Ma = sub[mediator]
    model_a = sm.OLS(Ma, Xa).fit()
    a = model_a.params[X_VAR]

    # Path b: Y ~ M + X + covars
    Xb = sm.add_constant(sub[[mediator, X_VAR] + covars])
    Yb = sub[Y_VAR]
    model_b = sm.OLS(Yb, Xb).fit()
    b = model_b.params[mediator]
    c_prime = model_b.params[X_VAR]

    # Total effect: Y ~ X + covars
    Xc = sm.add_constant(sub[[X_VAR] + covars])
    model_c = sm.OLS(Yb, Xc).fit()
    c_total = model_c.params[X_VAR]

    indirect = a * b
    prop = indirect / c_total if c_total != 0 else np.nan

    # Bootstrap
    rng = np.random.default_rng(seed)
    boot_indirect = np.empty(n_boot)
    idx_array = np.arange(n)
    for i in range(n_boot):
        idx = rng.choice(idx_array, size=n, replace=True)
        boot = sub.iloc[idx]
        try:
            a_i = sm.OLS(boot[mediator],
                         sm.add_constant(boot[[X_VAR] + covars])).fit().params[X_VAR]
            b_i = sm.OLS(boot[Y_VAR],
                         sm.add_constant(boot[[mediator, X_VAR] + covars])).fit().params[mediator]
            boot_indirect[i] = a_i * b_i
        except Exception:
            boot_indirect[i] = np.nan

    boot_indirect = boot_indirect[~np.isnan(boot_indirect)]
    ci_low, ci_high = np.percentile(boot_indirect, [2.5, 97.5])
    significant = (ci_low > 0) or (ci_high < 0)

    return {
        "mediator": mediator,
        "n": n,
        "a": a, "p_a": model_a.pvalues[X_VAR],
        "b": b, "p_b": model_b.pvalues[mediator],
        "direct_c_prime": c_prime, "p_c_prime": model_b.pvalues[X_VAR],
        "total_c": c_total, "p_c": model_c.pvalues[X_VAR],
        "indirect_ab": indirect,
        "ci_low": ci_low, "ci_high": ci_high,
        "prop_mediated": prop,
        "significant": significant,
    }


def screen_mediators(df: pd.DataFrame, candidates: list, covars: list) -> list:
    """
    각 candidate가 X와 Y 둘 다와 어느 정도 관계 있는지 확인.
    빠른 screening: X→M, M→Y가 p < SCREENING_P일 때만 통과.
    """
    passed = []
    for m in candidates:
        if m not in df.columns:
            continue
        # X → M
        model_xm = fit_simple(df, m, [X_VAR] + covars)
        if model_xm is None:
            continue
        p_xm = model_xm.pvalues.get(X_VAR, np.nan)
        # M → Y (X 통제)
        model_my = fit_simple(df, Y_VAR, [m, X_VAR] + covars)
        if model_my is None:
            continue
        p_my = model_my.pvalues.get(m, np.nan)
        if p_xm < SCREENING_P and p_my < SCREENING_P:
            passed.append(m)
    return passed


def main():
    print("=" * 70)
    print("Step 8: Exploratory Mediation Analysis")
    print("=" * 70)

    sample = pd.read_csv(OUTPUT_DIR / "analysis_sample.csv")
    graph = pd.read_csv(OUTPUT_DIR / "graph_metrics.csv")
    df = sample.merge(graph, on="src_subject_id", how="inner")

    # 음악 훈련자만
    trained = df[df["music_training_status"] == 1].copy()
    print(f"음악 훈련자: n={len(trained)}")

    # z-score
    cont = [X_VAR, Y_VAR, "age_years", "matrix_iq", "mean_fd",
            "log_training_duration", "training_duration"]
    cont += [c for c in trained.columns
             if c in ["global_efficiency", "char_path_length", "clustering_coef",
                      "modularity", "small_worldness"]
             or c.startswith(("within_", "between_"))]
    for c in cont:
        if c in trained.columns and pd.api.types.is_numeric_dtype(trained[c]):
            sd = trained[c].std(ddof=0)
            if sd > 0:
                trained[c] = (trained[c] - trained[c].mean()) / sd

    covars = [c for c in BASE_COVARS if c in trained.columns and trained[c].notna().sum() > 10]
    print(f"공변량: {covars}")

    # Mediator 후보: 모든 brain features
    candidates = [c for c in trained.columns
                  if c in ["global_efficiency", "char_path_length", "clustering_coef",
                           "modularity", "small_worldness"]
                  or c.startswith(("within_", "between_"))]
    print(f"Mediator 후보: {len(candidates)}개 — {candidates}")

    # Screening (선택적 — 빠른 실행 원하면 사용)
    passed = screen_mediators(trained, candidates, covars)
    print(f"\nScreening 통과 (X→M, M→Y 둘 다 p<{SCREENING_P}): {len(passed)}")
    for m in passed:
        print(f"  - {m}")

    if not passed:
        print("\n[info] Screening 통과한 mediator 없음 — primary graph metrics만 시도")
        passed = [c for c in ["global_efficiency", "clustering_coef", "modularity"]
                  if c in trained.columns]

    # Full mediation with bootstrap
    print(f"\nBootstrap mediation (n_boot={N_BOOTSTRAP})...")
    results = []
    for m in passed:
        print(f"  {m}...")
        res = mediation_one(trained, m, covars)
        results.append(res)

    df_res = pd.DataFrame(results)
    out = OUTPUT_DIR / "mediation_results.csv"
    df_res.to_csv(out, index=False)
    print(f"\n저장: {out}")
    print("\n--- Mediation 결과 요약 ---")
    if len(df_res):
        show_cols = ["mediator", "n", "a", "b", "indirect_ab",
                     "ci_low", "ci_high", "significant", "prop_mediated"]
        print(df_res[show_cols].round(3).to_string(index=False))

    print("\nStep 8 완료.")


if __name__ == "__main__":
    main()
