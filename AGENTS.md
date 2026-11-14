# astro-brain — Integration Contract

Health Monitoring Software for Astronauts (NASA Space Apps). This is the only document the
data team and the presentation team need to read. It defines exactly what goes into the
brain and exactly what comes out. You never need to open our source code.

---

## 1. Project zones

Three teams work in parallel on three independent zones. The **data team** produces vitals
samples (from sensors, a simulator, or a mock) as JSON matching the *input contract* below and
hands them to the brain. The **brain** (this repository: Scoring Engine + Doctor Layer) validates
each sample, computes a NEWS2 score and a set of clinical/operational flags, ranks IMM-lite
condition candidates, derives a single `alertLevel`, and attaches a short doctor recommendation. The **presentation team** consumes the
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
| `radiation_dose_rate` | number | µSv/h | ≥ 0 | yes | Current absorbed dose rate. ISS nominal background is ~0.2–0.5 mSv/day (≈8–21 µSv/h), episodes up to 1.2 mSv/day (≈50 µSv/h). |
| `exercise_minutes_today` | int or null | min | 0 – 1440 or null | no (paired with required_exercise_minutes) | Exercise completed so far today. |
| `required_exercise_minutes` | int or null | min | 1 – 1440 or null | no (paired with exercise_minutes_today) | Daily exercise target for this astronaut. |
| `caloric_intake` | int or null | kcal | 0 – 20000 or null | no (paired with caloric_target) | Calories consumed today. |
| `caloric_target` | int or null | kcal | 1 – 20000 or null | no (paired with caloric_intake) | Daily caloric target. |
| `sleep_hours` | number or null | h | 0 – 24 or null | no | Sleep in the last sleep period. |
| `mood_score` | int or null | — | 1 – 10 or null | no | Self-reported mood, 10 = best. |
| `on_supplemental_o2` | bool | — | `true` / `false` | no (default `false`) | Whether the astronaut is breathing supplemental oxygen (NEWS2 input). |
| `consciousness` | string | — | `"alert"` \| `"altered"` | no (default `"alert"`) | Level of consciousness (NEWS2 input). |
| `noaa_s_scale` | int or null | NOAA S-scale | 0 – 5 or `null` | no (default `null`) | Current NOAA Solar Radiation Storm scale, if known. |
| `bfo_dose_30day_mgy_eq` | number or null | mGy-Eq | ≥ 0 or `null` | no (default `null`) | BFO dose equivalent over the last 30 days; absent or null disables this rule. |
| `radiation_dose_career_msv` | number or null | mSv | ≥ 0 or `null` | no (default `null`) | Career effective dose; absent or null disables this rule. |
| `mission_day` | int or null | day | 1–3650 or null | no | ASTRALIS mission day. |
| `mission_phase` | string or null | — | `PHASE_1_ACUTE_ADAPTATION` or `PHASE_2_LONG_DURATION` | no | ASTRALIS phase. |
| `cabin_ppco2_mmhg` | number or null | mmHg | 0–20 or null | no | Cabin CO₂ partial pressure. |
| `iop_mmhg` | number or null | mmHg | 0–60 or null | no | Intraocular pressure. |
| `hrv_rmssd_ms` | number or null | ms | 0–300 or null | no | Passthrough HRV RMSSD. |
| `pvt_slowest10_rt_ms` | number or null | ms | 100–1000 or null | no | PVT-B slowest 10% reaction time. |
| `medical_kit` | array of strings or null | — | list or null | no | Validated onboard-kit codes; passed through as `medicalKit`. |

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
  "bfo_dose_30day_mgy_eq": 150.0,
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
      "threshold": 100,
      "evidenceRef": "Design thresholds; NOAA SWPC S2/S3; ISS background 0.2–0.5 mSv/day (≈8–21 µSv/h), episodes up to 1.2 mSv/day (≈50 µSv/h) — VERIFY"
    },
    {
      "code": "SLEEP_DEFICIT",
      "severity": "yellow",
      "message": "Only 4.5 h of sleep; minimum is 6 h.",
      "value": 4.5,
      "threshold": 6,
      "evidenceRef": "Barger et al. 2014, Lancet Neurol, Table 2; 6 h cutoff is a design choice"
    }
  ],
  "likelyConditions": [
    {
      "code": "SLEEP_DISORDER",
      "label": "Sleep disorder",
      "confidence": 0.88,
      "drivers": ["SLEEP_DEFICIT"],
      "evidenceRef": "ExMC EMCL/IMM condition vocabulary (JSC-65722; NASA IMM); evidence score is a prototype design decision, not a calibrated probability — VERIFY"
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
| `flagDetails[].evidenceRef` | string or null | Short source identifier; populated for every built-in flag. Verification status and limitations are in `docs/EVIDENCE.md`. |
| `likelyConditions` | array of object | **Experimental in v0.2:** condition names and weights are pending confirmation by the team's researcher; the field may change at the contract v0.2 freeze. UI must tolerate an empty list and unknown codes. Ranked IMM-lite condition candidates, most likely first. One entry is `{code, label, confidence, drivers, evidenceRef}`: `confidence` is an evidence score in 0–1 (two decimals, **not** a calibrated probability), `drivers` are the active flag codes that contributed, `evidenceRef` points to `docs/EVIDENCE.md`. At most 3 entries; empty when nothing reaches the floor. Never a diagnosis. |
| `doctorRecommendation` | string | 2–4 sentences of plain-language guidance for the crew. Always present, even at green. |
| `doctorSource` | `"llm"` \| `"cache"` \| `"fallback"` | Where the recommendation came from: live language model, a cached answer for an identical flag set, or a built-in rule-based text when the model is unavailable. Presentation may show this as a small badge; it does not change how the text should be displayed. |
| `bodySystems` | object | All 16 AstroCare zone IDs mapped to `green`/`yellow`/`red`; worst mapped severity wins. |
| `medicalKit` | array of string | Optional validated onboard-kit codes, passed through unchanged. |
| `plans` | object | Additive exercise and nutrition plan generated from current flags and conditions. |
| `likelyConditions[].resources[]` | object | Canonical CliFF code, human name, category, `essentialUnits`, and onboard status; see `src/astro_brain/cliff_resources.py`. |
| `likelyConditions[].resources` | array | Provisional resource codes with `onboard` true/false/null. |
| `likelyConditions[].onboardCapability` | object | `full`, `partial`, `none`, or `unknown`, plus missing codes. |

### Flag codes

NEWS2 was developed for adult NHS patients; no validation for astronauts or microgravity was found.
SpO₂, blood pressure, temperature, and consciousness may be confounded by spaceflight adaptation.
Treat these outputs as prototype signals, never as a validated clinical instrument.

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
| `RADIATION_30DAY_LIMIT` | yellow / red | One flag: dose ≥ 125 mGy-Eq (50% of 250) is yellow; ≥ 250 mGy-Eq (100%) is red. `value` = dose; `threshold` = triggered mGy-Eq threshold; message gives percent of limit. |
| `RADIATION_CAREER_LIMIT` | yellow / red | One flag: career dose ≥ 300 mSv (50% of 600) is yellow; ≥ 600 mSv (100%) is red. `value` = dose; `threshold` = triggered mSv threshold; message gives percent of limit. |
| `EXERCISE_DEFICIT` | yellow | `exercise_minutes_today < 50 %` of `required_exercise_minutes`. |
| `CALORIC_LOW` | yellow | `80 % ≤ caloric_intake / caloric_target < 90 %` (NASA yellow operating band). |
| `CALORIC_DEFICIT` | red | `caloric_intake < 80 %` of `caloric_target` (NASA red operating band). |
| `SLEEP_DEFICIT` | yellow | `sleep_hours < 6`. |
| `LOW_MOOD` | yellow | `mood_score ≤ 4`. |
| `CABIN_CO2_ELEVATED` | yellow | `cabin_ppco2_mmhg ≥ 3.0`. |
| `CABIN_CO2_HIGH` | red | `cabin_ppco2_mmhg ≥ 7.6`; replaces elevated. |
| `PHQ2_POSITIVE` | yellow | `phq2_score ≥ 3`; screening signal, not a diagnosis. |
| `PVT_SLOW` | yellow | `pvt_slowest10_rt_ms > 500`. |
| `IOP_HIGH` | yellow | `iop_mmhg > 21`. |

Reference: ISS nominal background radiation is ~0.2–0.5 mSv/day (≈8–21 µSv/h), episodes up to 1.2 mSv/day (≈50 µSv/h), so a nominal sample should never
trigger a radiation flag.

Rule for the UI: **`alertLevel` = worst severity among active flags; no flags → `green`.** Only
`NEWS2_HIGH`, `CALORIC_DEFICIT`, `RADIATION_CRITICAL`, `RADIATION_30DAY_LIMIT` (at ≥100% of its limit) and
`RADIATION_CAREER_LIMIT` (at ≥100% of its limit) can make a sample red. Do not recompute this from
the flags on the presentation side; read `alertLevel` directly.

### Likely conditions — IMM-lite

**Experimental in v0.2:** condition names and weights are pending confirmation by the team's
researcher; the field may change at the contract v0.2 freeze. UI must tolerate an empty list and
unknown codes.

`likelyConditions` is a prototype, ExMC-informed ranking of **possible** conditions to watch. It
reuses the condition vocabulary of the Exploration Medical Condition List (EMCL, JSC-65722) and the
Integrated Medical Model (IMM), but it is **not** the IMM Monte Carlo model and it is **never a
diagnosis**. It is a deterministic evidence score over the brain's own flags:

- every condition has weighted flag `drivers`; `confidence = min(1, Σ weights / saturation)`;
- a condition is emitted when `confidence ≥ 0.25` and it has enough drivers (SEPSIS needs ≥ 2);
- at most 3 are returned, sorted by `confidence` descending, then by `code`;
- `confidence` is relative evidence strength, not a probability of disease.

| code | label | supporting flags |
|---|---|---|
| `HYPOVOLEMIC_SHOCK` | Hypovolemic shock / acute hypovolemia (EMCL; ICL116) | `BP_LOW` plus one of `HR_HIGH`, `RESP_HIGH`, `CONSCIOUSNESS_ALTERED` |
| `SEPSIS` | Sepsis | `TEMP_HIGH`, `TEMP_LOW`, `HR_HIGH`, `RESP_HIGH`, `BP_LOW`, `SPO2_LOW` (≥ 2 drivers) |
| `RESPIRATORY_INFECTION_LOWER` | Lower respiratory tract infection (EMCL) | `TEMP_HIGH`, `RESP_HIGH`, `SPO2_LOW`, `HR_HIGH` (≥ 2 drivers) |
| `ALTITUDE_SICKNESS` | Altitude sickness / hypobaric hypoxia (EMCL) | `SPO2_LOW`, `RESP_HIGH`, `HR_HIGH` |
| `ACUTE_RADIATION_SYNDROME` | Acute radiation syndrome / radiation sickness | `RADIATION_CRITICAL`, `RADIATION_30DAY_LIMIT`, `RADIATION_CAREER_LIMIT`, `RADIATION_ELEVATED`, `TEMP_HIGH` |
| `CARDIAC_ARRHYTHMIA` | De novo cardiac arrhythmia | `HR_HIGH`, `HR_LOW`, `BP_LOW`, `CONSCIOUSNESS_ALTERED` |
| `SLEEP_DISORDER` | Sleep disorder | `SLEEP_DEFICIT`, `LOW_MOOD` |
| `DEPRESSION` | Depression / behavioral health concern | `LOW_MOOD`, `SLEEP_DEFICIT`, `EXERCISE_DEFICIT` |
| `NUTRITIONAL_DEFICIT` | Nutritional deficiency | `CALORIC_DEFICIT`, `EXERCISE_DEFICIT` |

Rule for the UI: show these as "possible conditions to monitor", never as a diagnosis, and never
compute them on the presentation side. An empty list is a normal, expected state.

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
| `POST` | `/ask` | `{"astronaut_id":"X","question":"..."}` | interactive doctor answer; CORS enabled |
| `OPTIONS` | `*` | — | CORS preflight, HTTP 204 |
| `GET` | `/log` | `?astronaut_id=X` optional | Mission episodes, globally or per astronaut |
| `GET` | `/report` | `?astronaut_id=X[&format=text]` | EMCL-vocabulary mission report, JSON or SBAR text |

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

### Body systems and WebSocket

Every output includes `bodySystems` with all 16 frontend zone IDs, defaulting to `green`; the worst mapped flag severity wins and a likely condition with confidence ≥ 0.5 contributes at least `yellow`. This mapping is a design decision aligned to the AstroCare frontend. With `--ws-port 8787`, the dashboard broadcasts AstroCare `BrainTick` JSON over `ws://localhost:8787` after each successful process.

## 5. Change policy

- Both contracts are **fixed by the orchestrator**. Neither team changes a field name, type,
  unit, range or default on its own.
- Want a change? Propose it to the orchestrator; it is applied to this document first, then to
  code, then announced to all three teams.
- The data team **must announce** any format change before shipping it, and **must never
  silently change** units, key names or ranges. Adding an extra key is allowed without
  announcement (it is ignored), but it will not be used until the contract is updated.
- Version of this contract: `astro-brain 0.6.0`.

---

## 6. Agent roster (for AI agents working in this repository)

| agent | zone |
|---|---|
| `contract-agent` | `src/astro_brain/contract.py`, `src/astro_brain/flags.py`, their tests, `AGENTS.md`, `pyproject.toml`. Owns input/output contract definitions. |
| `scoring-agent` | `src/astro_brain/news2.py`, `src/astro_brain/radiation.py`, `src/astro_brain/lifestyle.py`, `src/astro_brain/vitals_flags.py`, `src/astro_brain/scoring.py`, `src/astro_brain/conditions.py` (NEWS2 + all flag rules and IMM-lite conditions from section 3) and their tests. |
| `doctor-agent` | `src/astro_brain/doctor/` (`__init__.py`, `layer.py`, `fallback.py`, `ollama_client.py`, `prompts.py` — recommendation text: llm / cache / fallback) and its tests, `src/astro_brain/pipeline.py` (`Brain`). |
| `brain-qa-agent` | `src/astro_brain/mock.py`, `src/astro_brain/qa.py`, `examples/`, end-to-end tests, mock sample generators, contract conformance checks. |
| `dashboard-agent` | `src/astro_brain/dashboard.py`, `src/astro_brain/ws_server.py` and their tests. |
| `adapters-agent` | `src/astro_brain/adapters/`, `src/astro_brain/feed_astralis.py`, `docs/INTEGRATION.md` and adapter tests. |

All agents: stdlib only, work inside this repository, respect the two contracts above, and
**do not touch the data pipeline or the presentation UI** — those belong to the other teams.
