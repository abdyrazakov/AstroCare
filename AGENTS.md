# astro-brain — Integration Contract

Health Monitoring Software for Astronauts (NASA Space Apps). This is the only document the
data team and the presentation team need to read. It defines exactly what goes into the
brain and exactly what comes out. You never need to open our source code.

---

## 1. Project zones

Three teams work in parallel on three independent zones. The **data team** produces vitals
samples (from sensors, a simulator, or a mock) as JSON matching the *input contract* below and
hands them to the brain. The **brain** (this repository: Scoring Engine + Doctor Layer) validates
each sample, computes a NEWS2 score and a set of clinical/operational flags, derives a single
`alertLevel`, and attaches a short doctor recommendation. The **presentation team** consumes the
brain's *output contract* JSON and renders it (dashboard, alerts, history); it never computes
medical logic itself. Each zone can be developed and tested without the other two as long as
both contracts are respected.

---

## 2. Input contract (data team → brain)

One sample = one JSON object describing one astronaut at one instant. All numbers are plain
JSON numbers; booleans are JSON `true`/`false` (never `0`/`1`).

| field | type | unit | range | required | meaning |
|---|---|---|---|---|---|
| `timestamp` | string | ISO-8601 UTC | non-empty, e.g. `"2026-11-14T10:00:00Z"` | yes | When the sample was taken. Passed through unchanged. |
| `astronaut_id` | string | — | non-empty | yes | Stable identifier of the crew member, e.g. `"ASTRO-01"`. |
| `hr` | int | bpm | 0 – 300 | yes | Heart rate. |
| `spo2` | int | % | 0 – 100 | yes | Peripheral oxygen saturation. |
| `bp` | object | mmHg | `{"systolic": int 0–300, "diastolic": int 0–300}`, diastolic ≤ systolic | yes | Blood pressure. |
| `temp_c` | number | °C | 25 – 45 | yes | Core/body temperature. |
| `resp_rate` | int | breaths/min | 0 – 80 | yes | Respiratory rate. |
| `radiation_dose_rate` | number | µSv/h | ≥ 0 | yes | Current absorbed dose rate. ISS nominal background is ~12–30 µSv/h. |
| `exercise_minutes_today` | int | min | 0 – 1440 | yes | Exercise completed so far today. |
| `required_exercise_minutes` | int | min | 1 – 1440 | yes | Daily exercise target for this astronaut. |
| `caloric_intake` | int | kcal | 0 – 20000 | yes | Calories consumed today. |
| `caloric_target` | int | kcal | 1 – 20000 | yes | Daily caloric target. |
| `sleep_hours` | number | h | 0 – 24 | yes | Sleep in the last sleep period. |
| `mood_score` | int | — | 1 – 10 | yes | Self-reported mood, 10 = best. |
| `on_supplemental_o2` | bool | — | `true` / `false` | no (default `false`) | Whether the astronaut is breathing supplemental oxygen (NEWS2 input). |
| `consciousness` | string | — | `"alert"` \| `"altered"` | no (default `"alert"`) | Level of consciousness (NEWS2 input). |
| `noaa_s_scale` | int or null | NOAA S-scale | 0 – 5 or `null` | no (default `null`) | Current NOAA Solar Radiation Storm scale, if known. |
| `radiation_dose_30day_msv` | number or null | mSv | ≥ 0 or `null` | no (default `null`) | Dose over the last 30 days; absent or null disables this rule. Compared numerically to a BFO mGy-Eq limit as a prototype assumption. |
| `radiation_dose_career_msv` | number or null | mSv | ≥ 0 or `null` | no (default `null`) | Career effective dose; absent or null disables this rule. |

Type rules (enforced):

- **Integers**: a JSON number with an integer value is accepted for an `int` field (`72` and
  `72.0` are both fine); `72.5` is rejected.
