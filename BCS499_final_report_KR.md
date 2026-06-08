# 음악의 sensitive period는 episodic memory의 white matter에 흔적을 남기는가?
### HCP-D를 이용한 닭/달걀 문제의 graph-theoretic 검증

**서예슬 · 20230340 · Brain & Cognitive Sciences, KAIST**
BCS499 · Brain & Cognitive Sciences · Final Report

---

## 초록 (Abstract)

조기 음악 훈련이 아동의 인지 발달을 돕는다는 믿음은 널리 퍼져 있으나, 그 인과적 메커니즘은 여전히 논쟁적이다. 기존 문헌은 세 가지 경쟁 가설로 정리된다: **sensitive-period 가설**(언제 시작했는지가 중요), **dose-response 가설**(얼마나 훈련했는지가 중요), 그리고 **skeptical 입장**(겉보기 효과는 교란변수로 환원됨). 본 연구는 HCP-D 데이터(structural connectome 사용 가능 N = 473, trained-only n ≈ 183)를 사용해, **episodic memory**(Picture Sequence Memory, PSM 과제로 측정)에 대해 세 시나리오를 검증하였다. music onset age와 cumulative log-hours를 하나의 multiple regression(M3)에 함께 투입하여 두 변수의 partial effect를 공통 척도에서 비교하였다. white-matter connectome의 11개 graph-theoretic feature(global efficiency, modularity, small-worldness, characteristic path length, 그리고 DMN/FPN/MTL의 within/between-network strength) 중 small-worldness만 PSM과 명목적으로 유의하였다(β = +0.13, raw p = 0.019; FDR 비유의). 음악 측 결과는 전형적인 **suppressor pattern**을 보였다: cumulative hours를 통제하자 onset의 partial coefficient가 M1의 β = −0.092에서 M3의 β = −0.207로 커졌고, hours의 partial effect는 그보다 작은 크기에 머물렀다(β = −0.158). 11개 brain feature 전반의 bootstrap mediation에서는 간접효과가 검출되지 않았다(모든 95% CI가 0 포함). 종합하면, 데이터는 방향과 effect-size 순서 측면에서 sensitive-period 시나리오로 기울지만, 어느 β도 p < 0.05에 도달하지 못했고, mediation의 부재는 — 만약 HCP-D에 sensitive-period 효과가 존재하더라도 — 그것이 macroscale white-matter topology를 통해 전달되지는 않음을 시사한다.

---

## 1. 배경 및 의의 (Background and Significance)

이 프로젝트의 출발점은 흔한 부모의 직관이었다: 조기 음악 노출이 아이를 더 똑똑하게 만든다는 믿음. 많은 부모가 초등학교 입학 전부터 피아노 레슨을 시키며 그 경험이 뇌를 발달시키길 기대한다. 대중적 담론은 이를 강화하지만, 실증 문헌은 한목소리를 내지 않는다. 음악 훈련이 일반 인지를 인과적으로 향상시키는지는 수십 년간 논쟁되어 왔으며, 이 논쟁은 닭/달걀 문제의 구조를 가진다.

세 입장이 이 논쟁을 차지한다. 첫째, **sensitive-period view**는 훈련의 시점(timing)이 중요하다고 본다 — 발달 중인 뇌에는 음악 경험이 신경 회로를 조각할 수 있는 창(window)이 있고, 성숙한 뇌는 그렇게 하지 못한다는 것이다. Steele, Bailey, Zatorre & Penhune(2013)이 고전적 증거를 제시했다: posterior corpus callosum의 white-matter integrity가 7세 이전/이후 훈련 시작 여부와 체계적으로 관련되었으며, 이는 총 훈련 시간을 matching한 후에도 유지되었다. 둘째, **dose-response view**는 겉보기의 onset 효과가 실제로는 hours 효과라고 본다: 일찍 시작한 아이는 성인이 될 때까지 더 많은 총 연습량을 누적하며, 첫 레슨의 달력 나이가 아니라 그 누적 dose가 중요하다는 것이다(Schellenberg, 2020). 셋째, **skeptical view**는 socioeconomic status, 가정 환경, 선천적 적성의 교란을 적절히 통제하면 두 변수 어느 것도 정보를 담지 않는다고 본다(Sala & Gobet, 2017).

