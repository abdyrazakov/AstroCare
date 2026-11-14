# Body trajectory research — source material for a future "expected body change over the mission" module

Date: 2026-11-15
Purpose: research deliverable only, not a patch. Feeds a future module that shows the
**population-level expected trajectory** of body systems over mission day — explicitly not a
measurement of this astronaut. Same rigor bar as `docs/EVIDENCE_RESEARCH_2026-11-14.md` and
`docs/PHASE_PRIORS_AND_RESOURCES_RESEARCH_2026-11-14.md`: **VERIFIED** only where the document was
opened (WebFetch of the PDF/HTML/PMC page, or a local `pdftotext` extraction of that same fetched
file) and a sentence can be quoted; otherwise **VERIFY** with an explicit statement of what could
not be opened. No invented citations, DOIs, page numbers, or values.

---

## 1. Table

| # | parameter | expected change | rate / timeline | countermeasure effect | source (URL) | section/quote | status |
|---|---|---|---|---|---|---|---|
| 1a | Bone mineral density, weight-bearing sites (hip, spine) | areal BMD declines progressively through a 4–6 month mission | hip (trochanter) lost faster than spine; individual femur-neck rates up to ~1.9%/month in long-duration (>300 d) flyers; intertrochanter −1.24 ± 0.74%/month (p<0.001) across 18 Mir cosmonauts | Russian in-flight exercise program (bungee/cycle/treadmill) did **not** fully prevent loss | LeBlanc et al. 2000, *J Musculoskelet Neuronal Interact* 1(2):157–160 — [PDF](https://jmni.hylonome.net/published/2/leblanc.pdf) | Abstract: "the current in-flight exercise program is not sufficient to completely ameliorate bone and muscle loss during weightlessness." Results: "intertrochanter, −1.24 ± 0.74%/month, p<0.001" | VERIFIED (direction, hip>spine pattern, intertrochanter rate); **VERIFY** for the commonly-cited aggregate headline "~1%/month spine, 1–1.6%/month hip" — Table 1 of this paper is a scanned/image table that did not extract as text; the aggregate n=18 means could not be directly quoted from this PDF. |
| 1b | Bone mineral density — pre-ARED vs with-ARED | ARED (2009+) markedly reduced monthly BMD loss vs iRED era | Trochanter: pre-ARED mean **−1.56%/mo** (SD 0.99) → with ARED **−0.5%/mo** (SD 0.4). Lumbar spine: pre-ARED mean **−1.06%/mo** (SD 0.63) → with ARED **−0.32%/mo** (SD 0.44) | ARED (600 lbf) vs iRED (300 lbf); "sufficiently reduced the previously observed declines" | NASA HRP Evidence Report — Risk of Bone Fracture Due to Spaceflight-Induced Changes to Bone — [PDF](https://humanresearchroadmap.nasa.gov/evidence/reports/Fracture.pdf) (cites Smith et al. 2012, *J Bone Miner Res* 27(9):1896, doi:10.1002/jbmr.1647, not independently opened — paywalled, see VERIFY note) | "Declines in bone mineral density (BMD) occur during spaceflight at averaged loss rates between 1-1.5% per month..." / Table 4: Trochanter Mean −1.56 (Pre-ARED) → −0.5 (With ARED); Lumbar Spine Mean −1.06 (Pre-ARED) → −0.32 (With ARED) | VERIFIED (the evidence report itself, including its Table 4 numbers and the 1–1.5%/month headline); Smith et al. 2012 itself not opened — Wiley full text is paywalled — mark that specific citation **VERIFY**. |
| 2 | Skeletal muscle mass and strength (calf, thigh) | Significant atrophy and strength loss despite in-flight exercise; calf more affected than thigh | Calf muscles lost more than thigh (10–18% vs 4–7%, MRI ~4–5 days post-landing); soleus lost the most of any muscle; thigh knee-extensor strength −10%, calf strength −24%; ~half of muscle-mass loss still present 2 weeks post-return; soleus type-I fiber peak force −35%, peak power −~55% in the most-affected (soleus) fibers | ARED-era crewmembers "fared better" than iRED-era; both groups averaged under NASA's 20% strength-loss standard, but individuals still exceeded it; SPRINT (high-intensity, lower-volume, 3 d/wk resistance + 3 d/wk aerobic) attenuated some strength decrements for the same or less training time (33% less time than standard) | NASA HRP Evidence Report — Risk of Impaired Performance Due to Reduced Muscle Mass, Strength, and Endurance — [PDF](https://humanresearchroadmap.nasa.gov/Evidence/reports/Muscle.pdf) (cites Trappe et al. 2009, *J Appl Physiol* 106:1159–1168, and Fitts et al. 2010, *J Physiol* 588(18):3567–92 — PMC quoted directly, see below); English et al. 2020, *npj Microgravity* 6:21 ("SPRINT study") — [PMC7434884](https://pmc.ncbi.nlm.nih.gov/articles/PMC7434884/) | Evidence report: "Calf muscles were found to undergo greater decrements than thigh muscles (10-18% and 4-7% loss, respectively)... Approximately half of the loss of muscle mass still existed up to two weeks following return to Earth." / "calf muscle strength was reduced by 24%..." / "ARED-era crewmembers have fared better than iRED-era crewmembers... both groups have losses of less than the 20% standard." Fitts 2010 (PMC2988519): "peak force... for the soleus type I fibre declined 35%..."; "Peak power was depressed in all fibre types with the greatest loss (~55%) in the soleus." English 2020 (PMC7434884): "high intensity/lower volume integrated Sprint resistance (3 d wk⁻¹) and aerobic... knee flexor peak torque... reductions in strength were absent or attenuated in SPRINT"; "at least 33% less time than the standard exercise program." | VERIFIED. Trappe et al. 2009 itself was not independently opened (PubMed/EuropePMC blocked WebFetch with cookie/403 walls, Marquette repository returned HTTP 403) — its specific numbers above are VERIFIED via direct quotation of the NASA evidence report that cites and restates them, not via the original journal article; mark the Trappe 2009 primary citation **VERIFY**. |
| 3 | Aerobic capacity (VO2peak) | Early in-flight drop, partial in-flight recovery, never back to pre-flight in-flight, full recovery by 30 days post-landing | −17% in the first two weeks of flight, trending upward afterward but never returning to pre-flight in-flight; post-flight (24–28 h) still −~15%; fully recovered by R+30 | A subset who performed higher-intensity in-flight aerobic exercise maintained pre-flight VO2peak | NASA HRP Evidence Report — Risk of Reduced Physical Performance Capabilities Due to Reduced Aerobic Capacity — [PDF](https://humanresearchroadmap.nasa.gov/evidence/reports/Aerobic.pdf) (cites Moore, Downs et al. 2014, *J Appl Physiol* 117:231–238 — restated directly in the report, original journal article blocked by PubMed cookie wall) | "The results showed a mean decline in VO2peak of 17% in the first two weeks of spaceflight followed by a trend upward throughout the remainder of the mission. Post-flight (24-28 h after landing) VO2peak was reduced by ~15% from pre-flight and fully recovered 30 days after landing." / "A subset of astronauts in this study who performed higher intensity aerobic exercise during flight maintained their pre-flight VO2peak." | VERIFIED (via the evidence report's direct restatement of Moore et al. 2014); Moore et al. 2014 itself not independently opened — PubMed returned only a cookie-consent page to WebFetch — mark the original journal citation **VERIFY**. Ade et al. not opened; not needed given the above is already VERIFIED through the evidence report. |
| 4 | Body mass / caloric intake | Reduced caloric intake vs target, with measurable body-mass loss | Historical ISS/Mir intake "around 80% of recommended intake" associated with "an average weight decrease of 5%"; body-mass losses up to 10–15% recorded in some ISS/Mir crew | Skylab crews, "required to eat enough to meet their caloric needs, preserved body mass" — i.e. adequate intake is itself the countermeasure | NASA HRP Evidence Report — Risk of Performance Decrement and Crew Illness Due to an Inadequate Food System — [PDF](https://humanresearchroadmap.nasa.gov/Evidence/reports/Food.pdf) (cites Smith, Zwart et al. 2005/2009, not independently opened) | "The reduced caloric intake on ISS Expeditions (around 80% of recommended intake during space flight), as documented in 2005, led to an average weight decrease of 5%... Body mass losses in some ISS and Mir crewmembers have been measured as high as 10-15%." / "The Skylab crews, who were required to eat enough to meet their caloric needs, preserved body mass." | VERIFIED. Consistent with — and a trajectory-relevant cross-reference to — this repo's existing `CALORIC_DEFICIT` evidence (JSC-63555 "<80% EER = red" band, already VERIFIED in `docs/EVIDENCE_RESEARCH_2026-11-14.md` item 5). Smith/Zwart 2005/2009 primary reports not independently opened — mark **VERIFY**. |
| 5 | Cardiovascular deconditioning / orthostatic intolerance | High incidence of post-landing orthostatic intolerance after long-duration flight; rapidly declines over the first days back | >80% incidence on landing day after 4–6 month Mir missions (5 of 6 astronauts failed a 10-min tilt test); 4 of 6 (66%) ISS astronauts vs 13 of 66 (20%) Shuttle astronauts failed a 10-min 80° head-up tilt test on landing day; 8 of 9 ISS astronauts passed by R+1; 13 of 15 (87%) ISS and 19 of 19 (100%) Shuttle passed by R+3; some astronauts still symptomatic "for several days" | Lower-body compression garments used in week 1 post-landing to manage symptoms; no described in-flight countermeasure fully prevents it | NASA HRP Evidence Report — Risk of Cardiovascular Adaptations Contributing to Adverse Mission Outcomes — [PDF](https://humanresearchroadmap.nasa.gov/Evidence/reports/Cardio%20Risk%20EB%202022%20FINAL_4-3-2023.pdf) (cites Lee et al. 2015, not independently opened) | "The incidence of post-spaceflight orthostatic intolerance among US astronauts increased to greater than 80% on landing day following long duration (4 to 6 months) Mir spaceflights... On landing day, 4 of 6 (66%) ISS astronauts were unable to complete a 10-min 80° head-up tilt test compared to 13 of 66 (20%) Shuttle astronauts. The rates of presyncope quickly decline after just one day after return from space... On R+3, 13 of 15 (87%) of the ISS and 19 of 19 (100%) of the Shuttle astronauts completed the 10-min test... some astronauts continue to experience symptoms for several days." | VERIFIED (via the evidence report's direct restatement of Lee et al. 2015). Lee et al. 2015 (*Aerosp Med Hum Perform*) and Hughson's work not independently opened — mark those specific primary citations **VERIFY**. |
| 6 | Fluid shift / SANS (onset & persistence only) | Optic disc edema (ODE) and related ocular findings can appear within the first month of flight; most resolve post-flight but with wide individual variability, some persisting many months | ~15% of crew have "clinically significant" (Frisén ≥1) ODE during/after long-duration flight; onset "can develop within the first month of spaceflight, but interindividual variability is wide"; most cases resolve "within weeks" of return; documented outliers: one case unresolved for 20 months post-landing, another case of absent venous pulsations unresolved 21 months post-return, asymmetric disc swelling resolving over 180 d with morphologic change persisting 630 d | No proven in-flight countermeasure yet; LBNP / venous thigh cuffs / inspiratory threshold device are ground-tested candidates, not established operational fixes | NASA HRP Evidence Report — Risk of Spaceflight Associated Neuro-Ocular Syndrome (SANS), 2022 — [PDF](https://humanresearchroadmap.nasa.gov/evidence/reports/SANS%20EB%202022%20FINAL_8-15-22.pdf); Lee AG et al. 2020, *npj Microgravity* 6:7 — [PMC7005826](https://pmc.ncbi.nlm.nih.gov/articles/PMC7005826/) | SANS evidence report: "Based solely on fundoscopy data, 'clinically significant' ODE (i.e., Frisén grade ≥1) is diagnosed in about 15% of crewmembers during or after LDSF." / "The results of the Ocular Health Study suggest that ODE can develop within the first month of spaceflight, but the interindividual variability is wide." / "...did not resolve until 20 months after landing." Lee AG 2020 (PMC7005826): "unilateral loss of previously visible spontaneous venous pulsations during space flight...continued to be absent for 21 months after return to Earth." / "asymmetric disc swelling...over 180 days post-flight and asymmetric optic disc morphologic changes persisted for 630 days post-flight." | VERIFIED (both sources opened and quoted directly). Onset-vs-persistence distinction matters for a trajectory model: SANS is a Phase-1-onset, long-persistence condition, consistent with the SANS proportion treatment already VERIFIED in `docs/PHASE_PRIORS_AND_RESOURCES_RESEARCH_2026-11-14.md` §3 (IP 0.2593, model mean 0.2789). |
| 7 | Radiation cumulative dose, 6-month ISS mission (context only) | Typical mission accumulates a minority of the career limit; day-to-day rate is well below acute thresholds | ISS background ~0.2–0.5 mSv/day (Shavers et al. 2023), episodes to ~1.2 mSv/day; Simonsen 2025 estimates ~40–90 mSv over a typical 6-month expedition, vs the 600 mSv NASA career effective-dose limit and ~240–290 mSv seen in US multi-mission careers | N/A — radiation dose accrues passively; shielding/timing are the only levers, already covered elsewhere in this repo | Already VERIFIED in this repo: `docs/EVIDENCE_RESEARCH_2026-11-14.md` §2 item 3 and §5 item 9 (Shavers et al. 2023, [PMC10919966](https://pmc.ncbi.nlm.nih.gov/articles/PMC10919966/); Simonsen 2025, [NTRS 20250006168](https://ntrs.nasa.gov/api/citations/20250006168/downloads/ASCEND%20Simonsen%20draft%201.pdf)); cross-referenced here, not re-fetched. | See `docs/EVIDENCE_RESEARCH_2026-11-14.md` §2 row 3 and §5 row 9 for the exact quotes already on file. | VERIFIED (cross-reference to existing repo audit; not re-verified in this pass). |

---

## 2. What could not be opened in this pass

- Smith et al. 2012, *J Bone Miner Res* (ARED bone paper) — Wiley full text is paywalled; its headline numbers are VERIFIED only indirectly, via the NASA Fracture Evidence Report's own Table 4, which independently reports the same pre/with-ARED comparison.
- Trappe et al. 2009, *J Appl Physiol* — PubMed and EuropePMC both returned cookie-consent/403 pages to WebFetch; the Marquette University repository copy returned HTTP 403. Its numbers are VERIFIED only via direct quotation inside the NASA Muscle Evidence Report.
- Moore, Downs et al. 2014, *J Appl Physiol* — PubMed returned a cookie-consent page only; VERIFIED only via the NASA Aerobic Evidence Report's restatement.
- Lee et al. 2015 (orthostatic intolerance) and Hughson's cardiovascular work — not independently opened; VERIFIED only via the NASA Cardiovascular Evidence Report's restatement.
- Smith, Zwart et al. 2005/2009 (nutrition) — not independently opened; VERIFIED only via the NASA Food Evidence Report's restatement.
- Fitts et al. 2010 (*J Physiol*), English et al. 2020 (*npj Microgravity*, SPRINT), Lee AG et al. 2020 (*npj Microgravity*, SANS review), and all NASA HRP evidence-report PDFs themselves **were** opened directly (via WebFetch, with `pdftotext -layout` used on the saved PDF bytes when WebFetch's own PDF text extraction failed) and are quoted above as primary sources for this pass.
- LeBlanc et al. 2000's Table 1 (the paper's own summary table of mean %/month BMD loss by site) is a scanned/image table inside the PDF and did not extract as text under either WebFetch or `pdftotext`; only the narrative sentences and the secondary (non-Table-1) numbers quoted above could be verified from that document.

---

## 3. Proposed model shape (data-only; not a code change)

Not a patch — a sketch of the shape a future `body_trajectory.py` could take, reusing the table
above as its coefficients. Every curve-fit choice below (piecewise-linear vs. exponential,
breakpoints, the adherence modulation itself) is a **DESIGN DECISION**, not a cited number.

```python
# DESIGN DECISION: shape, breakpoints, and the adherence modulation below are prototype
# choices, not NASA-specified functions. Only the rate/asymptote magnitudes in `source`
# trace to the VERIFIED/VERIFY rows in section 1.
BODY_TRAJECTORY_PRIORS = {
    "BONE_BMD_HIP_PCT": {
        "shape": "linear_with_countermeasure_damping",     # DESIGN DECISION
        "rate_no_exercise_pct_per_month": -1.56,            # VERIFIED, row 1b (pre-ARED trochanter)
        "rate_with_exercise_pct_per_month": -0.50,          # VERIFIED, row 1b (with-ARED trochanter)
        "floor_pct": None,                                  # NOT FOUND — plateau point unknown
        "source": "row 1b",
    },
    "MUSCLE_CALF_STRENGTH_PCT": {
        "shape": "exponential_approach_to_asymptote",       # DESIGN DECISION
        "asymptote_pct_loss": -24.0,                         # VERIFIED, row 2 (calf strength)
        "half_life_days": None,                              # NOT FOUND — no in-flight time series in sources
        "post_landing_recovery_days_half": 14,               # VERIFIED, row 2 ("~half... still existed... two weeks")
        "source": "row 2",
    },
    "VO2PEAK_PCT": {
        "shape": "piecewise_linear",                         # DESIGN DECISION
        "breakpoints_days": [0, 14, 180, 210],               # VERIFIED timing: -17% by day 14; recovers by R+30
        "values_pct": [0, -17, -10, 0],                       # -10 is an interpolated guess mid-mission — DESIGN DECISION
        "source": "row 3",
    },
    "ORTHOSTATIC_INTOLERANCE_PROPORTION": {
        "shape": "step_at_landing_then_decay",               # DESIGN DECISION
        "proportion_landing_day": 0.66,                       # VERIFIED, row 5 (ISS, 66%)
        "proportion_r1": None,                                # "8 of 9" quoted; exact fraction left unrounded deliberately
        "proportion_r3": 0.13,                                 # VERIFIED, row 5 (13 of 15 PASSED -> 2/15 still failing)
        "source": "row 5",
    },
    "SANS_ODE_ONSET_PROPORTION": {
        "shape": "step_onset_within_first_month_then_flat",  # DESIGN DECISION; persistence handled separately
        "proportion": 0.15,                                   # VERIFIED, row 6 ("about 15% of crewmembers")
        "onset_window_days": [0, 30],                          # VERIFIED, row 6 ("within the first month")
        "source": "row 6",
    },
    "ADHERENCE_MODULATION": {
        # DESIGN DECISION in full: no cited source gives a continuous adherence->outcome
        # function. The table above only VERIFIES two discrete points (no-countermeasure vs.
        # ARED/SPRINT-era countermeasure); a continuous multiplier between them is invented
        # for prototype purposes only and must be labelled as such everywhere it is used.
        "model": "linear_interpolation_between_no_exercise_and_full_adherence_rates",
        "input": "exercise_minutes_today / required_exercise_minutes (already in the input contract)",
    },
}
```

---

## 4. What must be labelled on the UI

- **Population expectation, not measurement.** Every curve above is a group-level trajectory
  from NASA/ISS/Mir cohorts (n as small as 4–18 crew per study); it is not a prediction for any
  individual astronaut and must never be rendered as if it were derived from that astronaut's own
  sensor stream. Pair every trajectory line with the live measured value on the same chart, visibly
  distinguished (e.g. dashed "expected" line vs. solid "measured" line).
- **Confidence / evidence status must travel with the number.** Every value shown must carry its
  row's status from section 1 (VERIFIED vs. VERIFY) and, for VERIFY, the specific caveat (e.g.
  "primary paper not opened; value via NASA evidence report restatement" or "Table 1 unreadable,
  secondary-source number only"). This mirrors the `evidenceRef` pattern already required by
  `AGENTS.md` for `flagDetails` and `likelyConditions`.
- **Never a diagnosis, never a fitness-for-duty call.** The module shows "expected population
  trajectory for this mission day," not "this astronaut has condition X" or "this astronaut is
  cleared/not cleared." Any resemblance to a `likelyConditions` code must be presented as a
  separate, already-labelled field (per `AGENTS.md` §3), not merged into this module's output.
- **Label every DESIGN DECISION as such.** The piecewise/exponential shape choice, breakpoints,
  and — especially — the adherence-modulation curve in section 3 are prototype choices with no
  cited source; the UI (or its tooltip/evidence panel) must say so explicitly, not present them
  with the same confidence as a VERIFIED NASA number.
- **State the n and the population.** Several underlying cohorts are small (e.g. 9 ISS
  crewmembers for the Fitts/Trappe muscle-fiber data, 18 Mir cosmonauts for LeBlanc's bone data);
  surface this so viewers do not over-trust a smooth line drawn through sparse data.
