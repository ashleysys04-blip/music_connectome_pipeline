"""
pipeline.py — full 8-step analysis pipeline (structural connectivity version)
=============================================================================
For HCP-D data:
  - Structural connectivity matrices (DSI Studio QSDR, 246x246, .mat files)
  - Behavioral NDA .txt files (saiq, psm, flanker, dccs, lswmt, pcps, wisc, subject)
  - Brainnetome atlas with Yeo 7-network assignment

Steps:
  1. Data preparation (NDA -> analysis_sample.csv)
  2. Load structural connectivity matrices
  3. Compute graph metrics + within/between-network SC features
  4. Brain -> PSM GLM
  5. Music -> PSM GLM
  6. Music -> Brain GLM
  7. Mediation:  music_onset -> brain -> PSM
  8. Figures + summary
"""

import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path
from scipy.io import loadmat
from tqdm import tqdm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor as _vif

import config as C

warnings.filterwarnings("ignore", category=RuntimeWarning)


# =============================================================================
# Helpers
# =============================================================================
def read_nda(path):
    """Read NDA tab-delimited file, skipping the dictionary row (row 1)."""
    if not Path(path).exists():
        raise FileNotFoundError(f"NDA file not found: {path}")
    return pd.read_csv(path, sep="\t", skiprows=[1], low_memory=False)


def derive_music_variables(saiq, demo):
    df = saiq.merge(demo[[C.COL_SUBJECT_ID, C.COL_AGE]],
                    on=C.COL_SUBJECT_ID, how="left", suffixes=("", "_demo"))
    age_col_use = C.COL_AGE if C.COL_AGE in df.columns else f"{C.COL_AGE}_demo"
    for c in [age_col_use, C.MUSIC_YEARS_COL, C.MUSIC_MONTHS_COL,
              C.MUSIC_DPW_COL, C.MUSIC_MIN_COL]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    age_yr = df[age_col_use] / 12.0
    years  = df[C.MUSIC_YEARS_COL]
    months = df[C.MUSIC_MONTHS_COL]
    dpw    = df[C.MUSIC_DPW_COL]
    mins   = df[C.MUSIC_MIN_COL]

    onset_age = age_yr - years
    cum_hours = years * months * 4.33 * dpw * mins / 60.0

    out = pd.DataFrame({
        C.COL_SUBJECT_ID: df[C.COL_SUBJECT_ID],
        "age_years": age_yr,
        "music_years": years,
        "music_onset_age": onset_age,
        "cumulative_hours": cum_hours,
        "log_cumulative_hours": np.log1p(cum_hours.clip(lower=0)),
        "music_training_status": (years.fillna(0) > 0).astype(int),
    })

    def grp(a):
        if pd.isna(a): return np.nan
        if a < 7:  return "early"
        if a < 12: return "middle"
        return "late"
    out["early_onset_group"] = out["music_onset_age"].apply(grp)
    return out.drop_duplicates(subset=[C.COL_SUBJECT_ID])


def zero_diag(A):
    A = A.copy(); np.fill_diagonal(A, 0.0); return A

def symmetrize(A):
    return 0.5 * (A + A.T)


def threshold_proportional(W, p):
    """Keep top-p proportion of strongest |edges|, zero the rest."""
    W = symmetrize(zero_diag(W))
    n = W.shape[0]
    ti = np.triu_indices(n, k=1)
    vals = np.abs(W[ti])
    if vals.size == 0: return W
    k = int(np.round(p * vals.size))
    if k <= 0: return np.zeros_like(W)
    thr = np.sort(vals)[-k]
    mask = np.abs(W) >= thr
    np.fill_diagonal(mask, False)
    return np.where(mask, W, 0.0)


def load_atlas():
    """
    Return DataFrame with columns ['roi_idx' (0-indexed), 'network' (str name)]
    from the Brainnetome+Yeo CSV. Uses YEO_CODE_TO_NAME mapping.
    """
    df = pd.read_csv(C.ATLAS_FILE)
    if "Label" not in df.columns or "Yeo_7network_SubC" not in df.columns:
        raise ValueError(f"Atlas missing expected columns. Found: {df.columns.tolist()}")
    out = pd.DataFrame({
        "roi_idx": df["Label"].astype(int) - 1,  # 0-indexed
        "network_code": df["Yeo_7network_SubC"].astype(int),
    })
    out["network"] = out["network_code"].map(C.YEO_CODE_TO_NAME).fillna("Unknown")
    return out.sort_values("roi_idx").reset_index(drop=True)


