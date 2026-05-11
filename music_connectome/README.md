# Music Connectome Pipeline

Implements the 8-step analysis pipeline from the proposal:
**Early Musical Training, Episodic Memory, and Functional Brain Network Organization**.

## Directory layout

```
music_connectome/
├── scripts/
│   ├── config.py        # paths, column names, thresholds — edit me first
│   ├── pipeline.py      # all 8 steps as functions
│   └── run_all.py       # entry point
├── data/
│   ├── raw/             # put NDA .txt files, atlas, timeseries/, motion here
│   └── processed/fc/    # FC matrices (auto-generated)
├── outputs/             # CSV results + summary.md
└── figures/             # PNG figures
```

## Required data (under `data/raw/`)

| File | Description |
|---|---|
| `ndar_subject01.txt` | demographics (age, sex) |
| `saiq01.txt`         | music training (SAIQ) |
| `psm01.txt`          | Picture Sequence Memory (primary outcome) |
| `flanker01.txt`, `dccs01.txt`, `lswmt01.txt`, `pcps01.txt` | secondary cognitive |
| `wisc_v01.txt`       | WISC-V Matrix Reasoning (IQ control) |
| `subregion_func_network_Yeo_updated_wt_subcortical.csv` | Brainnetome + Yeo network assignment |
| `timeseries/<SUB>_timeseries.csv` | per-subject ROI time series (T × 246) |
| `motion_meanfd.csv`  | columns: `src_subject_id, mean_fd` |

If your column names differ from the assumptions in `config.py`, edit them there.

## Install

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# optional, recommended:
pip install bctpy
```

## Run

```bash
cd scripts
python run_all.py            # full pipeline
python run_all.py 1 2 3      # only steps 1-3
python run_all.py 4 5 6 7 8  # stats + figures only (assumes 1-3 already ran)
```

## Steps

| Step | Inputs | Outputs |
|---|---|---|
| 1 — Data prep | NDA files | `analysis_sample.csv`, `descriptive_statistics.csv` |
| 2 — FC matrices | time series | `data/processed/fc/<SUB>_fc.npy`, `fc_qc.csv` |
| 3 — Graph metrics | FC matrices | `graph_metrics.csv`, `network_features.csv` |
| 4 — Brain → PSM GLM | sample + brain | `glm_brain_behavior.csv` |
| 5 — Music → PSM GLM | sample | `glm_music_behavior.csv`, `..._secondary.csv` |
| 6 — Music → Brain GLM | sample + brain | `glm_music_brain.csv` |
| 7 — Mediation (onset → brain → PSM) | all | `mediation_results.csv` |
| 8 — Figures + summary | all | `figures/*.png`, `outputs/summary.md` |

## Statistical defaults

- Outcome (primary): Picture Sequence Memory, age-corrected standard score
- Predictors: `music_onset_age`, `log_cumulative_hours` (trained subjects only)
- Covariates: age, sex, MeanFD, WISC-V Matrix Reasoning
- All continuous variables z-scored before regression
- FC density thresholds: 10%, 15% (primary), 20%
- Multiple comparisons: BH-FDR (α = 0.05) within each predictor family
- Mediation: nonparametric bootstrap (5000 resamples, 95% CI)
