"""
pipeline.py
===========
Full 8-step analysis pipeline as importable functions.
Each step writes its outputs to outputs/ and reads inputs from the previous step.

Usage:
    from pipeline import step1, step2, step3, step4, step5, step6, step7, step8

Or run all steps via run_all.py.
"""

import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path
from tqdm import tqdm
from statsmodels.stats.multitest import multipletests

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
                    on=C.COL_SUBJECT_ID, how="left")
    for c in [C.COL_AGE, C.MUSIC_YEARS_COL, C.MUSIC_MONTHS_COL,
              C.MUSIC_DPW_COL, C.MUSIC_MIN_COL]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    age_yr = df[C.COL_AGE] / 12.0
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
        "log_cumulative_hours": np.log1p(cum_hours),
        "music_training_status": (years.fillna(0) > 0).astype(int),
    })

    def grp(a):
        if pd.isna(a): return np.nan
        if a < 7:  return "early"
        if a < 12: return "middle"
        return "late"
    out["early_onset_group"] = out["music_onset_age"].apply(grp)
    return out.drop_duplicates(subset=[C.COL_SUBJECT_ID])


def fisher_z(r):
    r = np.clip(r, -0.9999, 0.9999)
    return np.arctanh(r)


def zero_diag(A):
    A = A.copy()
    np.fill_diagonal(A, 0.0)
    return A


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
    df = pd.read_csv(C.ATLAS_FILE)
    roi_cands = ["roi_idx", "ROI", "roi_id", "Label", "index", "Index", "ID"]
    net_cands = ["network", "Network", "Yeo_Network", "Yeo7", "yeo7", "yeo_network"]
    roi_col = next((c for c in roi_cands if c in df.columns), None)
    net_col = next((c for c in net_cands if c in df.columns), None)
    if roi_col is None:
        df = df.reset_index().rename(columns={"index": "roi_idx"})
        roi_col = "roi_idx"
    if net_col is None:
        raise ValueError(f"No network column found. Atlas columns: {df.columns.tolist()}")
    out = df[[roi_col, net_col]].rename(columns={roi_col: "roi_idx", net_col: "network"})
    if out["roi_idx"].min() == 1:
        out["roi_idx"] = out["roi_idx"] - 1
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
    print(f"  music vars:   {len(music)}")

    # Cognitive
    spec = [("psm", C.PSM_SCORE_COL, "psm_score"),
            ("flanker", C.FLANKER_COL, "flanker"),
            ("dccs", C.DCCS_COL, "dccs"),
            ("lswmt", C.LSWMT_COL, "lswmt"),
            ("pcps", C.PCPS_COL, "pcps"),
            ("wisc", C.WISC_MR_COL, "wisc_mr")]
    cog = None
    for key, col, newname in spec:
        path = C.NDA_FILES[key]
        if not path.exists():
            print(f"  [warn] {path.name} missing — skipping {newname}")
            continue
        df = read_nda(path)
        if col not in df.columns:
            print(f"  [warn] {col} not in {path.name} — skipping {newname}")
            continue
        sub = df[[C.COL_SUBJECT_ID, col]].copy()
        sub[col] = pd.to_numeric(sub[col], errors="coerce")
        sub = sub.rename(columns={col: newname}).drop_duplicates(subset=[C.COL_SUBJECT_ID])
        cog = sub if cog is None else cog.merge(sub, on=C.COL_SUBJECT_ID, how="outer")
    if cog is None:
        raise RuntimeError("No cognitive data loaded.")
    print(f"  cognitive:    {len(cog)}")

    # Motion
    if C.MOTION_FILE.exists():
        mot = pd.read_csv(C.MOTION_FILE)
        if "subject_id" in mot.columns and C.COL_SUBJECT_ID not in mot.columns:
            mot = mot.rename(columns={"subject_id": C.COL_SUBJECT_ID})
        mot = mot[[C.COL_SUBJECT_ID, "mean_fd"]].drop_duplicates(subset=[C.COL_SUBJECT_ID])
    else:
        print(f"  [warn] motion file {C.MOTION_FILE.name} missing — mean_fd will be NaN")
        mot = pd.DataFrame(columns=[C.COL_SUBJECT_ID, "mean_fd"])

    df = (demo.merge(music.drop(columns=["age_years"], errors="ignore"),
                     on=C.COL_SUBJECT_ID, how="left")
              .merge(cog, on=C.COL_SUBJECT_ID, how="left")
              .merge(mot, on=C.COL_SUBJECT_ID, how="left"))
    df["age_years"] = df[C.COL_AGE] / 12.0
    if C.COL_SEX in df.columns:
        df["sex_code"] = df[C.COL_SEX].map(
            {"M": 0, "F": 1, "m": 0, "f": 1}).astype(float)

    # QC
    n0 = len(df)
    df = df.dropna(subset=["psm_score"])
    print(f"  after psm non-missing: {len(df)} (-{n0-len(df)})")
    if df["mean_fd"].notna().any():
        n0 = len(df)
        df = df[(df["mean_fd"].isna()) | (df["mean_fd"] <= C.MEAN_FD_MAX)]
        print(f"  after mean_fd <= {C.MEAN_FD_MAX}: {len(df)} (-{n0-len(df)})")

    df.to_csv(C.OUT_DIR / "analysis_sample.csv", index=False)
    print(f"  saved -> analysis_sample.csv  (n={len(df)})")

    desc_cols = [c for c in ["age_years", "sex_code", "mean_fd", "music_onset_age",
                             "music_years", "cumulative_hours", "log_cumulative_hours",
                             "psm_score", "flanker", "dccs", "lswmt", "pcps", "wisc_mr"]
                 if c in df.columns]
    desc = df[desc_cols].describe().T
    desc["n_nonmissing"] = df[desc_cols].notna().sum().values
    desc.to_csv(C.OUT_DIR / "descriptive_statistics.csv")
    return df