def standardize(df, cols):
    out = df.copy()
    for c in cols:
        if c in out.columns and pd.api.types.is_numeric_dtype(out[c]):
            mu, sd = out[c].mean(skipna=True), out[c].std(skipna=True, ddof=1)
            if sd and sd > 0:
                out[c] = (out[c] - mu) / sd
    return out


def fit_ols(df, y_col, predictor_cols, covariates):
    cols = [y_col] + predictor_cols + covariates
    sub = df[cols].dropna()
    if len(sub) < 20: return None
    X = sm.add_constant(sub[predictor_cols + covariates], has_constant="add")
    try:
        m = sm.OLS(sub[y_col], X).fit()
    except Exception:
        return None
    out = {"n": int(len(sub)), "r2": float(m.rsquared), "r2_adj": float(m.rsquared_adj)}
    for p in predictor_cols:
        out[f"beta_{p}"] = float(m.params.get(p, np.nan))
        out[f"se_{p}"]   = float(m.bse.get(p, np.nan))
        out[f"t_{p}"]    = float(m.tvalues.get(p, np.nan))
        out[f"p_{p}"]    = float(m.pvalues.get(p, np.nan))
    return out


def apply_fdr(df, p_col, alpha=None, q_col="q_fdr", reject_col="sig_fdr"):
    if alpha is None: alpha = C.FDR_ALPHA
    p = df[p_col].to_numpy(dtype=float)
    mask = ~np.isnan(p)
    q = np.full_like(p, np.nan, dtype=float)
    rej = np.zeros_like(p, dtype=bool)
    if mask.sum() > 0:
        r, qv, _, _ = multipletests(p[mask], alpha=alpha, method="fdr_bh")
        q[mask] = qv; rej[mask] = r
    df = df.copy(); df[q_col] = q; df[reject_col] = rej
    return df


# =============================================================================
# STEP 1 — Data preparation
# =============================================================================
def step1():
    print("\n=== Step 1: Data preparation ===")
    demo = read_nda(C.NDA_FILES["subject"])
    keep = [c for c in [C.COL_SUBJECT_ID, C.COL_AGE, C.COL_SEX] if c in demo.columns]
    demo = demo[keep].drop_duplicates(subset=[C.COL_SUBJECT_ID])
    demo[C.COL_AGE] = pd.to_numeric(demo[C.COL_AGE], errors="coerce")
    print(f"  demographics: {len(demo)}")

    saiq = read_nda(C.NDA_FILES["music"])
    music = derive_music_variables(saiq, demo)
    print(f"  music vars:   {len(music)} (trained={(music['music_training_status']==1).sum()})")

    spec = [("psm",     C.PSM_SCORE_COL, "psm_score"),
            ("flanker", C.FLANKER_COL,   "flanker"),
            ("dccs",    C.DCCS_COL,      "dccs"),
            ("lswmt",   C.LSWMT_COL,     "lswmt"),
            ("pcps",    C.PCPS_COL,      "pcps"),
            ("wisc",    C.WISC_MR_COL,   "wisc_mr")]
    cog = None
    for key, col, newname in spec:
        path = C.NDA_FILES[key]
        if not path.exists():
            print(f"  [warn] {path.name} missing — skipping {newname}"); continue
        df = read_nda(path)
        if col not in df.columns:
            print(f"  [warn] '{col}' not in {path.name} — skipping {newname}"); continue
        sub = df[[C.COL_SUBJECT_ID, col]].copy()
        sub[col] = pd.to_numeric(sub[col], errors="coerce")
        sub = sub.rename(columns={col: newname}).drop_duplicates(subset=[C.COL_SUBJECT_ID])
        cog = sub if cog is None else cog.merge(sub, on=C.COL_SUBJECT_ID, how="outer")
    if cog is None:
        raise RuntimeError("No cognitive data loaded.")
    print(f"  cognitive:    {len(cog)}")

    df = (demo.merge(music.drop(columns=["age_years"], errors="ignore"),
                     on=C.COL_SUBJECT_ID, how="left")
              .merge(cog, on=C.COL_SUBJECT_ID, how="left"))
    df["age_years"] = df[C.COL_AGE] / 12.0
    if C.COL_SEX in df.columns:
        df["sex_code"] = df[C.COL_SEX].map(
            {"M": 0, "F": 1, "m": 0, "f": 1}).astype(float)

    # Require primary outcome
    n0 = len(df)
    df = df.dropna(subset=["psm_score"])
    print(f"  after psm non-missing: {len(df)} (-{n0-len(df)})")

    df.to_csv(C.OUT_DIR / "analysis_sample.csv", index=False)
    print(f"  saved -> analysis_sample.csv  (n={len(df)})")

    desc_cols = [c for c in ["age_years", "sex_code", "music_onset_age",
                             "music_years", "cumulative_hours", "log_cumulative_hours",
                             "psm_score", "flanker", "dccs", "lswmt", "pcps", "wisc_mr"]
                 if c in df.columns]
    desc = df[desc_cols].describe().T
    desc["n_nonmissing"] = df[desc_cols].notna().sum().values
    desc.to_csv(C.OUT_DIR / "descriptive_statistics.csv")

    if "early_onset_group" in df.columns:
        print("  Onset group counts:")
        print(df["early_onset_group"].value_counts(dropna=False).to_string())
    return df


