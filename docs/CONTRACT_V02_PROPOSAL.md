# Контракт v0.2 — повестка встречи (30 минут)

Источники: `AGENTS.md` (текущий контракт astro-brain, v0.2.0), `docs/EVIDENCE.md`,
`src/astro_brain/conditions.py`, `src/astro_brain/doctor/layer.py`, и параллельный репозиторий
astralis — `AGENTS.md`, `shared/contracts.schema.json` (типы `StreamTick`, `DailyTelemetryLog`,
`TriageAssessment`, `AstronautProfile`, `MissionPhase`), `data_pipeline/stream_generator.py`.

---

## 1. Цель встречи и правило

**Один мозг (AstroCare), один контракт.** Вся клиническая логика (скоринг, флаги, IMM-lite,
рекомендация доктора) живёт только в этом репозитории (astro-brain) и описана только в его
`AGENTS.md`. astralis — поставщик данных и визуализации для демо: симулятор телеметрии
(`data_pipeline/stream_generator.py`), офлайн-бандл NASA-данных (`data_pipeline/`, `data_bundle/`)
и фронтенд-компоненты (`frontend/src/*`).

**Почему это нужно обсудить именно сейчас:** `astralis/AGENTS.md` §3 закрепляет за
Backend-agent (SPEC 2) зону `backend/app/*` с задачей "MFI, seven detectors, IMPACT, SBAR,
API/SSE" — то есть у astralis уже спроектирован **собственный** параллельный медицинский
движок: `TriageAssessment` (свой risk score `mfi_risk_score`, свой `triage_status`
GREEN/YELLOW/RED/INSUFFICIENT_DATA), семь детекторов DET-01…DET-07, прогноз `ImpactForecast`,
отчёты `SbarMedicalReport`, и в задачах (§~670) явно стоит пункт реализовать
`triageEngine.ts` и `impactPredictor.ts` "с численным паритетом Python". Это прямой дубликат
того, что уже делает astro-brain (`news2.py`, `radiation.py`, `lifestyle.py`, `conditions.py`).

**Правило, которое нужно утвердить голосованием (см. п.7, вопрос 1):** astralis не
реализует `triage_engine`, детекторы DET-01…07 и `lib/triageEngine.ts` как источник истины для
алертов/статуса; единственный источник `alertLevel`/`news2Score`/`likelyConditions` —
`astro_brain.pipeline.Brain`. Если какая-то часть этой логики у astralis уже написана —
она либо выбрасывается, либо переводится в чисто визуальный слой (рисует то, что прислал
мозг), но не пересчитывает статус самостоятельно.

---

## 2. Маппинг `StreamTick` (astralis) → входной контракт astro-brain

`StreamTick` — это один тик 1 Гц потока симулятора (`data_pipeline/stream_generator.py`,
`HEALTHY_BASELINE`). Ниже — что из него реально попадает в наш контракт.

| поле `StreamTick` | тип/единица (astralis) | наше поле | статус |
|---|---|---|---|
| `timestamp` | строка ISO-8601 UTC | `timestamp` | прямое соответствие |
| `astronaut_id` | строка | `astronaut_id` | прямое соответствие |
| `hr` | number, bpm, 20–250 | `hr` | соответствие с округлением: у нас `int`, диапазон 0–300; у них `number` 20–250 — данные нужно округлять до целого при передаче |
| `spo2` | number, %, 50–100 | `spo2` | соответствие с округлением: у нас `int` 0–100; их нижняя граница 50% уже внутри нашего диапазона, но тип надо округлять |
| `systolic_bp` | int, mmHg, 50–260 | `bp.systolic` | нужна обёртка: `bp: {"systolic": systolic_bp, "diastolic": diastolic_bp}` |
| `diastolic_bp` | int, mmHg, 20–160 | `bp.diastolic` | см. выше |
| `temp_c` | number, °C, 30–45 | `temp_c` | прямое соответствие (их диапазон — подмножество нашего 25–45) |
| `resp_rate` | number, breaths/min, 4–60 | `resp_rate` | соответствие с округлением: у нас `int` 0–80 |
| `radiation_dose_rate` | number, **mSv/h** (по докстрингу схемы), 0–1000 | `radiation_dose_rate` (µSv/h) | **несовпадение единиц, ×1000.** `HEALTHY_BASELINE["radiation_dose_rate"] = 0.012` (mSv/h) = 12 µSv/h, что совпадает с нашим "ISS nominal background 12–30 µSv/h" (AGENTS.md §2) — значит конверсия подтверждена на baseline-значении, но её должна явно сделать data-команда (или мы — в `contract.py`), не предполагать по умолчанию |
| `mission_day` | int, 1–3650 | нет поля | **новое аддитивное поле** (см. п.3) |
| `mission_phase` | enum `PHASE_1_ACUTE_ADAPTATION`/`PHASE_2_LONG_DURATION` | нет поля | **новое аддитивное поле** (см. п.3) |
| `hrv_rmssd` | number, ms, 0–300 | нет поля | **новое аддитивное поле** (см. п.3) |
| `iop_mmhg` | number, mmHg, 0–60 | нет поля | **новое аддитивное поле** (см. п.3) |
| `cabin_ppco2` | number, **по докстрингу схемы — mmHg**, 0–20 | нет поля | **новое аддитивное поле**; несмотря на то, что схема astralis уже фиксирует mmHg, это должна подтвердить data-команда как финальную единицу (см. п.3 и вопрос 1 в п.7) |
| `pvt_slowest10_rt` | number, ms, 100–1000 | нет поля | **новое аддитивное поле** (см. п.3) |
| `source_type` | enum `NASA_REAL`/`NASA_DERIVED`/`SYNTHETIC` | — | **не используется**: это метаданные происхождения данных для их провенанса, не клинический вход |
| `provenance_ids` | array of string, ≥1 | — | **не используется**: внутренний провенанс astralis, не часть нашего контракта |

