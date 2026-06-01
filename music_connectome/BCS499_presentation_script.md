# BCS499 Final Project — Presentation Script (English)
### "Does music's sensitive period leave a trace in episodic memory's white matter?"
**서예슬 20230340 · target time: 12–14 minutes**

> Timing guide is in brackets at each slide. Speak at a calm pace — roughly 130 words/minute. Where you see *(point)*, gesture to the figure on screen.

---

## SLIDE 1 — Title [~0:45]

Hi everyone, my name is Yesul Seo. The question I want to walk you through today is one that probably sounds familiar to a lot of parents: does starting music early actually make a child's brain better?

The title of my project is "Does music's sensitive period leave a trace in episodic memory's white matter?" I used the HCP-D dataset — the Human Connectome Project in Development — and I looked at structural connectomes from about 448 participants, with a trained-only subsample of around 183.

The short version of my answer, which I'll build up to, is: the timing of when you start music does seem to leave a fingerprint in episodic memory — but probably *not* in the kind of large-scale white-matter wiring I measured. Let me explain why.

---

## SLIDE 2 — The Question [~1:15]

So here's the actual debate. We've all seen the claim that kids with early music training score higher on cognitive tests. That part is true. But *why* it's true is genuinely contested, and it has the shape of a chicken-and-egg problem.

There are three competing explanations. *(point to first card)*

The first is the **sensitive period** view. What matters is *when* you start. The idea is that the developing brain has a window — roughly before age seven — during which musical experience can shape white matter in a way the adult brain can't. The classic evidence is Steele and colleagues, 2013, who found corpus callosum differences tied to whether musicians started before or after seven, even after matching total practice hours.

The second is the **dose-response** view. What matters is *how much* you trained. Early starters simply accumulate more total practice by adulthood — so maybe onset age is just a stand-in for hours. That's Schellenberg's argument.

And the third is the **skeptical** view: maybe neither matters once you properly control for family background, socioeconomic status, and pre-existing aptitude. That's Sala and Gobet.

The whole point of my project is that you cannot tell these three apart with a simple correlation — because onset age and total hours are themselves strongly correlated.

---

## SLIDE 3 — Motivation [~1:00]

Two quick design choices before the methods.

First, why episodic memory? Music learning is fundamentally sequential — you're encoding ordered patterns in time, remembering motor sequences, binding events to context. The Picture Sequence Memory task, from the NIH Toolbox, probes exactly that: you reproduce an ordered sequence of pictured events. I picked it because "intelligence" is too broad to measure cleanly, but PSM is concrete, validated, and theoretically tied to music.

Second, why this dataset and this age range? HCP-D gives me both the structural connectomes and a music-history questionnaire detailed enough to estimate onset age and cumulative hours. And critically, the 9-to-22 age range sits right inside what Mousley and colleagues, in 2025, call **Epoch 2** of lifespan white-matter development — the window where, as I'll come back to, small-worldness is the dominant developmental signal. So if music's sensitive period writes itself into the connectome, this is exactly where we'd expect to see it.

---

## SLIDE 4 — Hypothesis [~1:15]

Here's how I made the debate testable, and this is the part I'd most like you to evaluate.

I didn't just say "let's see if music helps." I pre-registered the three scenarios as three *specific* predictions about the coefficients in one regression — model M3 — where PSM is predicted by onset age and log-hours together, with covariates. *(point to equation)*

If it's a **sensitive period**, then the partial coefficient on onset should be larger in magnitude than the one on hours, with both negative.

If it's **dose-response**, the reverse — hours should dominate.

And if the **skeptics** are right, both coefficients collapse toward zero.

My pre-registered prediction was the first one: onset bigger than hours.

One thing I want to be explicit about, because the syllabus emphasizes it: I'm *not* resolving this with a simple "significant or not" test. Significance is one input. The *direction* and the *relative size* of the coefficients are just as important. That framing protects me from over-reading a marginal p-value, and from throwing away a real pattern just because it isn't starred.

---

## SLIDE 5 — Methods / Pipeline [~1:15]

Quickly, the pipeline — five conceptual stages. *(point along the boxes)*