# =============================================================================
# STEP 2 — Load structural connectivity matrices
# =============================================================================
def _load_sc(sub_id):
    """Find and load a subject's QSDR SC matrix. Returns 246x246 or None."""
    pats = [
        f"{sub_id}_qsdr_connectivity.mat",
        f"{sub_id}*qsdr*connectivity*.mat",
        f"{sub_id}*.mat",
    ]
    for pat in pats:
        cands = list(C.SC_DIR.glob(pat))
        if cands:
            try:
                m = loadmat(cands[0])
                if C.SC_KEY in m:
                    A = np.asarray(m[C.SC_KEY], dtype=np.float64)
                else:
                    keys = [k for k in m.keys() if not k.startswith("__")]
                    if not keys: return None
                    A = np.asarray(m[keys[0]], dtype=np.float64)
                if A.shape != (C.ATLAS_N_ROI, C.ATLAS_N_ROI):
                    return None
                return A
            except Exception:
                return None
    return None


def step2():
    print("\n=== Step 2: Load structural connectivity ===")
    sc_proc = C.PROC_DIR / "sc"
    sc_proc.mkdir(parents=True, exist_ok=True)
    sample = pd.read_csv(C.OUT_DIR / "analysis_sample.csv")
    if not C.SC_DIR.exists():
        raise FileNotFoundError(f"SC dir not found: {C.SC_DIR}")

    qc_rows = []
    found_subjects = []
    for sub in tqdm(sample[C.COL_SUBJECT_ID].astype(str), desc="SC"):
        A = _load_sc(sub)
        if A is None:
            qc_rows.append(dict(subject=sub, used=False, note="no_file_or_bad_shape"))
            continue
        A = symmetrize(zero_diag(A))
        n_pos = int((A[np.triu_indices(C.ATLAS_N_ROI, 1)] > 0).sum())
        if n_pos < C.MIN_NONZERO_EDGES:
            qc_rows.append(dict(subject=sub, used=False, n_pos_edges=n_pos,
                                note=f"too_sparse"))
            continue
        # Optional log1p stabilization (kept on disk for reuse)
        if C.SC_LOG_TRANSFORM:
            A_stable = np.log1p(np.clip(A, 0, None))
        else:
            A_stable = A.astype(np.float32)
        np.save(sc_proc / f"{sub}_sc.npy", A_stable.astype(np.float32))
        qc_rows.append(dict(subject=sub, used=True, n_pos_edges=n_pos,
                            mean_w=float(A[A > 0].mean()),
                            max_w=float(A.max()), note=""))
        found_subjects.append(sub)

    qc = pd.DataFrame(qc_rows)
    qc.to_csv(C.OUT_DIR / "sc_qc.csv", index=False)
    print(f"  used: {qc['used'].sum()} / {len(qc)}")
    print(f"  saved processed SC -> {sc_proc}")
    print(f"  saved QC          -> sc_qc.csv")


# =============================================================================
# STEP 3 — Graph metrics + within/between network SC features
# =============================================================================
try:
    import bct
    HAVE_BCT = True
except ImportError:
    HAVE_BCT = False
    import networkx as nx
    from networkx.algorithms.community import greedy_modularity_communities


def _to_distance(W):
    D = np.zeros_like(W); nz = W > 0; D[nz] = 1.0 / W[nz]
    return D