# =============================================================================
# STEP 2 — FC matrices
# =============================================================================
def _find_ts(sub_id):
    cands = list(C.TIMESERIES_DIR.glob(f"{sub_id}*timeseries*"))
    cands += list(C.TIMESERIES_DIR.glob(f"{sub_id}*_ts.*"))
    cands += list(C.TIMESERIES_DIR.glob(f"{sub_id}.csv"))
    cands += list(C.TIMESERIES_DIR.glob(f"{sub_id}.txt"))
    return cands[0] if cands else None


def _load_ts(path):
    sep = "\t" if path.suffix in (".tsv", ".txt") else ","
    df = pd.read_csv(path, sep=sep, header=None, engine="python")
    if df.iloc[0].apply(lambda v: isinstance(v, str)).any():
        df = pd.read_csv(path, sep=sep, header=0, engine="python")
    arr = df.to_numpy(dtype=np.float32)
    if arr.shape[0] == C.ATLAS_N_ROI and arr.shape[1] != C.ATLAS_N_ROI:
        arr = arr.T
    return arr


def _compute_fc(ts):
    ts = ts - ts.mean(axis=0, keepdims=True)
    sd = ts.std(axis=0, ddof=1, keepdims=True); sd[sd == 0] = 1.0
    ts = ts / sd
    n = ts.shape[0]
    R = symmetrize(zero_diag((ts.T @ ts) / (n - 1)))
    Z = fisher_z(R)
    np.fill_diagonal(Z, 0.0)
    return Z.astype(np.float32)


def step2():
    print("\n=== Step 2: FC matrices ===")
    fc_dir = C.PROC_DIR / "fc"
    fc_dir.mkdir(parents=True, exist_ok=True)
    sample = pd.read_csv(C.OUT_DIR / "analysis_sample.csv")
    if not C.TIMESERIES_DIR.exists():
        raise FileNotFoundError(f"Time series dir not found: {C.TIMESERIES_DIR}")
    qc_rows = []
    for sub in tqdm(sample[C.COL_SUBJECT_ID].astype(str), desc="FC"):
        p = _find_ts(sub)
        if p is None:
            qc_rows.append(dict(subject=sub, used=False, note="no_file")); continue
        try:
            ts = _load_ts(p)
        except Exception as e:
            qc_rows.append(dict(subject=sub, used=False, note=f"load_err:{e}")); continue
        if ts.shape[1] != C.ATLAS_N_ROI:
            qc_rows.append(dict(subject=sub, used=False, note=f"wrong_N={ts.shape[1]}")); continue
        if ts.shape[0] < C.MIN_TR_COUNT:
            qc_rows.append(dict(subject=sub, used=False, note=f"short_T={ts.shape[0]}")); continue
        Z = _compute_fc(ts)
        r_off = np.tanh(Z[np.triu_indices(C.ATLAS_N_ROI, k=1)])
        np.save(fc_dir / f"{sub}_fc.npy", Z)
        qc_rows.append(dict(subject=sub, n_timepoints=ts.shape[0],
                            mean_abs_r=float(np.nanmean(np.abs(r_off))),
                            used=True, note=""))
    qc = pd.DataFrame(qc_rows)
    qc.to_csv(C.OUT_DIR / "fc_qc.csv", index=False)
    print(f"  used: {qc['used'].sum()} / {len(qc)}")
    return qc


