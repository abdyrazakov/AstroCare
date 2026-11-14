# AstroCare v0.6 integration

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

## v0.4 operational notes

The Astralis feeder is run with the simulator interpreter and `PYTHONPATH=src`; the brain remains stdlib-only, while Astralis requires `pydantic` and `numpy` (it does not require `pyarrow`). The Astralis SPE scenario grows with its OU process toward 1.05 mSv/h; in an observed run `RADIATION_ELEVATED` appeared around mission minute 10. Use `controller.advance(N)` for accelerated runs. The SPE scenario is observed; other scenarios remain expected until a matching run is captured.

```bash
curl -X POST localhost:8765/ask -H 'Content-Type: application/json' \
  -d '{"astronaut_id":"A1","question":"Should I do my ARED session today?"}'
```

The frontend AI Assistant tab may call this HTTP endpoint directly.

Mission history is available at `/log?astronaut_id=ASTRO-01` and `/report?astronaut_id=ASTRO-01`; append `format=text` for an SBAR summary.

## Ollama on a GPU laptop

These are Ollama settings, not AstroBrain code: set `OLLAMA_KEEP_ALIVE=24h` and
`OLLAMA_FLASH_ATTENTION=1`, then verify `ollama ps` reports the model at 100% GPU.
Warm the model before the demo; the expected first recommendation has
`doctorSource: "llm"` within roughly three seconds.

For Mars operations, use the single wording “up to ~22 minutes one way” for
communication delay. Source: NASA Mars facts — VERIFY.