def _global_eff(W):
    if HAVE_BCT: return float(bct.efficiency_wei(W))
    return nx.global_efficiency(nx.from_numpy_array(_to_distance(W)))


def _char_path(W):
    if HAVE_BCT:
        D = bct.distance_wei(_to_distance(W))[0]
        D[D == np.inf] = np.nan
        return float(np.nanmean(D[np.triu_indices(D.shape[0], k=1)]))
    G = nx.from_numpy_array(_to_distance(W))
    try: return nx.average_shortest_path_length(G, weight="weight")
    except nx.NetworkXError: return np.nan


def _clustering(W):
    if HAVE_BCT: return float(np.mean(bct.clustering_coef_wu(W)))
    return nx.average_clustering(nx.from_numpy_array(W), weight="weight")


def _modularity(W):
    if HAVE_BCT:
        _, Q = bct.modularity_louvain_und(W, seed=C.RANDOM_SEED); return float(Q)
    G = nx.from_numpy_array(W)
    comms = list(greedy_modularity_communities(G, weight="weight"))
    return nx.algorithms.community.modularity(G, comms, weight="weight")


def _small_world(W, n_rand=5):
    Cr, Lr = _clustering(W), _char_path(W)
    Cs, Ls = [], []
    rng = np.random.default_rng(C.RANDOM_SEED)
    for _ in range(n_rand):
        if HAVE_BCT:
            Wr, _ = bct.randmio_und(W, itr=5)
        else:
            n = W.shape[0]; ti, tj = np.triu_indices(n, k=1)
            w = W[ti, tj]; perm = rng.permutation(len(w))
            Wr = np.zeros_like(W); Wr[ti, tj] = w[perm]; Wr = Wr + Wr.T
        Cs.append(_clustering(Wr)); Ls.append(_char_path(Wr))
    cR, lR = float(np.nanmean(Cs)), float(np.nanmean(Ls))
    if cR == 0 or lR == 0: return np.nan
    return (Cr / cR) / (Lr / lR)



def _all_global(W):
    return dict(global_efficiency=_global_eff(W),
                char_path_length=_char_path(W),
                mean_clustering=_clustering(W),
                modularity=_modularity(W),
                small_worldness=_small_world(W))


def _network_features(W, atlas):
    """Mean SC weight within/between target networks (DMN/MTL/FPN).

    W는 피험자의 full (log1p) SC matrix. 이 mean-weight feature가 피험자 간
    비교 가능하도록, 평균을 내기 전에 행렬을 [0,1]로 normalize해서
    피험자 수준의 곱셈적 스케일(head size / total streamline count)을 제거한다
    (= BCT weight_conversion 'normalize'). raw feature를 쓰고 싶을 때를 위해
    total_strength도 함께 반환한다 (GLM covariate로 쓸 수 있음).
    """
    iu_full = np.triu_indices(W.shape[0], k=1)
    total_strength = float(np.nansum(W[iu_full]))

    if C.NETWORK_FEATURE_NORMALIZE:
        mx = np.nanmax(W)
        Wn = W / mx if mx and mx > 0 else W
    else:
        Wn = W

    masks = {}
    for short, full_name in C.NETWORKS_OF_INTEREST.items():
        idx = atlas.index[atlas["network"] == full_name].to_numpy()
        masks[short] = idx

    feats = {"total_strength": total_strength}
    keys = list(masks.keys())
    for i, k in enumerate(keys):
        idx_i = masks[k]
        if len(idx_i) < 2:
            feats[f"{k}_within"] = np.nan
        else:
            sub = Wn[np.ix_(idx_i, idx_i)]
            iu = np.triu_indices(len(idx_i), k=1)
            feats[f"{k}_within"] = float(np.nanmean(sub[iu]))
        for j in range(i + 1, len(keys)):
            kj = keys[j]; idx_j = masks[kj]
            if len(idx_i) == 0 or len(idx_j) == 0:
                feats[f"{k}_{kj}_between"] = np.nan
            else:
                feats[f"{k}_{kj}_between"] = float(np.nanmean(Wn[np.ix_(idx_i, idx_j)]))
    return feats