# =============================================================================
# STEP 3 — Graph metrics
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


def _small_world(W, n_rand=10):
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


def _network_features(Z, atlas):
    masks = {}
    for short, long_name in C.NETWORKS_OF_INTEREST.items():
        idx = atlas.index[
            atlas["network"].astype(str).str.contains(long_name, case=False, na=False)
        ].to_numpy()
        masks[short] = idx
    feats = {}
    keys = list(masks.keys())
    for i, k in enumerate(keys):
        idx_i = masks[k]
        if len(idx_i) < 2:
            feats[f"{k}_within"] = np.nan
        else:
            sub = Z[np.ix_(idx_i, idx_i)]
            iu = np.triu_indices(len(idx_i), k=1)
            feats[f"{k}_within"] = float(np.nanmean(sub[iu]))
        for j in range(i + 1, len(keys)):
            kj = keys[j]; idx_j = masks[kj]
            if len(idx_i) == 0 or len(idx_j) == 0:
                feats[f"{k}_{kj}_between"] = np.nan
            else:
                feats[f"{k}_{kj}_between"] = float(np.nanmean(Z[np.ix_(idx_i, idx_j)]))
    return feats


def step3():
    print(f"\n=== Step 3: Graph metrics  (backend: {'bctpy' if HAVE_BCT else 'networkx'}) ===")
    sample = pd.read_csv(C.OUT_DIR / "analysis_sample.csv")
    atlas = load_atlas()
    fc_dir = C.PROC_DIR / "fc"
    rows_primary, rows_all, rows_net = [], [], []
    for sub in tqdm(sample[C.COL_SUBJECT_ID].astype(str), desc="metrics"):
        p = fc_dir / f"{sub}_fc.npy"
        if not p.exists(): continue
        Z = np.load(p)
        nf = _network_features(Z, atlas); nf[C.COL_SUBJECT_ID] = sub
        rows_net.append(nf)
        for thr in C.GRAPH_THRESHOLDS:
            W = threshold_proportional(Z, thr)
            Wp = np.where(W > 0, W, 0.0)
            g = _all_global(Wp)
            rows_all.append({C.COL_SUBJECT_ID: sub, "threshold": thr, **g})
            if thr == C.GRAPH_PRIMARY_THR:
                rows_primary.append({C.COL_SUBJECT_ID: sub, **g})
    pd.DataFrame(rows_primary).to_csv(C.OUT_DIR / "graph_metrics.csv", index=False)
    pd.DataFrame(rows_all).to_csv(C.OUT_DIR / "graph_metrics_all_thr.csv", index=False)
    pd.DataFrame(rows_net).to_csv(C.OUT_DIR / "network_features.csv", index=False)
    print("  saved -> graph_metrics.csv, graph_metrics_all_thr.csv, network_features.csv")


