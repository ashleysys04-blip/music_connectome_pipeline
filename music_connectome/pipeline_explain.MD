# 한국어 버전 readme

> 한국어로 재밌게 쓴 버전. (삭제 예정)

---

## 0. 큰 그림

음악을 일찍 시작한 것(**onset age**)이 좋은가, 아니면 그냥 누적으로 많이 연습한 것(**cumulative hours**)이 좋은가? 닭이 먼저냐 달걀이 먼저냐 같은 논쟁임
과연 학부모들이 애들한테 악기시키려는게 진짜 의미가 있는걸까 !!
카이스트 오케스트라 하면서 악기 붐 세대가 있다는걸 알게되었고, 약간 off the record지만 악기 잘하는 애들이 학점이 좋은거같다...는것이 카이오케의 정 설 (농담.)
연구는 자기가 좋아하는걸로 하라고 하길래 이걸로 한번 해봄. 난진짜클래식음악이정말좋아서미칠거같음.

이미 있는 입장은 아래 3가지가 있음
- **Sensitive-period view**: 시작 나이 자체가 중요하다 → onset이 핵심
- **Dose-response view**: 일찍 시작한 애가 어차피 더 많이 연습하니, 진짜 원인은 총 연습량이다 → hours가 핵심
- **Skeptical view**: 둘 다 진짜 효과가 아니라 집안 배경·동기 같은 선행 차이의 그림자다 → 위에 둘 다 의미없어!

**onset과 hours를 같은 회귀모형에 같이 넣고**(이게 뒤에 나올 모델 중 `M3`), 어느 쪽 부분 회귀계수 β가 더 크게/유의하게 살아남는지 보자.

분석 대상(outcome)은 episodic memory, 구체적으로 **Picture Sequence Memory (PSM)** 점수를 선정함. 그리고 뇌 쪽으로는 **white-matter structural connectome**의 조직(organization)이 음악과 관련 있는지 관찰할 예정임.

---

## 1. Step 1 — 데이터 준비 (`step1`)

NDA에서 받은 여러 `.txt` 파일을 하나의 분석용 표(`analysis_sample.csv`)로 합치는 단계.

### 어떤 파일에서 뭘 뽑았나

| 파일 | 뽑은 것 |
|---|---|
| `ndar_subject01.txt` | subject id, `interview_age`(개월), sex |
| `saiq01.txt` | 음악 훈련 변수 4개 (아래) |
| `psm01.txt` | **PSM** = `nih_picseq_ageadjusted` (primary outcome) |
| `flanker01 / dccs01 / lswmt01 / pcps01` | secondary 인지 점수들 |
| `wisc_v01.txt` | `scaled_matrix` = WISC-V Matrix Reasoning → fluid IQ의 proxy로 covariate에 씀 |

### 음악 변수를 어떻게 "계산"했나 (`derive_music_variables`)

- `saiq01.txt`에 있는 데이터 4개:
  - `ccf_sai_p_music_nyr` = 훈련 햇수 (years)
  - `ccf_sai_p_music_nmonth` = 1년 중 활동한 개월 수 (months/year)
  - `ccf_sai_p_music_perwk` = 주당 일수 (days/week)
  - `ccf_sai_p_music_tspent` = 1회당 분 (min/session)

- **onset age** = 현재 나이(세) − 훈련 햇수
  ```
  age_years = interview_age / 12
  music_onset_age = age_years − music_years
  ```

- **cumulative hours** = 모든 시간 단위를 곱해서 총 시간으로
  ```
  cumulative_hours = years × (months/year) × 4.33 × (days/week) × (min/session) ÷ 60
  ```
  `4.33`은 한 달 ≈ 4.33주 에서 나온 숫자임. 햇수 → 활동 개월 → 주 → 일 → 분 → 시간 순으로 환산.

- **log_cumulative_hours** = `log1p(cumulative_hours)`
  
  누적 시간은 한쪽으로 길게 늘어진(**heavy-tailed**) 분포라서, 몇몇 극단값이 회귀를 좌우함. `log1p`(= log(1+x))로 압축하면 분포가 안정되고 0도 안전하게 처리됨.