def step3():
    print(f"\n=== Step 3: Graph metrics  (backend: {'bctpy' if HAVE_BCT else 'networkx'}) ===")
    sample = pd.read_csv(C.OUT_DIR / "analysis_sample.csv")
    atlas = load_atlas()
    sc_proc = C.PROC_DIR / "sc"
    print(f"  network sizes: " + ", ".join(
        f"{k}={ (atlas['network']==v).sum() }" for k,v in C.NETWORKS_OF_INTEREST.items()))

    rows_primary, rows_all, rows_net = [], [], []
    for sub in tqdm(sample[C.COL_SUBJECT_ID].astype(str), desc="metrics"):
        p = sc_proc / f"{sub}_sc.npy"
        if not p.exists(): continue
        W = np.load(p).astype(np.float64)

        nf = _network_features(W, atlas); nf[C.COL_SUBJECT_ID] = sub
        rows_net.append(nf)

        for thr in C.GRAPH_THRESHOLDS:
            Wt = threshold_proportional(W, thr)
            Wp = np.where(Wt > 0, Wt, 0.0)
            # NEW: weighted clustering/small-worldness가 [0,1] weight를 가정하므로 normalize
            if HAVE_BCT:
                Wp = bct.weight_conversion(Wp, "normalize")
            else:
                mx = Wp.max()
                if mx > 0:
                    Wp = Wp / mx
            g = _all_global(Wp)
            rows_all.append({C.COL_SUBJECT_ID: sub, "threshold": thr, **g})
            if thr == C.GRAPH_PRIMARY_THR:
                rows_primary.append({C.COL_SUBJECT_ID: sub, **g})

    pd.DataFrame(rows_primary).to_csv(C.OUT_DIR / "graph_metrics.csv", index=False)
    pd.DataFrame(rows_all).to_csv(C.OUT_DIR / "graph_metrics_all_thr.csv", index=False)
    pd.DataFrame(rows_net).to_csv(C.OUT_DIR / "network_features.csv", index=False)
    print(f"  saved -> graph_metrics.csv  ({len(rows_primary)} subjects)")
    print(f"  saved -> network_features.csv")


# =============================================================================
# STEP 4 — Brain -> PSM
# =============================================================================
def step4():
    print("\n=== Step 4: Brain -> PSM ===")
    sample = pd.read_csv(C.OUT_DIR / "analysis_sample.csv")
    graph  = pd.read_csv(C.OUT_DIR / "graph_metrics.csv")
    netfc  = pd.read_csv(C.OUT_DIR / "network_features.csv")
    df = sample.merge(graph, on=C.COL_SUBJECT_ID, how="inner") \
               .merge(netfc, on=C.COL_SUBJECT_ID, how="inner")
    print(f"  n = {len(df)}")
    family = C.PRIMARY_GRAPH_METRICS + C.PRIMARY_NETWORK_FEATURES
    df = standardize(df, ["age_years", "wisc_mr", "psm_score"] +
                     [c for c in family if c in df.columns])
    covs = [c for c in ["age_years", "sex_code", "wisc_mr"]
            if c in df.columns and df[c].notna().any()]
    rows = []
    for feat in family:
        if feat not in df.columns: continue
        r = fit_ols(df, "psm_score", [feat], covs)
        if r is None: continue
        rows.append(dict(feature=feat, n=r["n"], beta=r[f"beta_{feat}"],
                         se=r[f"se_{feat}"], t=r[f"t_{feat}"],
                         p=r[f"p_{feat}"], r2=r["r2"]))
    res = pd.DataFrame(rows)
    if len(res):
        res = apply_fdr(res, p_col="p").sort_values("p")
    res.to_csv(C.OUT_DIR / "glm_brain_behavior.csv", index=False)
    print(res.to_string(index=False))
    return res


