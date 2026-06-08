# Does music's sensitive period leave a trace in episodic memory's white matter?
### A graph-theoretic test of the chicken-and-egg problem using HCP-D

**서예슬 · 20230340 · Brain & Cognitive Sciences, KAIST**
BCS499 · Brain & Cognitive Sciences · Final Report

---

## Abstract

Early music training is widely believed to enhance children's cognitive development, but the underlying causal story remains contested. Three competing explanations have shaped the literature: a sensitive-period account (when training starts matters), a dose-response account (how much one trains matters), and a skeptical account (apparent effects reduce to confounding). I used HCP-D data (N = 473 with usable structural connectomes; trained-only n ≈ 183) to test these scenarios on episodic memory, operationalized via the Picture Sequence Memory (PSM) task. Music onset age and cumulative log-hours of training were entered into a single multiple regression (M3) so their partial effects could be compared on a common scale. Across 11 graph-theoretic features of the white-matter connectome (global efficiency, modularity, small-worldness, characteristic path length, and within/between-network strength for DMN, FPN, and MTL), only small-worldness reached nominal significance with PSM (β = +0.13, raw p = 0.019; FDR n.s.). The music-side results showed a textbook suppressor pattern: onset's partial coefficient grew from β = −0.092 in M1 to β = −0.207 in M3 once cumulative hours was controlled, while hours' partial effect remained smaller in magnitude (β = −0.158). Bootstrap mediation across all 11 brain features yielded no indirect effects (all 95% CIs included zero). Together, the data lean toward the sensitive-period scenario in direction and effect-size ordering, but neither β reached p < 0.05, and the absence of mediation implies that — if a sensitive-period effect exists in HCP-D — it does not travel through macroscale white-matter topology.

---

## 1. Background and Significance

My motivation for this project began with a common parental intuition: that early musical exposure makes children smarter. Many parents enroll their children in piano lessons before elementary school, hoping the experience will sharpen the brain. The popular literature reinforces this idea, but the empirical literature does not speak with one voice. Whether music training causally improves general cognition has been debated for decades, and the debate has the structure of a chicken-and-egg problem.

Three positions occupy this debate. First, the **sensitive-period view** holds that the timing of training matters — that the developing brain has a window during which musical experience can sculpt neural circuitry in ways that mature brains cannot. Steele, Bailey, Zatorre and Penhune (2013) provided the classic evidence: white-matter integrity in the posterior corpus callosum was systematically related to whether musicians began training before or after age seven, even after matching for total hours. Second, the **dose-response view** holds that the apparent onset effect is really an hours effect: children who start earlier accumulate more total practice by adulthood, and that cumulative dose — not the calendar age at first lesson — is what matters (Schellenberg, 2020). Third, the **skeptical view** holds that neither variable carries information once one properly controls for the confounding effects of socioeconomic status, family environment, and pre-existing aptitude (Sala & Gobet, 2017).

These three positions cannot be distinguished by simple correlation. Because onset age and cumulative hours are strongly negatively correlated (early starters typically accumulate more hours), the bivariate relationship of either with cognition is ambiguous. The natural arbiter is a multiple regression including both predictors: the partial coefficients on onset and hours, holding the other constant, directly test which scenario fits the data. This is the analytic strategy this project pre-registered.

Episodic memory is a particularly appropriate behavioral outcome. Music learning is fundamentally sequential — practice consists of encoding ordered temporal patterns, remembering motor sequences, and binding melodic events to contextual cues. The NIH Toolbox Picture Sequence Memory (PSM) task probes this same machinery: participants reproduce ordered sequences of pictured events. Compared with the broad construct of "intelligence," PSM offers a concrete, well-validated, theoretically motivated dependent variable that is available across all HCP-D participants.

The white-matter side of the question is motivated by recent connectome-level work showing that structural network topology is itself developmentally dynamic. Mousley, Bethlehem, Yeh and Astle (2025) reported four major lifespan turning points in white-matter topology (ages 9, 32, 66, and 83) and identified small-worldness as the strongest LASSO-retained predictor of age in the 9–32 epoch — the very epoch that contains the HCP-D age range. If music's sensitive period writes itself into the connectome, this is the developmental window in which we would expect that trace to be detectable.

