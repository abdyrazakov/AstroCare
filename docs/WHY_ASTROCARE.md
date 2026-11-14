# Why AstroCare

Five differentiators for the pitch and the README "Why" section. Each claim is scoped to what
the code in this repository actually does today; limitations are stated honestly.

---

## 1. Fully local, offline AI

**Claim:** The recommendation text comes from a language model that runs entirely on local
hardware — no call to Earth, no internet dependency.

**Implementation today:** `src/astro_brain/doctor/layer.py` (`DoctorLayer`) talks to a local
[Ollama](https://ollama.com) server running `qwen2.5:7b-instruct` through
`src/astro_brain/doctor/ollama_client.py`. Each synchronous call has a 3-second timeout; on a
cache miss that times out, the layer returns `src/astro_brain/doctor/fallback.py`'s rule-based
text immediately (source `"fallback"`) and hands the same cache key to exactly one background
daemon thread, which retries with a longer timeout (`upgrade_timeout_s`, default 90 s) and, on
success, warms the cache for the next occurrence of the same flag combination (source then
becomes `"cache"`). This cache/debounce/timeout/fallback/upgrade sequence is documented in the
module docstring of `layer.py` and is exactly what runs — no network egress at any point.

**Why it matters for a Mars-class mission:** round-trip light delay to Earth is up to ~20
minutes each way at Mars distance, so a system that needs a ground-based model or ground
clearance for every triage decision is unusable in an emergency. A fully local model answers in
seconds (or falls back deterministically) regardless of comms availability.

**Honest limitation:** on CPU-only hardware the 7B model does not reliably answer within the
3-second synchronous timeout, so most live calls return the rule-based fallback text, not the
LLM's own text — the README states this directly ("this call almost always times out ... fallback
text is returned"). The LLM path is real and exercised by the background upgrade, but the
*common* case in the current demo environment is the deterministic fallback, not a live model
response. `doctorSource` always discloses which one actually produced the text.

---

## 2. ExMC-aligned IMM-lite

**Claim:** Candidate conditions use NASA's own exploration-medicine vocabulary, scored
deterministically and transparently — not a diagnosis, and not NASA's Monte Carlo model.

**Implementation today:** `src/astro_brain/conditions.py` reuses condition names from the
Exploration Medical Condition List (EMCL, JSC-65722) and the Integrated Medical Model (IMM)
vocabulary — e.g. `HYPOVOLEMIA`, `SEPSIS`, `HYPOXEMIA`, `ACUTE_RADIATION_SYNDROME`,
`CARDIAC_ARRHYTHMIA`, `SLEEP_DISORDER`, `DEPRESSION`, `NUTRITIONAL_DEFICIT` — but replaces IMM's
Monte Carlo mission simulation with a pure, deterministic function: `confidence = min(1, Σ
weights / saturation)` over the brain's own active flags, each condition requiring a minimum
number of drivers (`min_drivers`, e.g. 2 for `SEPSIS`), floored at `MIN_CONFIDENCE = 0.25`, capped
at `MAX_CONDITIONS = 3`, ties broken by code. The module docstring states explicitly: "deliberately
does NOT reimplement IMM's Monte Carlo model" and "never a diagnosis." The real IMM is a
multi-year mission-planning tool that estimates medical-event *probabilities and resource needs*
for a whole crew over a whole mission (ExMC IMPACT); this module is the real-time, per-sample
counterpart that watches the vitals IMM would have predicted risk for — the monitoring half of a
planning ↔ monitoring loop, not a substitute for the planning half.

**Why it matters for a Mars-class mission:** a crew medical officer needs condition hypotheses
they can inspect and trust, not a black-box probability. Every number here traces back to the
specific active flags listed in `drivers`.

**Honest limitation:** `confidence` is an evidence-strength score invented for this prototype
(`docs/EVIDENCE.md`: "DESIGN DECISION ... Not the IMM; not a calibrated probability"), not a
validated clinical probability, and several condition-name mappings are marked `VERIFY` in
`docs/EVIDENCE.md` pending a researcher confirming the exact EMCL entry (e.g. `HYPOVOLEMIA`,
`HYPOXEMIA`).

---

## 3. Evidence register

**Claim:** Every threshold the brain uses is written down with its source and an honest
verification status, not asserted as fact.

**Implementation today:** `docs/EVIDENCE.md` is a single table mapping each flag/threshold to a
source, a section/page reference, and one of four statuses — `VERIFIED`, `VERIFY`,
`ASSUMPTION`, or `DESIGN DECISION`. NEWS2 component bands (`HR_HIGH`, `SPO2_LOW`, `BP_LOW`,
`RESP_HIGH`, etc.) are sourced to the Royal College of Physicians' NEWS2 2017 report, Chart 1/2,
p.29–30 (`VERIFIED`). Radiation limits (`RADIATION_30DAY_LIMIT`, `RADIATION_CAREER_LIMIT`,
`CAREER_EFFECTIVE_DOSE_LIMIT_MSV = 600 mSv`, `THIRTY_DAY_BFO_LIMIT_MGY_EQ = 250 mGy-Eq`) are
sourced to NASA-STD-3001 Vol. 1 Rev C, §4.8.2 and Table 4.8-1, with the edition itself verified
against the actual Rev C PDF (not assumed to be a 2022 revision). Each row states exactly what
was checked and what was not — e.g. `SLEEP_DEFICIT`'s 6-hour cutoff cites Barger et al. 2014 for
the *observed* ISS actigraphy mean (6.09 h) but is explicit that this does not establish a safe
minimum.

**Why it matters for a Mars-class mission:** a flight surgeon reviewing this system's output
needs to know which numbers are load-bearing NASA standards and which are this prototype's own
design choices, so they can accept, challenge, or override them individually instead of trusting
or distrusting the whole system as one block.

**Honest limitation:** several rows are explicitly unresolved — e.g. `RADIATION_30DAY_LIMIT`
compares a dose in mSv directly against a 30-day limit specified in mGy-Eq for blood-forming
organs, which the register itself flags as `ASSUMPTION` ("not a physical unit conversion; organ/
RBE data are absent"), and `EXERCISE_DEFICIT`'s 50% cutoff is tied to the real ISS MORD exercise
prescription but the specific MORD edition/section is marked `VERIFY`, not confirmed.

---

## 4. Graceful degradation

**Claim:** Whether the local model is up, slow, or down, the astronaut always gets a complete,
safe recommendation — and is told honestly which path produced it.

**Implementation today:** `DoctorLayer.recommend()` (`src/astro_brain/doctor/layer.py`) has no
code path that returns nothing or raises past the caller. A disabled layer (`enabled=False`,
e.g. via `ASTRO_DOCTOR_OFFLINE=1`) always returns the rule-based fallback text with no network
call. A known-nominal sample (green, no active flags) also skips the model entirely — a known
"everything is fine" state needs no model opinion. On a cache miss under load, a second caller
racing the same flag combination never triggers a second LLM call; it gets the fallback text
immediately (`stats["inflight_skips"]`). Every outcome is labelled by `doctorSource`:
`"llm"` (fresh model answer), `"cache"` (previously computed, model or fallback), or
`"fallback"` (rule-based template). The output contract (`AGENTS.md` §3) guarantees
`doctorRecommendation` is "Always present, even at green."

**Why it matters for a Mars-class mission:** a health-monitoring tool that can silently fail to
produce guidance, or that blocks on a slow model during a medical event, is worse than no tool.
This system is designed so the worst case is "the same rule-based text as if the model were
never installed," not "no answer."

**Honest limitation:** the rule-based fallback text (`src/astro_brain/doctor/fallback.py`) is
necessarily less nuanced than a model-generated explanation — graceful degradation here means
"never nothing," not "never degraded."

---

## 5. Contract-driven parallel teamwork

**Claim:** Three teams (data, brain, presentation) build independently against one document,
without reading each other's source code.

**Implementation today:** `AGENTS.md` states directly: "This is the only document the data team
and the presentation team need to read... You never need to open our source code." It fixes the
exact input JSON shape with types/units/ranges/defaults, the exact output JSON shape with every
field and flag code, the HTTP dashboard API, and a five-way internal agent-zone split
(`contract-agent`, `scoring-agent`, `doctor-agent`, `brain-qa-agent`, `dashboard-agent`), each
owning a fixed set of files so parallel changes do not collide. The project currently has 435
tests passing and a dedicated offline QA runner (`src/astro_brain/qa.py`, 24/24 scenarios) that
exercises the full pipeline against mock data (`src/astro_brain/mock.py`) without needing the
other two teams' real systems running.

**Why it matters for a Mars-class mission:** the same contract discipline that lets a hackathon
team ship in parallel is what a real mission needs across sensor vendors, flight software, and
ground display systems — a single frozen interface, not a shared codebase, is what keeps those
systems independently replaceable and testable.

**Honest limitation:** the contract is enforced by convention and code review, not by a schema
tool shared across repositories — unlike the parallel astralis project, which generates a single
JSON Schema (`shared/contracts.schema.json`) from Pydantic models shared by Python and
TypeScript. AstroCare's contract is currently a Markdown document plus `contract.py`'s manual
validation, not a machine-checked cross-language schema.

---

## 60-second pitch

AstroCare is the brain of a health-monitoring system built for a mission where you cannot call
home for a medical opinion. It takes one vitals-and-lifestyle sample at a time, scores it with a
terrestrial early-warning algorithm (NEWS2) adapted for spaceflight inputs, layers on
radiation and lifestyle rules sourced from NASA's own standards, and ranks which NASA-named
exploration medical conditions the active signs support — transparently, with the exact flags
that drove each score, never as a diagnosis. Then it hands the crew a short, plain-language
recommendation generated by a language model running entirely on local hardware, with no
dependency on a connection to Earth; if that model is slow or unavailable, the astronaut still
gets a complete, safe answer from a deterministic fallback, and the system says so honestly
instead of hiding it. Every threshold is written down with its source and how confident we are
in it, in one evidence register anyone can audit. And the whole thing was built by three
independent teams working off one nine-page contract, never reading each other's code — the
same discipline a real mission needs when sensors, flight software, and ground systems are each
built by someone else. This is a hackathon prototype, not a medical device — but the architecture
is the part meant to survive the trip to Mars.
