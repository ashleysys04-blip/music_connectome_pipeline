"""
config.py — central configuration. Edit paths/column names here if your data layout differs.
Project: Early Musical Training, Episodic Memory, and Functional Brain Network Organization
"""
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR  = DATA_DIR / "raw"
PROC_DIR = DATA_DIR / "processed"
OUT_DIR  = PROJECT_ROOT / "outputs"
FIG_DIR  = PROJECT_ROOT / "figures"
for d in [PROC_DIR, OUT_DIR, FIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# NDA-format files. Row 0 = header, Row 1 = NDA dictionary (skip), Row 2+ = data
NDA_FILES = {
    "subject" : RAW_DIR / "ndar_subject01.txt",
    "music"   : RAW_DIR / "saiq01.txt",
    "psm"     : RAW_DIR / "psm01.txt",
    "flanker" : RAW_DIR / "flanker01.txt",
    "dccs"    : RAW_DIR / "dccs01.txt",
    "lswmt"   : RAW_DIR / "lswmt01.txt",
    "pcps"    : RAW_DIR / "pcps01.txt",
    "wisc"    : RAW_DIR / "wisc_v01.txt",
}

ATLAS_FILE = RAW_DIR / "subregion_func_network_Yeo_updated_wt_subcortical.csv"

# ROI time series. Expected: data/raw/timeseries/<SUB>_timeseries.csv (T × N=246)
TIMESERIES_DIR = RAW_DIR / "timeseries"
TIMESERIES_PATTERN = "*_timeseries.csv"

# Motion: subject_id, mean_fd
MOTION_FILE = RAW_DIR / "motion_meanfd.csv"

# NDA column names
COL_SUBJECT_ID = "src_subject_id"
COL_AGE        = "interview_age"   # months
COL_SEX        = "sex"

# Music variables (SAIQ)
MUSIC_YEARS_COL  = "ccf_sai_p_music_nyr"
MUSIC_MONTHS_COL = "ccf_sai_p_music_yrm"
MUSIC_DPW_COL    = "ccf_sai_p_music_dpw"
MUSIC_MIN_COL    = "ccf_sai_p_music_min"

# NIH Toolbox / WISC outcome columns (age-corrected std scores)
PSM_SCORE_COL = "tlbx_picseq_agecorrected"
FLANKER_COL   = "nih_flanker_agecorrected"
DCCS_COL      = "nih_dccs_agecorrected"
LSWMT_COL     = "nih_lswmt_agecorrected"
PCPS_COL      = "nih_pcps_agecorrected"
WISC_MR_COL   = "pea_wiscv_mr_tscore"

# QC
MEAN_FD_MAX  = 0.5
MIN_TR_COUNT = 100
ATLAS_N_ROI  = 246

# Networks of interest (Yeo 7-network names; substring match)
NETWORKS_OF_INTEREST = {
    "DMN": "Default",
    "FPN": "Frontoparietal",
    "MTL": "Limbic",
}

ONSET_GROUPS = {"early": (0, 7), "middle": (7, 12), "late": (12, 99)}

# Stats
RANDOM_SEED      = 42
N_PERMUTATIONS   = 5000
N_BOOTSTRAP      = 5000
FDR_ALPHA        = 0.05
GRAPH_THRESHOLDS = [0.10, 0.15, 0.20]
GRAPH_PRIMARY_THR = 0.15

PRIMARY_GRAPH_METRICS = [
    "global_efficiency", "char_path_length", "mean_clustering",
    "modularity", "small_worldness",
]
PRIMARY_NETWORK_FEATURES = [
    "DMN_within", "MTL_within", "FPN_within",
    "DMN_FPN_between", "DMN_MTL_between", "FPN_MTL_between",
]