### Откуда брать наши daily-поля (exercise/calories/sleep/mood)?

Проверено по `DailyTelemetryLog` в `shared/contracts.schema.json`. Честный ответ — по-разному:

- **`sleep_hours`** — есть прямой аналог: `sleep_duration_h` (number, часы, 0–24). Маппинг прямой.
- **`mood_score`** (1–10, у нас 10 = лучшее) — аналога **нет**. В `DailyTelemetryLog` есть только
  `mood_stress_vas` (0–100, Stress Visual Analogue Scale) — это другая шкала (стресс, не
  настроение), другая полярность (выше = хуже, а не лучше) и другой диапазон. Прямого
  преобразования без design-решения не существует.
- **`exercise_minutes_today` / `required_exercise_minutes`** — аналога **нет**. В
  `DailyTelemetryLog` есть только `ared_exercise_completed` (boolean — "сделал/не сделал") и
  `vo2max_ml_kg_min` (аэробная форма), но ни минут, ни целевого показателя в минутах нет.
- **`caloric_intake` / `caloric_target`** — аналога **нет вообще**. В `DailyTelemetryLog` нет ни
  одного поля про калории или питание.

Вывод: только сон переносится автоматически из их данных; mood/exercise/calories для демо либо
синтезируются отдельно data-командой, либо `EXERCISE_DEFICIT`/`CALORIC_DEFICIT`/`LOW_MOOD`
временно не демонстрируются на их потоке (см. вопрос 3 в п.7).

---

## 3. Предлагаемые аддитивные поля входа v0.2

Все поля **optional**, `default = null`, правило не применяется при `null` (как у существующих
`noaa_s_scale`/`radiation_dose_30day_msv`/`radiation_dose_career_msv`).

| поле | тип/единица | зачем мозгу | правило (кратко) | источник |
|---|---|---|---|---|
| `mission_phase` | enum `PHASE_1_ACUTE_ADAPTATION` \| `PHASE_2_LONG_DURATION` (их же enum) | контекст фазы миссии для будущей настройки темпа кумулятивных радиационных лимитов и EVA-политики | пока без правила, чисто информационное поле на выходе/в промптах доктора | VERIFY — правило не спроектировано |
| `mission_day` | int, 1–3650 | привязка к окну кумулятивной дозы (NASA-STD-3001 30-дневное окно уже используется в `RADIATION_30DAY_LIMIT`, но без привязки ко дню) | пока без правила | VERIFY |
| `cabin_ppco2` | number — **кПа или мм рт.ст., финальную единицу должна зафиксировать data-команда** | гиперкапния — реальная экологическая угроза на орбите; у astralis это уже их аномалия DET-01 "Hypercapnic Cabin" | предлагается флаг `CO2_ELEVATED`/`CO2_CRITICAL` по аналогии с радиацией | VERIFY — пороги не выбраны, источник (NASA SMAC CO2 limits) не внесён в EVIDENCE.md |
| `iop_mmhg` | number, mmHg | внутриглазное давление — биомаркер SANS (neuro-ocular syndrome), релевантно долгим миссиям | без правила на v0.2, информационное | VERIFY |
| `hrv_rmssd` | number, ms | более чувствительный маркер автономной нервной системы/утомления, чем сырой `hr` | предлагается `HRV_LOW` как дополнительный driver для `CARDIAC_ARRHYTHMIA`/стрессовых IMM-lite условий | VERIFY — порог не выбран |
| `pvt_slowest10_rt` | number, ms | PVT-B — стандартный NASA-тест бдительности/усталости, прямо дополняет уже существующий `SLEEP_DEFICIT` и условия `SLEEP_DISORDER`/`DEPRESSION` | предлагается `PVT_IMPAIRED` при замедлении относительно базовой линии | VERIFY — нужна ссылка на NASA PVT-B пороги |
| `phq2_score` | int, 0–6 (замена `mood_score` в будущем) | PHQ-2 — валидированный 2-пунктовый скрининг депрессии (Kroenke et al. 2003, уже процитирован в `docs/EVIDENCE.md` для `LOW_MOOD`), в отличие от текущей ad hoc шкалы 1–10 | предлагается заменить `LOW_MOOD` на `PHQ2_POSITIVE` при `phq2_score ≥ 3` (опубликованный клинический cutoff) | источник надёжный (Kroenke 2003), но маппинг cutoff → наш флаг — VERIFY |
| `medical_kit` | array of string (коды доступных средств) | позволяет Doctor Layer и будущему `onboardCapability` (см. п.4) честно говорить "у вас есть/нет нужного средства", а не советовать то, чего нет на борту (это уже в README "Next: onboard medical-kit awareness") | без правила на v0.2, вход для промпта доктора и для `onboardCapability` | VERIFY — словарь кодов не определён |

