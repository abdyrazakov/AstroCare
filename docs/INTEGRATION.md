# AstroCare v0.3 integration

Run the three repositories locally:

1. Brain: `.venv/bin/python -m astro_brain.dashboard --ws-port 8787`.
2. Simulator: `.venv/bin/python -m astro_brain.feed_astralis --live --astralis-path /tmp/astralis --scenario SOLAR_PARTICLE_EVENT`.
3. Frontend: `NEXT_PUBLIC_BRAIN_WS_URL=ws://localhost:8787 npm run dev` in `/tmp/astrocare-fe`.

The frontend should show live crew ticks, alert severity, mapped body zones, active flags and the doctor recommendation. Brain radiation input is µSv/h; ASTRALIS supplies mSv/h and the adapter multiplies by 1000. When a daily record is present, `ared_exercise_completed` maps to the target minutes or zero; this is an adapter heuristic.

| ASTRALIS scenario | Expected brain output | 3D zones |
|---|---|---|
| HYPERCAPNIC_CABIN | `CABIN_CO2_ELEVATED` / `CABIN_CO2_HIGH` | lungs |
| SOLAR_PARTICLE_EVENT | `RADIATION_*`, possibly `ACUTE_RADIATION_SYNDROME` | skin_immune, skeleton_upper/lower |
| SANS_FLUID_SHIFT | `IOP_HIGH` | eyes |
| NEUROCOGNITIVE_FATIGUE | `PVT_SLOW`, `SLEEP_DEFICIT` | brain |
| MISSED_ARED | `EXERCISE_DEFICIT` | muscles_legs, skeleton_lower |

Scenario mappings are expected until a live ASTRALIS run is completed. JSONL mode is available with `--jsonl PATH [--daily PATH]`; `--inprocess` prints alert level, flags and likely conditions without HTTP.