- **training status** = 훈련 햇수 > 0 이면 1 (음악 배웠는지 안배웠는지)

- **onset group** (3개의 그룹으로 나눠봄): `early` < 7세, 7 ≤ `middle` < 12세, `late` ≥ 12세

이게 7세인 이유가 또 좀 나름 흥미로운데, 조성진이랑 임윤찬이 딱 6-7세때 배움. 이게 전공하려면 진짜 늦은 나이인데 너무 신기했음... 나는 5살 때 배웠는데 진짜 재능의 차이를 느껴버림.

데이터 수 중간점검 : 전체 **N = 473**, 그중 음악 배운 사람은 **N = 201**.

---

## 2. Step 2 — structural connectivity 만들기

`_load_sc`:
- `<SUB>_qsdr_connectivity.mat`에서 key `"connectivity"`로 **246×246 행렬**을 읽음. 이 값은 두 영역을 잇는 **streamline count**(추적된 섬유 가닥 수)임.
- `zero_diag`: 대각선(자기 자신과의 연결) 0으로
- `symmetrize`: A와 A.T 평균 → 대칭 행렬 보장 (연결은 방향이 없으니까)

QC와 안정화:
- **QC**: 양수 off-diagonal edge가 `MIN_NONZERO_EDGES = 100`개 미만이면 너무 sparse하다고 보고 버림
- **log1p 변환** (`SC_LOG_TRANSFORM = True`): streamline count도 heavy-tailed라 `log1p(count)`로 압축해서 저장.

정리된 행렬은 `data/processed/sc/<SUB>_sc.npy`로 저장되고, 통과 여부는 `sc_qc.csv`에 기록.

---

## 3. Step 3 — 위에서 만든 행렬 숫자로 나타내기 (이게 03 method의 03 metrics 부분임)

두 종류 - global graph metrics, network features

### (A) Global graph metrics — 뇌 전체 네트워크의 topology (`_all_global`)

전처리:
- `threshold_proportional(W, p)`: 각 subject에서 **가장 강한 상위 p% edge만 남기고** 나머지는 0. `p`는 10%, 15%, 20% 세 가지로 돌리고(`GRAPH_THRESHOLDS`), 15%가 primary(`GRAPH_PRIMARY_THR`). 이유: 사람마다 총 연결량이 다른데, 같은 density(같은 edge 개수)로 맞춰야 "네트워크 모양"을 공정하게 비교 가능함.

- `weight_conversion(..., 'normalize')`로 weight를 [0,1]로 정규화

`_all_global`: 수업시간에 배웠던 다양한 measure 방법들 수식 이용해서 apply하기

| 변수 | 의미 복습 | 분류 |
|---|---|---|
| `global_efficiency` | 정보가 네트워크 전체로 **얼마나 빨리/쉽게** 퍼지나 | integration |
| `char_path_length` | 두 영역 사이 평균 최단 경로 길이 (길수록 integration ↓) | integration |
| `mean_clustering` | 내 이웃들끼리도 서로 연결돼 있나 (국소적 뭉침) | segregation |
| `modularity` | 네트워크가 **모듈(하위 그룹)로 깔끔히 나뉘나** | segregation |
| `small_worldness` | clustering은 높으면서 경로는 짧은 "small-world" 정도 | - |

저장: `graph_metrics.csv`(primary 15%), `graph_metrics_all_thr.csv`(세 threshold 전부).

- `small_worldness`는 null model랑 이따가 비교할거임

### (B) Network features — episodic memory와 관련된 애들에서만 강도를 보자 (`_network_features`)

Brainnetome 246 영역에 Yeo 7-network 라벨 붙어있음. 이거를 이용

- `NETWORKS_OF_INTEREST`:
  - **DMN** (Default mode network) — 기억 관련...
  - **FPN** (Frontoparietal) — 인지 능력.
  - **MTL** (Yeo의 Limbic) — hippocampus 등 memory 핵심!
