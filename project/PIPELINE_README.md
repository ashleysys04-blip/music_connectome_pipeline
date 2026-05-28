# Pipeline 사용 가이드

새 proposal에 맞춰 만든 분석 코드. 7개 스크립트가 순차 실행되도록 짜여있음.

## 디렉토리 구조 (코드가 가정하는 구조)

```
project/
├── data/
│   ├── raw/                  ← NDA 텍스트 파일들 여기에
│   │   ├── ndar_subject01.txt
│   │   ├── saiq01.txt
│   │   ├── psm01.txt         ← Picture Sequence Memory (NEW)
│   │   ├── lswmt01.txt
│   │   ├── flanker01.txt
│   │   ├── dccs01.txt
│   │   ├── pcps01.txt
│   │   ├── wisc_v01.txt
│   │   ├── edinburgh_hand01.txt
│   │   └── motion.csv        ← MeanFD 별도 파일 (선택)
│   │
│   ├── time_series/          ← rs-fMRI ROI time series
│   │   ├── HCD0001234.csv    (shape: T × N, 헤더 있으면 자동 감지)
│   │   ├── HCD0001235.csv
│   │   └── ...
│   │
│   └── atlas/
│       └── subregion_func_network_Yeo_updated_wt_subcortical.csv
│           ← ROI별 Yeo network 매핑 (Brainnetome atlas 등)
│
├── scripts/
│   ├── 01_prepare_data.py
│   ├── 02_construct_fc.py
│   ├── 03_graph_metrics.py
│   ├── 04_glm_analyses.py
│   ├── 05_fdr_correction.py
│   ├── 06_mediation.py
│   ├── 07_make_figures.py
│   └── run_all.py
│
├── outputs/                  ← 모든 중간/최종 산출물
└── figures/                  ← 발표용 그림
```

## 실행


```bash
cd music_connectome
pip install -r requirements.txt
pip install bctpy  # optional but recommended
# 데이터를 data/raw/ 에 배치
cd scripts
python run_all.py  # 전체 11단계
```



```bash
pip install -r requirements.txt
python scripts/run_all.py
```

개별 실행도 가능. Step 1만 먼저 돌려서 분석 sample을 확인한 다음 진행하는 걸 추천.

## 데이터 구조 체크리스트

코드가 작동하려면 확인해야 할 것들:

1. **NDA 파일 컬럼명**
   - `saiq01.txt`에 `ccf_sai_p_music_nyr`, `ccf_sai_p_music_nm`, `ccf_sai_p_music_perwk`, `ccf_sai_p_music_min` 존재 여부
   - `psm01.txt`에 `nih_tlbx_agecsc_dom` (age-corrected standard score) 존재 여부
   - 없으면 step 01 실행시 warning 메시지에서 후보 컬럼을 보여줌. 코드의 `COG_COLUMNS` 딕셔너리 수정.

2. **ROI time series 포맷**
   - 한 subject당 하나의 파일, shape `(T timepoints, N ROIs)`
   - 파일명에서 subject ID 추출: 예) `HCD0001234.csv` → `HCD0001234`
   - 헤더 행이 있어도 자동 감지함

3. **Atlas label 파일**
   - 행 순서가 FC matrix의 ROI 순서와 일치해야 함
   - "network" 또는 "yeo" 컬럼이 있어야 함 (자동 탐지)
   - 컬럼명이 다르면 코드의 `load_yeo_labels()` 수정

## 모델 요약

| 모델 | 식 | Sample |
|---|---|---|
| **M1: Brain→Behavior** | EpisodicMemory ~ BrainFeature + age + sex + MeanFD + IQ | 전체 |
| **M2: Music→Behavior** | EpisodicMemory ~ MusicOnsetAge + log(duration) + covars | 훈련자만 |
| **M3: Music→Brain** | BrainFeature ~ MusicOnsetAge + log(duration) + covars | 훈련자만 |
| **M4: Mediation** | X(onset) → M(brain) → Y(memory), bootstrap CI | 훈련자만 |

모든 연속변수는 z-scoring → β는 표준화 계수.

## FDR Family

| Family | 검정 |
|---|---|
| Primary | onset→memory, primary brain→memory, onset→primary brain |
| Secondary | onset→다른 인지 outcome |
| Exploratory | network-level FC |

각 family 내에서 BH-FDR q < 0.05.

## 출력

- `outputs/analysis_sample.csv` — 최종 분석 sample
- `outputs/descriptive_statistics.csv` — 변수 요약
- `outputs/fc_matrices.npz` — 모든 FC matrix
- `outputs/graph_metrics.csv` — subject별 graph 측정치
- `outputs/glm_brain_behavior.csv`
- `outputs/glm_music_behavior.csv`
- `outputs/glm_music_brain.csv`
- `outputs/fdr_corrected_results.csv`
- `outputs/mediation_results.csv`
- `figures/fig1~6_*.png`
