# Astralis validation

Run with the simulator interpreter so its `pydantic` and `numpy` environment is used:

```bash
PYTHONPATH=src /tmp/astralis/.venv/bin/python -m astro_brain.qa_astralis --astralis-path /tmp/astralis --mission-seconds 600 --step 30
```

The shortened run detected `CABIN_CO2_ELEVATED` in `HYPERCAPNIC_CABIN` and `RADIATION_ELEVATED` in `SOLAR_PARTICLE_EVENT`. The other scenario-specific signals require longer mission time or daily logs; generic simulator signals are reported separately and are not treated as proof of the scenario-specific condition.

| scenario | brain signal observed | EMCL state | 3D zones |
|---|---|---|---|
| HYPERCAPNIC_CABIN | CABIN_CO2_ELEVATED | expected HYPERCAPNIA | lungs, brain |
| SOLAR_PARTICLE_EVENT | RADIATION_ELEVATED | expected ARS only at higher exposure | skin_immune |
| SANS_FLUID_SHIFT | expected, not observed in 600 s | SANS | eyes, brain |
| NEUROCOGNITIVE_FATIGUE | expected, not observed in 600 s | expected fatigue/sleep | brain |
| MISSED_ARED | requires daily log | no flag without daily log | muscles_legs |