Step one, I built the sample: HCP-D demographics merged with the music questionnaire and the PSM scores, giving me 473 with behavior. Step two, I loaded the structural connectomes — 246-by-246 matrices from DSI Studio's QSDR reconstruction — and 448 passed quality control. Step three, I computed eleven graph-theory features per person: things like global efficiency, modularity, small-worldness, characteristic path length, and within- and between-network strength for the DMN, FPN, and MTL.

Then the confirmatory part. Steps four and five are the GLMs: brain-to-PSM, and the nested music-to-PSM models M1 through M4. Steps six and seven take it to the brain side: music-to-brain, and a bootstrap mediation asking whether onset reaches PSM *through* the brain.

Throughout, I adjust for age, sex, log family income, and race, and I apply FDR correction within each step. The primary trained-only sample is about 183.

---

## SLIDE 6 — Sample [~1:00]

Before results, an honest look at who's actually in the data — because it sets a hard limit on what I can claim. *(point to histogram)*

The onset ages cluster heavily between 8 and 11 years. And here's the catch: only about 40 participants — roughly 20% — started before age seven.

That matters a lot. The classic sensitive-period studies, like Steele, contrast *before* seven versus *after* seven. I basically don't have enough early starters to do that clean contrast. *(point to caveat box)*

So I'm honest about this in the report: what I'm really testing is "relatively earlier versus relatively later onset" within a typical population — not the classical pre-seven sensitive period. I'd rather state that limit up front than overclaim.

---

## SLIDE 7 — Result A: The headline [~1:30]

Okay, the main result. This is the slide I care about most. *(point to the bar chart)*

Look at the three models from left to right. In M1, with onset alone, the coefficient is weak — about minus 0.09. In M2, hours alone, it's basically nothing — minus 0.04. So on their own, neither variable looks like it does much.

But watch what happens in M3, when I put them *together*. *(trace the red arrow)* Onset's coefficient more than doubles — it jumps to minus 0.207. Hours also grows, to minus 0.158, but it stays smaller than onset.

This is a classic **suppressor effect**. The two variables were masking each other's true partial contributions, and only when you control them simultaneously does onset's real effect emerge — and it emerges in the sensitive-period direction.

The numbers on the right: onset is minus 0.207 at p equals 0.073; hours is minus 0.158 at p equals 0.129. And the interaction term — onset times hours — is essentially zero, p of 0.74. So the suppression is simply additive; there's no "you need both" story.

Now — yes, p is 0.073, not under 0.05. I'll address that head-on in two slides. But notice: the *pattern* — onset bigger than hours, both negative — is exactly what the sensitive-period scenario predicted.

---

## SLIDE 8 — Interpretation of the suppressor [~1:15]

Let me make the suppressor effect intuitive, because it's a little counterintuitive. *(point to the box plot)*

If you just look at raw PSM scores by onset group — no adjustment — the *late*-onset group actually looks slightly *higher* than the early group. At face value, that's the opposite of my hypothesis.

But that's misleading. Late starters in this dataset tend to be older, and they've completed more development, so their raw PSM looks a bit better. That older-age advantage is sitting on top of, and hiding, the onset effect.

Once I hold hours and the demographic covariates constant in M3, that confound is stripped away, and onset's true partial effect appears — the magnitude more than doubles and it flips to the sensitive-period direction.

This, by the way, is exactly *why* I pre-registered M3 as the primary model, and it's my direct answer to Schellenberg's critique. He says onset effects are confounded with hours and background. My design's response is: yes — and when you control for that confound properly, the onset signal doesn't disappear, it gets *stronger*.

---

## SLIDE 9 — Result B: the brain side [~1:30]

Now the brain side — and here the story gets quieter. *(point to left figure)*

On the left, brain predicting PSM: of my eleven graph features, only **small-worldness** reaches even nominal significance — beta of positive 0.13, raw p of 0.02 — and it does *not* survive FDR correction. Everything else is noise.

In the middle, music predicting brain: 22 tests, nothing survives correction.

And on the right, the mediation — this is the key negative result. *(point to forest plot)* I tested whether onset reaches PSM *through* each of the eleven brain features. Every single confidence interval crosses zero. There is no mediation. Even small-worldness, which has the biggest point estimate, has an interval that includes zero.

