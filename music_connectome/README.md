# Music Connectome Pipeline (HCP-D Structural Connectivity)

Analysis pipeline for the BCS499 final project:
**Early Musical Training, Episodic Memory, and White-Matter Network Organization**

Uses HCP-D **structural connectivity** matrices (DSI Studio QSDR output, 246×246
Brainnetome atlas) with NDA behavioral data.

## Directory layout

```
music_connectome/
├── scripts/
│   ├── config.py        # paths, column names, thresholds — edit me first
│   ├── pipeline.py      # all 8 steps as functions
│   └── run_all.py       # entry point
├── data/
│   ├── raw/
│   │   ├── behavioral/hcp-d/         # NDA .txt files
│   │   ├── structural_connectome/hcp-d/  # <SUB>_qsdr_connectivity.mat
│   │   └── Brainnetome_atlas/        # atlas CSV
│   └── processed/sc/                 # normalized SC matrices (.npy, auto-generated)
├── outputs/             # CSV results + summary.md
└── figures/             # PNG figures
```

## Required data layout

Put the unzipped HCP-D data folder contents under `data/raw/`:
- `data/raw/behavioral/hcp-d/saiq01.txt`, `psm01.txt`, `flanker01.txt`, ...
- `data/raw/structural_connectome/hcp-d/HCD*_qsdr_connectivity.mat` (one per subject)
- `data/raw/Brainnetome_atlas/subregion_func_network_Yeo_updated_wt_subcortical.csv`

All column names and paths are verified against the actual HCP-D files in the
project zip — including the music training variable names in `saiq01.txt`:
`ccf_sai_p_music_nyr / nmonth / perwk / tspent`.

## Install

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# optional but recommended (faster, more standard graph metrics):
pip install bctpy
```

## Run

```bash
cd scripts
python run_all.py            # all 8 steps
python run_all.py 1 2 3      # data prep + SC loading + graph metrics
python run_all.py 4 5 6 7 8  # stats + figures only
```

## Steps

| Step | Inputs | Outputs |
|---|---|---|
| 1 — Data prep | NDA files | `analysis_sample.csv`, `descriptive_statistics.csv` |
| 2 — Load SC | .mat files | `data/processed/sc/<SUB>_sc.npy`, `sc_qc.csv` |
| 3 — Graph metrics | SC matrices | `graph_metrics.csv`, `network_features.csv` |
| 4 — Brain → PSM | sample + brain | `glm_brain_behavior.csv` |
| 5 — Music → PSM | sample | `glm_music_behavior.csv`, `..._secondary.csv` |
| 6 — Music → Brain | sample + brain | `glm_music_brain.csv` |
| 7 — Mediation | all | `mediation_results.csv` |
| 8 — Figures + summary | all | `figures/*.png`, `outputs/summary.md` |

## Statistical defaults

- **Outcome (primary):** Picture Sequence Memory, age-adjusted score
- **Predictors (trained only):** `music_onset_age`, `log_cumulative_hours`
- **Covariates:** age, sex, WISC-V Matrix Reasoning (proxy for fluid IQ)
- **Brain features (per subject):**
  - Global graph metrics at 15% edge density (primary): efficiency,
    char path length, clustering, modularity, small-worldness
  - Within-/between-network SC for DMN (33 ROIs), FPN (25), MTL/Limbic (26)
- **Multiple comparisons:** BH-FDR (α = 0.05) within each predictor family
- **Mediation:** nonparametric bootstrap (5000 resamples, 95% CI)
- **SC stabilization:** log1p transform of streamline counts (set `SC_LOG_TRANSFORM=False`
  in config.py to disable)

## Expected sample sizes

From the HCP-D data in this project:
- 652 demographics → 500 with SAIQ → **473 with PSM** → **~448 with both PSM + SC**
- Of these, ~286 are music-trained (`music_years > 0`)
- Onset groups: early (<7y) ~44, middle (7-12y) ~119, late (>12y) ~40

## Notes on the original repo

The earlier version of this project used `flanker / dccs / lswmt / pcps` as
outcomes and structural connectivity. This pipeline keeps those as **secondary
outcomes** (Step 5) while focusing on PSM as the primary episodic memory measure,
per the course-ready proposal. The Step 5 secondary table will let you compare
against the original DCCS finding (β=-3.57, p=0.066) without losing it.
