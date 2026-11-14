# Astralis validation

Run with the simulator interpreter:

```bash
PYTHONPATH=src /tmp/astralis/.venv/bin/python -m astro_brain.qa_astralis \
  --astralis-path /tmp/astralis --mission-seconds 2400 --step 15
```

The run below uses scenario-specific expected signals. Generic signals do not
count toward PASS.

| scenario | signal | first mission second | driver value | EMCL state | zones |
|---|---|---:|---:|---|---|
| HYPERCAPNIC_CABIN | CABIN_CO2_ELEVATED | 450 | ppCO₂ 3.0039 mmHg | CO2_HEADACHE / ICL64 | lungs, brain |
| HYPERCAPNIC_CABIN | CO2_HEADACHE | 450 | ppCO₂ 3.0039 mmHg | CO2_HEADACHE / ICL64 | lungs, brain |
| SOLAR_PARTICLE_EVENT | RADIATION_ELEVATED | 600 | 0.1098 mSv/h simulator input | radiation exposure | skin_immune |
| SANS_FLUID_SHIFT | not detected | — | — | SANS / ICL100 | eyes, brain |
| NEUROCOGNITIVE_FATIGUE | not detected | — | — | sleep/cognitive condition | brain |
| MISSED_ARED | EXERCISE_DEFICIT | 15 | daily `ared_exercise_completed=false` | operational deficit | muscles_legs, skeleton_lower |

## Simulator baseline observations

The simulator emits background `TEMP_LOW` around mission second 555 with
`temp_c ≈ 34.8479 °C`; this is below the brain's existing 35 °C low threshold
and is retained as a simulator baseline observation. `NEWS2_MEDIUM` appears at
the same point as a consequence of those synthetic vitals. `EXERCISE_DEFICIT`
appears at second 15 when the first daily record has
`ared_exercise_completed=false`; it is expected generic noise unless the
scenario is `MISSED_ARED`. No adapter unit correction was justified by these
observations.

SANS and neurocognitive signals were not detected in 2400 seconds. The
scenario catalog describes longer trajectories, so this short validation run
does not establish absence of those conditions.
