"""
Step 4-6: GLM Analyses

세 가지 모델:

  Model 1 (Step 4 / Brain → Behavior):
    EpisodicMemory ~ BrainFeature + Age + Sex + MeanFD + IQ

  Model 2 (Step 5 / Music → Behavior):
    EpisodicMemory ~ MusicOnsetAge + log_TrainingDuration + Age + Sex + MeanFD + IQ
    (음악 훈련자만, n ≈ trained subjects)

  Model 3 (Step 6 / Music → Brain):
    BrainFeature ~ MusicOnsetAge + log_TrainingDuration + Age + Sex + MeanFD + IQ
    (음악 훈련자만)

모든 연속 변수는 z-score되어 있으므로 β는 standardized.

Output:
  - outputs/glm_brain_behavior.csv
  - outputs/glm_music_behavior.csv
  - outputs/glm_music_brain.csv
"""

from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.simplefilter("ignore", category=UserWarning)

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "outputs"

# 분석 대상 brain features (Step 3 graph_metrics.csv의 컬럼들)
GRAPH_FEATURES = [
    "global_efficiency",
    "char_path_length",
    "clustering_coef",
    "modularity",
    "small_worldness",
]

NETWORK_FEATURES_PREFIX = ("within_", "between_")

# Outcomes
PRIMARY_OUTCOME = "episodic_memory"
SECONDARY_OUTCOMES = ["working_memory", "cognitive_flexibility",
                      "inhibition", "processing_speed"]

# Base covariates (있을 때만 사용)
BASE_COVARS = ["age_years", "sex_male", "mean_fd", "matrix_iq"]


# =============================================================================
# Helpers
# =============================================================================

def zscore_inplace(df: pd.DataFrame, cols: list) -> None:
    for c in cols:
        if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
            s = df[c]
            sd = s.std(ddof=0)
            if sd > 0:
                df[c] = (s - s.mean()) / sd


def fit_glm(df: pd.DataFrame, outcome: str, predictor: str, covars: list) -> dict:
    """
    OLS: outcome ~ predictor + covars.
    필요한 변수에 NaN이 있는 row는 제외.
    """
    cols = [outcome, predictor] + covars
    sub = df[cols].dropna()
    n = len(sub)
    if n < 30:
        return {"n": n, "beta": np.nan, "se": np.nan, "t": np.nan,
                "p": np.nan, "ci_low": np.nan, "ci_high": np.nan, "r2": np.nan}

    X = sm.add_constant(sub[[predictor] + covars])
    y = sub[outcome]
    try:
        model = sm.OLS(y, X).fit()
    except Exception as e:
        return {"n": n, "beta": np.nan, "se": np.nan, "t": np.nan,
                "p": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                "r2": np.nan, "error": str(e)}

    beta = model.params[predictor]
    se = model.bse[predictor]
    ci = model.conf_int().loc[predictor]
    return {
        "n": n,
        "beta": beta,
        "se": se,
        "t": model.tvalues[predictor],
        "p": model.pvalues[predictor],
        "ci_low": ci[0],
        "ci_high": ci[1],
        "r2": model.rsquared,
    }


def available_covars(df: pd.DataFrame) -> list:
    return [c for c in BASE_COVARS if c in df.columns and df[c].notna().sum() > 10]


# =============================================================================
# Step 4: Brain → Behavior
# =============================================================================

def step4_brain_behavior(df: pd.DataFrame, brain_features: list, outcomes: list,
                        covars: list) -> pd.DataFrame:
    rows = []
    for outcome in outcomes:
        if outcome not in df.columns:
            continue
        for feat in brain_features:
            if feat not in df.columns:
                continue
            res = fit_glm(df, outcome=outcome, predictor=feat, covars=covars)
            rows.append({"outcome": outcome, "predictor": feat,
                         "family": "brain_behavior", **res})
    return pd.DataFrame(rows)


# =============================================================================
# Step 5: Music → Behavior
# =============================================================================

def step5_music_behavior(df: pd.DataFrame, outcomes: list, covars: list) -> pd.DataFrame:
    """
    음악 훈련자만 (music_training_status == 1) 사용.
    onset age와 log_training_duration을 같이 넣어서 timing vs dose 분리.
    """
    trained = df[df["music_training_status"] == 1].copy()
    print(f"  음악 훈련자: n={len(trained)}")

    rows = []
    for outcome in outcomes:
        if outcome not in trained.columns:
            continue
        # onset age 효과 (training duration 통제)
        res_onset = fit_glm(
            trained, outcome=outcome,
            predictor="music_onset_age",
            covars=["log_training_duration"] + covars,
        )
        rows.append({"outcome": outcome, "predictor": "music_onset_age",
                     "controlling_for": "log_training_duration + covars",
                     "family": "music_behavior", **res_onset})
        # training duration 효과 (onset 통제)
        res_dur = fit_glm(
            trained, outcome=outcome,
            predictor="log_training_duration",
            covars=["music_onset_age"] + covars,
        )
        rows.append({"outcome": outcome, "predictor": "log_training_duration",
                     "controlling_for": "music_onset_age + covars",
                     "family": "music_behavior", **res_dur})
    return pd.DataFrame(rows)