이 세 입장은 단순 상관으로 구분할 수 없다. onset age와 cumulative hours는 강하게 음의 상관을 가지므로(일찍 시작한 사람이 보통 더 많은 시간을 누적), 둘 중 어느 하나와 인지의 이변량 관계는 모호하다. 자연스러운 판별자는 두 변수를 함께 넣은 multiple regression이다: 다른 변수를 고정한 채 본 onset과 hours의 partial coefficient가 어느 시나리오가 데이터에 부합하는지 직접 검증한다. 이것이 본 프로젝트가 사전 등록한 분석 전략이다.

episodic memory는 특히 적절한 행동 outcome이다. 음악 학습은 근본적으로 순차적이다 — 연습은 순서화된 시간 패턴을 부호화하고, 운동 시퀀스를 기억하며, 선율 사건을 맥락 단서에 결합하는 것으로 이루어진다. NIH Toolbox Picture Sequence Memory(PSM) 과제는 바로 이 기제를 측정한다: 참가자는 그림으로 제시된 사건의 순서를 재현한다. "지능"이라는 광범위한 구성 개념에 비해, PSM은 모든 HCP-D 참가자에게 가용한, 구체적이고 잘 검증되었으며 이론적으로 동기화된 종속변수를 제공한다.

white-matter 측면의 동기는 구조적 네트워크 topology 자체가 발달적으로 역동적이라는 최근 커넥톰 연구에서 나온다. Mousley, Bethlehem, Yeh & Astle(2025)은 white-matter topology에 네 개의 주요 lifespan turning point(9, 32, 66, 83세)가 있음을 보고하고, 9–32세 epoch에서 small-worldness를 나이를 가장 강하게 예측하는 LASSO 지표로 식별했다 — 바로 HCP-D 연령대를 포함하는 구간이다. 음악의 sensitive period가 커넥톰에 흔적을 남긴다면, 그 흔적이 탐지될 것으로 기대되는 발달 창이 바로 이 구간이다.

---

## 2. 연구 질문 및 가설 (Research Questions and Hypotheses)

### 2.1 연구 질문

**RQ1.** music onset age는 PSM 수행과 관련되는가? 그 관련은 cumulative training hours를 통제한 후에도 유지되는가?

**RQ2.** music onset age는 white-matter 네트워크 조직과 관련되는가? 행동적 효과가 존재한다면, 그것은 이 네트워크 feature들에 의해 mediation되는가?

### 2.2 사전 등록한 시나리오

닭/달걀 논쟁은 M3의 partial coefficient에 대한 상호 배타적인 세 예측으로 조작화된다:

> PSM ~ β₁ · onset_age + β₂ · log(hours) + covariates

- **H1a (Sensitive period):** |β(onset)| > |β(hours)|, 둘 다 음수.
- **H1b (Dose-response):** |β(hours)| > |β(onset)|, hours 음수.
- **H1c (Skeptical):** 둘 다 β ≈ 0; 교란변수 통제 후 살아남는 것이 없음.

이 사전 등록 하에서 세 시나리오는 p < 0.05 대 null의 이분법으로 판정되지 않는다. 통계적 유의성은 하나의 입력일 뿐이며, partial coefficient의 방향과 상대적 크기가 똑같이 중요하다. 강의계획서가 유의한 결과가 필수가 아니며 프로젝트는 가설의 명확성, 파이프라인의 논리성, 예비 결론으로 평가됨을 강조하기 때문이다. 이 프레임은 marginal p-value의 과대해석과 정보적 effect-size 패턴의 기각을 모두 방지한다.