# =============================================================================
# STEP 5 — Music -> PSM
# =============================================================================
def _run_music_models(df, y_col):
    covs = [c for c in ["age_years", "sex_code", "wisc_mr"]
            if c in df.columns and df[c].notna().any()]
    out = []
    r = fit_ols(df, y_col, ["music_onset_age"], covs)
    if r: out.append(dict(model="M1_onset_only", outcome=y_col,
                          predictor="music_onset_age",
                          beta=r["beta_music_onset_age"], se=r["se_music_onset_age"],
                          t=r["t_music_onset_age"], p=r["p_music_onset_age"],
                          n=r["n"], r2=r["r2"]))
    r = fit_ols(df, y_col, ["log_cumulative_hours"], covs)
    if r: out.append(dict(model="M2_hours_only", outcome=y_col,
                          predictor="log_cumulative_hours",
                          beta=r["beta_log_cumulative_hours"], se=r["se_log_cumulative_hours"],
                          t=r["t_log_cumulative_hours"], p=r["p_log_cumulative_hours"],
                          n=r["n"], r2=r["r2"]))
    r = fit_ols(df, y_col, ["music_onset_age", "log_cumulative_hours"], covs)
    if r:
        for pp in ["music_onset_age", "log_cumulative_hours"]:
            out.append(dict(model="M3_both", outcome=y_col, predictor=pp,
                            beta=r[f"beta_{pp}"], se=r[f"se_{pp}"],
                            t=r[f"t_{pp}"], p=r[f"p_{pp}"],
                            n=r["n"], r2=r["r2"]))
    tmp = df.copy(); tmp["onset_x_hours"] = tmp["music_onset_age"] * tmp["log_cumulative_hours"]
    r = fit_ols(tmp, y_col, ["music_onset_age", "log_cumulative_hours", "onset_x_hours"], covs)
    if r:
        for pp in ["music_onset_age", "log_cumulative_hours", "onset_x_hours"]:
            out.append(dict(model="M4_interaction", outcome=y_col, predictor=pp,
                            beta=r[f"beta_{pp}"], se=r[f"se_{pp}"],
                            t=r[f"t_{pp}"], p=r[f"p_{pp}"],
                            n=r["n"], r2=r["r2"]))
    return out


def step5():
    print("\n=== Step 5: Music -> behavior ===")
    df_all = pd.read_csv(C.OUT_DIR / "analysis_sample.csv")
    df = df_all[df_all["music_training_status"] == 1].copy()
    print(f"  trained-only n = {len(df)}")
    df = standardize(df, ["age_years", "wisc_mr",
                          "music_onset_age", "log_cumulative_hours",
                          "psm_score", "flanker", "dccs", "lswmt", "pcps"])
    # --- M3 predictor multicollinearity 진단 (onset–hours 상관 + VIF) ---
    m3_terms = ["music_onset_age", "log_cumulative_hours"]
    covs = [c for c in ["age_years", "sex_code", "wisc_mr"]
            if c in df.columns and df[c].notna().any()]
    Xv = df[m3_terms + covs].dropna()
    r_oh = Xv["music_onset_age"].corr(Xv["log_cumulative_hours"])
    Xc = sm.add_constant(Xv, has_constant="add")
    vif_rows = []
    for i, col in enumerate(Xc.columns):
        if col == "const":
            continue
        vif_rows.append({"term": col,
                         "vif": float(_vif(Xc.values, i)),
                         "is_m3_predictor": col in m3_terms})
    vif_df = pd.DataFrame(vif_rows)
    vif_df["onset_hours_r"] = r_oh
    vif_df["n"] = len(Xv)
    vif_df.to_csv(C.OUT_DIR / "vif_music_predictors.csv", index=False)
    print(f"  onset–hours r = {r_oh:.3f}  (n={len(Xv)})")
    print(vif_df[["term", "vif"]].to_string(index=False))
    # --- VIF 끝 ---
    
    primary = pd.DataFrame(_run_music_models(df, "psm_score"))
    if len(primary):
        m3 = primary[primary["model"] == "M3_both"].copy()
        m3 = apply_fdr(m3, p_col="p")
        primary = pd.concat([primary[primary["model"] != "M3_both"], m3], ignore_index=True)
    primary.to_csv(C.OUT_DIR / "glm_music_behavior.csv", index=False)
    print(primary.to_string(index=False))

    sec_rows = []
    for outcome in ["flanker", "dccs", "lswmt", "pcps"]:
        if outcome in df.columns:
            sec_rows.extend(_run_music_models(df, outcome))
    sec = pd.DataFrame(sec_rows)
    if len(sec):
        m3s = sec[sec["model"] == "M3_both"].copy()
        m3s = apply_fdr(m3s, p_col="p")
        sec = pd.concat([sec[sec["model"] != "M3_both"], m3s], ignore_index=True)
    sec.to_csv(C.OUT_DIR / "glm_music_behavior_secondary.csv", index=False)


