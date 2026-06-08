## Slide 1. Variables by Role

### Outcome Variables — what music is expected to influence

#### `psm_score`

Primary outcome for H1.

Used in:

* Step 4: Brain → PSM
* Step 5: Music → PSM models M1–M4
* Step 7: Mediation analysis

#### `flanker`, `dccs`, `lswmt`, `pcps`

Secondary cognitive outcomes used in Step 5.

These variables test whether the music-training effect is specific to episodic memory or extends to other cognitive domains, distinguishing near transfer from general transfer.

---

### Covariates — confounds that must be controlled

#### `age_years`, `sex_code`

Basic demographic covariates.

#### `wisc_mr`

Fluid reasoning covariate.

This variable is included only in the covariate list, not as an outcome.

It directly addresses the skeptical view that apparent music-training effects may simply reflect pre-existing differences in general intelligence.

If onset age or cumulative hours still predict PSM after controlling for WISC-MR, the result provides evidence against this skeptical interpretation.

---

### Predictors — derived from `saiq01`

#### `music_onset_age`

Tests the sensitive-period hypothesis.

#### `log_cumulative_hours`

Tests the dose-response hypothesis.

In M3, both predictors are included simultaneously, allowing a direct comparison of their partial regression coefficients.

This is the key model for the timing vs. training amount question.

---

## Slide 2. Measurement Files and Their Pipeline Roles

| File             | What it measures                      | Variable                                          | Pipeline role                                                    |
| ---------------- | ------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------- |
| `ndar_subject01` | Demographics                          | `age`, `sex`                                      | Base sample + `age_years` / `sex_code` covariates                |
| `saiq01`         | Music-training history                | `years`, `months`, `days/week`, `minutes/session` | Predictor derivation → `music_onset_age`, `log_cumulative_hours` |
| `psm01`          | Episodic memory                       | `psm_score`                                       | Primary outcome — sample cut + Steps 4/5/7                       |
| `flanker01`      | Inhibitory control / attention        | `flanker`                                         | Secondary outcome in Step 5                                      |
| `dccs01`         | Cognitive flexibility / set-shifting  | `dccs`                                            | Secondary outcome in Step 5                                      |
| `lswmt01`        | Working memory / List Sorting         | `lswmt`                                           | Secondary outcome in Step 5                                      |
| `pcps01`         | Processing speed / Pattern Comparison | `pcps`                                            | Secondary outcome in Step 5                                      |
| `wisc_v01`       | Fluid reasoning / nonverbal reasoning | `wisc_mr`                                         | Covariate only — controls for general intelligence               |