---

## 3. 방법 (Methods)

### 3.1 데이터셋 및 표본 구성

데이터는 NIMH Data Archive를 통해 접근한 Human Connectome Project — Development(HCP-D)에서 나온다. 시작 demographic table은 652명을 포함했다. 음악 변수는 NDA SAIQ instrument(500명, 286명 ever-trained)에서 병합되었다. 인지 변수(PSM, Flanker, DCCS, list sorting, pattern comparison)는 해당 NIH Toolbox 파일에서 병합되었다(인지 점수 1개 이상 보유 611명). PSM 점수 결측 제거 후 **473명이 남았으며, 이들 전원이 quality control(Step 2) 후 사용 가능한 structural connectivity 행렬을 가졌다**.

### 3.2 음악 변수

music onset age는 참가자의 현재 나이에서 보고된 총 훈련 햇수를 뺀 값으로 추정하였다. 훈련 이력이 없는 참가자는 untrained로 간주하여 trained-only 분석에서 제외하였다.

cumulative hours는 보고된 햇수 × 주/년 × 일/주 × 분/세션으로 추정한 뒤 log 변환(log(hours + 1))하여 긴 오른쪽 꼬리를 압축하고 분산을 안정화하였다.

### 3.3 Structural connectome 및 graph metric

각 참가자의 246×246 structural connectivity(SC) 행렬은 HCP-D가 Brainnetome 아틀라스 위에서 DSI Studio의 QSDR 파이프라인으로 재구성하였다. edge weight는 streamline count이며, 긴 꼬리 분포를 안정화하기 위해 log 변환(log1p)하였다. 행렬은 **proportional thresholding(primary density = 상위 15% edge; robustness로 10%, 15%, 20%)을 적용하고 weight를 [0, 1]로 정규화**하였다. bctpy로 11개 graph-theoretic feature를 계산하였다: global efficiency, modularity, mean clustering coefficient, characteristic path length, small-worldness, 그리고 세 Yeo 하위망(DMN, FPN, MTL)의 within/between-network 평균 연결강도(DMN_within, FPN_within, MTL_within, DMN_FPN_between, DMN_MTL_between, FPN_MTL_between).

두 integration 지표는 shortest-path communication model을 구현한다: 각 edge weight를 connection length(1/weight)로 변환하고, 모든 영역 쌍의 최단 가중 경로를 계산하여, characteristic path length는 평균 경로 거리, global efficiency는 평균 역최단거리로 정의한다(communication-model 용어로 각각 SPL과 SPE). navigation(greedy routing)이나 diffusion model(random walk, communicability) 등 더 decentralized한 communication model은 본 연구 범위를 벗어나며, robustness 확장 항목으로 남긴다.

robustness check로, edge weight를 [0, 1]로 정규화(BCT `weight_conversion`)하여 모든 graph metric을 재계산하였다. 정규화 후에도 brain–behavior 및 music–brain 연관의 패턴은 동일하게 유지되었으며(모두 FDR 보정 후 비유의), modularity와 small-worldness는 정의상 weight 스케일에 불변이므로, 보고된 결론은 weight 정규화 선택에 의존하지 않는다.

### 3.4 통계 모형

모든 확증적 분석은 **age, sex, WISC-V Matrix Reasoning(fluid-reasoning proxy)**을 covariate로 하는 multiple linear regression을 사용하였다. predictor는 z-표준화하여 β 계수의 크기를 직접 비교 가능하게 하였다. FDR(Benjamini–Hochberg)는 각 step 내에서 적용하였다(Step 4: 11 feature; Step 5: M3의 2 predictor; Step 6: 22 검정; Step 7: 11 mediator).