- **Booleans are not numbers**: `true` for `hr` is rejected, `1` for `on_supplemental_o2` is rejected.
- **Ranges are inclusive** on both ends. `NaN`/`Infinity` are rejected.
- **Optional fields**: omit the key to get the default. If you send the key, the value must be valid
  (`"consciousness": null` is rejected; `"noaa_s_scale": null` is the one allowed null).
- **Unknown extra keys are ignored** (forward compatibility). Add new fields freely, but they will
  not be used until the contract is updated.

**Samples that violate this contract are rejected with an error naming the field; the brain never
guesses.** Error messages look like `'spo2' out of range: 101 not within [0, 100]`,
`'hr' is missing (required field)`, `'bp.diastolic' (120) must not exceed 'bp.systolic' (80)`.

### Example — nominal sample (only required fields)

```json
{
  "timestamp": "2026-11-14T10:00:00Z",
  "astronaut_id": "ASTRO-01",
  "hr": 72,
  "spo2": 98,
  "bp": { "systolic": 120, "diastolic": 80 },
  "temp_c": 36.8,
  "resp_rate": 14,
  "radiation_dose_rate": 20.5,
  "exercise_minutes_today": 90,
  "required_exercise_minutes": 120,
  "caloric_intake": 2600,
  "caloric_target": 2800,
  "sleep_hours": 7.5,
  "mood_score": 8
}
```

### Example — with all optional fields set (degraded astronaut during a solar storm)

```json
{
  "timestamp": "2026-11-14T10:05:00Z",
  "astronaut_id": "ASTRO-02",
  "hr": 118,
  "spo2": 91,
  "bp": { "systolic": 88, "diastolic": 56 },
  "temp_c": 38.6,
  "resp_rate": 26,
  "radiation_dose_rate": 1450.0,
  "exercise_minutes_today": 20,
  "required_exercise_minutes": 120,
  "caloric_intake": 1500,
  "caloric_target": 2800,
  "sleep_hours": 4.0,
  "mood_score": 3,
  "on_supplemental_o2": true,
  "consciousness": "altered",
  "noaa_s_scale": 3,
  "radiation_dose_30day_msv": 150.0,
  "radiation_dose_career_msv": 120.0
}
```

---

## 3. Output contract (brain → presentation team)

One output object per processed input sample. Keys are **camelCase**.

```json
{
  "timestamp": "2026-11-14T10:00:00Z",
  "astronautId": "ASTRO-01",
  "alertLevel": "yellow",
  "news2Score": 2,
  "activeFlags": ["RADIATION_ELEVATED", "SLEEP_DEFICIT"],
  "flagDetails": [
    {
      "code": "RADIATION_ELEVATED",
      "severity": "yellow",
      "message": "Radiation dose rate 140.0 µSv/h is above the 100 µSv/h elevated threshold.",
      "value": 140.0,
      "threshold": 100
    },
    {
      "code": "SLEEP_DEFICIT",
      "severity": "yellow",
      "message": "Only 4.5 h of sleep; minimum is 6 h.",
      "value": 4.5,
      "threshold": 6
    }
  ],
  "doctorRecommendation": "Radiation is elevated but not critical; move to the shielded area until the dose rate drops. Sleep deficit may degrade reaction time, so schedule a rest period before any EVA tasks. Re-check vitals in 30 minutes.",
  "doctorSource": "llm"
}
```