---

## 2. Research Questions and Hypotheses

### 2.1 Research questions

**RQ1.** Is music onset age associated with PSM performance? Does the association survive controlling for cumulative training hours?

**RQ2.** Is music onset age associated with white-matter network organization? If a behavioral effect exists, is it mediated by these network features?

### 2.2 Pre-registered scenarios

The chicken-and-egg debate is operationalized as three mutually exclusive predictions for the partial coefficients of M3:

> PSM ~ β₁ · onset_age + β₂ · log(hours) + covariates

- **H1a (Sensitive period):** |β(onset)| > |β(hours)|, with both negative.
- **H1b (Dose-response):** |β(hours)| > |β(onset)|, with hours negative.
- **H1c (Skeptical):** Both β ≈ 0; nothing survives once confounders are controlled.

Note that under this pre-registration the three scenarios are not resolved by p < 0.05 versus null. Statistical significance is one input; the direction and relative magnitude of the partial coefficients are equally important, because the syllabus emphasizes that significant results are not required and the project is to be evaluated on hypothesis clarity, pipeline logic, and preliminary conclusions. This framing protects against both overinterpretation of marginal p-values and dismissal of informative effect-size patterns.

---

## 3. Methods

### 3.1 Dataset and sample construction

Data come from the Human Connectome Project — Development (HCP-D), accessed through the NIMH Data Archive. The starting demographic table contained 652 participants. Music variables were merged from the NDA SAIQ instrument (500 participants, 286 ever-trained). Cognitive variables (PSM, Flanker, DCCS, list sorting, pattern comparison) were merged from the corresponding NIH Toolbox files (611 participants with at least one cognitive score). After requiring a non-missing PSM score, **473 participants remained, all of which had usable structural connectivity matrices after quality control (Step 2)**.

### 3.2 Music variables

Music onset age was estimated as the participant's current age minus their reported total years of training. Participants reporting no training were treated as untrained and excluded from the trained-only analyses.

Cumulative hours was estimated from the reported years × weeks/year × days/week × minutes/session, then log-transformed (log(hours + 1)) to compress the heavy right tail and stabilize variance.

### 3.3 Structural connectomes and graph metrics

Each participant's 246×246 structural connectivity (SC) matrix was reconstructed by HCP-D using DSI Studio's QSDR pipeline on the Brainnetome atlas; edge weights are streamline counts, which were log-transformed (log1p) to stabilize their heavy-tailed distribution. Matrices were **proportionally thresholded (primary density = top 15% of edges; robustness across 10%, 15%, and 20%) and weight-normalized to [0, 1]**. Eleven graph-theoretic features were computed using bctpy: global efficiency, modularity, mean clustering coefficient, characteristic path length, small-worldness, and the average within-network and between-network connection strengths for three Yeo subnetworks (DMN, FPN, MTL): DMN_within, FPN_within, MTL_within, DMN_FPN_between, DMN_MTL_between, FPN_MTL_between.

The two integration metrics implement a shortest-path communication model: each edge weight is converted to a connection length (1/weight), all-pairs shortest weighted paths are computed, and characteristic path length is the mean path distance while global efficiency is the mean inverse shortest path (i.e., SPL and SPE in the communication-model terminology). More decentralized communication models (navigation/greedy routing; diffusion models such as random walk and communicability) were outside the scope of this study and are noted as a robustness extension.

As a robustness check, all graph metrics were recomputed after normalizing edge weights to [0, 1] using BCT `weight_conversion`. The pattern of brain–behavior and music–brain associations was unchanged (all remained non-significant after FDR correction), and modularity and small-worldness are by construction invariant to weight scaling, so the reported conclusions do not depend on the weight-normalization choice.

### 3.4 Statistical models