- **Step 4 — Brain → PSM (n = 306).** 11개 graph feature 각각을 PSM의 predictor로 하나씩 검정, 전체 covariate 보정.
- **Step 5 — Music → PSM (trained-only, n ≈ 183).** 네 개의 nested model: M1(onset only), M2(hours only), M3(both, primary model), M4(both + onset × hours interaction).
- **Step 6 — Music → Brain (n = 175).** 11개 graph feature 각각을 onset과 log-hours에 대해 별도로 회귀, covariate 포함.
- **Step 7 — Mediation (n = 175).** 11개 graph feature 각각에 대해 onset → PSM의 간접효과(a×b)를 추정하고, 95% bootstrap 신뢰구간(5,000 resample)을 계산.

---

## 4. 결과 (Results)

### 4.1 표본 기술

trained 하위표본(음악 변수 완전 보유 n = 201)의 onset age 분포는 8–11세에 크게 집중되어 있다(그림 1). 7세 이전에 시작한 참가자는 **44명(≈22%)**에 불과하다. 이 분포는 프로젝트의 해석적 경계를 규정한다: 우리는 Steele et al.(2013)을 동기화한 고전적인 7세 이전 대 이후 sensitive-period 대비가 아니라, 전형적 모집단 내에서 "상대적으로 더 이른 vs. 더 늦은" onset을 검증하는 것이다.

*그림 1. trained 하위표본(n = 201)의 추정 music onset age 분포.*

### 4.2 Brain → PSM (Step 4)

11개 graph feature 중 small-worldness만 PSM과 명목적으로 유의한 양의 관련을 보였으나(β = +0.130, raw p = 0.019), FDR 보정은 통과하지 못했다(q = 0.21). 나머지 feature는 모두 raw p > 0.26이었다(그림 2). small-worldness 효과의 방향(높은 small-worldness ↔ 더 나은 PSM)은 청소년기 integration–segregation 균형 문헌과 일관된다.

*그림 2. PSM을 예측하는 각 graph-theoretic feature의 표준화 회귀계수(Step 4, n = 306). 모든 FDR 보정 q-value가 0.21을 초과한다.*

### 4.3 Music → PSM 및 suppressor pattern (Step 5)

프로젝트의 핵심 결과는 M1, M2, M3의 비교이다(표 1, 그림 3). marginal regression에서는 onset(M1: β = −0.092, p = 0.30)도 hours(M2: β = −0.039, p = 0.63)도 유의하지 않았다. 그러나 joint model M3에서는 onset의 partial coefficient가 β = −0.207(p = 0.073)로 크기가 두 배 이상 커졌고, hours의 partial coefficient는 β = −0.158(p = 0.129)로 보다 완만하게 커졌다. M4의 onset × hours interaction은 사실상 0이었으므로(β = +0.030, p = 0.742), suppression 효과는 가산적(additive)이다.

**표 1.** nested model 전반의 표준화 partial regression 계수. trained-only 하위표본(n ≈ 183). M3가 사전 등록한 primary model이다.

| Model | Predictor | β | SE | p |
|---|---|---|---|---|
| M1 (onset only) | onset age | −0.092 | 0.088 | 0.300 |
| M2 (hours only) | log hours | −0.039 | 0.080 | 0.629 |
| **M3 (both)** | **onset age** | **−0.207** | **0.115** | **0.073** |
| **M3 (both)** | **log hours** | **−0.158** | **0.104** | **0.129** |
| M4 (+ interaction) | onset age | −0.215 | 0.118 | 0.070 |
| M4 (+ interaction) | log hours | −0.160 | 0.104 | 0.126 |
| M4 (+ interaction) | onset × hours | +0.030 | 0.091 | 0.742 |

*그림 3. M1, M2, M3 nested model 시퀀스 전반의 suppressor pattern. 오차 막대는 ± 1 SE. 빨간 곡선은 onset 계수가 −0.092(M1, marginal)에서 −0.207(M3, partial)로 커지는 양상을 추적한다.*