# =============================================================================
# STEP 4 — Brain → Episodic memory
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
    df = standardize(df, ["age_years", "mean_fd", "wisc_mr", "psm_score"] +
                     [c for c in family if c in df.columns])
    covs = [c for c in ["age_years", "sex_code", "mean_fd", "wisc_mr"]
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
# STEP 5 — Music → Episodic memory
# =============================================================================
def _run_music_models(df, y_col):
    covs = [c for c in ["age_years", "sex_code", "mean_fd", "wisc_mr"]
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
    df = standardize(df, ["age_years", "mean_fd", "wisc_mr",
                          "music_onset_age", "log_cumulative_hours",
                          "psm_score", "flanker", "dccs", "lswmt", "pcps"])
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
# STEP 6 — Music → Brain
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
    df = standardize(df, ["age_years", "mean_fd", "wisc_mr",
                          "music_onset_age", "log_cumulative_hours"] +
                     [c for c in family if c in df.columns])
    covs = [c for c in ["age_years", "sex_code", "mean_fd", "wisc_mr"]
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
        # FDR per predictor across brain features
        out = []
        for pp, grp in res.groupby("predictor"):
            out.append(apply_fdr(grp, p_col="p"))
        res = pd.concat(out, ignore_index=True).sort_values(["predictor", "p"])
    res.to_csv(C.OUT_DIR / "glm_music_brain.csv", index=False)
    print(res.to_string(index=False))
    return res


# =============================================================================
# STEP 7 — Mediation: Music onset -> Brain -> PSM
# =============================================================================
def _bootstrap_indirect(df, x, m, y, covs, n_boot=None):
    """
    Simple nonparametric bootstrap of the indirect effect a*b in:
        m ~ x + covs       (a path)
        y ~ x + m + covs   (b path; c' = direct effect of x)
    Returns dict with a, b, c (total), c_prime (direct), ab, ci_low, ci_high, p.
    """
    if n_boot is None: n_boot = C.N_BOOTSTRAP
    cols = [x, m, y] + covs
    sub = df[cols].dropna().reset_index(drop=True)
    if len(sub) < 30:
        return None

    def _fit(d):
        Xa = sm.add_constant(d[[x] + covs], has_constant="add")
        a = sm.OLS(d[m], Xa).fit().params.get(x, np.nan)
        Xb = sm.add_constant(d[[x, m] + covs], has_constant="add")
        b_fit = sm.OLS(d[y], Xb).fit()
        b = b_fit.params.get(m, np.nan)
        cp = b_fit.params.get(x, np.nan)
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
    if len(ab_boot) < 100:
        return None
    lo, hi = np.percentile(ab_boot, [2.5, 97.5])
    # two-sided "p" via proportion of resamples crossing 0
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
    df = standardize(df, ["age_years", "mean_fd", "wisc_mr",
                          "music_onset_age", "log_cumulative_hours", "psm_score"] +
                     [c for c in family if c in df.columns])
    covs = [c for c in ["age_years", "sex_code", "mean_fd", "wisc_mr",
                        "log_cumulative_hours"]
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

    # Fig 1: distribution of music_onset_age in trained sample
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

    # Fig 2: PSM by onset group
    if "early_onset_group" in sample.columns and sample["psm_score"].notna().any():
        groups = ["early", "middle", "late"]
        data = [sample.loc[sample["early_onset_group"] == g, "psm_score"].dropna()
                for g in groups]
        ns = [len(d) for d in data]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.boxplot(data, labels=[f"{g}\n(n={n})" for g, n in zip(groups, ns)])
        ax.set_ylabel("Picture Sequence Memory (age-corr.)")
        ax.set_title("PSM by music onset group")
        plt.tight_layout()
        plt.savefig(C.FIG_DIR / "fig2_psm_by_group.png", dpi=150)
        plt.close()

    # Fig 3: top brain-behavior associations
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

    # Fig 4: mediation indirect effects
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

    # Summary report
    summary = ["# Analysis Summary\n"]
    summary.append(f"## Sample\n- N (after QC): {len(sample)}\n")
    if "music_training_status" in sample.columns:
        n_tr = int((sample["music_training_status"] == 1).sum())
        summary.append(f"- N trained: {n_tr}\n")
    for name, path in [
        ("Brain -> PSM", C.OUT_DIR / "glm_brain_behavior.csv"),
        ("Music -> PSM (primary)", C.OUT_DIR / "glm_music_behavior.csv"),
        ("Music -> Brain", C.OUT_DIR / "glm_music_brain.csv"),
        ("Mediation",  C.OUT_DIR / "mediation_results.csv"),
    ]:
        if path.exists():
            d = pd.read_csv(path)
            summary.append(f"\n## {name}  ({path.name})\n")
            summary.append("```\n" + d.to_string(index=False) + "\n```\n")
    (C.OUT_DIR / "summary.md").write_text("".join(summary))
    print(f"  figures -> {C.FIG_DIR}")
    print(f"  summary -> {C.OUT_DIR / 'summary.md'}")
