"""
config.py - central configuration for HCP-D structural-connectivity pipeline.
Project: Early Musical Training, Episodic Memory, and White-Matter Network Organization
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

# Behavioral / demographic NDA files (HCP-D)
NDA_DIR = RAW_DIR / "behavioral" / "hcp-d"
NDA_FILES = {
    "subject" : NDA_DIR / "ndar_subject01.txt",
    "music"   : NDA_DIR / "saiq01.txt",
    "psm"     : NDA_DIR / "psm01.txt",
    "flanker" : NDA_DIR / "flanker01.txt",
    "dccs"    : NDA_DIR / "dccs01.txt",
    "lswmt"   : NDA_DIR / "lswmt01.txt",
    "pcps"    : NDA_DIR / "pcps01.txt",
    "wisc"    : NDA_DIR / "wisc_v01.txt",
}

# Atlas
ATLAS_FILE = RAW_DIR / "Brainnetome_atlas" / "subregion_func_network_Yeo_updated_wt_subcortical.csv"

# Structural connectome (DSI Studio QSDR output, one .mat per subject)
# Each file is e.g. HCD0001305_qsdr_connectivity.mat with key "connectivity" (246x246)
SC_DIR     = RAW_DIR / "structural_connectome" / "hcp-d"
SC_PATTERN = "*_qsdr_connectivity.mat"
SC_KEY     = "connectivity"

# NDA column names
COL_SUBJECT_ID = "src_subject_id"
COL_AGE        = "interview_age"   # months
COL_SEX        = "sex"

# Music variables in saiq01.txt (verified against actual HCP-D file)
MUSIC_YEARS_COL  = "ccf_sai_p_music_nyr"      # years of training
MUSIC_MONTHS_COL = "ccf_sai_p_music_nmonth"   # active months per year
MUSIC_DPW_COL    = "ccf_sai_p_music_perwk"    # days per week
MUSIC_MIN_COL    = "ccf_sai_p_music_tspent"   # minutes per session

# NIH Toolbox / WISC outcomes (verified)
PSM_SCORE_COL = "nih_picseq_ageadjusted"
FLANKER_COL   = "nih_flanker_ageadjusted"
DCCS_COL      = "nih_dccs_ageadjusted"
LSWMT_COL     = "age_corrected_standard_score"   # lswmt01 col name
PCPS_COL      = "nih_patterncomp_ageadjusted"
WISC_MR_COL   = "scaled_matrix"                  # WISC-V Matrix Reasoning scaled score

# QC
ATLAS_N_ROI  = 246
MIN_NONZERO_EDGES = 100  # SC matrix must have at least this many positive off-diag edges

# Yeo 7-network code mapping (numeric in atlas)
#   1=Visual  2=Somatomotor  3=DorsAttn  4=VentAttn/Salience
#   5=Limbic  6=Frontoparietal  7=Default  8-11=Subcortical
YEO_CODE_TO_NAME = {
    1: "Visual", 2: "SomMot", 3: "DorsAttn", 4: "SalVentAttn",
    5: "Limbic", 6: "Frontoparietal", 7: "Default",
    8: "SubCx_8", 9: "SubCx_9", 10: "SubCx_10", 11: "SubCx_11",
}

# Networks of interest for music-memory hypotheses.
# DMN/FPN/Limbic correspond directly to Yeo codes 7/6/5.
NETWORKS_OF_INTEREST = {
    "DMN": "Default",
    "FPN": "Frontoparietal",
    "MTL": "Limbic",
}

ONSET_GROUPS = {"early": (0, 7), "middle": (7, 12), "late": (12, 99)}

# Stats
RANDOM_SEED       = 42
N_BOOTSTRAP       = 5000
FDR_ALPHA         = 0.05
GRAPH_THRESHOLDS  = [0.10, 0.15, 0.20]
GRAPH_PRIMARY_THR = 0.15

# Whether to log-transform SC weights before graph metrics.
# DSI Studio streamline counts are heavy-tailed; log1p stabilizes them.
SC_LOG_TRANSFORM = True

# 각 피험자 SC를 max weight로 normalize(BCT weight_conversion 'normalize')한 뒤
# network within/between 평균을 계산 → head size / total streamline 스케일 제거.
NETWORK_FEATURE_NORMALIZE = True

PRIMARY_GRAPH_METRICS = [
    "global_efficiency", "char_path_length", "mean_clustering",
    "modularity", "small_worldness", 
]
PRIMARY_NETWORK_FEATURES = [
    "DMN_within", "MTL_within", "FPN_within",
    "DMN_FPN_between", "DMN_MTL_between", "FPN_MTL_between",
]