이 패턴은 진단적이다. 순수 dose-response 설명이라면 두 predictor를 함께 넣었을 때 hours의 계수가 더 커야 하지만, 실제로는 그 반대로 상대적 순서가 나타나며 |β(onset)| / |β(hours)| ≈ 1.31이다. 두 계수의 방향은 모두 음수로, 더 이른 onset과 더 많은 hours가 각각 더 나은 PSM을 예측한다는 것과 일관된다. interaction의 거의 0에 가까운 값은 onset 효과가 어떤 훈련 임계치 도달에 의존한다는 하위 가설을 기각한다.

M3에서 onset age와 log cumulative hours는 약한 음의 상관을 보였으나(r = −0.27), 두 predictor의 variance inflation factor(VIF)는 각각 2.37, 2.14로 통상적 임계값(5)을 크게 밑돌았다. 따라서 관찰된 suppressor effect는 multicollinearity로 인한 추정 불안정이 아니라, 공유 분산을 통제한 후 드러난 onset age의 partial effect 분리에 기인한 것으로 해석된다.

짚어둘 만한 작은 퍼즐: raw, 비보정 수준(그림 4)에서 late-onset 집단의 PSM 중앙값이 early/middle-onset 집단보다 약간 높다. 이것이 suppressor effect를 시각적으로 보여주는 것이다 — HCP-D의 late starter는 더 나이가 많고 발달적으로 더 완성된 PSM 점수를 가지는 경향이 있어, M3의 joint adjustment에서만 기저의 onset 효과가 드러난다.

*그림 4. 음악 onset 집단별 raw(비보정) PSM. late 집단의 중앙값이 early 집단보다 근소하게 높은데, 이는 cumulative hours와 demographic covariate를 통제하면 역전되는 패턴이다.*

### 4.4 Music → Brain (Step 6)

22개 회귀(11 graph feature × 2 음악 predictor)를 추정했으며 FDR 보정을 통과한 것은 없었다. 가장 두드러진 raw 신호는 DMN_FPN_between과 log-hours(β = +0.13, p = 0.25), small-worldness와 onset(β = −0.13, p = 0.28)이었다. 둘 다 개별 해석에는 너무 약하지만 방향은 더 넓은 패턴과 일관된다(더 많은 연습 → 더 강한 망 간 연결; 늦은 onset → 더 약한 small-world 구조).

### 4.5 Mediation: Onset → Brain → PSM (Step 7)

11개 후보 매개변수 전반에서 간접효과(a × b)의 bootstrap 95% 신뢰구간은 모두 0을 포함했다(그림 5). 가장 큰 점추정치는 small-worldness였고(a×b = −0.016, CI [−0.063, +0.020], p_boot = 0.40), 방향은 sensitive-period 예측과 일관되었으나 간접효과는 통계적으로 영(null)이었다. 중요하게도, onset의 PSM에 대한 직접효과(c-path: β = −0.236)는 모든 매개변수별 모형에서 c′ ≈ −0.22로 거의 감쇠하지 않았으며, 이는 onset → PSM 신호가 이 macroscale white-matter feature를 통과하지 않음을 나타낸다.

*그림 5. 11개 후보 white-matter 매개변수를 통한 music onset age의 PSM에 대한 간접효과. 수염은 95% bootstrap 신뢰구간(5,000 resample). 모든 구간이 0을 포함한다.*

---

## 5. 논의 (Discussion)

### 5.1 세 시나리오에 대한 판정

**sensitive-period 시나리오**가 사전 등록한 세 가설 중 가장 잘 부합하지만, 약하게만 그렇다. 두 증거가 이를 지지한다: (i) 상대적 크기 패턴, M3에서 |β(onset)| > |β(hours)| — 바로 H1a의 예측; 그리고 (ii) 두 계수의 방향, 예상대로 음수. 두 증거가 지지를 제한한다: (i) 어느 β도 p < 0.05에 도달하지 못했고, 주 onset 계수가 p ≈ 0.07이라는, 관례적 기준에서 기각도 채택도 정당화되지 않는 애매한 구간에 있다; 그리고 (ii) macroscale 매개 경로가 실증적으로 부재한다 — 이 표본에서 sensitive period가 실재한다 해도, 우리가 측정한 11개 topology feature를 통해 작동하지는 않는다.