- **within**: 그 시스템 내부 ROI들끼리의 평균 연결강도 (예: `DMN_within`)
- **between**: 두 시스템 사이의 평균 연결강도 (예: `DMN_FPN_between`)
- subject별로 행렬을 normalize한 뒤 평균을 내고, `total_strength`(전체 연결량 합)도 같이 저장

저장: `network_features.csv`.

→ 이렇게 Step 3이 끝나면, 각 subject는 **brain feature 한 묶음**(global 5개 + network 6개 = `PRIMARY_GRAPH_METRICS + PRIMARY_NETWORK_FEATURES`)을 가지게 된다!

---

## 4. Analyze

4개 GLM 분석 전부 공통 규칙이 있습니다:
- **trained-only**: 음악을 배운 사람(`music_training_status == 1`)만 사용 (onset/hours가 정의되는 사람들)
- 모든 변수 **z-score 표준화**(`standardize`) → β를 서로 비교 가능하게
- **covariate**: `age_years`, `sex`, `wisc_mr`(fluid IQ proxy)를 항상 통제

"다중 회귀 = covariate를 통제한 GLM, β는 **부분 효과(partial effect)**로 해석" — 즉 다른 변수를 고정한 채 그 변수만의 고유 기여.

### Step 4 — Brain → PSM (`step4`): 뇌가 기억을 설명하나?

각 brain feature 하나로 PSM을 예측 → predictor family 안에서 FDR 보정.

**실제 결과**: `small_worldness`만 보정 전 p = 0.019(t = 2.35)로 살짝 떴다가, **FDR 보정 후 q = 0.21 → 비유의**. 나머지는 전부 null. 즉 뇌 지표로 episodic memory를 설명하는 강한 신호는 없음.

### Step 5 — Music → PSM (`step5`, `_run_music_models`): ★ 핵심, 닭/달걀 ★

같은 outcome(PSM)에 대해 **모형 4개**를 비교합니다.

| 모형 | predictor | 실제 β (p) |
|---|---|---|
| **M1** onset only | onset | β = −0.092 (p = .30) |
| **M2** hours only | hours | β = −0.039 (p = .63) |
| **M3** both | onset, hours | β_onset = **−0.207** (p = .073), β_hours = −0.158 (p = .129) |
| **M4** + interaction | onset, hours, onset×hours | 상호작용 β = 0.030 (p = .74, 즉 없음) |

여기서 핵심 현상이 **suppressor effect**입니다. onset만 넣었을 때(M1)는 β가 −0.092로 약했는데, hours와 **같이** 넣으니(M3) −0.207로 **오히려 커졌습니다.** 왜 이런 일이?

- onset과 hours는 서로 강하게 얽혀 있습니다(일찍 시작 → 보통 더 많이 연습). 둘이 공유하는 분산이 서로의 효과를 가립니다.
- 둘을 같이 모형에 넣으면 그 공유분이 통제되면서, 각자의 **고유 효과**가 드러나 β가 커집니다.
- 이게 `fig5_suppressor.png`가 M1→M3 화살표로 강조하는 그림입니다.

**닭/달걀 판정 읽는 법**: M3에서 |β_onset| = 0.207 > |β_hours| = 0.158. onset이 hours보다 약간 우세 → **sensitive-period 쪽으로 살짝 기울지만** 둘 다 FDR 비유의(q ≈ 0.13). 그래서 정직한 결론은 "약하게 onset 우위, 그러나 skeptical view를 배제할 만큼은 아님". 평가 기준이 "유의성 불필요, 시나리오별 해석 프레임"이라 이게 정확히 맞는 진술 방식입니다.

(secondary outcome인 flanker/dccs/lswmt/pcps에도 같은 M1–M4를 돌려 `glm_music_behavior_secondary.csv`에 저장 — 음악 효과가 PSM에만 특이적인지 보려는 대조군 성격.)

### Step 6 — Music → Brain (`step6`): RQ2, 음악이 뇌 네트워크와 관련 있나?

