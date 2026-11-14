# Evidence register

Статусы VERIFY закрывает исследователь команды; пороги со статусом ASSUMPTION подлежат пересмотру до сдачи.

VERIFIED means the cited source was checked, not that the prototype is clinically validated.
Source checks: 2026-11-14. NEWS2 alert colors and component-flag emission are prototype choices. New dose fields are supplied totals, not integrated from sample timestamps.

| flag/threshold | value | source | section/page | status (VERIFIED / VERIFY / ASSUMPTION / DESIGN DECISION) | note |
|---|---|---|---|---|---|
| CAREER_EFFECTIVE_DOSE_LIMIT_MSV | 600 mSv | [NASA-STD-3001 Vol.1](https://www.nasa.gov/reference/4-0-human-performance/) | §4.8.2, V1 4030 | VERIFIED | Universal career spaceflight effective-dose limit; NASA-specific dose model. |
| THIRTY_DAY_BFO_LIMIT_MGY_EQ | 250 mGy-Eq | [NASA-STD-3001 Vol.1](https://www.nasa.gov/reference/4-0-human-performance/) | Table 4.8-1, Blood-forming Organs, 30-Day | VERIFIED | Organ-specific dose, not effective dose in mSv. |
| RADIATION_30DAY_LIMIT | yellow ≥125 mSv; red ≥250 mSv | [NASA table](https://www.nasa.gov/reference/4-0-human-performance/) + prototype choice | Table 4.8-1 | ASSUMPTION | Direct numeric comparison of mSv to mGy-Eq is not a physical unit conversion; organ/RBE data are absent. |
| RADIATION_CAREER_LIMIT | yellow ≥300 mSv; red ≥600 mSv | [NASA limit](https://www.nasa.gov/reference/4-0-human-performance/) + prototype choice | §4.8.2, V1 4030 | DESIGN DECISION | 50% warning and red at the limit are application severities, not NASA clinical triage. |
| WARN_FRACTION | 0.5 | v0.2 specification | Operational policy | DESIGN DECISION | Warn at half of either cumulative limit. |
| CRITICAL_FRACTION | 1.0 | v0.2 specification | Operational policy | DESIGN DECISION | Red at or above the cumulative limit. |
| radiation_dose_career_msv input provenance | NASA effective dose | [NASA definition](https://www.nasa.gov/reference/4-0-human-performance/) | §4.8.2 note | VERIFY | Data team must confirm input dosimetry uses the NASA effective-dose model. |
| NASA edition provenance | Rev C, approved 2023-09-15 | [NASA PDF](https://www.nasa.gov/wp-content/uploads/2023/11/nasa-std-3001-vol-1-rev-c-with-signature.pdf) | title page; §4.8.2 p.39; Table 4.8-1 p.40 | VERIFIED | Checked the actual Rev C PDF; not a 2022 revision. |
| NCRP 2021 attribution | origin of universal 600 mSv recommendation | v0.2 specification | Exact document not established | VERIFY | Do not attribute this recommendation to NCRP 2021 without researcher confirmation. |
| nominal mock cumulative doses | 15 mSv / 30 days; 120 mSv career | v0.2 specification | Synthetic fixture | ASSUMPTION | 15 assumes 0.5 mSv/day; neither value is a measured crew history or safety threshold. |
| cumulative-dose mock anomalies | 150 mSv / 30 days; 660 mSv career | v0.2 specification and limits above | Synthetic fixture | DESIGN DECISION | Test stimuli for warning and exceeded-limit paths, not additional thresholds. |
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
| ISS background context | 12–30 µSv/h | Legacy contract; exact primary citation not established | — | VERIFY | Context only; not a NASA permissible-exposure limit. |
| EXERCISE_DEFICIT | <50% prescribed minutes | ISS MORD exercise prescription; [NASA MORD context](https://www.nasa.gov/reference/6-0-medical-operations/) | Specific ISS MORD edition/section not verified | VERIFY | MORD exists; the 50% alert is a design decision, not a verified MORD cutoff. |
| CALORIC_DEFICIT | <70% caloric target | JSC-63555; [NASA handbook reference](https://www.nasa.gov/wp-content/uploads/2023/03/human-integration-design-handbook-revision-1.pdf) | Exact JSC-63555 section not verified | VERIFY | Document identified through NASA handbook; 70% is a design decision, not a verified nutrition standard. |
| SLEEP_DEFICIT | <6 h | [Barger et al. 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4188436/) | Table 2, Results (ISS actigraphy 6.09 h) | DESIGN DECISION | Observed mean is verified; it does not establish a safe minimum or this alert cutoff. |
| LOW_MOOD | ≤4 on ad hoc 1–10 scale | Application policy; [Kroenke et al. 2003](https://pubmed.ncbi.nlm.nih.gov/14583691/) | PHQ-2 abstract, context only | DESIGN DECISION | Current scale is not PHQ-2 and has no validated mapping to it; PHQ-2 implementation awaits phase 0. |

No diagnosis is inferred from these flags. Sources identify provenance and limitations;
they do not turn operational prototype cutoffs into validated clinical rules.