**dose-response 시나리오**는 약하게 비선호된다. onset을 고정한 후 hours의 partial coefficient는 onset보다 크기가 작다. interaction이 null이므로, 고용량 훈련이 onset 효과를 증폭한다는 것도 아니다.

**skeptical 시나리오는 자신 있게 기각할 수 없다**: FDR을 통과하는 것이 없고, trained-only 표본(n = 183)이 다변량 회귀에는 작으며, 결정적으로 우리의 covariate 세트(age, sex, fluid reasoning)에는 skeptical 입장이 강조하는 바로 그 교란변수인 socioeconomic status나 가정 환경 측정치가 포함되어 있지 않다. 따라서 onset 패턴이 부분적으로 측정되지 않은 배경 변수를 반영할 가능성을 배제할 수 없다. 정직한 보고라면 이 가능성을 열어두어야 한다.

### 5.2 macroscale 커넥톰이 침묵하는 이유

가장 정보적인 음성(negative) 결과는 mediation null이다. Steele et al.(2013)은 sensitive-period 효과를 posterior corpus callosum에 국소화했으며, tractography의 fractional anisotropy — 미세구조적이고 트랙 특이적인 측정치 — 를 사용했다. 대조적으로 우리의 11개 feature는 thresholding 후 전뇌 그래프의 네트워크 수준 요약치이다. 두 가지 해석이 그럴듯하다:

- **잘못된 공간 척도.** 특정 commissural 트랙의 국소적 FA 차이는 small-worldness나 modularity 같은 네트워크 수준 topology 지표를 바꾸지 않을 수 있다. 신호가 트랙 수준에 존재하지만 전역 수준에서 보이지 않을 수 있다.
- **잘못된 조직.** 시퀀스 기억은 hippocampal–prefrontal 회로에 결정적으로 의존한다. MTL의 gray-matter volume이나 MTL–FPN 간 functional connectivity가 집계된 structural-connectome topology보다 더 직접적인 기질일 수 있다.

어느 쪽이든, 적절한 다음 실험은 동일 파이프라인의 더 큰 N 반복이 아니라, 관심 트랙의 트랙 특이적 미세구조 지표(FA, RD)나 hippocampal/MTL volumetry를 동일 HCP-D 표본에 적용하는 재설계이다.

### 5.3 lifespan turning-point 프레임워크와의 연결

유일하게 명목적으로 유의한 Brain → PSM 신호인 small-worldness(β = +0.13)는 임의적이지 않다. Mousley et al.(2025)은 small-worldness가 9–32세 epoch(HCP-D 전 연령대를 포함)에서 나이를 예측하는 가장 큰 LASSO 계수를 가진다고 보고했다. 우리의 유일한 행동적 적중이, 생애 논문이 이 연령 창의 지배적 발달 축으로 지목한 바로 그 지표라는 점은, 이 구간의 PSM 관련 커넥톰 재조직이 부분적으로 small-worldness를 통해 작동한다는 생각과 적어도 일관된다. 이는 본 연구가 해소할 수 없는 가설로서, 후속 연구 거리로 남는다.

### 5.4 한계 (Limitations)

