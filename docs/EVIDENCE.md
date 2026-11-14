# Evidence register

Статусы VERIFY закрывает исследователь команды; пороги со статусом ASSUMPTION подлежат пересмотру до сдачи.

VERIFIED means the cited source was checked, not that the prototype is clinically validated.
Source checks: 2026-11-14. New dose fields are supplied totals, not integrated from sample timestamps.

| flag/threshold | value | source | section/page | status (VERIFIED / VERIFY / ASSUMPTION / DESIGN DECISION) | note |
|---|---|---|---|---|---|
| CAREER_EFFECTIVE_DOSE_LIMIT_MSV | 600 mSv | [NASA-STD-3001 Vol.1](https://www.nasa.gov/reference/4-0-human-performance/) | §4.8.2, V1 4030 | VERIFIED | Universal career spaceflight effective-dose limit; NASA-specific dose model. |
| THIRTY_DAY_BFO_LIMIT_MGY_EQ | 250 mGy-Eq | [NASA-STD-3001 Vol.1](https://www.nasa.gov/reference/4-0-human-performance/) | Table 4.8-1, Blood-forming Organs, 30-Day | VERIFIED | Organ-specific dose, not effective dose in mSv. |
| RADIATION_30DAY_LIMIT | yellow ≥125 mSv; red ≥250 mSv | [NASA table](https://www.nasa.gov/reference/4-0-human-performance/) + prototype choice | Table 4.8-1 | ASSUMPTION | Direct numeric comparison of mSv to mGy-Eq is not a physical unit conversion; organ/RBE data are absent. |
| RADIATION_CAREER_LIMIT | yellow ≥300 mSv; red ≥600 mSv | [NASA limit](https://www.nasa.gov/reference/4-0-human-performance/) + prototype choice | §4.8.2, V1 4030 | DESIGN DECISION | 50% warning and red at the limit are application severities, not NASA clinical triage. |
| WARN_FRACTION | 0.5 | v0.2 specification | Operational policy | DESIGN DECISION | Warn at half of either cumulative limit. |
| CRITICAL_FRACTION | 1.0 | v0.2 specification | Operational policy | DESIGN DECISION | Red at or above the cumulative limit. |
| radiation_dose_career_msv input provenance | NASA effective dose | [NASA definition](https://www.nasa.gov/reference/4-0-human-performance/) | §4.8.2 note | VERIFY | Data team must confirm input dosimetry uses the NASA effective-dose model. |
| NASA edition provenance | Rev C / 2022+; NCRP 2021 attribution | v0.2 specification; [NASA standard landing page](https://www.nasa.gov/reference/nasa-std-3001v1/) | Exact revision/date and NCRP document not checked | VERIFY | Values/sections checked in official HTML; edition history and NCRP attribution not asserted. |
| nominal mock cumulative doses | 15 mSv / 30 days; 120 mSv career | v0.2 specification | Synthetic fixture | ASSUMPTION | 15 assumes 0.5 mSv/day; neither value is a measured crew history or safety threshold. |
| cumulative-dose mock anomalies | 150 mSv / 30 days; 660 mSv career | v0.2 specification and limits above | Synthetic fixture | DESIGN DECISION | Test stimuli for warning and exceeded-limit paths, not additional thresholds. |
