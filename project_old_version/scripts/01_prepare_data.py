"""
Step 1: Data Preparation

목적:
  - HCP-D NDA 텍스트 파일에서 음악 훈련 변수, 일화기억 점수, 공변량을 추출
  - 모든 subject-level 변수를 하나의 분석 테이블로 병합
  - 결측 처리 및 z-scoring

Input (DATA_DIR 안에):
  - ndar_subject01.txt    : 나이, 성별, 인종
  - saiq01.txt            : 음악·스포츠 활동 (부모 보고)
  - psm01.txt             : Picture Sequence Memory (일화기억, primary outcome)
  - lswmt01.txt           : List Sorting Working Memory (작업기억, secondary)
  - flanker01.txt         : Flanker (억제, secondary)
  - dccs01.txt            : DCCS (인지유연성, secondary)
  - pcps01.txt            : Pattern Comparison (처리속도, secondary)
  - wisc_v01.txt          : 행렬추론 (fluid IQ, covariate)
  - edinburgh_hand01.txt  : 손잡이
  - motion.csv (선택)     : MeanFD per subject

Output:
  - outputs/analysis_sample.csv
  - outputs/descriptive_statistics.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd

# =============================================================================
# Config
# =============================================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "raw"        # NDA txt 파일들 위치
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Motion threshold
MEAN_FD_THRESHOLD = 0.5  # mm. NeuroImage 표준 (Power et al. 2014)

# Subject ID 컬럼명 (NDA 표준)
SUBJECT_ID_COL = "src_subject_id"


# =============================================================================
# NDA loader
# =============================================================================

def load_nda_txt(path: Path) -> pd.DataFrame:
    """
    NDA 텍스트 파일 로더.
    NDA 포맷은 첫 줄에 short name, 두 번째 줄에 변수 description이 있음.
    실제 데이터는 3번째 줄부터.
    """
    if not path.exists():
        raise FileNotFoundError(f"NDA file not found: {path}")
    # 두 번째 줄(description) 건너뛰기
    df = pd.read_csv(path, sep="\t", skiprows=[1], low_memory=False)
    # subject ID 표준화
    if SUBJECT_ID_COL not in df.columns:
        raise ValueError(f"{SUBJECT_ID_COL} not in {path.name} columns: {df.columns.tolist()[:10]}")
    df[SUBJECT_ID_COL] = df[SUBJECT_ID_COL].astype(str).str.strip()
    return df


# =============================================================================
# Step 1a: Music training variables
# =============================================================================

def extract_music_variables(saiq_path: Path) -> pd.DataFrame:
    """
    saiq01에서 음악 훈련 변수 계산.

    핵심 변수:
      music_training_status : 1 if 훈련 경험 있음, 0 else
      music_onset_age       : 시작 연령 = (현재 나이) - (훈련 기간 years)
      training_duration     : 누적 훈련량 (시간) = years * months_per_year * 4.33 * days_per_week * minutes_per_session / 60
      log_training_duration : log(누적량 + 1)
      early_onset_group     : 'early' (<7), 'middle' (7-12), 'late' (>12), 'none'
    """
    saiq = load_nda_txt(saiq_path)

    # HCP-D saiq01 변수명 (부모 보고 prefix: ccf_sai_p_)
    age_col = "interview_age"          # months
    music_years_col = "ccf_sai_p_music_nyr"      # 훈련 기간 (년)
    music_months_col = "ccf_sai_p_music_nm"      # 연중 활동 개월
    music_days_col = "ccf_sai_p_music_perwk"     # 주당 일수
    music_minutes_col = "ccf_sai_p_music_min"    # 회당 분

    needed = [age_col, music_years_col, music_months_col, music_days_col, music_minutes_col]
    missing = [c for c in needed if c not in saiq.columns]
    if missing:
        print(f"  [warning] saiq01에 다음 컬럼 없음: {missing}")
        print(f"  available columns starting with 'ccf_sai_p_music': "
              f"{[c for c in saiq.columns if c.startswith('ccf_sai_p_music')]}")

    df = saiq[[SUBJECT_ID_COL] + [c for c in needed if c in saiq.columns]].copy()

    # 현재 나이 (years)
    df["age_years"] = pd.to_numeric(df.get(age_col), errors="coerce") / 12.0

    # 음악 훈련 변수
    years = pd.to_numeric(df.get(music_years_col), errors="coerce")
    mpy = pd.to_numeric(df.get(music_months_col), errors="coerce")  # months per year
    dpw = pd.to_numeric(df.get(music_days_col), errors="coerce")    # days per week
    mps = pd.to_numeric(df.get(music_minutes_col), errors="coerce") # minutes per session

    # 시작 연령
    df["music_onset_age"] = df["age_years"] - years

    # 누적 훈련량 (시간)
    df["training_duration"] = (years * mpy * 4.33 * dpw * mps) / 60.0
    df["log_training_duration"] = np.log1p(df["training_duration"])

    # 훈련 status: years > 0 이고 onset_age 유효
    df["music_training_status"] = ((years > 0) & df["music_onset_age"].notna()).astype(int)

    # 그룹화
    def categorize(onset):
        if pd.isna(onset):
            return "none"
        if onset < 7:
            return "early"
        if onset <= 12:
            return "middle"
        return "late"
    df["early_onset_group"] = df["music_onset_age"].apply(categorize)
    df.loc[df["music_training_status"] == 0, "early_onset_group"] = "none"

    # 결과 컬럼만 반환
    keep = [SUBJECT_ID_COL, "music_training_status", "music_onset_age",
            "training_duration", "log_training_duration", "early_onset_group"]
    return df[keep]


# =============================================================================
# Step 1b: NIH Toolbox cognitive scores
# =============================================================================

# 각 task별 score 컬럼명 (HCP-D NDA 명세, age-corrected standard score)
COG_COLUMNS = {
    "episodic_memory":      ("psm01.txt",     "nih_tlbx_agecsc_dom"),  # Picture Sequence Memory (primary)
    "working_memory":       ("lswmt01.txt",   "age_corrected_standard_score"),
    "cognitive_flexibility":("dccs01.txt",    "nih_dccs_ageadjusted"),
    "inhibition":           ("flanker01.txt", "nih_flanker_ageadjusted"),
    "processing_speed":     ("pcps01.txt",    "age_corrected_standard_score"),
}


def extract_cognitive_scores(data_dir: Path) -> pd.DataFrame:
    """
    NIH Toolbox 5개 task의 age-corrected standard score 추출.
    """
    merged = None
    for label, (fname, col) in COG_COLUMNS.items():
        path = data_dir / fname
        try:
            df = load_nda_txt(path)
        except FileNotFoundError:
            print(f"  [warning] {fname} 없음 — {label} 건너뜀")
            continue
        if col not in df.columns:
            # fallback: 점수처럼 보이는 컬럼 찾기
            candidates = [c for c in df.columns if "ageadjusted" in c.lower()
                          or "agecsc" in c.lower()
                          or "age_corrected" in c.lower()]
            print(f"  [warning] {fname}에 {col} 없음. 후보: {candidates}")
            if not candidates:
                continue
            col = candidates[0]
        sub = df[[SUBJECT_ID_COL, col]].copy()
        sub[col] = pd.to_numeric(sub[col], errors="coerce")
        sub = sub.rename(columns={col: label})
        # 같은 피험자가 여러 visit이면 첫 값 사용
        sub = sub.drop_duplicates(subset=[SUBJECT_ID_COL], keep="first")
        merged = sub if merged is None else merged.merge(sub, on=SUBJECT_ID_COL, how="outer")
    return merged


# =============================================================================
# Step 1c: Demographics + IQ + Motion
# =============================================================================

def extract_demographics(data_dir: Path) -> pd.DataFrame:
    """나이, 성별, 인종."""
    df = load_nda_txt(data_dir / "ndar_subject01.txt")
    keep = [SUBJECT_ID_COL]
    if "interview_age" in df.columns:
        df["age_years"] = pd.to_numeric(df["interview_age"], errors="coerce") / 12.0
        keep.append("age_years")
    if "sex" in df.columns:
        # M=1, F=0으로 인코딩
        df["sex_male"] = (df["sex"].astype(str).str.upper() == "M").astype(int)
        keep.append("sex_male")
    if "race" in df.columns:
        keep.append("race")
    return df[keep].drop_duplicates(subset=[SUBJECT_ID_COL], keep="first")


def extract_iq(data_dir: Path) -> pd.DataFrame:
    """WISC-V 행렬추론 (fluid IQ proxy)."""
    path = data_dir / "wisc_v01.txt"
    try:
        df = load_nda_txt(path)
    except FileNotFoundError:
        print(f"  [warning] wisc_v01.txt 없음")
        return pd.DataFrame(columns=[SUBJECT_ID_COL, "matrix_iq"])
    # WISC-V 행렬추론 scaled score 후보
    candidates = [c for c in df.columns if "matrix" in c.lower() and "scaled" in c.lower()]
    if not candidates:
        candidates = [c for c in df.columns if "mr" in c.lower() and "ss" in c.lower()]
    col = candidates[0] if candidates else None
    if col is None:
        print(f"  [warning] WISC matrix reasoning 컬럼을 못 찾음")
        return df[[SUBJECT_ID_COL]].drop_duplicates()
    df["matrix_iq"] = pd.to_numeric(df[col], errors="coerce")
    return df[[SUBJECT_ID_COL, "matrix_iq"]].drop_duplicates(subset=[SUBJECT_ID_COL], keep="first")


def extract_handedness(data_dir: Path) -> pd.DataFrame:
    path = data_dir / "edinburgh_hand01.txt"
    try:
        df = load_nda_txt(path)
    except FileNotFoundError:
        return pd.DataFrame(columns=[SUBJECT_ID_COL, "handedness"])
    candidates = [c for c in df.columns if "lq" in c.lower() or "hand" in c.lower()]
    candidates = [c for c in candidates if c != SUBJECT_ID_COL]
    if not candidates:
        return df[[SUBJECT_ID_COL]].drop_duplicates()
    df["handedness"] = pd.to_numeric(df[candidates[0]], errors="coerce")
    return df[[SUBJECT_ID_COL, "handedness"]].drop_duplicates(subset=[SUBJECT_ID_COL], keep="first")


def extract_motion(data_dir: Path) -> pd.DataFrame:
    """
    MeanFD per subject. 별도 motion.csv 파일을 가정.
    없으면 빈 DataFrame을 반환하고, 이후 단계에서 motion 제외.
    """
    path = data_dir / "motion.csv"
    if not path.exists():
        print(f"  [info] motion.csv 없음 — MeanFD 공변량 사용 못 함")
        return pd.DataFrame(columns=[SUBJECT_ID_COL, "mean_fd"])
    df = pd.read_csv(path)
    if SUBJECT_ID_COL not in df.columns:
        # 첫 컬럼이 subject id라고 가정
        df = df.rename(columns={df.columns[0]: SUBJECT_ID_COL})
    df[SUBJECT_ID_COL] = df[SUBJECT_ID_COL].astype(str).str.strip()
    fd_col = next((c for c in df.columns if "fd" in c.lower() and c != SUBJECT_ID_COL), None)
    if fd_col is None:
        raise ValueError(f"motion.csv에 FD 컬럼이 없음. columns={df.columns.tolist()}")
    df["mean_fd"] = pd.to_numeric(df[fd_col], errors="coerce")
    return df[[SUBJECT_ID_COL, "mean_fd"]].drop_duplicates(subset=[SUBJECT_ID_COL], keep="first")


# =============================================================================
# Main
# =============================================================================

def zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std(ddof=0)


def main():
    print("=" * 70)
    print("Step 1: Data Preparation")
    print("=" * 70)
    print(f"DATA_DIR: {DATA_DIR}")

    # 음악 변수
    print("\n[1/5] Music training variables...")
    music = extract_music_variables(DATA_DIR / "saiq01.txt")
    print(f"  음악 변수: {len(music)} subjects, "
          f"trained={music['music_training_status'].sum()}")

    # 인지 점수
    print("\n[2/5] Cognitive scores...")
    cog = extract_cognitive_scores(DATA_DIR)
    print(f"  인지 점수: {len(cog)} subjects, columns={list(cog.columns)[1:]}")

    # 인구통계 + IQ + 손잡이 + motion
    print("\n[3/5] Demographics, IQ, handedness, motion...")
    demo = extract_demographics(DATA_DIR)
    iq = extract_iq(DATA_DIR)
    hand = extract_handedness(DATA_DIR)
    motion = extract_motion(DATA_DIR)

    # 병합 (outer join → 단계적 dropna)
    print("\n[4/5] Merging...")
    merged = demo.merge(music, on=SUBJECT_ID_COL, how="outer", suffixes=("", "_music"))
    # demo의 age_years를 우선 사용 (saiq의 age는 동일해야 함)
    if "age_years_music" in merged.columns:
        merged = merged.drop(columns=["age_years_music"])
    merged = merged.merge(cog, on=SUBJECT_ID_COL, how="left")
    merged = merged.merge(iq, on=SUBJECT_ID_COL, how="left")
    merged = merged.merge(hand, on=SUBJECT_ID_COL, how="left")
    merged = merged.merge(motion, on=SUBJECT_ID_COL, how="left")

    print(f"  전체 병합 후: {len(merged)} rows, {merged.shape[1]} cols")

    # Analysis sample: primary outcome + 기본 공변량 필수
    required_for_sample = ["episodic_memory", "age_years", "sex_male"]
    have_all_required = all(c in merged.columns for c in required_for_sample)
    if not have_all_required:
        print(f"  [warning] required 컬럼 누락: "
              f"{[c for c in required_for_sample if c not in merged.columns]}")

    sample = merged.dropna(subset=[c for c in required_for_sample if c in merged.columns]).copy()
    print(f"  primary outcome + 기본 공변량 있는 subject: {len(sample)}")

    # Motion exclusion (motion 있을 때만)
    if "mean_fd" in sample.columns and sample["mean_fd"].notna().any():
        before = len(sample)
        sample = sample[(sample["mean_fd"].isna()) | (sample["mean_fd"] <= MEAN_FD_THRESHOLD)]
        print(f"  motion exclusion (MeanFD <= {MEAN_FD_THRESHOLD}): {before} → {len(sample)}")

    # Z-score 연속 변수 (음악 훈련자 only 분석에서 사용할 거니까 별도 컬럼으로)
    print("\n[5/5] Z-scoring continuous variables...")
    cont_cols = ["music_onset_age", "log_training_duration", "training_duration",
                 "age_years", "matrix_iq", "mean_fd", "handedness"]
    cont_cols += [c for c in cog.columns if c != SUBJECT_ID_COL]
    for c in cont_cols:
        if c in sample.columns:
            sample[f"z_{c}"] = zscore(sample[c])

    # 저장
    out_path = OUTPUT_DIR / "analysis_sample.csv"
    sample.to_csv(out_path, index=False)
    print(f"\n저장: {out_path}  ({len(sample)} subjects, {sample.shape[1]} cols)")

    # Descriptive statistics
    desc_rows = []
    for c in cont_cols:
        if c in sample.columns:
            s = sample[c]
            desc_rows.append({
                "variable": c,
                "n": s.notna().sum(),
                "mean": s.mean(),
                "sd": s.std(),
                "min": s.min(),
                "median": s.median(),
                "max": s.max(),
            })
    desc = pd.DataFrame(desc_rows)
    desc_path = OUTPUT_DIR / "descriptive_statistics.csv"
    desc.to_csv(desc_path, index=False)
    print(f"저장: {desc_path}")

    # 그룹별 요약 (음악 훈련자 vs 비훈련자)
    print("\n--- 음악 훈련자 vs 비훈련자 (primary outcome) ---")
    if "episodic_memory" in sample.columns:
        for status, grp in sample.groupby("music_training_status"):
            label = "trained" if status == 1 else "untrained"
            print(f"  {label}: n={len(grp)}, "
                  f"episodic_memory mean={grp['episodic_memory'].mean():.2f} "
                  f"(SD={grp['episodic_memory'].std():.2f})")

    print("\nStep 1 완료.")


if __name__ == "__main__":
    main()