# =============================================================================
# Step 6: Music → Brain
# =============================================================================

def step6_music_brain(df: pd.DataFrame, brain_features: list, covars: list) -> pd.DataFrame:
    trained = df[df["music_training_status"] == 1].copy()

    rows = []
    for feat in brain_features:
        if feat not in trained.columns:
            continue
        res_onset = fit_glm(
            trained, outcome=feat,
            predictor="music_onset_age",
            covars=["log_training_duration"] + covars,
        )
        rows.append({"outcome": feat, "predictor": "music_onset_age",
                     "controlling_for": "log_training_duration + covars",
                     "family": "music_brain", **res_onset})
        res_dur = fit_glm(
            trained, outcome=feat,
            predictor="log_training_duration",
            covars=["music_onset_age"] + covars,
        )
        rows.append({"outcome": feat, "predictor": "log_training_duration",
                     "controlling_for": "music_onset_age + covars",
                     "family": "music_brain", **res_dur})
    return pd.DataFrame(rows)


# =============================================================================
# Main
# =============================================================================

def main():
    print("=" * 70)
    print("Step 4-6: GLM Analyses")
    print("=" * 70)

    # Load data
    sample = pd.read_csv(OUTPUT_DIR / "analysis_sample.csv")
    graph = pd.read_csv(OUTPUT_DIR / "graph_metrics.csv")
    df = sample.merge(graph, on="src_subject_id", how="inner")
    print(f"행동 + brain 모두 있는 subject: {len(df)}")

    # Brain feature 컬럼 자동 탐지 (GRAPH_FEATURES + network features)
    brain_features = [c for c in df.columns if c in GRAPH_FEATURES
                      or c.startswith(NETWORK_FEATURES_PREFIX)]
    print(f"분석 대상 brain features: {len(brain_features)}")
    print(f"  → {brain_features}")

    # Z-score: 연속 공변량/예측변수/종속변수 모두
    to_zscore = (
        brain_features
        + [PRIMARY_OUTCOME] + SECONDARY_OUTCOMES
        + ["music_onset_age", "log_training_duration", "training_duration"]
        + ["age_years", "matrix_iq", "mean_fd", "handedness"]
    )
    zscore_inplace(df, to_zscore)

    covars = available_covars(df)
    print(f"사용할 공변량: {covars}")

    outcomes = [PRIMARY_OUTCOME] + SECONDARY_OUTCOMES

    # Step 4
    print("\n[Step 4] Brain → Behavior...")
    bb = step4_brain_behavior(df, brain_features, outcomes, covars)
    bb.to_csv(OUTPUT_DIR / "glm_brain_behavior.csv", index=False)
    print(f"  결과: {len(bb)}개 모델. 저장: glm_brain_behavior.csv")
    # primary outcome만 요약
    primary = bb[bb["outcome"] == PRIMARY_OUTCOME].sort_values("p")
    print("\n  ◆ Primary outcome (episodic_memory) 결과:")
    print(primary[["predictor", "n", "beta", "p"]].to_string(index=False))

    # Step 5
    print("\n[Step 5] Music → Behavior...")
    mb = step5_music_behavior(df, outcomes, covars)
    mb.to_csv(OUTPUT_DIR / "glm_music_behavior.csv", index=False)
    print(f"  결과: {len(mb)}개 모델. 저장: glm_music_behavior.csv")
    primary_mb = mb[mb["outcome"] == PRIMARY_OUTCOME]
    print("\n  ◆ Primary outcome (episodic_memory) 결과:")
    print(primary_mb[["predictor", "controlling_for", "n", "beta", "p"]].to_string(index=False))

    # Step 6
    print("\n[Step 6] Music → Brain...")
    mbr = step6_music_brain(df, brain_features, covars)
    mbr.to_csv(OUTPUT_DIR / "glm_music_brain.csv", index=False)
    print(f"  결과: {len(mbr)}개 모델. 저장: glm_music_brain.csv")
    # onset age effect만 표시
    onset_brain = mbr[mbr["predictor"] == "music_onset_age"].sort_values("p")
    print("\n  ◆ music_onset_age → brain feature (top 5):")
    print(onset_brain[["outcome", "n", "beta", "p"]].head().to_string(index=False))

    print("\nStep 4-6 완료.")


if __name__ == "__main__":
    main()
