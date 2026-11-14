# IMM/CliFF evidence register

This register records the research-backed inputs used by `phase_priors.py` and
`cliff_resources.py`. Derived phase values are arithmetic splits of published
rates, not calibrated clinical probabilities.

## 1. IMM priors

| code | EMCL/ICL | measure | phase_1 | phase_2 | source | section | status | note |
|---|---|---:|---:|---:|---|---|---|---|
| HYPOVOLEMIC_SHOCK | ICL116 | rate | 8.78e-6 | 3.073e-4 | IMM research report | §3 | DERIVED | general-rate split |
| SEPSIS | ICL84 | rate | 3.288e-5 | 1.151e-3 | IMM research report | §3 | DERIVED | general-rate split |
| ACUTE_RADIATION_SYNDROME | ICL4 | conditional proportion | 0.05 | 0.05 | IMM research report | §3 | VERIFIED_CONDITIONAL | conditional on SPE |
| CARDIAC_ARRHYTHMIA | ICL10 | rate | 6.478e-6 | 2.267e-4 | IMM research report | §3 | DERIVED | sex-mean rate |
| SLEEP_DISORDER | ICL95 | proportion | 0.4721 | 0 | IMM research report | §3 | VERIFIED | SA onset |
| SANS | ICL100 | proportion | 0.2789 | 0 | IMM research report | §3 | VERIFIED | ongoing cases can persist |
| CO2_HEADACHE | ICL64 | rate | 0.02078 | 0.7272 | IMM research report | §3 | DERIVED | Headache - CO2 |
| RESPIRATORY_INFECTION_LOWER | ICL81/82 | rate | 0.01054 | 0.3689 | IMM research report | §3 | DERIVED | general-rate split |
| DEPRESSION | ICL15 | rate | 4.452e-5 | 1.558e-3 | IMM research report | §3 | DERIVED | sex-mean rate |
| ALTITUDE_SICKNESS | — | none | — | — | no record found | §4 | NOT_FOUND | no RT/incidence row |
| NUTRITIONAL_DEFICIT | — | none | — | — | no record found | §4 | NOT_FOUND | no RT/incidence row |

### Multiplier methodology

| mechanism/tier | phase 1 | phase 2 | status |
|---|---:|---:|---|
| SA | ×1.25 | ×0.85 | DESIGN DECISION |
| high-rate general | ×1.0 | ×1.0 | DESIGN DECISION |
| mid-rate general | ×0.9 | ×0.9 | DESIGN DECISION |
| low-rate general | ×0.8 | ×0.8 | DESIGN DECISION |
| spe_conditional | ×1.0 | ×1.0 | DESIGN DECISION |
| default | ×1.0 | ×1.0 | DESIGN DECISION |

## 2. CliFF resource provenance

Essential resources are transcribed from CliFF RT tables dated 2020-05-11;
SANS uses CRT prose dated 2022-09-19 and has no published quantities.

## 3. State/resource rows

| condition | source | status | note |
|---|---|---|---|
| HYPOVOLEMIC_SHOCK | Traumatic Hypovolemic Shock Cliff, 2020-05-11, RT pp.7–9 | VERIFIED_RT | canonical Essential rows |
| SEPSIS | Sepsis Cliff, 2020-05-11, RT pp.9–11 | VERIFIED_RT | canonical Essential rows |
| ACUTE_RADIATION_SYNDROME | ARS Cliff, 2020-05-11, RT pp.6–7 | VERIFIED_RT | canonical Essential rows |
| CARDIAC_ARRHYTHMIA | AF/AFL Cliff, 2020-05-11, RT p.6 | VERIFIED_RT | canonical Essential rows |
| SLEEP_DISORDER | Insomnia Cliff, 2020-05-11, RT p.5 | VERIFIED_RT | canonical Essential rows |
| DEPRESSION | Depression Cliff, 2020-05-11, RT p.5 | VERIFIED_RT | canonical Essential rows |
| CO2_HEADACHE | Headache (CO2-induced) Cliff, 2020-05-11, RT p.8 | VERIFIED_RT | EMCL ICL64 |
| SANS | ICL100 SANS Cliff, 2022-09-19, CRT prose p.6 | VERIFIED_CRT_PROSE | units unavailable |
| RESPIRATORY_INFECTION_LOWER | Respiratory Infection Cliff, 2020-05-11, RT p.6 | VERIFIED_RT | canonical Essential rows |
| ALTITUDE_SICKNESS | — | NO_RT | no CliFF RT |
| NUTRITIONAL_DEFICIT | — | NO_RT | no CliFF RT |

### LEGACY_CODE_MAP

The v0.4 provisional names are accepted at input and mapped only when an
honest canonical CliFF code exists. Unknown names are ignored; they are not
validation errors. A null map means the provisional concept has no Essential
RT equivalent and is therefore not silently invented.

| legacy | canonical | rationale |
|---|---|---|
| IV_FLUIDS | IV_FLUID_1L | direct fluid row |
| IV_ACCESS_KIT | IV_CATHETER | direct procedure row |
| ANTIBIOTICS_BROAD_SPECTRUM | ERTAPENEM_1G | antibiotic row |
| PULSE_OXIMETER | BLOOD_OXIMETER | equivalent measurement device |
| SUPPLEMENTAL_O2 | VARIABLE_OXYGEN_SYSTEM | direct oxygen-system row |
| ANTIEMETICS | ONDANSETRON_8MG | direct antiemetic row |
| ECG_MONITOR | ECG_MONITOR | exact match |
| BETA_BLOCKER | METOPROLOL_50MG | direct medication row |
| SLEEP_AID | ZOLPIDEM_5MG | direct insomnia row |
| SSRI | SERTRALINE_50MG | direct medication row |
| BHP_TELECONSULT | PSYCHOTHERAPY | closest CliFF BHP service |

## 4. Open questions

- SANS incidence differs between NASA-STD-3001 Table E.2-1 and the CliFF-derived
  observed proportion; the selected value is documented in the research report.
- Full CRT capability quantities are in an external Excel/IMPACT-MD source and
  are not represented by the RT-only table.
- NO_RT states require a researcher-supplied resource source before resources
  can be asserted.