| field | type | meaning |
|---|---|---|
| `timestamp` | string | Copied from the input sample, unchanged. |
| `astronautId` | string | Copied from the input `astronaut_id`. |
| `alertLevel` | `"green"` \| `"yellow"` \| `"red"` | Overall status. **Worst severity among active flags; no flags → `"green"`.** This is the single value to colour the UI by. |
| `news2Score` | int (0–20) | National Early Warning Score 2, computed from `hr`, `spo2`, `bp.systolic`, `temp_c`, `resp_rate`, `on_supplemental_o2`, `consciousness`. 0 = all vitals nominal. |
| `activeFlags` | array of string | Codes of all flags currently active (same order as `flagDetails`). Empty array when everything is nominal. |
| `flagDetails` | array of object | One entry per active flag: `code`, `severity` (`"yellow"` or `"red"`), human-readable `message`, the measured `value` that triggered it and the `threshold` it was compared with (`value`/`threshold` may be `null` when there is no single number, e.g. `CONSCIOUSNESS_ALTERED`). |
| `doctorRecommendation` | string | 2–4 sentences of plain-language guidance for the crew. Always present, even at green. |
| `doctorSource` | `"llm"` \| `"cache"` \| `"fallback"` | Where the recommendation came from: live language model, a cached answer for an identical flag set, or a built-in rule-based text when the model is unavailable. Presentation may show this as a small badge; it does not change how the text should be displayed. |

### Flag codes

NEWS2 components score 0–3 each. A component flag is emitted when **that component scores ≥ 2**.

| code | severity | trigger |
|---|---|---|
| `HR_HIGH` | yellow | Heart-rate NEWS2 component ≥ 2 (high side). |
| `HR_LOW` | yellow | Heart-rate NEWS2 component ≥ 2 (low side). |
| `SPO2_LOW` | yellow | SpO₂ NEWS2 component ≥ 2. |
| `BP_LOW` | yellow | Systolic BP NEWS2 component ≥ 2 (low side). |
| `BP_HIGH` | yellow | Systolic BP NEWS2 component ≥ 2 (high side). |
| `TEMP_HIGH` | yellow | Temperature NEWS2 component ≥ 2 (high side). |
| `TEMP_LOW` | yellow | Temperature NEWS2 component ≥ 2 (low side). |
| `RESP_HIGH` | yellow | Respiratory-rate NEWS2 component ≥ 2 (high side). |
| `RESP_LOW` | yellow | Respiratory-rate NEWS2 component ≥ 2 (low side). |
| `CONSCIOUSNESS_ALTERED` | yellow | `consciousness == "altered"` (NEWS2 component = 3). |
| `NEWS2_MEDIUM` | yellow | Two variants: **(a) total** — NEWS2 total 5–6; `value`/`threshold` = the total/5, message `"NEWS2 total {total} is medium risk."`. **(b) single parameter** — total < 5 but some component scores 3 (and no component is on the total-5–6 path); `value`/`threshold` = 3, message `"NEWS2 single parameter at maximum score (3) — {component} — urgent re-check required."` where `{component}` names the scoring-3 component(s) (e.g. `spo2`, `bp_systolic`), joined with `, `. If total is 5–6, variant (a) applies even when a component also scores 3. |
| `NEWS2_HIGH` | red | NEWS2 total ≥ 7. |
| `RADIATION_ELEVATED` | yellow | `radiation_dose_rate ≥ 100 µSv/h` **or** `noaa_s_scale ≥ 2`. |
| `RADIATION_CRITICAL` | red | `radiation_dose_rate ≥ 1000 µSv/h` **or** `noaa_s_scale ≥ 3`. |
| `RADIATION_30DAY_LIMIT` | yellow / red | One flag: dose ≥ 125 mSv (50% of 250) is yellow; ≥ 250 mSv (100%) is red. Numeric BFO mGy-Eq comparison is an assumption. `value` = dose; `threshold` = triggered mSv threshold; message gives percent of limit. |
| `RADIATION_CAREER_LIMIT` | yellow / red | One flag: career dose ≥ 300 mSv (50% of 600) is yellow; ≥ 600 mSv (100%) is red. `value` = dose; `threshold` = triggered mSv threshold; message gives percent of limit. |
| `EXERCISE_DEFICIT` | yellow | `exercise_minutes_today < 50 %` of `required_exercise_minutes`. |
| `CALORIC_DEFICIT` | yellow | `caloric_intake < 70 %` of `caloric_target`. |
| `SLEEP_DEFICIT` | yellow | `sleep_hours < 6`. |
| `LOW_MOOD` | yellow | `mood_score ≤ 4`. |

