"""
Step 3: Graph-theoretical Measures

목적:
  - 각 subject의 FC matrix에서 graph metric 계산
  - Global: global efficiency, characteristic path length, mean clustering,
            modularity, small-worldness
  - Network-level: DMN, FPN, MTL 등 Yeo network 내/간 평균 FC

전처리:
  - Fisher z FC → absolute value 또는 양수만 사용 (negative weight 제거)
  - 본 구현은 양수 weight만 사용 (가장 흔한 관행). 필요시 --use_abs 옵션 추가.
  - Sparsity-based proportional thresholding (density 10%, 15%, 20%) 후 평균 OR
    fully-weighted graph. 본 구현은 weighted graph 사용 (정보 손실 최소화).

Input:
  - outputs/fc_matrices.npz
  - data/atlas/<atlas_labels>.csv  (ROI → Yeo 네트워크 매핑, optional)

Output:
  - outputs/graph_metrics.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd

# bctpy (Brain Connectivity Toolbox Python). 없으면 networkx 폴백.
try:
    import bct  # pip install bctpy
    HAS_BCT = True
except ImportError:
    HAS_BCT = False
    import networkx as nx

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "outputs"
ATLAS_DIR = PROJECT_DIR / "data" / "atlas"

# Yeo 네트워크 매핑 파일 (선택)
YEO_LABEL_FILE = ATLAS_DIR / "subregion_func_network_Yeo_updated_wt_subcortical.csv"

# 본 분석에서 관심 있는 네트워크 (memory-related)
TARGET_NETWORKS = ["Default", "FrontoParietal", "Limbic", "DorsalAttention"]
# Limbic이 MTL/hippocampus 영역 포함 (Yeo 7 network 기준)

# Null model 반복 (small-worldness 계산용)
# Null model 반복 (small-worldness 계산용)
N_NULL = 5  # 논문 수준은 50~100. 테스트엔 작게.
COMPUTE_SMALL_WORLDNESS = False  # True면 small-worldness 계산. 매우 느림 (subj당 수십초).

RANDOM_SEED = 42


# =============================================================================
# Graph metric helpers
# =============================================================================

def threshold_positive(z: np.ndarray) -> np.ndarray:
    """Fisher z matrix → 양수만 유지, 음수는 0."""
    w = z.copy()
    w[w < 0] = 0.0
    np.fill_diagonal(w, 0.0)
    return w


def normalize_weights(w: np.ndarray) -> np.ndarray:
    """가장 강한 weight가 1이 되도록 정규화 (BCT 표준)."""
    mx = w.max()
    return w / mx if mx > 0 else w


def global_efficiency_weighted(w: np.ndarray) -> float:
    """Weighted global efficiency. distance = 1 / weight."""
    if HAS_BCT:
        # bct.efficiency_wei는 distance matrix를 내부적으로 변환
        return bct.efficiency_wei(w)
    # networkx fallback
    n = w.shape[0]
    dist = np.where(w > 0, 1.0 / w, np.inf)
    np.fill_diagonal(dist, 0)
    G = nx.from_numpy_array(dist)
    # 약간 비효율적이지만 정확
    eff = 0.0
    paths = dict(nx.all_pairs_dijkstra_path_length(G))
    for i in range(n):
        for j in range(n):
            if i != j and j in paths.get(i, {}) and paths[i][j] > 0:
                eff += 1.0 / paths[i][j]
    return eff / (n * (n - 1))


def char_path_length_weighted(w: np.ndarray) -> float:
    """Characteristic path length (weighted)."""
    if HAS_BCT:
        D = bct.distance_wei(1.0 / np.where(w > 0, w, np.inf))[0]
        # diag, inf 제외 평균
        D_off = D[~np.eye(D.shape[0], dtype=bool)]
        D_off = D_off[np.isfinite(D_off)]
        return float(D_off.mean()) if D_off.size else np.nan
    # fallback
    dist = np.where(w > 0, 1.0 / w, np.inf)
    np.fill_diagonal(dist, 0)
    G = nx.from_numpy_array(dist)
    lengths = []
    for i, paths in nx.all_pairs_dijkstra_path_length(G):
        for j, d in paths.items():
            if i != j and np.isfinite(d):
                lengths.append(d)
    return float(np.mean(lengths)) if lengths else np.nan


def clustering_weighted(w: np.ndarray) -> float:
    """Mean weighted clustering coefficient (Onnela)."""
    if HAS_BCT:
        c = bct.clustering_coef_wu(w)
        return float(np.mean(c))
    G = nx.from_numpy_array(w)
    c = nx.clustering(G, weight="weight")
    return float(np.mean(list(c.values())))


def modularity_louvain(w: np.ndarray, seed: int = RANDOM_SEED) -> float:
    """Modularity Q via Louvain."""
    if HAS_BCT:
        _, q = bct.modularity_louvain_und(w, seed=seed)
        return float(q)
    import networkx.algorithms.community as nx_comm
    G = nx.from_numpy_array(w)
    communities = nx_comm.louvain_communities(G, weight="weight", seed=seed)
    return float(nx_comm.modularity(G, communities, weight="weight"))


def small_worldness(w: np.ndarray, n_null: int = N_NULL,
                    seed: int = RANDOM_SEED) -> float:
    """
    σ = (C / C_rand) / (L / L_rand).
    Null = degree-preserving random rewiring (BCT의 randmio_und).
    """
    C_obs = clustering_weighted(w)
    L_obs = char_path_length_weighted(w)
    if not np.isfinite(L_obs) or L_obs == 0:
        return np.nan

    rng = np.random.default_rng(seed)
    C_nulls, L_nulls = [], []
    for k in range(n_null):
        if HAS_BCT:
            w_rand, _ = bct.randmio_und(w, itr=5, seed=rng.integers(1, 1e6))
        else:
            # 간단한 weight shuffle (degree 보존 못함, fallback)
            mask = np.triu(np.ones_like(w, dtype=bool), k=1)
            vals = w[mask]
            rng.shuffle(vals)
            w_rand = np.zeros_like(w)
            w_rand[mask] = vals
            w_rand = w_rand + w_rand.T
        C_nulls.append(clustering_weighted(w_rand))
        L_nulls.append(char_path_length_weighted(w_rand))
    C_rand = np.nanmean(C_nulls)
    L_rand = np.nanmean(L_nulls)
    if not (np.isfinite(C_rand) and np.isfinite(L_rand)) or C_rand == 0 or L_rand == 0:
        return np.nan
    return (C_obs / C_rand) / (L_obs / L_rand)


# =============================================================================
# Network-level FC
# =============================================================================

def load_yeo_labels() -> pd.DataFrame | None:
    """ROI → network 매핑 로드. 첫 컬럼이 ROI index, 다른 컬럼에 network 이름."""
    if not YEO_LABEL_FILE.exists():
        print(f"  [info] Yeo label file 없음: {YEO_LABEL_FILE}")
        print(f"          network-level FC는 건너뜀.")
        return None
    df = pd.read_csv(YEO_LABEL_FILE)
    # network 이름이 들어있는 컬럼 자동 탐지
    net_col = None
    for c in df.columns:
        if "yeo" in c.lower() or "network" in c.lower():
            net_col = c
            break
    if net_col is None:
        print(f"  [warning] Yeo file에서 network 컬럼을 못 찾음: {df.columns.tolist()}")
        return None
    df = df.rename(columns={net_col: "network"})
    return df


def network_mean_fc(z: np.ndarray, labels: pd.DataFrame) -> dict:
    """
    각 네트워크 within FC 및 주요 between FC 평균 (Fisher z).
    """
    result = {}
    if labels is None or "network" not in labels.columns:
        return result

    networks = labels["network"].dropna().unique().tolist()
    # within
    for net in TARGET_NETWORKS:
        idx = labels.index[labels["network"] == net].to_numpy()
        if len(idx) < 2:
            continue
        sub = z[np.ix_(idx, idx)]
        triu = sub[np.triu_indices_from(sub, k=1)]
        result[f"within_{net}"] = float(np.mean(triu))

    # between (memory-related coupling)
    pairs = [
        ("Default", "FrontoParietal"),   # DMN-FPN
        ("Default", "Limbic"),           # DMN-MTL
        ("Default", "DorsalAttention"),  # DMN-DAN (memory retrieval)
        ("FrontoParietal", "Limbic"),    # FPN-MTL
    ]
    for a, b in pairs:
        idx_a = labels.index[labels["network"] == a].to_numpy()
        idx_b = labels.index[labels["network"] == b].to_numpy()
        if len(idx_a) == 0 or len(idx_b) == 0:
            continue
        sub = z[np.ix_(idx_a, idx_b)]
        result[f"between_{a}_{b}"] = float(np.mean(sub))

    return result


# =============================================================================
# Main
# =============================================================================

def main():
    print("=" * 70)
    print("Step 3: Graph-theoretical Measures")
    print("=" * 70)
    print(f"BCT 라이브러리: {'사용 가능' if HAS_BCT else '없음 (networkx fallback)'}")

    fc_path = OUTPUT_DIR / "fc_matrices.npz"
    if not fc_path.exists():
        raise FileNotFoundError(f"먼저 step 2를 실행하세요: {fc_path}")
    archive = np.load(fc_path)
    subjects = list(archive.files)
    print(f"FC matrices: {len(subjects)}개 로드")

    labels = load_yeo_labels()
    if labels is not None:
        print(f"Yeo label: {len(labels)} ROIs, {labels['network'].nunique()} networks")

    rows = []
    for i, sid in enumerate(subjects):
        z = archive[sid]
        # FC matrix가 ROI label 개수와 안 맞으면 network-level은 skip
        labels_for_subj = labels if (labels is not None and len(labels) == z.shape[0]) else None

        # 양수 weight만, max-normalize
        w = normalize_weights(threshold_positive(z))

        row = {"src_subject_id": sid}
        try:
            row["global_efficiency"] = global_efficiency_weighted(w)
            row["char_path_length"] = char_path_length_weighted(w)
            row["clustering_coef"] = clustering_weighted(w)
            row["modularity"] = modularity_louvain(w)
            if COMPUTE_SMALL_WORLDNESS:
                row["small_worldness"] = small_worldness(w)
            else:
                row["small_worldness"] = np.nan
        except Exception as e:
            print(f"  [warning] {sid} graph metric 실패: {e}")
            for m in ["global_efficiency", "char_path_length", "clustering_coef",
                      "modularity", "small_worldness"]:
                row.setdefault(m, np.nan)

        # Network-level FC
        try:
            row.update(network_mean_fc(z, labels_for_subj))
        except Exception as e:
            print(f"  [warning] {sid} network FC 실패: {e}")

        rows.append(row)

        if (i + 1) % 25 == 0:
            print(f"  진행: {i + 1}/{len(subjects)}")

    df = pd.DataFrame(rows)
    out = OUTPUT_DIR / "graph_metrics.csv"
    df.to_csv(out, index=False)
    print(f"\n저장: {out}  ({len(df)} subjects, {df.shape[1]} cols)")
    print("\n--- Graph metric 요약 ---")
    print(df.describe().T[["mean", "std", "min", "max"]].round(3))
    print("\nStep 3 완료.")


if __name__ == "__main__":
    main()
