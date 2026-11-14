# Evidence register

Статусы VERIFY закрывает исследователь команды; пороги со статусом ASSUMPTION подлежат пересмотру до сдачи.

VERIFIED means the cited source was checked, not that the prototype is clinically validated.
Source checks: 2026-11-14. Research audit: `docs/EVIDENCE_RESEARCH_2026-11-14.md`. NEWS2 alert colors and component-flag emission are prototype choices. New dose fields are supplied totals, not integrated from sample timestamps.

| flag/threshold | value | source | section/page | status (VERIFIED / VERIFY / ASSUMPTION / DESIGN DECISION) | note |
|---|---|---|---|---|---|
| CAREER_EFFECTIVE_DOSE_LIMIT_MSV | 600 mSv | [NASA-STD-3001 Vol.1](https://www.nasa.gov/reference/4-0-human-performance/) | §4.8.2, V1 4030 | VERIFIED | Universal career spaceflight effective-dose limit; NASA-specific dose model. |
| THIRTY_DAY_BFO_LIMIT_MGY_EQ | 250 mGy-Eq | [NASA-STD-3001 Vol.1](https://www.nasa.gov/reference/4-0-human-performance/) | Table 4.8-1, Blood-forming Organs, 30-Day | VERIFIED | Organ-specific dose, not effective dose in mSv. |
| RADIATION_30DAY_LIMIT | yellow ≥125 mGy-Eq; red ≥250 mGy-Eq | NASA-STD-3001 Table 4.8-1 + prototype choice | p.40 | ASSUMPTION | Input is BFO mGy-Eq; direct comparison to effective dose would be invalid. |
| RADIATION_CAREER_LIMIT | yellow ≥300 mSv; red ≥600 mSv | [NASA limit](https://www.nasa.gov/reference/4-0-human-performance/) + prototype choice | §4.8.2, V1 4030 | DESIGN DECISION | 50% warning and red at the limit are application severities, not NASA clinical triage. |
| WARN_FRACTION | 0.5 | v0.2 specification | Operational policy | DESIGN DECISION | Warn at half of either cumulative limit. |
| CRITICAL_FRACTION | 1.0 | v0.2 specification | Operational policy | DESIGN DECISION | Red at or above the cumulative limit. |
| radiation_dose_career_msv input provenance | NASA effective dose | [NASA definition](https://www.nasa.gov/reference/4-0-human-performance/) | §4.8.2 note | VERIFY | Data team must confirm input dosimetry uses the NASA effective-dose model. |
| NASA edition provenance | Rev C, approved 2023-09-15 | [NASA PDF](https://www.nasa.gov/wp-content/uploads/2023/11/nasa-std-3001-vol-1-rev-c-with-signature.pdf) | title page; §4.8.2 p.39; Table 4.8-1 p.40 | VERIFIED | Checked the actual Rev C PDF; not a 2022 revision. |
| Former career-limit attribution | origin of universal 600 mSv recommendation | NASA-STD-3001 Rev C §4.8.2; NASEM 2021 | p.39; Box 3-1 | CONFLICT | NASA cites NASEM 2021; legacy attribution was incorrect; NCRP Report 132 is only for organ limits. |
| nominal mock cumulative doses | 12 mGy-Eq / 30 days; 120 mSv career | Shavers et al. 2023; synthetic fixture | Results | ASSUMPTION | Synthetic fixture, not measured crew history. |
| cumulative-dose mock anomalies | 150/260 mGy-Eq 30-day; 350/660 mSv career | v0.2 specification and limits above | Synthetic fixture | DESIGN DECISION | Test stimuli for warning and exceeded-limit paths, not additional thresholds. |
| HR_HIGH | ≥111 bpm | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 1, p.29 | VERIFIED | NEWS2 bands; prototype color. |
| HR_LOW | ≤40 bpm | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 1, p.29 | VERIFIED | NEWS2 bands; prototype color. |
| SPO2_LOW | ≤93% | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 1, p.29 | VERIFIED | Scale 1. |
| BP_LOW | ≤100 mmHg | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 1, p.29 | VERIFIED | Systolic. |
| BP_HIGH | ≥220 mmHg | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 1, p.29 | VERIFIED | Systolic. |
| TEMP_HIGH | >39.0°C | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 1, p.29 | DESIGN DECISION | Continuous input; source uses ≥39.1°C. |
| TEMP_LOW | ≤35.0°C | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 1, p.29 | VERIFIED | Prototype color. |
| RESP_HIGH | ≥21/min | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 1, p.29 | VERIFIED | Prototype color. |
| RESP_LOW | ≤8/min | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 1, p.29 | VERIFIED | Prototype color. |
| CONSCIOUSNESS_ALTERED | altered → 3 | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 1, p.29 | DESIGN DECISION | Binary proxy for CVPU. |
| NEWS2_MEDIUM | total 5–6 or component 3 | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 2, p.30 | DESIGN DECISION | Combines medium and low-medium. |
| NEWS2_HIGH | total ≥7 | [RCP](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Chart 2, p.30 | VERIFIED | Prototype red. |
| FLAGGED_MIN_SCORE | component score ≥2 | Existing application policy | — | DESIGN DECISION | Component flag emission/color is not an RCP prescription. |
| RADIATION_ELEVATED | ≥100 µSv/h or S≥2 | [NOAA SWPC](https://www.swpc.noaa.gov/noaa-scales-explanation); existing contract | Solar Radiation Storms, S2 | DESIGN DECISION | Rate threshold and yellow mapping are ours; NOAA defines a particle-flux storm scale, not a crew dose threshold. |
| RADIATION_CRITICAL | ≥1000 µSv/h or S≥3 | [NOAA SWPC](https://www.swpc.noaa.gov/noaa-scales-explanation); existing contract | Solar Radiation Storms, S3 | DESIGN DECISION | Rate threshold and red mapping are ours; NOAA recommends astronaut EVA hazard avoidance at S3. |
| ISS background context | 0.2–0.5 mSv/day (≈8–21 µSv/h); episodes up to 1.2 mSv/day (≈50 µSv/h) | Shavers et al. 2023; NASA/JSC acute effects | Results; text | CONFLICT | The former narrow range was a derived envelope, not a quoted measured range. |
| EXERCISE_DEFICIT | <50% prescribed minutes | NASA SP-20250000273; NTRS 20110016265 | Current exercise practices; Abstract | VERIFIED / DESIGN DECISION | Prescription verified; <50% cutoff is our design decision; MORD SSP 50260 not publicly opened. |
| CALORIC_DEFICIT | <80% of EER red; 80–90% yellow | JSC-63555 (2005), Energy intake operating bands | Table | VERIFIED | NASA operating bands: 90–100% green, 80–90% yellow, <80% red. |
| SLEEP_DEFICIT | <6 h | [Barger et al. 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4188436/) | Table 2, Results (ISS actigraphy 6.09 h) | DESIGN DECISION | Observed mean is verified; it does not establish a safe minimum or this alert cutoff. |
| LOW_MOOD | ≤4 on ad hoc 1–10 scale | Application policy; Kroenke 2003 | PHQ-2 abstract | DESIGN DECISION | Current scale is unvalidated; NASA operational cognitive monitoring uses monthly WinSCAT. |
| EMCL/IMM condition vocabulary | EMCL ~100 conditions; IMM 100 conditions | [ExMC evidence report (EMCL JSC-65722; IMM)](https://ntrs.nasa.gov/api/citations/20170004604/downloads/20170004604.pdf); [NASA Appendix E](https://www.nasa.gov/reference/appendix-e-health-and-medical-care-technical-requirements/); [NASA IMM overview](https://www.nasa.gov/nasa-integrated-medical-model-imm-overview) | EMCL and IMM sections | VERIFIED | Used for condition names only; the IMM itself is a Monte Carlo mission-planning model, not a runtime classifier. |
| IMM-lite scoring model | confidence = min(1, Σ weights / saturation); floor 0.25; top 3 | v0.2 prototype | `src/astro_brain/conditions.py` | DESIGN DECISION | Not the IMM; not a calibrated probability; never a diagnosis. |
| HYPOVOLEMIC_SHOCK | EMCL “Hypovolemic Shock”; ICL116 | EMCL Table 2; SMEMCL 2011; HRP-48036 Rev B | Table 2; ICL116 | VERIFIED | ICL116 also lists CNES synonym “Acute Hypovolemia”; weights are ours. |
| SEPSIS | EMCL/IMM "Sepsis" | [NASA Appendix E](https://www.nasa.gov/reference/appendix-e-health-and-medical-care-technical-requirements/) | Other conditions not captured elsewhere | VERIFIED | Condition name only; weights are ours. |
| ALTITUDE_SICKNESS | EMCL “Altitude sickness” | EMCL Table 2; NASA Appendix E | Table 2; Table E.2-2 | VERIFIED | Hypoxia is ARCL88 only; weights are ours. |
| ACUTE_RADIATION_SYNDROME | EMCL/IMM "Acute radiation syndrome" | [NASA Appendix E](https://www.nasa.gov/reference/appendix-e-health-and-medical-care-technical-requirements/); [IMM overview](https://www.nasa.gov/nasa-integrated-medical-model-imm-overview) | Environmental or spaceflight induced medical conditions | VERIFIED | Condition name only; weights are ours. |
| CARDIAC_ARRHYTHMIA | EMCL "De Novo Cardiac Arrhythmia" | [SMEMCL 2011](https://ntrs.nasa.gov/api/citations/20110008645/downloads/20110008645.pdf) | Priority Condition list | VERIFIED | Condition name only; weights are ours. |
| SLEEP_DISORDER | IMM "Sleep Disorders" | [IMM overview](https://www.nasa.gov/nasa-integrated-medical-model-imm-overview) | Modeled Medical Conditions | VERIFIED | Condition name only; weights are ours. |
| DEPRESSION | IMM "Depression"; EMCL behavioral conditions | [IMM overview](https://www.nasa.gov/nasa-integrated-medical-model-imm-overview); [NASA Appendix E](https://www.nasa.gov/reference/appendix-e-health-and-medical-care-technical-requirements/) | Modeled Medical Conditions | VERIFIED | Condition name only; weights are ours. |
| NUTRITIONAL_DEFICIT | EMCL "Nutritional deficiency" | [NASA Appendix E](https://www.nasa.gov/reference/appendix-e-health-and-medical-care-technical-requirements/) | Environmental or spaceflight induced medical conditions | VERIFIED | Condition name only; weights are ours. |

No diagnosis is inferred from these flags. Sources identify provenance and limitations;
they do not turn operational prototype cutoffs into validated clinical rules.

| NEWS2 spaceflight validation | no validation found | RCP NEWS2 2017 | Recommendations; §3 | NOT FOUND | Terrestrial adult acute-illness tool; no astronaut/microgravity validation found. |
| CALORIC_LOW | 80–90% of EER | JSC-63555 (2005) | Energy intake operating bands | VERIFIED | Yellow operating band. |
| RESPIRATORY_INFECTION_LOWER | EMCL lower respiratory tract infection | EMCL Table 2 | Table 2 | VERIFIED | Weights are prototype. |
| CABIN_CO2_ELEVATED | ≥3.0 mmHg | NASA-STD-3001 Rev C [V2 6004] | 1-hour average | VERIFIED | Threshold source supplied by audit. |
| CABIN_CO2_HIGH | ≥7.6 mmHg | ISS Flight Rule B17-5 / OCHMO-TB-004 | Flight rule section | VERIFY | Operational red threshold pending document review. |
| PVT_SLOW | >500 ms | Basner & Dinges PVT-B | Lapse convention | VERIFY | PVT lapse threshold; spaceflight applicability pending. |
| IOP_HIGH | >21 mmHg | OCHMO/HRP SANS context | Ocular hypertension | VERIFY | Common screening boundary; astronaut threshold pending. |
| PHQ2_POSITIVE | ≥3 | Kroenke et al. 2003, J Gen Intern Med | 41(11):1284–92 | VERIFIED | Screening flag; not a diagnosis. |
| daily plans | exercise/nutrition plan bands | NASA SP-20250000273; NTRS 20110016265; JSC-63555 | VERIFY | DESIGN DECISION | Operational plan generation pending mission-specific review. |
| CO2_HEADACHE | weighted prototype | EMCL ICL64 Headache - CO2; CliFF RT p.8 | CliFF 2020 | VERIFIED | Code and resource source wired. |
| SANS | weighted prototype | NASA HRP Risk of SANS | VERIFY | VERIFY | EMCL name “VIIP” not confirmed. |
| IMM phase priors | listed multipliers | `docs/EVIDENCE_IMM.md` | §1 | DERIVED | Derived from the merged research register. |
| medical-kit resources | canonical CliFF Essential rows | `docs/EVIDENCE_IMM.md` | §3 | VERIFIED | RT/CRT status is explicit per condition. |
| IMM/CliFF register | phase priors and canonical resources | `docs/EVIDENCE_IMM.md` | §§1–3 | DERIVED / VERIFIED | Detailed provenance and legacy map. |
| Mars communication delay | up to ~22 minutes one way | NASA Mars facts | — | VERIFY | Mission-operations context only. |