---

## 4. Аддитивные поля выхода v0.2

| поле | статус | форма |
|---|---|---|
| `likelyConditions[]` | **уже реализовано** (experimental) | `{code, label, confidence, drivers[], evidenceRef}` на запись; `confidence` — evidence score 0–1 (2 знака), не калиброванная вероятность; максимум 3 записи, floor `confidence ≥ 0.25`; `SEPSIS` требует ≥ 2 драйверов (`conditions.py`, `MIN_CONFIDENCE = 0.25`, `MAX_CONDITIONS = 3`) |
| `flagDetails[].evidenceRef` | **уже реализовано** | строка или `null`, заполнена для каждого встроенного флага (AGENTS.md §3) |
| `onboardCapability` | **предложено, не реализовано** | булево/enum — есть ли на борту средство для выданной рекомендации, на основе входного `medical_kit`; зависит от словаря кодов countermeasure ↔ `medical_kit`, который ещё не спроектирован |

---

## 5. Новые эндпоинты дашборда (уже реализованы)

`GET /state?astronaut_id=X`, `GET /state/all`, `GET /history?astronaut_id=X` — уже в
`AGENTS.md` §4 и `dashboard.py`. Фронтенду достаточно читать их напрямую, ничего пересчитывать
не нужно.

---

## 6. Что НЕ меняется (гарантии для UI)

- Все существующие поля входного и выходного контракта (имена, типы, единицы, диапазоны) и все
  существующие коды флагов остаются как в `AGENTS.md` v0.2.0.
- UI должен игнорировать незнакомые коды `activeFlags`/`flagDetails[].code` и незнакомые поля
  верхнего уровня — ровно так же, как брейн уже игнорирует незнакомые входные ключи
  ("Unknown extra keys are ignored", AGENTS.md §2).
- `alertLevel` остаётся единственным полем для раскраски UI; пересчитывать его из флагов на
  стороне presentation запрещено (AGENTS.md §3).

---

## 7. Открытые вопросы для голосования

1. **Разграничение "один мозг":** закрепляем ли мы сейчас, что astralis не реализует
   `triage_engine`/DET-01…07/`triageEngine.ts`/`impactPredictor.ts` как источник правды, а
   astro-brain — единственный источник `alertLevel`/скоринга? *(Самый приоритетный вопрос —
   иначе на демо будет два конфликтующих статуса одного и того же астронавта.)*
   — отвечает: оба архитектора + orchestrator.
2. **Единица `cabin_ppco2`:** кПа или мм рт.ст.? Схема astralis уже пишет mmHg в докстринге —
   фиксируем это как финальное решение или нет?
   — отвечает: data-команда (researcher), статус должен попасть в `docs/EVIDENCE.md`.
3. **Единица `radiation_dose_rate`:** подтверждаем конверсию ×1000 (mSv/h → µSv/h) и кто её
   делает — data-pipeline на их стороне или `contract.py` на нашей?
   — отвечает: data-agent (astralis) + contract-agent (astro-brain).
4. **Lifestyle-поля без аналога (exercise minutes, calories):** на демо с их потоком —
   отключаем `EXERCISE_DEFICIT`/`CALORIC_DEFICIT` или data-команда синтезирует отдельные
   значения специально для нас?
   — отвечает: orchestrator + data-agent.
5. **`mood_score` vs `phq2_score`:** для демо остаёмся на текущей ad hoc шкале 1–10 (отдельно
   синтезированной) или сразу переходим на `phq2_score`?
   — отвечает: orchestrator + scoring-agent.
6. **Источники порогов для новых полей** (`cabin_ppco2`, `hrv_rmssd`, `pvt_slowest10_rt`,
   `iop_mmhg`) — кто ищет и вносит в `docs/EVIDENCE.md` до того, как появится код правила?
   — отвечает: researcher.
7. **Словарь `medical_kit` и дизайн `onboardCapability`:** нужен отдельный короткий
   design-документ до реализации — кто его пишет и к какому сроку?
   — отвечает: doctor-agent + orchestrator.