So here's the takeaway. *(point to bottom bar)* If the onset-to-PSM signal from a few slides ago is real, it does **not** travel through these large-scale white-matter features. The only flicker of a brain signal — small-worldness — is interesting because it's the very same metric that Mousley and colleagues flag as the dominant developmental axis for this exact age window. But I can't claim more than a hint.

---

## SLIDE 10 — Verdict [~1:15]

So, scenario by scenario — with appropriate caution. *(point down the rows)*

**Sensitive period: partially supported.** The direction matches, and onset's magnitude beats hours, exactly as predicted. But p is 0.073, and there's no mediation — so even if the behavioral signal is real, the trace is *not* in macroscale topology.

**Dose-response: weakly disfavored.** Once onset is controlled, hours has the *smaller* effect, and there's no interaction — so it's not the case that more training simply amplifies an onset effect.

**Skeptical: cannot be fully rejected.** Nothing survived FDR, and with n of 183 I don't have the power to confidently rule it out. An honest report leaves it on the table.

So the one-line verdict *(point to bottom)*: the data lean toward sensitive period — but the route, if it exists, isn't through the large-scale white-matter wiring I measured.

---

## SLIDE 11 — Limitations & Next Steps [~1:15]

Let me be upfront about limitations, and then say where I'd look next. *(point left)*

On power: trained-only n is 183, and that p of 0.07 sits in the frustrating zone where another fifty to a hundred participants would probably settle it. On coverage: too few pre-seven starters to do the classical contrast. The music history is self-reported and retrospective, so cumulative hours is noisy. And the design is cross-sectional, so I genuinely cannot separate "earlier start causes better brain" from "better brain causes earlier start."

But the negative mediation result actually points somewhere productive. *(point right)* Steele found the original effect in a *specific tract* using microstructure — fractional anisotropy in the corpus callosum. My features are whole-brain network summaries, which may simply be the wrong spatial scale, or the wrong tissue. So the next experiment isn't a bigger version of this one — it's tract-specific FA and RD, or hippocampal and MTL gray-matter and functional measures, which are closer to the actual substrate of sequence memory.

---

## SLIDE 12 — Take-home [~0:45]

To wrap up. Three numbers capture the whole project. *(point to each)*

Onset's coefficient grows by more than a factor of two when I control for hours — that's the suppressor signature of a sensitive period. Zero out of eleven brain features carry that effect — so it's not in macroscale topology. And of the three scenarios, sensitive period is the best fit, though only weakly.

So: music's onset age does seem to leave a fingerprint in episodic memory — but probably not in the large-scale white matter. The interesting next question is *where* it actually lives.

Thank you — I'm happy to take questions.

---

## ANTICIPATED Q&A — prep notes (not spoken)

**"Your p is 0.073 — isn't this just a null result?"**
The claim isn't "sensitive period is proven." It's "of three pre-registered scenarios, which way do the partial coefficients lean?" Beta of −0.21 at p = 0.07, with n = 183, is more consistent with the sensitive-period pattern than with dose-response or with a flat null. A decisive test needs more pre-7 starters — e.g., a conservatory-oversampled sample.

**"Why did you log-transform hours?"**
Cumulative hours has a heavy right tail — a few participants with enormous totals. Log compresses that tail, stabilizes variance, and keeps a handful of extreme cases from dominating the regression.

**"Couldn't the suppressor effect be an artifact of multicollinearity?"**
Onset and hours are correlated, but their VIFs were acceptable, and a suppressor pattern is a substantive finding, not an artifact — it's the standard reason you enter correlated predictors jointly rather than separately.

**"Why these eleven graph metrics and not others?"**
They cover the three canonical topology families — integration (efficiency, path length), segregation (modularity, clustering, small-worldness), and network-specific strength for the systems most tied to memory and control: DMN, FPN, MTL. They also match the metric family used in the Mousley lifespan paper, so the comparison is principled.

**"What about the other cognitive tasks — Flanker, DCCS?"**
Those were planned as secondary analyses. PSM is the pre-registered primary outcome because of its sequential-memory link to music; reporting everything would invite fishing, so I kept the confirmatory test focused.
