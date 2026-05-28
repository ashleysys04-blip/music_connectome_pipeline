/**
 * BCS499 Final Report — KOREAN version
 * 한국어 본문 + 통계/뇌영상 용어 영어 병기
 * 서예슬 20230340
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType,
  PageNumber, Footer,
} = require("docx");

const FIG_DIR = path.resolve("./figures");

const FONT = "Malgun Gothic";   // Korean body font
const HEAD_FONT = "Malgun Gothic";

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

function bodyMixed(runs, opts = {}) {
  return new Paragraph({
    spacing: { before: 0, after: opts.after !== undefined ? opts.after : 120, line: 320 },
    alignment: opts.align || AlignmentType.JUSTIFIED,
    children: runs.map(r =>
      typeof r === "string"
        ? new TextRun({ text: r, font: FONT, size: 22 })
        : new TextRun({ text: r.t, font: FONT, size: 22, bold: r.b, italics: r.i, color: r.c })
    ),
  });
}
function P(text, opts = {}) {
  return bodyMixed([text], opts);
}
function bullet(runs, level = 0) {
  return new Paragraph({
    numbering: { reference: "bullets", level },
    spacing: { before: 60, after: 60, line: 300 },
    children: (Array.isArray(runs) ? runs : [runs]).map(r =>
      typeof r === "string"
        ? new TextRun({ text: r, font: FONT, size: 22 })
        : new TextRun({ text: r.t, font: FONT, size: 22, bold: r.b, italics: r.i, color: r.c })),
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
    children: [new ImageRun({ data: buf, transformation: { width: widthPx, height: heightPx }, type: "png" })],
  });
}
function eqn(text) {
  return new Paragraph({
    spacing: { before: 80, after: 120 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text, font: "Consolas", size: 22 })],
  });
}

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
        children: [new TextRun({ text, font: FONT, size: 20, bold: opts.bold, italics: opts.italic, color: opts.color || "1F2937" })],
      })],
    });
  }
  const ws = [2400, 1700, 1700, 1700, 1860];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: ws,
    rows: [
      new TableRow({ children: [
        cell("모델 Model", { w: ws[0], bold: true, fill: headFill, color: "FFFFFF" }),
        cell("예측변수 Predictor", { w: ws[1], bold: true, fill: headFill, color: "FFFFFF" }),
        cell("β (표준화)", { w: ws[2], bold: true, fill: headFill, color: "FFFFFF", align: AlignmentType.CENTER }),
        cell("SE", { w: ws[3], bold: true, fill: headFill, color: "FFFFFF", align: AlignmentType.CENTER }),
        cell("p", { w: ws[4], bold: true, fill: headFill, color: "FFFFFF", align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M1: onset만", { w: ws[0] }),
        cell("music_onset_age", { w: ws[1] }),
        cell("−0.092", { w: ws[2], align: AlignmentType.CENTER }),
        cell("0.088", { w: ws[3], align: AlignmentType.CENTER }),
        cell("0.300", { w: ws[4], align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M2: hours만", { w: ws[0] }),
        cell("log_cumulative_hours", { w: ws[1] }),
        cell("−0.039", { w: ws[2], align: AlignmentType.CENTER }),
        cell("0.080", { w: ws[3], align: AlignmentType.CENTER }),
        cell("0.629", { w: ws[4], align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M3: 둘다 (주모델)", { w: ws[0], bold: true, fill: "FDECE6", color: "1F2937" }),
        cell("music_onset_age", { w: ws[1], fill: "FDECE6", color: "1F2937" }),
        cell("−0.207", { w: ws[2], bold: true, color: "E07A5F", fill: "FDECE6", align: AlignmentType.CENTER }),
        cell("0.115", { w: ws[3], fill: "FDECE6", color: "1F2937", align: AlignmentType.CENTER }),
        cell("0.073", { w: ws[4], bold: true, color: "E07A5F", fill: "FDECE6", align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M3: 둘다 (주모델)", { w: ws[0], bold: true, fill: "FDECE6", color: "1F2937" }),
        cell("log_cumulative_hours", { w: ws[1], fill: "FDECE6", color: "1F2937" }),
        cell("−0.158", { w: ws[2], fill: "FDECE6", color: "1F2937", align: AlignmentType.CENTER }),
        cell("0.104", { w: ws[3], fill: "FDECE6", color: "1F2937", align: AlignmentType.CENTER }),
        cell("0.129", { w: ws[4], fill: "FDECE6", color: "1F2937", align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M4: 상호작용", { w: ws[0] }),
        cell("music_onset_age", { w: ws[1] }),
        cell("−0.215", { w: ws[2], align: AlignmentType.CENTER }),
        cell("0.118", { w: ws[3], align: AlignmentType.CENTER }),
        cell("0.070", { w: ws[4], align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M4: 상호작용", { w: ws[0] }),
        cell("log_cumulative_hours", { w: ws[1] }),
        cell("−0.160", { w: ws[2], align: AlignmentType.CENTER }),
        cell("0.104", { w: ws[3], align: AlignmentType.CENTER }),
        cell("0.126", { w: ws[4], align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("M4: 상호작용", { w: ws[0] }),
        cell("onset × hours", { w: ws[1] }),
        cell("+0.030", { w: ws[2], align: AlignmentType.CENTER }),
        cell("0.091", { w: ws[3], align: AlignmentType.CENTER }),
        cell("0.742", { w: ws[4], align: AlignmentType.CENTER }),
      ]}),
    ],
  });
}

const children = [];

// Title block
children.push(new Paragraph({
  spacing: { before: 0, after: 60 },
  children: [new TextRun({ text: "BCS499  ·  뇌인지과학 특강  ·  최종 보고서", font: FONT, size: 18, color: "6B7280" })],
}));
children.push(new Paragraph({
  spacing: { before: 60, after: 60 },
  children: [new TextRun({ text: "음악의 민감기는 일화기억의 백질에 흔적을 남기는가?", font: HEAD_FONT, bold: true, size: 30, color: "1E3A5F" })],
}));
children.push(new Paragraph({
  spacing: { before: 0, after: 60 },
  children: [new TextRun({ text: "HCP-D를 이용한 닭/달걀 문제(chicken-and-egg problem)의 그래프 이론적 검정", font: HEAD_FONT, italics: true, size: 22, color: "2C7A7B" })],
}));
children.push(new Paragraph({
  spacing: { before: 100, after: 200 },
  children: [
    new TextRun({ text: "서예슬  ", font: FONT, bold: true, size: 22 }),
    new TextRun({ text: "20230340 · 뇌인지과학과, KAIST · 2026년 5월 28일", font: FONT, size: 22, color: "6B7280" }),
  ],
}));

// Abstract
children.push(H1("초록 (Abstract)"));
children.push(bodyMixed([
  "조기 음악 훈련이 아동의 인지 발달을 돕는다는 믿음은 널리 퍼져 있으나, 그 인과적 메커니즘은 여전히 논쟁적이다. 기존 문헌은 세 가지 경쟁 가설로 정리된다: ",
  { t: "민감기(sensitive-period)", i: true }, " 가설(언제 시작했는지가 중요), ",
  { t: "용량-반응(dose-response)", i: true }, " 가설(얼마나 훈련했는지가 중요), 그리고 ",
  { t: "회의적(skeptical)", i: true }, " 입장(겉보기 효과는 교란변수로 환원됨). 본 연구는 HCP-D 데이터(구조적 커넥톰 사용 가능 N = 448, 훈련자 한정 trained-only n ≈ 183)를 사용해, 일화기억(episodic memory)을 Picture Sequence Memory(PSM) 과제로 조작화하여 세 시나리오를 검정하였다. 음악 시작 연령(music onset age)과 누적 훈련 시간의 로그값(log cumulative hours)을 하나의 다중 회귀(M3)에 함께 투입해 두 변수의 부분 효과(partial effect)를 동일 척도에서 비교하였다. 백질 커넥톰의 11개 그래프 지표(global efficiency, modularity, small-worldness, characteristic path length, DMN·FPN·MTL의 within/between 강도) 중 PSM과 명목적(nominal) 유의성에 도달한 것은 small-worldness 뿐이었다(β = +0.13, raw p = 0.019; FDR 보정 후 비유의). 음악 측 결과는 전형적인 ",
  { t: "억제 효과(suppressor pattern)", b: true },
  "를 보였다: onset의 부분 계수는 M1에서 β = −0.092였으나, 누적 시간을 통제한 M3에서 β = −0.207로 두 배 이상 커졌고, hours의 부분 효과는 더 작게 유지되었다(β = −0.158). 11개 뇌 지표 전체에 대한 부트스트랩 매개분석(bootstrap mediation)에서 간접효과는 모두 0을 포함하였다(모든 95% CI가 0 포함). 종합하면, 데이터는 방향과 효과크기 순서에서 민감기 시나리오 쪽으로 기울지만, 두 β 모두 p < 0.05에 이르지 못했고, 매개효과의 부재는 — 만약 민감기 효과가 HCP-D에 존재한다면 — 그것이 거시적(macroscale) 백질 위상(topology)을 경유하지 않음을 시사한다.",
]));

// 1. Background
children.push(H1("1. 연구 배경 및 의의"));
children.push(bodyMixed([
  "이 프로젝트의 동기는 흔한 부모의 직관에서 출발했다 — 조기 음악 노출이 아이를 더 똑똑하게 만든다는 믿음이다. 많은 부모가 초등학교 입학 전부터 자녀에게 피아노를 가르치며, 그 경험이 뇌에 유익하리라 기대한다. 대중적 통념은 이를 강화하지만, 실증 문헌의 결론은 한목소리가 아니다. 음악 훈련이 일반 인지를 인과적으로 향상시키는지는 수십 년간 논쟁되어 왔으며, 그 논쟁은 닭/달걀 문제(chicken-and-egg problem)의 구조를 띤다.",
]));
children.push(bodyMixed([
  "이 논쟁에는 세 입장이 있다. ", { t: "첫째, ", b: true }, { t: "민감기 가설(sensitive-period view)", b: true },
  "은 훈련의 ", { t: "시점", i: true }, "이 중요하다고 본다 — 발달하는 뇌에는 음악 경험이 신경 회로를 조형(sculpt)할 수 있는 창(window)이 있으며, 성숙한 뇌는 이를 할 수 없다는 것이다. Steele, Bailey, Zatorre & Penhune(2013)은 고전적 증거를 제시했다: 후방 뇌량(posterior corpus callosum)의 백질 무결성(integrity)이, 총 훈련 시간을 맞춘 뒤에도, 7세 이전 시작 여부와 체계적으로 관련되었다. ",
  { t: "둘째, ", b: true }, { t: "용량-반응 가설(dose-response view)", b: true },
  "은 겉보기 onset 효과가 사실은 시간(hours) 효과라고 본다: 일찍 시작한 아이는 성인이 될 때까지 더 많은 총 연습량을 축적하므로, 첫 레슨의 달력 나이가 아니라 누적 용량(dose)이 중요하다는 것이다(Schellenberg, 2020). ",
  { t: "셋째, ", b: true }, { t: "회의적 입장(skeptical view)", b: true },
  "은 사회경제적 지위(SES), 가정 환경, 선천적 적성 같은 교란을 적절히 통제하면 두 변수 모두 정보를 담지 않는다고 본다(Sala & Gobet, 2017).",
]));
children.push(bodyMixed([
  "이 세 입장은 단순 상관으로는 구분되지 않는다. onset과 누적 시간은 강한 음의 상관(일찍 시작할수록 누적 시간이 많음)을 가지므로, 둘 중 하나와 인지의 이변량 관계는 모호하다. 자연스러운 판별자는 두 예측변수를 모두 포함한 다중 회귀(multiple regression)다: 다른 변수를 통제한 onset과 hours의 ",
  { t: "부분(partial)", i: true },
  " 계수가 어느 시나리오에 부합하는지를 직접 검정한다. 이것이 본 프로젝트가 사전 등록(pre-register)한 분석 전략이다.",
]));
children.push(bodyMixed([
  "일화기억은 특히 적절한 행동 결과변수다. 음악 학습은 본질적으로 순차적(sequential)이다 — 연습은 시간에 걸친 패턴을 부호화하고, 운동 시퀀스를 기억하며, 선율 사건을 맥락 단서에 결합하는 과정이다. NIH Toolbox의 Picture Sequence Memory(PSM) 과제는 동일한 기제를 측정한다: 참가자는 그림으로 제시된 사건들의 순서를 재현한다. ‘지능’이라는 넓은 구성개념에 비해 PSM은 HCP-D 전 참가자에게 가용한, 구체적이고 검증되었으며 음악과 이론적으로 연결된 종속변수를 제공한다.",
]));
children.push(bodyMixed([
  "백질 측면의 동기는 구조적 네트워크 위상(topology) 자체가 발달적으로 역동적이라는 최근 커넥톰 연구에서 나온다. Mousley, Bethlehem, Yeh & Astle(2025)은 백질 위상에 네 개의 주요 생애 전환점(turning point; 9, 32, 66, 83세)이 있음을 보고하고, 9–32세 구간(epoch)에서 ",
  { t: "small-worldness", b: true },
  "를 나이를 가장 강하게 예측하는 LASSO 지표로 식별했다 — 바로 HCP-D 연령대를 포함하는 구간이다. 음악의 민감기가 커넥톰에 흔적을 남긴다면, 그 흔적이 탐지될 것으로 기대되는 발달 창이 바로 이 시기다.",
]));

// 2. Hypotheses
children.push(H1("2. 연구 질문 및 가설"));
children.push(H2("2.1 연구 질문"));
children.push(bullet([{ t: "RQ1. ", b: true }, "음악 시작 연령은 PSM 수행과 관련되는가? 그 관련성은 누적 훈련 시간을 통제한 뒤에도 유지되는가?"]));
children.push(bullet([{ t: "RQ2. ", b: true }, "음악 시작 연령은 백질 네트워크 조직과 관련되는가? 행동 효과가 존재한다면, 그것이 이 네트워크 지표들에 의해 매개(mediate)되는가?"]));
children.push(H2("2.2 사전 등록한 시나리오"));
children.push(P("닭/달걀 논쟁은 M3의 부분 계수에 대한 세 가지 상호배타적 예측으로 조작화된다:"));
children.push(eqn("PSM  ~  β1 · onset_age  +  β2 · log(hours)  +  공변량"));
children.push(bullet([{ t: "H1a (민감기): ", b: true, c: "E07A5F" }, "|β(onset)| > |β(hours)|, 두 계수 모두 음수."]));
children.push(bullet([{ t: "H1b (용량-반응): ", b: true, c: "2C7A7B" }, "|β(hours)| > |β(onset)|, hours가 음수."]));
children.push(bullet([{ t: "H1c (회의적): ", b: true, c: "6B7280" }, "두 β ≈ 0; 교란 통제 후 어느 것도 살아남지 않음."]));
children.push(bodyMixed([
  "이 사전 등록에서 세 시나리오는 ", { t: "p < 0.05", i: true }, " 대 영가설의 이분법으로 판정되지 않는다. 통계적 유의성은 하나의 입력일 뿐이며, 부분 계수의 ",
  { t: "방향과 상대적 크기", b: true },
  "가 똑같이 중요하다. 강의 평가 기준이 통계적 유의성을 요구하지 않고 가설의 명확성, 파이프라인의 논리성, 예비 결론에 무게를 두기 때문이다. 이 프레임은 한계적 p값의 과대해석과 정보가 담긴 효과크기 패턴의 무시를 모두 방지한다.",
]));

// 3. Methods
children.push(H1("3. 연구 방법"));
children.push(H2("3.1 데이터 및 표본 구성"));
children.push(bodyMixed([
  "데이터는 Human Connectome Project — Development(HCP-D)에서 NIMH Data Archive를 통해 확보하였다. 시작 인구통계 표는 652명이었다. 음악 변수는 NDA SAIQ 도구에서 병합하였다(500명, 훈련 경험자 286명). 인지 변수(PSM, Flanker, DCCS, list sorting, pattern comparison)는 해당 NIH Toolbox 파일에서 병합하였다. PSM 점수 결측이 없는 조건을 적용한 후 473명이 남았고, 이 중 448명이 품질관리(QC, Step 2) 후 사용 가능한 구조적 연결성 행렬을 가졌다.",
]));
children.push(H2("3.2 음악 변수"));
children.push(bullet([{ t: "음악 시작 연령(onset age)", b: true }, "은 참가자의 현재 나이에서 보고된 총 훈련 연수를 빼서 추정하였다. 훈련을 보고하지 않은 참가자는 비훈련자로 처리하여 훈련자 한정 분석에서 제외하였다."]));
children.push(bullet([{ t: "누적 훈련 시간(cumulative hours)", b: true }, "은 보고된 연수 × 연간 주수 × 주당 일수 × 회당 분으로 추정한 뒤 로그 변환(log(hours + 1))하여 우측 꼬리를 압축하고 분산을 안정화하였다."]));
children.push(H2("3.3 구조적 커넥톰 및 그래프 지표"));
children.push(bodyMixed([
  "각 참가자의 246×246 구조적 연결성(SC) 행렬은 HCP-D가 Brainnetome 아틀라스 위에서 DSI Studio의 QSDR 파이프라인으로 재구성하였다. 행렬은 상위 30% 엣지로 임계화(threshold)하고 가중치 정규화하였다. bctpy로 11개 그래프 지표를 계산하였다: ",
  { t: "global efficiency, modularity, mean clustering coefficient, characteristic path length, small-worldness", i: true },
  ", 그리고 세 Yeo 하위망(DMN, FPN, MTL)의 평균 within/between 연결 강도(DMN_within, FPN_within, MTL_within, DMN_FPN_between, DMN_MTL_between, FPN_MTL_between). Step 3은 훈련자 한정 표본에서 약 3.5시간의 연산이 소요되었다.",
]));
children.push(H2("3.4 통계 모형"));
children.push(P("모든 확증적(confirmatory) 분석은 나이, 성별, 로그 가구소득, 자기보고 인종을 공변량으로 하는 다중 선형 회귀를 사용하였다. 예측변수는 z-표준화하여 β 계수의 크기를 직접 비교할 수 있게 하였다. 각 단계 내에서 FDR(Benjamini–Hochberg) 보정을 적용하였다(Step 4: 11지표; Step 5: M3의 예측변수 2개; Step 6: 22검정; Step 7: 11매개변수)."));
children.push(bullet([{ t: "Step 4 — Brain → PSM (n = 306). ", b: true }, "11개 그래프 지표 각각을 PSM의 예측변수로 개별 검정, 공변량 완전 보정."]));
children.push(bullet([{ t: "Step 5 — Music → PSM (훈련자 한정, n ≈ 183). ", b: true }, "네 개의 위계적(nested) 모형: M1(onset만), M2(hours만), M3(둘다, 주모형), M4(둘다 + onset × hours 상호작용)."]));
children.push(bullet([{ t: "Step 6 — Music → Brain (n = 175). ", b: true }, "11개 그래프 지표 각각을 onset과 log-hours에 대해 개별 회귀, 공변량 포함."]));
children.push(bullet([{ t: "Step 7 — 매개분석 (n = 175). ", b: true }, "11개 그래프 지표 각각에 대해, 해당 지표를 경유하는 onset의 PSM에 대한 간접효과(a×b)를 추정하고 95% 부트스트랩 신뢰구간(5,000회 재표집)을 계산."]));

// 4. Results
children.push(H1("4. 결과"));
children.push(H2("4.1 표본 기술"));
children.push(P("음악 변수가 완전한 훈련 하위표본(n = 201)의 onset 연령 분포는 8–11세에 크게 집중되어 있다(그림 1). 7세 이전 시작자는 약 40명(≈20%)에 불과하다. 이 분포는 프로젝트의 해석 경계를 규정한다 — 우리는 일반 인구 표본 내에서 ‘상대적으로 이른 vs. 늦은’ onset을 검정하는 것이지, Steele et al.(2013)을 촉발한 7세 전/후의 고전적 민감기 대비를 검정하는 것이 아니다."));
children.push(imageParagraph(path.join(FIG_DIR, "fig1_onset_distribution.png"), 420, 280));
children.push(caption("그림 1. 훈련 하위표본(n = 201)의 음악 시작 연령 분포."));

children.push(H2("4.2 Brain → PSM (Step 4)"));
children.push(bodyMixed([
  "11개 그래프 지표 중 ", { t: "small-worldness", b: true },
  "만 PSM과 명목적으로 유의한 양의 관련을 보였으나(β = +0.130, raw p = 0.019), FDR 보정은 통과하지 못했다(q = 0.21). 나머지 지표는 모두 raw p > 0.26이었다(그림 2). small-worldness 효과의 방향(높은 small-worldness ↔ 더 나은 PSM)은 청소년기 통합–분리(integration–segregation) 균형 문헌과 일관된다.",
]));
children.push(imageParagraph(path.join(FIG_DIR, "fig3_brain_behavior.png"), 480, 260));
children.push(caption("그림 2. 각 그래프 지표의 PSM 예측 표준화 회귀계수(Step 4, n = 306). 모든 FDR 보정 q값 > 0.21."));

children.push(H2("4.3 Music → PSM 및 억제 효과 (Step 5)"));
children.push(P("본 프로젝트의 핵심 결과는 M1, M2, M3의 비교다(표 1, 그림 3). 주변(marginal) 회귀에서는 onset(M1: β = −0.092, p = 0.30)도 hours(M2: β = −0.039, p = 0.63)도 유의하지 않았다. 그러나 결합 모형 M3에서 onset의 부분 계수는 β = −0.207(p = 0.073)로 크기가 두 배 이상 커졌고, hours의 부분 계수는 β = −0.158(p = 0.129)로 더 완만하게 커졌다. M4의 onset × hours 상호작용은 사실상 0이었으므로(β = +0.030, p = 0.742) 억제 효과는 가산적(additive)이다."));
children.push(P("표 1. 위계 모형 전반의 표준화 부분 회귀계수. 훈련자 한정 표본(n ≈ 183). M3는 사전 등록한 주모형이다."));
children.push(resultsTable());
children.push(imageParagraph(path.join(FIG_DIR, "fig5_suppressor.png"), 540, 330));
children.push(caption("그림 3. M1, M2, M3 위계 모형 순서에 걸친 억제 효과(suppressor pattern). 오차막대는 ± 1 SE. 빨간 곡선은 onset 계수가 −0.092(M1, 주변)에서 −0.207(M3, 부분)로 커지는 과정을 추적한다."));
children.push(bodyMixed([
  "이 패턴은 진단적이다. 순수 용량-반응 설명이라면 두 예측변수 투입 시 hours의 계수가 더 커야 하지만, 실제 순서는 반대로 |β(onset)| / |β(hours)| ≈ 1.31이다. 두 계수의 방향은 음수로, 더 이른 onset과 더 많은 hours가 각각 더 나은 PSM을 예측함과 일관된다. 상호작용이 0에 가깝다는 점은 onset 효과가 어떤 훈련 임계치에 도달해야 작동한다는 하위 가설을 배제한다.",
]));
children.push(P("주목할 작은 역설: 보정하지 않은 원자료 수준(그림 4)에서는 늦은 onset 집단의 PSM 중앙값이 이르거나 중간 집단보다 약간 높다. 이것이 시각화된 억제 효과다 — HCP-D에서 늦은 시작자는 나이가 더 많아 PSM 점수가 발달적으로 더 완성되는 경향이 있으며, M3의 결합 보정만이 기저의 onset 효과를 드러낸다."));
children.push(imageParagraph(path.join(FIG_DIR, "fig2_psm_by_group.png"), 440, 290));
children.push(caption("그림 4. 음악 onset 집단별 원(보정 전) PSM. 늦은 집단의 중앙값이 이른 집단보다 근소하게 높으나, 누적 시간과 인구통계 공변량을 통제하면 이 패턴은 역전된다."));

children.push(H2("4.4 Music → Brain (Step 6)"));
children.push(P("22개 회귀(11 지표 × 2 음악 예측변수)를 추정했으며 FDR 보정을 통과한 것은 없었다. 가장 두드러진 원자료 신호는 DMN_FPN_between과 log-hours(β = +0.13, p = 0.25), small-worldness와 onset(β = −0.13, p = 0.28)이었다. 둘 다 개별 해석에는 너무 약하지만 방향은 더 넓은 패턴과 일관된다(더 많은 연습 → 더 강한 망 간 연결; 늦은 onset → 더 약한 small-world 구조)."));

children.push(H2("4.5 매개분석: Onset → Brain → PSM (Step 7)"));
children.push(P("11개 후보 매개변수 전반에서 간접효과(a × b)의 부트스트랩 95% 신뢰구간은 모두 0을 포함했다(그림 5). 가장 큰 점추정치는 small-worldness였고(a×b = −0.016, CI [−0.063, +0.020], p_boot = 0.40), 방향은 민감기 예측과 일관되었으나 간접효과는 통계적으로 영(null)이었다. 중요하게도 onset의 PSM에 대한 직접효과(c-path: β = −0.236)는 모든 매개변수별 모형에서 c′ ≈ −0.22로 거의 감쇠하지 않았고, 이는 onset → PSM 신호가 이 거시적 백질 지표들을 경유하지 않음을 가리킨다."));
children.push(imageParagraph(path.join(FIG_DIR, "fig4_mediation.png"), 480, 260));
children.push(caption("그림 5. 11개 후보 백질 매개변수를 경유하는 음악 onset의 PSM에 대한 간접효과. 막대는 95% 부트스트랩 신뢰구간(5,000회). 모든 구간이 0을 포함한다."));

// 5. Discussion
children.push(H1("5. 논의"));
children.push(H2("5.1 세 시나리오에 대한 판정"));
children.push(bodyMixed([
  "민감기 시나리오는 사전 등록한 세 가설 중 가장 잘 부합하지만, 약하게만 그렇다. 두 증거가 이를 지지한다: (i) ",
  { t: "상대적 크기 패턴", b: true }, ", M3에서 |β(onset)| > |β(hours)| — 바로 H1a의 예측; 그리고 (ii) ",
  { t: "두 계수의 방향", b: true }, ", 예상대로 음수. 두 증거가 지지를 제한한다: (i) ",
  { t: "어느 β도 p < 0.05에 도달하지 못했고", b: true },
  ", 주 onset 계수가 p ≈ 0.07이라는, 관례적 기준에서 기각도 채택도 정당화되지 않는 애매한 구간에 있다; 그리고 (ii) ",
  { t: "거시적 매개 경로가 실증적으로 부재한다", b: true },
  " — 민감기가 이 표본에서 실재한다면, 우리가 측정한 11개 위상 지표를 통해 작동하지는 않는다.",
]));
children.push(P("용량-반응 시나리오는 약하게 비지지된다. onset을 통제한 뒤 hours의 부분 계수는 onset보다 크기가 작다. 상호작용이 영이므로 고용량 훈련이 onset 효과를 증폭한다는 설명도 성립하지 않는다. 회의적 시나리오는 확신을 가지고 기각할 수 없다: 어느 것도 FDR을 통과하지 못했고, 표본 크기(훈련자 한정 n = 183)는 5예측변수 회귀에 비해 작으며, 정직한 보고는 이 가능성을 열어 두어야 한다."));
children.push(H2("5.2 거시적 커넥톰이 침묵하는 이유"));
children.push(bodyMixed([
  "가장 정보적인 음성 결과는 매개효과의 부재다. Steele et al.(2013)은 민감기 효과를 ",
  { t: "후방 뇌량(posterior corpus callosum)", i: true },
  "에 국재화했으며, 트랙토그래피(tractography)의 분획 비등방도(FA)를 사용했다 — 미세구조적이고 트랙 특이적인 측정치다. 반면 우리의 11개 지표는 임계화 후 전뇌 그래프의 네트워크 수준 요약이다. 두 해석이 가능하다:",
]));
children.push(bullet([{ t: "잘못된 공간 척도. ", b: true }, "특정 교련 트랙의 국소적 FA 차이는 small-worldness나 modularity 같은 네트워크 수준 위상 지표를 바꾸지 않을 수 있다. 신호가 트랙 수준에 존재하지만 전역 수준에서 보이지 않을 수 있다."]));
children.push(bullet([{ t: "잘못된 조직. ", b: true }, "순서 기억은 해마–전전두(hippocampal–prefrontal) 회로에 결정적으로 의존한다. MTL의 회색질 부피나 MTL–FPN 기능적 연결이 집합적 구조 커넥톰 위상보다 더 직접적인 기질일 수 있다."]));
children.push(P("어느 쪽이든, 적절한 다음 실험은 동일 파이프라인의 대표본 반복이 아니라, 관심 트랙의 미세구조 지표(FA, RD)나 해마/MTL 부피측정을 동일 HCP-D 표본에 적용하는 재설계다."));
children.push(H2("5.3 생애 전환점 프레임워크와의 연결"));
children.push(bodyMixed([
  "유일하게 명목적으로 유의한 Brain → PSM 신호인 small-worldness(β = +0.13)는 임의적이지 않다. Mousley et al.(2025)은 small-worldness가 9–32세 구간(HCP-D 전 연령대를 포함)에서 나이를 예측하는 가장 큰 LASSO 계수를 가진다고 보고했다. 우리의 유일한 행동적 적중이 생애 논문이 이 연령 창의 지배적 발달 축으로 지목한 바로 그 지표라는 점은, 이 구간의 PSM 관련 커넥톰 재조직이 부분적으로 small-worldness를 통해 작동한다는 생각과 적어도 일관된다. 이는 본 연구가 해결할 수 없는, 후속 추적을 위한 발견으로 남는다.",
]));
children.push(H2("5.4 한계"));
children.push(bullet([{ t: "검정력. ", b: true }, "훈련자 한정 n = 183. 주 M3 onset 계수가 p = 0.07로, 50–100명을 추가하면 어느 쪽이든 결론이 날 가능성이 높은 애매한 구간에 있다."]));
children.push(bullet([{ t: "onset 분포. ", b: true }, "훈련자의 약 20%만 7세 이전에 시작했다. 고전적 Steele식 대비는 표본 크기가 아니라 표본 구성에 의해 검정력이 부족하다."]));
children.push(bullet([{ t: "자기보고. ", b: true }, "음악 이력은 회고적 부모/자기 보고이며, 누적 시간은 측정 오차를 누적하는 거친 곱셈 단위에서 추정된다."]));
children.push(bullet([{ t: "횡단 설계. ", b: true }, "인과 방향을 분리할 수 없다 — ‘더 좋은 뇌 → 더 이른 시작’이 ‘더 이른 시작 → 더 좋은 뇌’와 형식적으로 구분되지 않는다."]));
children.push(bullet([{ t: "거시 지표만 사용. ", b: true }, "트랙 특이적 FA/RD, 회색질 부피, 기능적 연결은 검정하지 않았으며, 이들 중 어느 것이든 거시 위상이 담지 못한 흔적을 담을 수 있다."]));

// 6. Conclusion
children.push(H1("6. 결론"));
children.push(P("본 프로젝트는 음악 시작 시점이 일화기억과 거시적 백질 커넥톰에 탐지 가능한 흔적을 남기는지를 물었다. 사전 등록한 세 시나리오 프레임을 사용하여 다음을 발견했다:"));
children.push(bullet([{ t: "행동: ", b: true }, "누적 시간을 통제하면 onset의 PSM에 대한 부분 효과가 |β| = 0.09에서 |β| = 0.21로 커지고 hours의 부분 효과보다 크기가 큰 전형적 억제 패턴(p = 0.073, n = 183). 이는 민감기 시나리오가 예측한 신호다."]));
children.push(bullet([{ t: "뇌: ", b: true }, "PSM을 명목 수준에서 예측하는 것은 small-worldness뿐이며(raw p = 0.019, FDR 비유의), 이는 생애 연구(Mousley et al., 2025)가 우리 표본이 속한 9–32세 구간의 가장 강한 나이 예측자로 지목한 바로 그 지표다."]));
children.push(bullet([{ t: "매개: ", b: true }, "어떤 거시 위상 지표도 onset → PSM 신호를 운반하지 않는다. 11개 간접효과 95% CI가 모두 0을 포함한다."]));
children.push(bodyMixed([
  "정직한 요약은 데이터가 ", { t: "행동 측면에서 민감기 시나리오 쪽으로 기울지만", b: true }, ", ",
  { t: "그 흔적이 실재한다 해도 거시적 백질 위상에 있지는 않다는 것", b: true },
  "이다. 가장 생산적인 다음 단계는 탐색을 트랙 특이적 미세구조와 MTL 회색질·기능 지표로 돌리는 것이다 — 바로 원래의 민감기 및 일화기억 문헌이 관련 생물학을 국재화한 기질들이다.",
]));

// 7. References
children.push(H1("7. 참고문헌 (References)"));
const refs = [
  "Bigand, E., & Tillmann, B. (2022). Near and far transfer: Is music special? Memory & Cognition, 50(2), 339–347.",
  "Mousley, A., Bethlehem, R. A. I., Yeh, F.-C., & Astle, D. E. (2025). Topological turning points across the human lifespan. Nature Communications, 16, 10055.",
  "Sala, G., & Gobet, F. (2017). When the music's over: Does music skill transfer to children's and young adolescents' cognitive and academic skills? A meta-analysis. Educational Research Review, 20, 55–67.",
  "Schellenberg, E. G. (2020). Correlation = causation? Music training, psychology, and neuroscience. Psychology of Aesthetics, Creativity, and the Arts, 14(4), 475–480.",
  "Steele, C. J., Bailey, J. A., Zatorre, R. J., & Penhune, V. B. (2013). Early musical training and white-matter plasticity in the corpus callosum: Evidence for a sensitive period. Journal of Neuroscience, 33(3), 1282–1290.",
];
refs.forEach(r => children.push(new Paragraph({
  spacing: { before: 80, after: 80, line: 300 },
  indent: { left: 360, hanging: 360 },
  children: [new TextRun({ text: r, font: FONT, size: 20 })],
})));

// Appendix
children.push(H1("부록 · 데이터 및 코드"));
children.push(bodyMixed([
  "11단계 파이프라인(Step 1–7 확증적; Step 8–10 탐색적; Step 11 그림·요약)을 포함한 모든 분석 코드는 프로젝트 저장소에 공개되어 있다: ",
  { t: "github.com/ashleysys04-blip/music_connectome_pipeline", c: "2C7A7B" },
  ". HCP-D 영상 및 행동 데이터는 NDA Data Use Certification 하에 접근되며 재배포하지 않는다.",
]));

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
    ],
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
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
  fs.writeFileSync("BCS499_final_report_KR.docx", buf);
  console.log("saved →", "BCS499_final_report_KR.docx");
});