All confirmatory analyses used multiple linear regression with **age, sex, and WISC-V Matrix Reasoning (a fluid-reasoning proxy)** as covariates. Predictors were z-standardized so that β coefficients are directly comparable in magnitude. FDR (Benjamini–Hochberg) was applied within each step (Step 4: 11 features; Step 5: M3's 2 predictors; Step 6: 22 tests; Step 7: 11 mediators).

- **Step 4 — Brain → PSM (n = 306).** Each of 11 graph features was tested as a predictor of PSM, one at a time, with full covariate adjustment.
- **Step 5 — Music → PSM (trained-only, n ≈ 183).** Four nested models: M1 (onset only), M2 (hours only), M3 (both, the primary model), and M4 (both + onset × hours interaction).
- **Step 6 — Music → Brain (n = 175).** Each of 11 graph features regressed on onset and on log-hours separately, with covariates.
- **Step 7 — Mediation (n = 175).** For each of the 11 graph features, the indirect effect (a×b) of onset on PSM via that feature was estimated, and a 95% bootstrap confidence interval (5,000 resamples) was computed.

---

## 4. Results

### 4.1 Sample description

The trained subsample (n = 201 with complete music variables) has an onset age distribution heavily concentrated between 8 and 11 years (Fig. 1). Only **44 participants (≈22%)** started before age 7. This distribution shapes the interpretive boundary of the project: we are testing "relatively earlier vs. later" onset within a typical-population sample, not the classical pre-7 versus post-7 sensitive-period contrast that motivated Steele et al. (2013).

*Figure 1. Distribution of estimated music onset age in the trained subsample (n = 201).*

### 4.2 Brain → PSM (Step 4)

Among the 11 graph features, only small-worldness showed a nominally significant positive association with PSM (β = +0.130, raw p = 0.019), but this did not survive FDR correction (q = 0.21). All other features had raw p > 0.26 (Fig. 2). The direction of the small-worldness effect — higher small-worldness associated with better PSM — is consistent with the integration–segregation balance literature in adolescence.

*Figure 2. Standardized regression coefficients for each graph-theoretic feature predicting PSM (Step 4, n = 306). All FDR-corrected q-values exceed 0.21.*

### 4.3 Music → PSM and the suppressor pattern (Step 5)

The headline result of the project is the comparison of M1, M2, and M3 (Table 1, Fig. 3). In the marginal regressions, neither onset (M1: β = −0.092, p = 0.30) nor hours (M2: β = −0.039, p = 0.63) reached significance. In the joint model M3, however, onset's partial coefficient more than doubled in magnitude to β = −0.207 (p = 0.073), while hours' partial coefficient grew more modestly to β = −0.158 (p = 0.129). The onset × hours interaction in M4 was effectively zero (β = +0.030, p = 0.742), so the suppression effect is additive.

**Table 1.** Standardized partial regression coefficients across nested models. Trained-only subsample (n ≈ 183). M3 is the pre-registered primary model.

| Model | Predictor | β | SE | p |
|---|---|---|---|---|
| M1 (onset only) | onset age | −0.092 | 0.088 | 0.300 |
| M2 (hours only) | log hours | −0.039 | 0.080 | 0.629 |
| **M3 (both)** | **onset age** | **−0.207** | **0.115** | **0.073** |
| **M3 (both)** | **log hours** | **−0.158** | **0.104** | **0.129** |
| M4 (+ interaction) | onset age | −0.215 | 0.118 | 0.070 |
| M4 (+ interaction) | log hours | −0.160 | 0.104 | 0.126 |
| M4 (+ interaction) | onset × hours | +0.030 | 0.091 | 0.742 |

*Figure 3. Suppressor pattern across the M1, M2, M3 nested model sequence. Error bars are ± 1 SE. The red curve traces the growth in onset's coefficient from −0.092 (M1, marginal) to −0.207 (M3, partial).*

This pattern is diagnostic. A pure dose-response account would predict that hours' coefficient should be the larger one once both predictors are entered; instead, the relative ordering is the opposite, with |β(onset)| / |β(hours)| ≈ 1.31. The direction of both coefficients is negative, consistent with earlier onset and more hours each predicting better PSM. The interaction's near-zero value rules out the sub-hypothesis that the onset effect depends on having reached some training threshold.

In M3, onset age and log cumulative hours were weakly negatively correlated (r = −0.27), but their variance inflation factors were 2.37 and 2.14 respectively — well below the conventional threshold of 5. The observed suppressor effect therefore reflects the separation of the two predictors' partial effects once their shared variance is controlled, rather than estimation instability arising from multicollinearity.

A small puzzle worth flagging: at the raw, unadjusted level (Fig. 4), the late-onset group has a slightly higher median PSM than the early- or middle-onset groups. This is the suppressor effect made visual — late starters in HCP-D tend to be older, with more developmentally completed PSM scores, and only the joint adjustment in M3 reveals the underlying onset effect.

*Figure 4. Raw (unadjusted) PSM by music onset group. Note that the late group has a marginally higher median than the early group — a pattern that reverses once cumulative hours and demographic covariates are controlled.*

### 4.4 Music → Brain (Step 6)

Twenty-two regressions (11 graph features × 2 music predictors) were estimated. None survived FDR correction. The most prominent raw signals were DMN_FPN_between with log-hours (β = +0.13, p = 0.25) and small-worldness with onset (β = −0.13, p = 0.28); both are too weak to interpret individually but their directions are consistent with the broader pattern (more practice → stronger between-network connectivity; later onset → less small-world structure).

### 4.5 Mediation: Onset → Brain → PSM (Step 7)

Across all 11 candidate mediators, the bootstrap 95% confidence intervals for the indirect effect (a × b) included zero (Fig. 5). The largest point estimate was for small-worldness (a×b = −0.016, CI [−0.063, +0.020], p_boot = 0.40), and the direction was consistent with the sensitive-period prediction — but the indirect effect was statistically null. Importantly, the direct effect of onset on PSM (the c-path: β = −0.236) was barely attenuated to c′ ≈ −0.22 in every mediator-specific model, indicating that the onset → PSM signal does not pass through these macroscale white-matter features.

*Figure 5. Indirect effects of music onset age on PSM through each of 11 candidate white-matter mediators. Whiskers are 95% bootstrap confidence intervals (5,000 resamples). All intervals include zero.*

---

## 5. Discussion

### 5.1 Verdict on the three scenarios

The **sensitive-period scenario** is the best-fitting of the three pre-registered hypotheses, but only weakly. Two pieces of evidence support it: (i) the relative-magnitude pattern, |β(onset)| > |β(hours)| in M3 — exactly the prediction made by H1a; and (ii) the direction of both coefficients, negative as expected. Two pieces of evidence qualify the support: (i) neither β reached p < 0.05, with the primary onset coefficient sitting in the awkward p ≈ 0.07 zone where neither rejection nor acceptance is justified at conventional thresholds; and (ii) the macroscale mediation pathway is empirically absent — if the sensitive period is real in this sample, it does not operate through the eleven topology features we measured.

The **dose-response scenario** is weakly disfavored. After onset is held constant, hours' partial coefficient is smaller in magnitude than onset's. The interaction is null, so it is not the case that high-dose training amplifies an onset effect.

The **skeptical scenario cannot be confidently rejected**: nothing survives FDR, the trained-only sample (n = 183) is modest for a multi-predictor regression, and — critically — our covariate set (age, sex, fluid reasoning) does not include socioeconomic status or family-environment measures, the very confounders the skeptical account emphasizes. We therefore cannot rule out that the onset pattern partly reflects unmeasured background variables. An honest report has to leave this possibility on the table.

### 5.2 Why the macroscale connectome may be silent

The most informative negative result is the mediation null. Steele et al. (2013) localized their sensitive-period effect to the posterior corpus callosum, using fractional anisotropy from tractography — a microstructural and tract-specific measure. Our 11 features are by contrast network-level summaries of the whole-brain graph after thresholding. Two interpretations are plausible:

- **Wrong spatial scale.** A localized FA difference in a specific commissural tract may not change network-level topology metrics like small-worldness or modularity. The signal could be there at the tract level and invisible at the global level.
- **Wrong tissue.** Sequence memory depends critically on hippocampal–prefrontal circuitry. Gray-matter volume in MTL or functional connectivity between MTL and FPN may be a more direct substrate than aggregate structural-connectome topology.

Either way, the appropriate next experiment is not a larger-N replication of the same pipeline; it is a redesign with tract-specific microstructural metrics (FA, RD) in tracts of interest, or with hippocampal/MTL volumetry, applied to the same HCP-D sample.

### 5.3 Connection to the lifespan turning-points framework

The single nominally-significant Brain → PSM signal — small-worldness, β = +0.13 — is not arbitrary. Mousley et al. (2025) reported that small-worldness has the largest LASSO coefficient for predicting age in the 9–32 lifespan epoch, the epoch that contains the entire HCP-D age range. That our only behavioral hit is in the same metric the lifespan paper flags as the dominant developmental axis in this age window is at least consistent with the idea that PSM-relevant connectome reorganization in this epoch operates partly through small-worldness. This is a hypothesis the present study cannot resolve — it survives as a finding to follow up.

### 5.4 Limitations

- **Power.** Trained-only n = 183. The primary M3 onset coefficient sits at p = 0.07, in the uncomfortable zone where adding 50–100 participants would likely settle the question one way or the other.
- **Onset coverage.** Only ≈ 22% of trained participants started before age 7. The classical Steele-style contrast is underpowered by sample composition, not by sample size.
- **Unmeasured confounders.** No socioeconomic-status or family-income covariate was available in the analysis sample, so the skeptical scenario cannot be fully addressed.
- **Self-report.** Music history is retrospective parental/self-report, and cumulative hours is estimated from coarse multiplicative units that compound measurement noise.
- **Cross-sectional.** Causal direction cannot be separated — "better brain → earlier start" remains formally indistinguishable from "earlier start → better brain."
- **Macroscale features only.** We did not test tract-specific FA/RD, gray-matter volume, or functional connectivity, any of which could carry the trace that macroscale topology does not.

---

## 6. Conclusion

This project asked whether the timing of musical onset leaves a detectable trace in episodic memory and in the macroscale white-matter connectome. Using a pre-registered three-scenario framework, I found:

- **Behavior:** a textbook suppressor pattern in which onset's partial effect on PSM grows from |β| = 0.09 to |β| = 0.21 when cumulative hours is controlled, and is larger in magnitude than hours' partial effect (p = 0.073, n = 183). This pattern is the signature predicted by the sensitive-period scenario.
- **Brain:** only small-worldness predicts PSM at the nominal level (raw p = 0.019, FDR n.s.), and it is the same metric that lifespan work (Mousley et al., 2025) identifies as the strongest age predictor for the 9–32 epoch our sample sits in.
- **Mediation:** no macroscale topology feature carries the onset → PSM signal. All 11 indirect-effect 95% CIs include zero.

The honest summary is that the data lean toward the sensitive-period scenario in behavior, but the trace, if real, is not in macroscale white-matter topology. The most productive next step is to redirect the search toward tract-specific microstructure and toward MTL gray-matter and functional measures — exactly the substrates where the original sensitive-period and episodic-memory literatures locate the relevant biology.

---

## 7. References

Bigand, E., & Tillmann, B. (2022). Near and far transfer: Is music special? *Memory & Cognition, 50*(2), 339–347.

Mousley, A., Bethlehem, R. A. I., Yeh, F.-C., & Astle, D. E. (2025). Topological turning points across the human lifespan. *Nature Communications, 16*, 10055.

Sala, G., & Gobet, F. (2017). When the music's over: Does music skill transfer to children's and young adolescents' cognitive and academic skills? A meta-analysis. *Educational Research Review, 20*, 55–67.

Schellenberg, E. G. (2020). Correlation = causation? Music training, psychology, and neuroscience. *Psychology of Aesthetics, Creativity, and the Arts, 14*(4), 475–480.

Steele, C. J., Bailey, J. A., Zatorre, R. J., & Penhune, V. B. (2013). Early musical training and white-matter plasticity in the corpus callosum: Evidence for a sensitive period. *Journal of Neuroscience, 33*(3), 1282–1290.

---

## Appendix · Data and Code Availability

All analysis code, including the 11-step pipeline (Steps 1–7 confirmatory; Steps 8–10 exploratory; Step 11 figures and summary), is available at the project repository: github.com/ashleysys04-blip/music_connectome_pipeline. HCP-D imaging and behavioral data are accessed under the NDA Data Use Certification and are not redistributed.
