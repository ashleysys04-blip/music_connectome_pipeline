"""
Step 2: Construct Functional Connectivity Matrices

목적:
  - 각 subject의 ROI time series에서 N×N functional connectivity matrix 계산
  - Pearson r → Fisher z-transform
  - 모든 subject의 FC matrix를 하나의 .npz로 저장

Input:
  - data/time_series/<subject_id>.csv  (또는 .npy, .tsv)
      모양: (T timepoints, N ROIs). 첫 행이 ROI 이름이면 자동으로 skip.

Output:
  - outputs/fc_matrices.npz  (key: subject_id → N×N z-matrix)
  - outputs/fc_subjects.csv  (성공적으로 FC 계산된 subject 리스트)
"""

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
TS_DIR = PROJECT_DIR / "data" / "time_series"
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Time series 파일 확장자 우선순위
TS_EXTENSIONS = [".csv", ".tsv", ".npy", ".txt"]


def load_time_series(path: Path) -> np.ndarray:
    """
    Time series 파일을 (T, N) array로 로드.
    파일에 헤더 행이 있으면 자동 감지.
    """
    if path.suffix == ".npy":
        ts = np.load(path)
    elif path.suffix in (".csv", ".tsv", ".txt"):
        sep = "\t" if path.suffix == ".tsv" else ("," if path.suffix == ".csv" else None)
        # 첫 행이 헤더인지 자동 감지
        with open(path) as f:
            first = f.readline().strip().split(sep) if sep else f.readline().split()
        try:
            [float(x) for x in first]
            header = None  # 모두 숫자 → 헤더 없음
        except ValueError:
            header = 0
        df = pd.read_csv(path, sep=sep, header=header)
        ts = df.values
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    if ts.ndim != 2:
        raise ValueError(f"Time series must be 2D, got shape {ts.shape}")

    # (T, N) 가정. 만약 N > T면 transpose 의심.
    if ts.shape[0] < ts.shape[1] and ts.shape[1] > 100:
        # 일반적으로 ROI N개 (200~400) < T (200~1200)
        # 그런데 N > T이면 transpose 확인 필요 — 그냥 안내만
        pass

    return ts.astype(np.float64)


def fc_from_timeseries(ts: np.ndarray) -> np.ndarray:
    """
    (T, N) time series → (N, N) Fisher-z FC matrix.
    Diagonal은 0으로 설정 (self-connection 제거).
    """
    # 각 ROI 평균 0, std 1로 정규화 후 correlation
    ts_z = (ts - ts.mean(axis=0, keepdims=True)) / ts.std(axis=0, ddof=0, keepdims=True)
    # nan이 있으면 zero variance ROI — 0으로 채움
    ts_z = np.nan_to_num(ts_z, nan=0.0, posinf=0.0, neginf=0.0)
    n_time = ts_z.shape[0]
    r = (ts_z.T @ ts_z) / n_time  # (N, N) Pearson correlation
    # Fisher z-transform. r=1이 되지 않게 clip.
    r = np.clip(r, -0.999999, 0.999999)
    z = np.arctanh(r)
    np.fill_diagonal(z, 0.0)
    return z


def find_subject_files(ts_dir: Path) -> dict:
    """디렉토리에서 subject_id → 파일 경로 매핑."""
    if not ts_dir.exists():
        raise FileNotFoundError(f"Time series directory not found: {ts_dir}")

    files = {}
    for ext in TS_EXTENSIONS:
        for p in ts_dir.glob(f"*{ext}"):
            # 파일명에서 subject id 추출 (확장자 제거)
            sid = p.stem
            # 흔한 prefix/suffix 정리: sub-, _ts, _bold 등
            sid = sid.replace("sub-", "").replace("_ts", "").replace("_bold", "")
            sid = sid.replace("_timeseries", "")
            if sid not in files:  # 첫 번째 확장자만
                files[sid] = p
    return files


def main():
    print("=" * 70)
    print("Step 2: Construct Functional Connectivity Matrices")
    print("=" * 70)
    print(f"Time series dir: {TS_DIR}")

    sample_path = OUTPUT_DIR / "analysis_sample.csv"
    if not sample_path.exists():
        raise FileNotFoundError(f"먼저 step 1을 실행하세요: {sample_path}")
    sample = pd.read_csv(sample_path)
    target_subjects = set(sample["src_subject_id"].astype(str))
    print(f"Step 1 분석 sample: {len(target_subjects)} subjects")

    files = find_subject_files(TS_DIR)
    print(f"Time series 파일: {len(files)}개 발견")

    fc_dict = {}
    failed = []
    n_rois = None

    for i, sid in enumerate(target_subjects):
        if sid not in files:
            failed.append((sid, "no time series file"))
            continue
        try:
            ts = load_time_series(files[sid])
            z = fc_from_timeseries(ts)
            fc_dict[sid] = z
            if n_rois is None:
                n_rois = z.shape[0]
                print(f"  [info] N ROIs = {n_rois}, T (first subj) = {ts.shape[0]}")
            elif z.shape[0] != n_rois:
                failed.append((sid, f"ROI mismatch: {z.shape[0]} vs {n_rois}"))
                del fc_dict[sid]
        except Exception as e:
            failed.append((sid, str(e)))

        if (i + 1) % 50 == 0:
            print(f"  진행: {i + 1}/{len(target_subjects)}")

    print(f"\nFC 계산 성공: {len(fc_dict)} / {len(target_subjects)}")
    if failed:
        print(f"실패: {len(failed)}")
        for sid, reason in failed[:5]:
            print(f"  {sid}: {reason}")
        if len(failed) > 5:
            print(f"  ... 외 {len(failed) - 5}건")

    # 저장
    out_npz = OUTPUT_DIR / "fc_matrices.npz"
    np.savez_compressed(out_npz, **fc_dict)
    print(f"\n저장: {out_npz}  ({len(fc_dict)} matrices)")

    out_subjects = OUTPUT_DIR / "fc_subjects.csv"
    pd.DataFrame({"src_subject_id": list(fc_dict.keys()), "n_rois": n_rois}).to_csv(
        out_subjects, index=False
    )
    print(f"저장: {out_subjects}")

    print("\nStep 2 완료.")


if __name__ == "__main__":
    main()