- **검정력(Power).** trained-only n = 183. 주 M3 onset 계수가 p = 0.07에 있어, 50–100명을 추가하면 한쪽으로 결론이 정리될 가능성이 높은 애매한 구간이다.
- **Onset 커버리지.** trained 참가자의 ≈ 22%만 7세 이전에 시작했다. 고전적 Steele 식 대비는 표본 크기가 아니라 표본 구성에 의해 검정력이 부족하다.
- **측정되지 않은 교란변수.** 분석 표본에 socioeconomic-status나 family-income covariate가 없어 skeptical 시나리오를 완전히 다룰 수 없다.
- **자기보고(Self-report).** 음악 이력은 후향적 부모/자기보고이며, cumulative hours는 측정 오차를 누적시키는 거친 곱셈 단위로 추정된다.
- **횡단(Cross-sectional).** 인과 방향을 분리할 수 없다 — "더 나은 뇌 → 더 이른 시작"은 "더 이른 시작 → 더 나은 뇌"와 형식적으로 구분 불가능하다.
- **macroscale feature만 사용.** 트랙 특이적 FA/RD, gray-matter volume, functional connectivity를 검정하지 않았으며, 이들 중 어느 것이라도 macroscale topology가 담지 못한 흔적을 담을 수 있다.

---

## 6. 결론 (Conclusion)

본 프로젝트는 음악 onset의 시점이 episodic memory와 macroscale white-matter connectome에 탐지 가능한 흔적을 남기는지를 물었다. 사전 등록한 세 시나리오 프레임을 사용하여 다음을 발견했다:

- **행동(Behavior):** cumulative hours를 통제하자 PSM에 대한 onset의 partial effect가 |β| = 0.09에서 |β| = 0.21로 커지고, hours의 partial effect보다 크기가 큰 전형적인 suppressor pattern(p = 0.073, n = 183). 이 패턴은 sensitive-period 시나리오가 예측하는 signature이다.
- **뇌(Brain):** PSM을 명목 수준에서 예측하는 것은 small-worldness뿐이며(raw p = 0.019, FDR 비유의), 이는 생애 연구(Mousley et al., 2025)가 우리 표본이 속한 9–32세 epoch의 가장 강한 나이 예측자로 지목한 바로 그 지표다.
- **Mediation:** 어떤 macroscale topology feature도 onset → PSM 신호를 담지 않는다. 11개 간접효과 95% CI가 모두 0을 포함한다.

정직한 요약은, 데이터가 행동 측면에서 sensitive-period 시나리오로 기울지만 그 흔적은 — 실재한다 해도 — macroscale white-matter topology에 있지 않다는 것이다. 가장 생산적인 다음 단계는 탐색을 트랙 특이적 미세구조와 MTL gray-matter 및 functional 측정치로 — 원래의 sensitive-period 및 episodic-memory 문헌이 관련 생물학을 위치시키는 바로 그 기질로 — 재조준하는 것이다.

---

## 7. 참고문헌 (References)

Bigand, E., & Tillmann, B. (2022). Near and far transfer: Is music special? *Memory & Cognition, 50*(2), 339–347.

Mousley, A., Bethlehem, R. A. I., Yeh, F.-C., & Astle, D. E. (2025). Topological turning points across the human lifespan. *Nature Communications, 16*, 10055.

Sala, G., & Gobet, F. (2017). When the music's over: Does music skill transfer to children's and young adolescents' cognitive and academic skills? A meta-analysis. *Educational Research Review, 20*, 55–67.

Schellenberg, E. G. (2020). Correlation = causation? Music training, psychology, and neuroscience. *Psychology of Aesthetics, Creativity, and the Arts, 14*(4), 475–480.

Steele, C. J., Bailey, J. A., Zatorre, R. J., & Penhune, V. B. (2013). Early musical training and white-matter plasticity in the corpus callosum: Evidence for a sensitive period. *Journal of Neuroscience, 33*(3), 1282–1290.

---

## 부록 · 데이터 및 코드 가용성 (Appendix · Data and Code Availability)

11-step 파이프라인(Step 1–7 확증; Step 8–10 탐색; Step 11 figure 및 summary)을 포함한 모든 분석 코드는 프로젝트 저장소에서 이용 가능하다: github.com/ashleysys04-blip/music_connectome_pipeline. HCP-D 영상 및 행동 데이터는 NDA Data Use Certification 하에 접근하며 재배포하지 않는다.