# =============================================================================
# STEP 6 — Music -> Brain
# =============================================================================
def step6():
    print("\n=== Step 6: Music -> Brain ===")
    sample = pd.read_csv(C.OUT_DIR / "analysis_sample.csv")
    graph  = pd.read_csv(C.OUT_DIR / "graph_metrics.csv")
    netfc  = pd.read_csv(C.OUT_DIR / "network_features.csv")
    df = sample.merge(graph, on=C.COL_SUBJECT_ID, how="inner") \
               .merge(netfc, on=C.COL_SUBJECT_ID, how="inner")
    df = df[df["music_training_status"] == 1].copy()
    print(f"  trained-only with brain n = {len(df)}")
    family = C.PRIMARY_GRAPH_METRICS + C.PRIMARY_NETWORK_FEATURES
    df = standardize(df, ["age_years", "wisc_mr",
                          "music_onset_age", "log_cumulative_hours"] +
                     [c for c in family if c in df.columns])
    covs = [c for c in ["age_years", "sex_code", "wisc_mr"]
            if c in df.columns and df[c].notna().any()]
    rows = []
    for feat in family:
        if feat not in df.columns: continue
        r = fit_ols(df, feat, ["music_onset_age", "log_cumulative_hours"], covs)
        if r is None: continue
        for pp in ["music_onset_age", "log_cumulative_hours"]:
            rows.append(dict(brain_feature=feat, predictor=pp, n=r["n"],
                             beta=r[f"beta_{pp}"], se=r[f"se_{pp}"],
                             t=r[f"t_{pp}"], p=r[f"p_{pp}"], r2=r["r2"]))
    res = pd.DataFrame(rows)
    if len(res):
        out = []
        for pp, grp in res.groupby("predictor"):
            out.append(apply_fdr(grp, p_col="p"))
        res = pd.concat(out, ignore_index=True).sort_values(["predictor", "p"])
    res.to_csv(C.OUT_DIR / "glm_music_brain.csv", index=False)
    print(res.to_string(index=False))
    return res


# =============================================================================
# STEP 7 — Mediation
# =============================================================================
def _bootstrap_indirect(df, x, m, y, covs, n_boot=None):
    if n_boot is None: n_boot = C.N_BOOTSTRAP
    cols = [x, m, y] + covs
    sub = df[cols].dropna().reset_index(drop=True)
    if len(sub) < 30: return None

    def _fit(d):
        Xa = sm.add_constant(d[[x] + covs], has_constant="add")
        a = sm.OLS(d[m], Xa).fit().params.get(x, np.nan)
        Xb = sm.add_constant(d[[x, m] + covs], has_constant="add")
        b_fit = sm.OLS(d[y], Xb).fit()
        b = b_fit.params.get(m, np.nan); cp = b_fit.params.get(x, np.nan)
        Xc = sm.add_constant(d[[x] + covs], has_constant="add")
        c = sm.OLS(d[y], Xc).fit().params.get(x, np.nan)
        return a, b, c, cp

    a, b, c, cp = _fit(sub)
    rng = np.random.default_rng(C.RANDOM_SEED)
    ab_boot = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, len(sub), len(sub))
        try:
            ai, bi, _, _ = _fit(sub.iloc[idx])
            ab_boot[i] = ai * bi
        except Exception:
            ab_boot[i] = np.nan
    ab_boot = ab_boot[~np.isnan(ab_boot)]
    if len(ab_boot) < 100: return None
    lo, hi = np.percentile(ab_boot, [2.5, 97.5])
    p_boot = 2 * min((ab_boot >= 0).mean(), (ab_boot <= 0).mean())
    return dict(a=a, b=b, c=c, c_prime=cp, ab=a * b,
                ci_low=lo, ci_high=hi, p_boot=p_boot, n=len(sub))


def step7():
    print("\n=== Step 7: Mediation (music_onset -> brain -> PSM) ===")
    sample = pd.read_csv(C.OUT_DIR / "analysis_sample.csv")
    graph  = pd.read_csv(C.OUT_DIR / "graph_metrics.csv")
    netfc  = pd.read_csv(C.OUT_DIR / "network_features.csv")
    df = sample.merge(graph, on=C.COL_SUBJECT_ID, how="inner") \
               .merge(netfc, on=C.COL_SUBJECT_ID, how="inner")
    df = df[df["music_training_status"] == 1].copy()
    family = C.PRIMARY_GRAPH_METRICS + C.PRIMARY_NETWORK_FEATURES
    df = standardize(df, ["age_years", "wisc_mr",
                          "music_onset_age", "log_cumulative_hours", "psm_score"] +
                     [c for c in family if c in df.columns])
    covs = [c for c in ["age_years", "sex_code", "wisc_mr", "log_cumulative_hours"]
            if c in df.columns and df[c].notna().any()]
    rows = []
    for feat in family:
        if feat not in df.columns: continue
        r = _bootstrap_indirect(df, x="music_onset_age", m=feat, y="psm_score", covs=covs)
        if r is None: continue
        rows.append({"mediator": feat, **r,
                     "ci_excludes_zero": (r["ci_low"] > 0) or (r["ci_high"] < 0)})
    res = pd.DataFrame(rows).sort_values("p_boot") if rows else pd.DataFrame()
    res.to_csv(C.OUT_DIR / "mediation_results.csv", index=False)
    print(res.to_string(index=False) if len(res) else "  (no mediators converged)")
    return res