이번엔 brain feature가 **outcome**입니다. 각 brain feature를 onset + hours로 동시에 예측(M3와 같은 구조), predictor별로 FDR.

**실제 결과**: onset·hours 둘 다, 11개 feature 전부 **비유의**(가장 센 게 `DMN_FPN_between` ~ hours, p = .25). 즉 음악 변수로 white-matter 조직을 설명하는 신호 없음.

### Step 7 — Mediation (`step7`, `_bootstrap_indirect`): onset → brain → PSM 경로가 있나?

"일찍 시작 → 뇌가 바뀜 → 그래서 기억이 좋아짐"이라는 **간접 경로**를 검정합니다.

- `a` = onset → mediator(brain) 효과
- `b` = mediator → PSM 효과 (onset 통제한 상태)
- `ab` = a × b = **간접효과(indirect effect)**
- 이 ab가 0과 다른지를 **bootstrap 5000회**(`N_BOOTSTRAP`)로 재표집해 95% CI로 판정. CI가 0을 포함하지 않으면 mediation 있음.

**실제 결과**: 11개 mediator 전부 `ci_excludes_zero = False`, p_boot > 0.40 → mediation 없음. (애초에 a, b 자체가 다 약하니 당연한 귀결.)

---

## 5. 그래서 전체 결론은? (숫자 → 해석)

- **Behavioral (RQ1, 핵심)**: M3에서 onset이 hours보다 약간 우세(−0.207 vs −0.158)하나 둘 다 비유의 → **sensitive-period 시나리오를 약하게 지지**, 단 skeptical view 배제 불가.
- **Brain (RQ2)**: Music → Brain 연관 사실상 없음, Brain → PSM도 (FDR 후) 없음, mediation도 없음 → 이 표본/방법에서 white-matter 조직이 음악-기억 관계를 매개한다는 증거 없음.
- 평가 기준상 유의성은 필수가 아니므로, 결론은 "예비적으로 onset 쪽으로 기우는 패턴, 효과는 약함"이라는 **시나리오 프레임**으로 진술하면 충분합니다.

---

## 6. 내가 추가한 normalize 패치가 이 그림을 바꾸나?

- **Behavioral(M1–M4, fig5)은 뇌를 안 쓰므로 그대로** — 닭/달걀 핵심 결과 불변.
- **Brain 쪽**은 값이 재스케일될 뿐이고, `modularity`와 `small_worldness`는 weight 스케일에 **수학적으로 불변**입니다. 게다가 baseline이 전부 null이라 결론이 안 바뀝니다.
- 따라서 normalize는 "결과를 갈아엎는 것"이 아니라 **confound(head size·streamline 수)를 통제했다는 robustness 보강**으로 보면 됩니다.

검산 포인트: 패치 후 `glm_brain_behavior.csv`에서 `small_worldness` β ≈ 0.1295, `modularity` β ≈ 0.0653이 **이전과 거의 같게** 나오면 패치가 의도대로 작동한 것입니다(불변 지표는 그대로, 나머지만 재스케일, 어차피 다 null).

---

## 부록 — 파일 흐름 한눈에

```
NDA .txt + .mat
   │  step1
   ▼
analysis_sample.csv ──────────────┐
   │  step2 (.mat → 정리/QC/log1p) │
   ▼                              │
data/processed/sc/*.npy           │
   │  step3                       │
   ▼                              │
graph_metrics.csv                 │  (brain features)
network_features.csv ─────────────┤
                                  ▼
           ┌──────────────┬───────────────┬──────────────┐
           ▼              ▼               ▼              ▼
   step4 Brain→PSM   step5 Music→PSM  step6 Music→   step7 mediation
   glm_brain_        glm_music_       Brain          mediation_
   behavior.csv      behavior.csv     glm_music_     results.csv
   (FDR)             (M1–M4, fig5)    brain.csv      (bootstrap)
                                  │
                                  ▼  step8
                          summary.md + figures/*.png
```