Reference: ISS nominal background radiation is ~12–30 µSv/h, so a nominal sample should never
trigger a radiation flag.

Rule for the UI: **`alertLevel` = worst severity among active flags; no flags → `green`.** Only
`NEWS2_HIGH` and `RADIATION_CRITICAL` can make a sample red. Do not recompute this from the
flags on the presentation side; read `alertLevel` directly.

---

## 4. Integration

### In-process (Python)

```python
from astro_brain.pipeline import Brain

brain = Brain()
output = brain.process(raw_dict)   # raw_dict: input-contract JSON object (already json.loads'ed)
# output: output-contract dict, ready for json.dumps
```

`Brain().process` raises `astro_brain.contract.ContractError` (a `ValueError`) if the input
violates the contract; the message names the offending field.

### HTTP test dashboard (local, default port 8765)

| method | path | body | returns |
|---|---|---|---|
| `POST` | `/ingest` | one input-contract JSON object | the output-contract JSON for that sample (HTTP 200), or HTTP 400 with `{"error": "<message naming the field>"}` on contract violation |
| `GET` | `/state` | — | the latest output-contract JSON produced (HTTP 200), or HTTP 200 with `{"status": "no data yet"}` if nothing has been ingested yet |
| `GET` | `/state?astronaut_id=X` | — | latest output for X, or HTTP 200 with `{"status":"no data yet","astronautId":"X"}` |
| `GET` | `/state/all` | — | HTTP 200 with `{"astronauts":{"ASTRO-01":{...}},"count":N}` |
| `GET` | `/history` | — | HTTP 200 with the last 50 outputs in global arrival order |
| `GET` | `/history?astronaut_id=X` | — | HTTP 200 with the last 50 outputs for X, or `[]` |
| `GET` | `/` | — | plain text: one latest-output block per astronaut, followed by doctorStats |

Example:

```bash
curl -s -X POST http://localhost:8765/ingest \
  -H 'Content-Type: application/json' \
  -d @sample.json

curl -s http://localhost:8765/state
```

The dashboard is a development aid for the data and presentation teams to test against; it is
not the production transport.

---

## 5. Change policy

- Both contracts are **fixed by the orchestrator**. Neither team changes a field name, type,
  unit, range or default on its own.
- Want a change? Propose it to the orchestrator; it is applied to this document first, then to
  code, then announced to all three teams.
- The data team **must announce** any format change before shipping it, and **must never
  silently change** units, key names or ranges. Adding an extra key is allowed without
  announcement (it is ignored), but it will not be used until the contract is updated.
- Version of this contract: `astro-brain 0.1.0`.

---

## 6. Agent roster (for AI agents working in this repository)

| agent | zone |
|---|---|
| `contract-agent` | `src/astro_brain/contract.py`, `src/astro_brain/flags.py`, their tests, `AGENTS.md`, `pyproject.toml`. Owns input/output contract definitions. |
| `scoring-agent` | `src/astro_brain/news2.py`, `src/astro_brain/radiation.py`, `src/astro_brain/lifestyle.py`, `src/astro_brain/vitals_flags.py`, `src/astro_brain/scoring.py` (NEWS2 + all flag rules from section 3) and their tests. |
| `doctor-agent` | `src/astro_brain/doctor/` (`__init__.py`, `layer.py`, `fallback.py`, `ollama_client.py`, `prompts.py` — recommendation text: llm / cache / fallback) and its tests, `src/astro_brain/pipeline.py` (`Brain`). |
| `brain-qa-agent` | `src/astro_brain/mock.py`, `src/astro_brain/qa.py`, `examples/`, end-to-end tests, mock sample generators, contract conformance checks. |
| `dashboard-agent` | `src/astro_brain/dashboard.py` (HTTP `POST /ingest`, `GET /state` on port 8765) and its tests. |

All agents: stdlib only, work inside this repository, respect the two contracts above, and
**do not touch the data pipeline or the presentation UI** — those belong to the other teams.