# =============================================================================
# STEP 8 — Figures + summary
# =============================================================================
def step8():
    print("\n=== Step 8: Figures + summary ===")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["figure.dpi"] = 120

    sample = pd.read_csv(C.OUT_DIR / "analysis_sample.csv")
    trained = sample[sample["music_training_status"] == 1]

    if len(trained):
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(trained["music_onset_age"].dropna(), bins=20, edgecolor="black")
        ax.set_xlabel("Music onset age (years)")
        ax.set_ylabel("N participants")
        ax.set_title(f"Music onset age (trained, n={len(trained)})")
        plt.tight_layout()
        plt.savefig(C.FIG_DIR / "fig1_onset_distribution.png", dpi=150)
        plt.close()

    if "early_onset_group" in sample.columns and sample["psm_score"].notna().any():
        groups = ["early", "middle", "late"]
        data = [sample.loc[sample["early_onset_group"] == g, "psm_score"].dropna()
                for g in groups]
        ns = [len(d) for d in data]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.boxplot(data, labels=[f"{g}\n(n={n})" for g, n in zip(groups, ns)])
        ax.set_ylabel("Picture Sequence Memory (age-corrected)")
        ax.set_title("PSM by music onset group")
        plt.tight_layout()
        plt.savefig(C.FIG_DIR / "fig2_psm_by_group.png", dpi=150)
        plt.close()

    bb_path = C.OUT_DIR / "glm_brain_behavior.csv"
    if bb_path.exists():
        bb = pd.read_csv(bb_path)
        if len(bb):
            bb = bb.sort_values("p").head(10)
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.barh(bb["feature"][::-1], bb["beta"][::-1])
            ax.axvline(0, color="k", linewidth=0.8)
            ax.set_xlabel("β (standardized)")
            ax.set_title("Top brain features predicting PSM")
            plt.tight_layout()
            plt.savefig(C.FIG_DIR / "fig3_brain_behavior.png", dpi=150)
            plt.close()

    med_path = C.OUT_DIR / "mediation_results.csv"
    if med_path.exists():
        med = pd.read_csv(med_path)
        if len(med):
            med = med.sort_values("ab")
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.errorbar(med["ab"], range(len(med)),
                        xerr=[med["ab"] - med["ci_low"], med["ci_high"] - med["ab"]],
                        fmt="o", capsize=3)
            ax.set_yticks(range(len(med))); ax.set_yticklabels(med["mediator"])
            ax.axvline(0, color="k", linewidth=0.8)
            ax.set_xlabel("Indirect effect a*b  (95% bootstrap CI)")
            ax.set_title("Onset -> Brain -> PSM mediation")
            plt.tight_layout()
            plt.savefig(C.FIG_DIR / "fig4_mediation.png", dpi=150)
            plt.close()

    summary = ["# Analysis Summary\n"]
    summary.append(f"\n## Sample\n- N after QC: {len(sample)}\n")
    if "music_training_status" in sample.columns:
        n_tr = int((sample["music_training_status"] == 1).sum())
        summary.append(f"- N trained: {n_tr}\n")
    for name, path in [
        ("Brain -> PSM",           C.OUT_DIR / "glm_brain_behavior.csv"),
        ("Music -> PSM (primary)", C.OUT_DIR / "glm_music_behavior.csv"),
        ("Music -> Brain",         C.OUT_DIR / "glm_music_brain.csv"),
        ("Mediation",              C.OUT_DIR / "mediation_results.csv"),
    ]:
        if path.exists():
            d = pd.read_csv(path)
            summary.append(f"\n## {name}  ({path.name})\n")
            summary.append("```\n" + d.to_string(index=False) + "\n```\n")
    (C.OUT_DIR / "summary.md").write_text("".join(summary))
    print(f"  figures -> {C.FIG_DIR}")
    print(f"  summary -> {C.OUT_DIR / 'summary.md'}")
