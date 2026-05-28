/**
 * BCS499 Final Report (Word docx)
 * "Does music's sensitive period leave a trace in episodic memory's white matter?"
 * 서예슬 20230340
 *
 * Target length: ~10 pages including figures.
 * Style: US Letter, Arial body 11pt, single column.
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  AlignmentType, PageOrientation, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, TabStopType, TabStopPosition,
  PageNumber, Footer, Header,
} = require("docx");

const FIG_DIR = path.resolve("./figures");

// ---------- style helpers ----------
const FONT = "Arial";
const HEAD_FONT = "Arial";

function P(text, opts = {}) {
  const runOpts = { font: FONT, size: opts.size || 22, ...opts.run };
  return new Paragraph({
    spacing: { before: 0, after: opts.after !== undefined ? opts.after : 120, line: 300 },
    alignment: opts.align || AlignmentType.JUSTIFIED,
    children: Array.isArray(text)
      ? text.map(t => (t instanceof TextRun ? t : new TextRun({ text: t, ...runOpts })))
      : [new TextRun({ text, ...runOpts })],
  });
}

function H1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 320, after: 160 },
    children: [new TextRun({ text, font: HEAD_FONT, bold: true, size: 28, color: "1E3A5F" })],
  });
}

function H2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, font: HEAD_FONT, bold: true, size: 24, color: "1E3A5F" })],
  });
}

function H3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 180, after: 90 },
    children: [new TextRun({ text, font: HEAD_FONT, bold: true, italics: true, size: 22, color: "2C7A7B" })],
  });
}

// Body paragraph with mixed runs
function bodyMixed(runs, opts = {}) {
  return new Paragraph({
    spacing: { before: 0, after: opts.after !== undefined ? opts.after : 120, line: 300 },
    alignment: opts.align || AlignmentType.JUSTIFIED,
    children: runs.map(r =>
      typeof r === "string"
        ? new TextRun({ text: r, font: FONT, size: 22 })
        : new TextRun({ text: r.t, font: FONT, size: 22, bold: r.b, italics: r.i, color: r.c })
    ),
  });
}

function bullet(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "bullets", level },
    spacing: { before: 60, after: 60, line: 280 },
    children: Array.isArray(text)
      ? text.map(t => typeof t === "string"
          ? new TextRun({ text: t, font: FONT, size: 22 })
          : new TextRun({ text: t.t, font: FONT, size: 22, bold: t.b, italics: t.i, color: t.c }))
      : [new TextRun({ text, font: FONT, size: 22 })],
  });
}

function caption(text) {
  return new Paragraph({
    spacing: { before: 60, after: 200 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text, font: FONT, size: 18, italics: true, color: "6B7280" })],
  });
}

function imageParagraph(filePath, widthPx, heightPx) {
  const buf = fs.readFileSync(filePath);
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60 },
    children: [
      new ImageRun({
        data: buf,
        transformation: { width: widthPx, height: heightPx },
        type: "png",
      }),
    ],
  });
}

// Equation-as-text helper (no real eqn editor; keep readable)
function eqn(text) {
  return new Paragraph({
    spacing: { before: 80, after: 120 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text, font: "Consolas", size: 22, italics: false })],
  });
}

// Small table for M3 results
function resultsTable() {
  const border = { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const headFill = "1E3A5F";

  function cell(text, opts = {}) {
    return new TableCell({
      borders,
      width: { size: opts.w, type: WidthType.DXA },
      shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({
        alignment: opts.align || AlignmentType.LEFT,
        spacing: { before: 0, after: 0 },
        children: [new TextRun({
          text, font: FONT, size: 20, bold: opts.bold, italics: opts.italic,
          color: opts.color || (opts.fill ? "FFFFFF" : "1F2937"),
        })],
      })],
    });
  }

  // Total width 9360, columns: 2400 / 1700 / 1700 / 1700 / 1860
  const ws = [2400, 1700, 1700, 1700, 1860];

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: ws,
    rows: [
      new TableRow({ children: [
        cell("Model", { w: ws[0], bold: true, fill: headFill, color: "FFFFFF" }),
        cell("Predictor", { w: ws[1], bold: true, fill: headFill, color: "FFFFFF" }),
        cell("β (std.)", { w: ws[2], bold: true, fill: headFill, color: "FFFFFF", align: AlignmentType.CENTER }),
        cell("SE", { w: ws[3], bold: true, fill: headFill, color: "FFFFFF", align: AlignmentType.CENTER }),
        cell("p", { w: ws[4], bold: true, fill: headFill, color: "FFFFFF", align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M1: onset only", { w: ws[0] }),
        cell("music_onset_age", { w: ws[1] }),
        cell("−0.092", { w: ws[2], align: AlignmentType.CENTER }),
        cell("0.088", { w: ws[3], align: AlignmentType.CENTER }),
        cell("0.300", { w: ws[4], align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M2: hours only", { w: ws[0] }),
        cell("log_cumulative_hours", { w: ws[1] }),
        cell("−0.039", { w: ws[2], align: AlignmentType.CENTER }),
        cell("0.080", { w: ws[3], align: AlignmentType.CENTER }),
        cell("0.629", { w: ws[4], align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M3: both (primary)", { w: ws[0], bold: true, fill: "FDECE6", color: "1F2937" }),
        cell("music_onset_age", { w: ws[1], fill: "FDECE6", color: "1F2937" }),
        cell("−0.207", { w: ws[2], bold: true, color: "E07A5F", fill: "FDECE6", align: AlignmentType.CENTER }),
        cell("0.115", { w: ws[3], fill: "FDECE6", color: "1F2937", align: AlignmentType.CENTER }),
        cell("0.073", { w: ws[4], bold: true, color: "E07A5F", fill: "FDECE6", align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M3: both (primary)", { w: ws[0], bold: true, fill: "FDECE6", color: "1F2937" }),
        cell("log_cumulative_hours", { w: ws[1], fill: "FDECE6", color: "1F2937" }),
        cell("−0.158", { w: ws[2], fill: "FDECE6", color: "1F2937", align: AlignmentType.CENTER }),
        cell("0.104", { w: ws[3], fill: "FDECE6", color: "1F2937", align: AlignmentType.CENTER }),
        cell("0.129", { w: ws[4], fill: "FDECE6", color: "1F2937", align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M4: interaction", { w: ws[0] }),
        cell("music_onset_age", { w: ws[1] }),
        cell("−0.215", { w: ws[2], align: AlignmentType.CENTER }),
        cell("0.118", { w: ws[3], align: AlignmentType.CENTER }),
        cell("0.070", { w: ws[4], align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M4: interaction", { w: ws[0] }),
        cell("log_cumulative_hours", { w: ws[1] }),
        cell("−0.160", { w: ws[2], align: AlignmentType.CENTER }),
        cell("0.104", { w: ws[3], align: AlignmentType.CENTER }),
        cell("0.126", { w: ws[4], align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M4: interaction", { w: ws[0] }),
        cell("onset × hours", { w: ws[1] }),
        cell("+0.030", { w: ws[2], align: AlignmentType.CENTER }),
        cell("0.091", { w: ws[3], align: AlignmentType.CENTER }),
        cell("0.742", { w: ws[4], align: AlignmentType.CENTER }),
      ]}),
    ],
  });
}

// ---------- build document ----------
const children = [];

// Title block
children.push(new Paragraph({
  alignment: AlignmentType.LEFT,
  spacing: { before: 0, after: 60 },
  children: [new TextRun({
    text: "BCS499  ·  Brain & Cognitive Sciences  ·  Final Report",
    font: FONT, size: 18, color: "6B7280", bold: false,
  })],
}));
children.push(new Paragraph({
  spacing: { before: 60, after: 60 },
  children: [new TextRun({
    text: "Does music's sensitive period leave a trace in episodic memory's white matter?",
    font: HEAD_FONT, bold: true, size: 32, color: "1E3A5F",
  })],
}));
children.push(new Paragraph({
  spacing: { before: 0, after: 60 },
  children: [new TextRun({
    text: "A graph-theoretic test of the chicken-and-egg problem using HCP-D",
    font: HEAD_FONT, italics: true, size: 22, color: "2C7A7B",
  })],
}));
children.push(new Paragraph({
  spacing: { before: 100, after: 200 },
  children: [
    new TextRun({ text: "서예슬  ", font: FONT, bold: true, size: 22 }),
    new TextRun({ text: "20230340 · ", font: FONT, size: 22, color: "6B7280" }),
    new TextRun({ text: "Brain & Cognitive Sciences, KAIST · ", font: FONT, size: 22, color: "6B7280" }),
    new TextRun({ text: "May 28, 2026", font: FONT, size: 22, color: "6B7280" }),
  ],
}));

// --- Abstract ---
children.push(H1("Abstract"));
children.push(bodyMixed([
  { t: "Early music training is widely believed to enhance children's cognitive development, but the underlying causal story remains contested. Three competing explanations have shaped the literature: a " },
  { t: "sensitive-period", i: true },
  " account (when training starts matters), a ",
  { t: "dose-response", i: true },
  " account (how much one trains matters), and a ",
  { t: "skeptical", i: true },
  " account (apparent effects reduce to confounding). I used HCP-D data (N = 448 with usable structural connectomes; trained-only n ≈ 183) to test these scenarios on episodic memory, operationalized via the Picture Sequence Memory (PSM) task. Music onset age and cumulative log-hours of training were entered into a single multiple regression (M3) so their partial effects could be compared on a common scale. Across 11 graph-theoretic features of the white-matter connectome (global efficiency, modularity, small-worldness, characteristic path length, and within/between-network strength for DMN, FPN, and MTL), only small-worldness reached nominal significance with PSM (β = +0.13, raw p = 0.019; FDR n.s.). The music-side results showed a textbook ",
  { t: "suppressor pattern", b: true },
  ": onset's partial coefficient grew from β = −0.092 in M1 to β = −0.207 in M3 once cumulative hours was controlled, while hours' partial effect remained smaller in magnitude (β = −0.158). Bootstrap mediation across all 11 brain features yielded no indirect effects (all 95% CIs included zero). Together, the data lean toward the sensitive-period scenario in direction and effect-size ordering, but neither β reached p < 0.05, and the absence of mediation implies that — if a sensitive-period effect exists in HCP-D — it does not travel through macroscale white-matter topology.",
]));

// --- 1. Background ---
children.push(H1("1. Background and Significance"));

children.push(bodyMixed([
  "My motivation for this project began with a common parental intuition: that early musical exposure makes children smarter. Many parents enroll their children in piano lessons before elementary school, hoping the experience will sharpen the brain. The popular literature reinforces this idea, but the empirical literature does not speak with one voice. Whether music training causally improves general cognition has been debated for decades, and the debate has the structure of a chicken-and-egg problem.",
]));

children.push(bodyMixed([
  "Three positions occupy this debate. ",
  { t: "First, ", b: true },
  "the ",
  { t: "sensitive-period view", b: true },
  " holds that the timing of training matters — that the developing brain has a window during which musical experience can sculpt neural circuitry in ways that mature brains cannot. Steele, Bailey, Zatorre and Penhune (2013) provided the classic evidence: white-matter integrity in the posterior corpus callosum was systematically related to whether musicians began training before or after age seven, even after matching for total hours. ",
  { t: "Second, ", b: true },
  "the ",
  { t: "dose-response view", b: true },
  " holds that the apparent onset effect is really a hours effect: children who start earlier accumulate more total practice by adulthood, and that cumulative dose — not the calendar age at first lesson — is what matters (Schellenberg, 2020). ",
  { t: "Third, ", b: true },
  "the ",
  { t: "skeptical view", b: true },
  " holds that neither variable carries information once one properly controls for the confounding effects of socioeconomic status, family environment, and pre-existing aptitude (Sala & Gobet, 2017).",
]));

children.push(bodyMixed([
  "These three positions cannot be distinguished by simple correlation. Because onset age and cumulative hours are strongly negatively correlated (early starters typically accumulate more hours), the bivariate relationship of either with cognition is ambiguous. The natural arbiter is a multiple regression including both predictors: the ",
  { t: "partial", i: true },
  " coefficients on onset and hours, holding the other constant, directly test which scenario fits the data. This is the analytic strategy this project pre-registered.",
]));

children.push(bodyMixed([
  "Episodic memory is a particularly appropriate behavioral outcome. Music learning is fundamentally sequential — practice consists of encoding ordered temporal patterns, remembering motor sequences, and binding melodic events to contextual cues. The NIH Toolbox Picture Sequence Memory (PSM) task probes this same machinery: participants reproduce ordered sequences of pictured events. Compared with the broad construct of \"intelligence,\" PSM offers a concrete, well-validated, theoretically motivated dependent variable that is available across all HCP-D participants.",
]));

children.push(bodyMixed([
  "The white-matter side of the question is motivated by recent connectome-level work showing that structural network topology is itself developmentally dynamic. Mousley, Bethlehem, Yeh and Astle (2025) reported four major lifespan turning points in white-matter topology (ages 9, 32, 66, and 83) and identified ",
  { t: "small-worldness", b: true },
  " as the strongest LASSO-retained predictor of age in the 9–32 epoch — the very epoch that contains the HCP-D age range. If music's sensitive period writes itself into the connectome, this is the developmental window in which we would expect that trace to be detectable.",
]));

// --- 2. Hypotheses ---
children.push(H1("2. Research Questions and Hypotheses"));

children.push(H2("2.1 Research questions"));
children.push(bullet([
  { t: "RQ1.", b: true }, " Is music onset age associated with PSM performance? Does the association survive controlling for cumulative training hours?",
]));
children.push(bullet([
  { t: "RQ2.", b: true }, " Is music onset age associated with white-matter network organization? If a behavioral effect exists, is it mediated by these network features?",
]));

children.push(H2("2.2 Pre-registered scenarios"));
children.push(P("The chicken-and-egg debate is operationalized as three mutually exclusive predictions for the partial coefficients of M3:"));
children.push(eqn("PSM  ~  β1 · onset_age  +  β2 · log(hours)  +  covariates"));
children.push(bullet([
  { t: "H1a (Sensitive period):", b: true, c: "E07A5F" }, " |β(onset)| > |β(hours)|, with both negative.",
]));
children.push(bullet([
  { t: "H1b (Dose-response):", b: true, c: "2C7A7B" }, " |β(hours)| > |β(onset)|, with hours negative.",
]));
children.push(bullet([
  { t: "H1c (Skeptical):", b: true, c: "6B7280" }, " Both β ≈ 0; nothing survives once confounders are controlled.",
]));

children.push(bodyMixed([
  "Note that under this pre-registration the three scenarios are not resolved by ",
  { t: "p < 0.05", i: true },
  " versus null. Statistical significance is one input; the ",
  { t: "direction and relative magnitude", b: true },
  " of the partial coefficients are equally important, because the syllabus emphasizes that significant results are not required and the project is to be evaluated on hypothesis clarity, pipeline logic, and preliminary conclusions. This framing protects against both overinterpretation of marginal p-values and dismissal of informative effect-size patterns.",
]));

// --- 3. Methods ---
children.push(H1("3. Methods"));

children.push(H2("3.1 Dataset and sample construction"));
children.push(bodyMixed([
  "Data come from the Human Connectome Project — Development (HCP-D), accessed through the NIMH Data Archive. The starting demographic table contained 652 participants. Music variables were merged from the NDA SAIQ instrument (500 participants, 286 ever-trained). Cognitive variables (PSM, Flanker, DCCS, list sorting, pattern comparison) were merged from the corresponding NIH Toolbox files. After requiring a non-missing PSM score, 473 participants remained; 448 of these had usable structural connectivity matrices after quality control (Step 2).",
]));

children.push(H2("3.2 Music variables"));
children.push(bullet([
  { t: "Music onset age", b: true }, " was estimated as the participant's current age minus their reported total years of training. Participants reporting no training were treated as untrained and excluded from the trained-only analyses.",
]));
children.push(bullet([
  { t: "Cumulative hours", b: true }, " was estimated from the reported years × weeks/year × days/week × minutes/session, then log-transformed (log(hours + 1)) to compress the heavy right tail and stabilize variance.",
]));

children.push(H2("3.3 Structural connectomes and graph metrics"));
children.push(bodyMixed([
  "Each participant's 246×246 structural connectivity (SC) matrix was reconstructed by HCP-D using DSI Studio's QSDR pipeline on the Brainnetome atlas. Matrices were thresholded at the top 30% of edges and weight-normalized. Eleven graph-theoretic features were computed using bctpy: ",
  { t: "global efficiency, modularity, mean clustering coefficient, characteristic path length, small-worldness,", i: true },
  " and the average within-network and between-network connection strengths for three Yeo subnetworks (DMN, FPN, MTL): ",
  { t: "DMN_within, FPN_within, MTL_within, DMN_FPN_between, DMN_MTL_between, FPN_MTL_between", i: true },
  ". Step 3 took roughly 3.5 hours of compute on the trained-only subsample.",
]));

children.push(H2("3.4 Statistical models"));
children.push(P("All confirmatory analyses used multiple linear regression with age, sex, log family income, and self-reported race as covariates. Predictors were z-standardized so that β coefficients are directly comparable in magnitude. FDR (Benjamini–Hochberg) was applied within each step (Step 4: 11 features; Step 5: M3 has 2 predictors; Step 6: 22 tests; Step 7: 11 mediators)."));

children.push(bullet([
  { t: "Step 4 — Brain → PSM (n = 306).", b: true }, " Each of 11 graph features was tested as a predictor of PSM, one at a time, with full covariate adjustment.",
]));
children.push(bullet([
  { t: "Step 5 — Music → PSM (trained-only, n ≈ 183).", b: true }, " Four nested models: M1 (onset only), M2 (hours only), M3 (both, the primary model), and M4 (both + onset × hours interaction).",
]));
children.push(bullet([
  { t: "Step 6 — Music → Brain (n = 175).", b: true }, " Each of 11 graph features regressed on onset and on log-hours separately, with covariates.",
]));
children.push(bullet([
  { t: "Step 7 — Mediation (n = 175).", b: true }, " For each of the 11 graph features, the indirect effect (a×b) of onset on PSM via that feature was estimated, and a 95% bootstrap confidence interval (5,000 resamples) was computed.",
]));

// --- 4. Results ---
children.push(H1("4. Results"));

children.push(H2("4.1 Sample description"));
children.push(P("The trained subsample (n = 201 with complete music variables) has an onset age distribution heavily concentrated between 8 and 11 years (Fig. 1). Only ~40 participants (≈20%) started before age 7. This distribution shapes the interpretive boundary of the project: we are testing \"relatively earlier vs. later\" onset within a typical-population sample, not the classical pre-7 versus post-7 sensitive-period contrast that motivated Steele et al. (2013)."));
children.push(imageParagraph(path.join(FIG_DIR, "fig1_onset_distribution.png"), 420, 280));
children.push(caption("Figure 1. Distribution of estimated music onset age in the trained subsample (n = 201)."));

children.push(H2("4.2 Brain → PSM (Step 4)"));
children.push(bodyMixed([
  "Among the 11 graph features, only ",
  { t: "small-worldness", b: true },
  " showed a nominally significant positive association with PSM (β = +0.130, raw p = 0.019), but this did not survive FDR correction (q = 0.21). All other features had raw p > 0.26 (Fig. 2). The direction of the small-worldness effect — higher small-worldness associated with better PSM — is consistent with the integration–segregation balance literature in adolescence.",
]));
children.push(imageParagraph(path.join(FIG_DIR, "fig3_brain_behavior.png"), 480, 260));
children.push(caption("Figure 2. Standardized regression coefficients for each graph-theoretic feature predicting PSM (Step 4, n = 306). All FDR-corrected q-values exceed 0.21."));

children.push(H2("4.3 Music → PSM and the suppressor pattern (Step 5)"));
children.push(P("The headline result of the project is the comparison of M1, M2, and M3 (Table 1, Fig. 3). In the marginal regressions, neither onset (M1: β = −0.092, p = 0.30) nor hours (M2: β = −0.039, p = 0.63) reached significance. In the joint model M3, however, onset's partial coefficient more than doubled in magnitude to β = −0.207 (p = 0.073), while hours' partial coefficient grew more modestly to β = −0.158 (p = 0.129). The onset × hours interaction in M4 was effectively zero (β = +0.030, p = 0.742), so the suppression effect is additive."));
children.push(P("Table 1. Standardized partial regression coefficients across nested models. Trained-only subsample (n ≈ 183). M3 is the pre-registered primary model."));
children.push(resultsTable());

children.push(imageParagraph(path.join(FIG_DIR, "fig5_suppressor.png"), 540, 330));
children.push(caption("Figure 3. Suppressor pattern across the M1, M2, M3 nested model sequence. Error bars are ± 1 SE. The red curve traces the growth in onset's coefficient from −0.092 (M1, marginal) to −0.207 (M3, partial)."));

children.push(bodyMixed([
  "This pattern is diagnostic. A pure dose-response account would predict that hours' coefficient should be the larger one once both predictors are entered; instead, the relative ordering is the opposite, with |β(onset)| / |β(hours)| ≈ 1.31. The direction of both coefficients is negative, consistent with earlier onset and more hours each predicting better PSM. The interaction's near-zero value rules out the sub-hypothesis that the onset effect depends on having reached some training threshold.",
]));

children.push(P("A small puzzle worth flagging: at the raw, unadjusted level (Fig. 4), the late-onset group has a slightly higher median PSM than the early- or middle-onset groups. This is the suppressor effect made visual — late starters in HCP-D tend to be older, with more developmentally completed PSM scores, and only the joint adjustment in M3 reveals the underlying onset effect."));
children.push(imageParagraph(path.join(FIG_DIR, "fig2_psm_by_group.png"), 440, 290));
children.push(caption("Figure 4. Raw (unadjusted) PSM by music onset group. Note that the late group has a marginally higher median than the early group — a pattern that reverses once cumulative hours and demographic covariates are controlled."));

children.push(H2("4.4 Music → Brain (Step 6)"));
children.push(P("Twenty-two regressions (11 graph features × 2 music predictors) were estimated. None survived FDR correction. The most prominent raw signals were DMN_FPN_between with log-hours (β = +0.13, p = 0.25) and small-worldness with onset (β = −0.13, p = 0.28); both are too weak to interpret individually but their directions are consistent with the broader pattern (more practice → stronger between-network connectivity; later onset → less small-world structure)."));

children.push(H2("4.5 Mediation: Onset → Brain → PSM (Step 7)"));
children.push(P("Across all 11 candidate mediators, the bootstrap 95% confidence intervals for the indirect effect (a × b) included zero (Fig. 5). The largest point estimate was for small-worldness (a×b = −0.016, CI [−0.063, +0.020], p_boot = 0.40), and the direction was consistent with the sensitive-period prediction — but the indirect effect was statistically null. Importantly, the direct effect of onset on PSM (the c-path: β = −0.236) was barely attenuated to c′ ≈ −0.22 in every mediator-specific model, indicating that the onset → PSM signal does not pass through these macroscale white-matter features."));
children.push(imageParagraph(path.join(FIG_DIR, "fig4_mediation.png"), 480, 260));
children.push(caption("Figure 5. Indirect effects of music onset age on PSM through each of 11 candidate white-matter mediators. Whiskers are 95% bootstrap confidence intervals (5,000 resamples). All intervals include zero."));

// --- 5. Discussion ---
children.push(H1("5. Discussion"));

children.push(H2("5.1 Verdict on the three scenarios"));
children.push(bodyMixed([
  "The sensitive-period scenario is the best-fitting of the three pre-registered hypotheses, but only weakly. Two pieces of evidence support it: (i) ",
  { t: "the relative-magnitude pattern", b: true },
  ", |β(onset)| > |β(hours)| in M3 — exactly the prediction made by H1a; and (ii) ",
  { t: "the direction of both coefficients", b: true },
  ", negative as expected. Two pieces of evidence qualify the support: (i) ",
  { t: "neither β reached p < 0.05", b: true },
  ", with the primary onset coefficient sitting in the awkward p ≈ 0.07 zone where neither rejection nor acceptance is justified at conventional thresholds; and (ii) ",
  { t: "the macroscale mediation pathway is empirically absent", b: true },
  " — if the sensitive period is real in this sample, it does not operate through the eleven topology features we measured.",
]));

children.push(bodyMixed([
  "The dose-response scenario is weakly disfavored. After onset is held constant, hours' partial coefficient is smaller in magnitude than onset's. The interaction is null, so it is not the case that high-dose training amplifies an onset effect. The skeptical scenario cannot be confidently rejected: nothing survives FDR, the sample size (n = 183 trained-only) is modest for a five-predictor regression, and an honest report has to leave this possibility on the table.",
]));

children.push(H2("5.2 Why the macroscale connectome may be silent"));
children.push(bodyMixed([
  "The most informative negative result is the mediation null. Steele et al. (2013) localized their sensitive-period effect to the ",
  { t: "posterior corpus callosum", i: true },
  ", using fractional anisotropy from tractography — a microstructural and tract-specific measure. Our 11 features are by contrast network-level summaries of the whole-brain graph after thresholding. Two interpretations are plausible:",
]));
children.push(bullet([
  { t: "Wrong spatial scale.", b: true }, " A localized FA difference in a specific commissural tract may not change network-level topology metrics like small-worldness or modularity. The signal could be there at the tract level and invisible at the global level.",
]));
children.push(bullet([
  { t: "Wrong tissue.", b: true }, " Sequence memory depends critically on hippocampal–prefrontal circuitry. Gray-matter volume in MTL or functional connectivity between MTL and FPN may be a more direct substrate than aggregate structural-connectome topology.",
]));
children.push(bodyMixed([
  "Either way, the appropriate next experiment is not a larger-N replication of the same pipeline; it is a redesign with tract-specific microstructural metrics (FA, RD) in tracts of interest, or with hippocampal/MTL volumetry, applied to the same HCP-D sample.",
]));

children.push(H2("5.3 Connection to the lifespan turning-points framework"));
children.push(bodyMixed([
  "The single nominally-significant Brain → PSM signal — small-worldness, β = +0.13 — is not arbitrary. Mousley et al. (2025) reported that small-worldness has the largest LASSO coefficient for predicting age in the 9–32 lifespan epoch, the epoch that contains the entire HCP-D age range. That our only behavioral hit is in the same metric the lifespan paper flags as the dominant developmental axis in this age window is at least consistent with the idea that PSM-relevant connectome reorganization in this epoch operates partly through small-worldness. This is a hypothesis the present study cannot resolve — it survives as a finding to follow up.",
]));

children.push(H2("5.4 Limitations"));
children.push(bullet([{ t: "Power.", b: true }, " Trained-only n = 183. The primary M3 onset coefficient sits at p = 0.07, in the uncomfortable zone where adding 50–100 participants would likely settle the question one way or the other."]));
children.push(bullet([{ t: "Onset coverage.", b: true }, " Only ≈ 20% of trained participants started before age 7. The classical Steele-style contrast is underpowered by sample composition, not by sample size."]));
children.push(bullet([{ t: "Self-report.", b: true }, " Music history is retrospective parental/self-report, and cumulative hours is estimated from coarse multiplicative units that compound measurement noise."]));
children.push(bullet([{ t: "Cross-sectional.", b: true }, " Causal direction cannot be separated — \"better brain → earlier start\" remains formally indistinguishable from \"earlier start → better brain\"."]));
children.push(bullet([{ t: "Macroscale features only.", b: true }, " We did not test tract-specific FA/RD, gray-matter volume, or functional connectivity, any of which could carry the trace that macroscale topology does not."]));

// --- 6. Conclusion ---
children.push(H1("6. Conclusion"));
children.push(bodyMixed([
  "This project asked whether the timing of musical onset leaves a detectable trace in episodic memory and in the macroscale white-matter connectome. Using a pre-registered three-scenario framework, I found:",
]));
children.push(bullet([
  { t: "Behavior:", b: true }, " a textbook suppressor pattern in which onset's partial effect on PSM grows from |β| = 0.09 to |β| = 0.21 when cumulative hours is controlled, and is larger in magnitude than hours' partial effect (p = 0.073, n = 183). This pattern is the signature predicted by the sensitive-period scenario.",
]));
children.push(bullet([
  { t: "Brain:", b: true }, " only small-worldness predicts PSM at the nominal level (raw p = 0.019, FDR n.s.), and it is the same metric that lifespan work (Mousley et al., 2025) identifies as the strongest age predictor for the 9–32 epoch our sample sits in.",
]));
children.push(bullet([
  { t: "Mediation:", b: true }, " no macroscale topology feature carries the onset → PSM signal. All 11 indirect-effect 95% CIs include zero.",
]));
children.push(bodyMixed([
  "The honest summary is that the data ",
  { t: "lean toward the sensitive-period scenario in behavior", b: true },
  ", but ",
  { t: "the trace, if real, is not in macroscale white-matter topology", b: true },
  ". The most productive next step is to redirect the search toward tract-specific microstructure and toward MTL gray-matter and functional measures — exactly the substrates where the original sensitive-period and episodic-memory literatures locate the relevant biology.",
]));

// --- 7. References ---
children.push(H1("7. References"));
const refs = [
  "Bigand, E., & Tillmann, B. (2022). Near and far transfer: Is music special? Memory & Cognition, 50(2), 339–347.",
  "Mousley, A., Bethlehem, R. A. I., Yeh, F.-C., & Astle, D. E. (2025). Topological turning points across the human lifespan. Nature Communications, 16, 10055.",
  "Sala, G., & Gobet, F. (2017). When the music's over: Does music skill transfer to children's and young adolescents' cognitive and academic skills? A meta-analysis. Educational Research Review, 20, 55–67.",
  "Schellenberg, E. G. (2020). Correlation = causation? Music training, psychology, and neuroscience. Psychology of Aesthetics, Creativity, and the Arts, 14(4), 475–480.",
  "Steele, C. J., Bailey, J. A., Zatorre, R. J., & Penhune, V. B. (2013). Early musical training and white-matter plasticity in the corpus callosum: Evidence for a sensitive period. Journal of Neuroscience, 33(3), 1282–1290.",
];
refs.forEach(r => children.push(new Paragraph({
  spacing: { before: 80, after: 80, line: 280 },
  indent: { left: 360, hanging: 360 },
  children: [new TextRun({ text: r, font: FONT, size: 20 })],
})));

// --- Appendix: data & code ---
children.push(H1("Appendix · Data and Code Availability"));
children.push(bodyMixed([
  "All analysis code, including the 11-step pipeline (Steps 1–7 confirmatory; Steps 8–10 exploratory; Step 11 figures and summary), is available at the project repository: ",
  { t: "github.com/ashleysys04-blip/music_connectome_pipeline", c: "2C7A7B" },
  ". HCP-D imaging and behavioral data are accessed under the NDA Data Use Certification and are not redistributed.",
]));

// ---------- write doc ----------
const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: HEAD_FONT, color: "1E3A5F" },
        paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: HEAD_FONT, color: "1E3A5F" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, italics: true, font: HEAD_FONT, color: "2C7A7B" },
        paragraph: { spacing: { before: 180, after: 90 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1080, hanging: 360 } } } },
        ] },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [
            new TextRun({ text: "서예슬 20230340  ·  BCS499  ·  ", font: FONT, size: 18, color: "6B7280" }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: "6B7280" }),
            new TextRun({ text: " / ", font: FONT, size: 18, color: "6B7280" }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 18, color: "6B7280" }),
          ],
        })],
      }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
    fs.writeFileSync("BCS499_final_report.docx", buf);
    console.log("saved → BCS499_final_report.docx");    
});