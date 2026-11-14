# Питч-outline — AstroCare (NASA Space Apps 2026)

Для стратега/презентатора команды. Факты, без маркетинговых прилагательных. Каждое
утверждение привязано к файлу репозитория; где источника нет — сказано прямо.

---

## 1. Контекст челленджа

NASA Space Apps Challenge 2026, тема **"Create Health Monitoring Software for Astronauts on
Space Missions"** (заголовок у обоих смежных репозиториев: `/tmp/astrocare-fe/README.md` и
`/tmp/astralis/README.md`; у нас — `README.md:8`, "NASA Space Apps 2026").

Система — три независимых репозитория, каждый со своей ролью:

1. **astralis** (`/tmp/astralis/README.md`) — офлайн-симулятор и дата-пайплайн: синтетический
   1 Гц поток, 180-дневные ряды, сценарии аномалий, данные NASA OSDR (Inspiration4: OSD-569…
   OSD-656), провенанс `NASA_REAL`/`NASA_DERIVED`/`SYNTHETIC`.
2. **astro-brain** (этот репозиторий) — мозг: скоринг, флаги, IMM-lite, рекомендация доктора.
   Единственный источник `alertLevel`/`news2Score`/`likelyConditions` (`AGENTS.md` §1, §5;
   `docs/CONTRACT_V02_PROPOSAL.md` §1 — явное правило "один мозг, один контракт").
3. **astrocare** / astrocare-fe (`/tmp/astrocare-fe/README.md`) — фронтенд: интерактивный 3D
   двойник, 16 кликабельных зон тела, подключается к мозгу по WebSocket
   (`docs/INTEGRATION.md:5-7`, `--ws-port 8787`).

Поток интеграции: симулятор → мозг → фронт, подтверждён инструкцией запуска трёх репозиториев
в одном файле (`docs/INTEGRATION.md:1-9`).

---

## 2. Таблица: критерий жюри → что закрываем → демо → доказательство

| Критерий Space Apps | Чем закрываем | Где видно в демо | Доказательство |
|---|---|---|---|
| **Validity** | Evidence register со статусами VERIFIED/VERIFY/ASSUMPTION/DESIGN DECISION на каждый порог; два независимых аудита первичных источников | Показываем таблицу `docs/EVIDENCE.md` живьём, называем 1-2 конкретные строки | `docs/EVIDENCE.md:8` (заголовок таблицы и 4 статуса); `docs/EVIDENCE_RESEARCH_2026-11-14.md` (аудит №1: NASA-STD-3001 Rev C, JSC-63555, EMCL/ICL, NASEM 2021, RCP NEWS2 — 11 пунктов, 3 конфликта, 3 not found); `docs/PHASE_PRIORS_AND_RESOURCES_RESEARCH_2026-11-14.md` (аудит №2: CliFF Resource Tables, IMM 2015, HRP-48036, NASA-STD-3001 Table E.2-1) |
| **Creativity** | ExMC-aligned IMM-lite как real-time мониторинговый двойник ExMC IMPACT mission planning (не замена, а дополняющая половина); ресурсная осведомлённость из CliFF Resource Tables; полностью локальный ИИ без связи с Землёй | Карточка `likelyConditions` с `drivers`, `resources`, `onboardCapability`; рекомендация доктора появляется без интернета | `src/astro_brain/conditions.py:1-12` (докстринг модуля: "deliberately does NOT reimplement IMM's Monte Carlo model"); `docs/WHY_ASTROCARE.md:50-54` ("real-time counterpart to ExMC IMPACT mission planning"); `src/astro_brain/resources.py:6-18` (`RESOURCES_BY_CONDITION`); `docs/PHASE_PRIORS_AND_RESOURCES_RESEARCH_2026-11-14.md` §5 (источник CliFF RT); `src/astro_brain/doctor/layer.py:1-21` (докстринг: cache/timeout/fallback/upgrade, никакого сетевого вызова) |
| **Impact** | Автономность на дистанции Марса (связь с Землёй задержана); деградация без потери ответа; доктор по запросу (`/ask`) | Отключаем сеть/модель на сцене (`--offline`), система всё равно отвечает; вызываем `/ask` вживую | `docs/WHY_ASTROCARE.md:22-26` ("round-trip light delay to Earth is up to ~20 minutes each way at Mars distance"); README.md:91-98 (`--offline`, `ASTRO_DOCTOR_OFFLINE`); `AGENTS.md` §4 (`POST /ask`); `src/astro_brain/dashboard.py:160-247` (`_handle_ask`) |
| **Relevance** | Пороги привязаны к реальным NASA-стандартам (NASA-STD-3001, JSC-63555, RCP NEWS2), а не придуманы с нуля; честная маркировка, где это не так | Показываем одну строку `docs/EVIDENCE.md` со статусом VERIFIED и одну со статусом DESIGN DECISION рядом | `docs/EVIDENCE.md:10-11` (`CAREER_EFFECTIVE_DOSE_LIMIT_MSV`, `THIRTY_DAY_BFO_LIMIT_MGY_EQ` — VERIFIED); `docs/EVIDENCE.md:34-35` (`RADIATION_ELEVATED`/`RADIATION_CRITICAL` — DESIGN DECISION) |
| **Presentation** | Три живых сценария вместо слайдов; контракт на одном документе, который можно открыть на сцене | См. раздел 4 (сценарий выступления) | `AGENTS.md` (единый 9-страничный контракт, §0: "You never need to open our source code") |

---

## 3. Что мы НЕ утверждаем

Честный список ограничений — заготовка ответов на вопросы жюри, не для зачитывания со сцены
целиком.

- **NEWS2 не валидирован для космоса.** Пороги RCP подтверждены (VERIFIED), но валидации для
  астронавтов/микрогравитации не найдено. `docs/EVIDENCE.md:55` (`NEWS2 spaceflight validation
  | NOT FOUND`); `README.md:234-239` (медицинский дисклеймер).
- **IMM-lite — не IMM Monte Carlo и не диагноз.** `confidence` — эвристическая оценка силы
  улик, придуманная для прототипа, не калиброванная вероятность. `src/astro_brain/conditions.py:9-11`;
  `docs/EVIDENCE.md:42` (`IMM-lite scoring model | DESIGN DECISION | Not the IMM; not a
  calibrated probability; never a diagnosis`).
- **RT ≠ полный CRT.** Таблица ресурсов (`resources.py`) построена по CliFF Resource Table;
  полный Capability Resource Table живёт в непубличном Excel/IMPACT-MD и не воспроизведён.
  `docs/PHASE_PRIORS_AND_RESOURCES_RESEARCH_2026-11-14.md:128-131` и §8 п.6.
- **Пороги с пометкой DESIGN DECISION — не клинические нормативы NASA**, а наши операционные
  решения (например, цвет для радиационных порогов, объединение NEWS2 medium/low-medium,
  `CONSCIOUSNESS_ALTERED` как бинарный суррогат CVPU). `docs/EVIDENCE.md:26,30,31,34,35`.
- **Симулятор синтетический, не реальные астронавты.** OSDR-исследования Inspiration4 — это
  пре/постполётные биообразцы 3-дневной миссии, а не 180-дневная непрерывная телеметрия; явно
  написано "must not be used as a substitute for continuous physiology".
  `/tmp/astralis/README.md` (раздел "Verified Inspiration4 References"); фронт сам пишет
  "all data is synthetic" (`/tmp/astrocare-fe/README.md:5`).
- **Живой ответ модели — не типичный случай в демо-среде.** На CPU 7B-модель почти всегда не
  успевает за 3 секунды; чаще всего звучит детерминированный fallback-текст, а не живой ответ
  LLM — `doctorSource` это честно показывает. `docs/WHY_ASTROCARE.md:28-33`; `README.md:179-181`.
- **Сравнение накопленной дозы с 30-дневным лимитом — методическое допущение, не конверсия
  единиц.** `RADIATION_30DAY_LIMIT` сравнивает мЗв (effective dose) с лимитом в мГр-экв
  (органная доза) — статус `ASSUMPTION`, не точный расчёт. `docs/EVIDENCE.md:12`.
- **Контракт держится конвенцией и код-ревью, не общей схемой.** В отличие от astralis
  (`shared/contracts.schema.json`, единая Pydantic/TS/JSON Schema), у нас контракт — Markdown +
  ручная валидация в `contract.py`. `docs/WHY_ASTROCARE.md:145-149`.
- **Расхождение в демо-параметре задержки связи:** мозг использует ориентир "до ~20 минут"
  (`docs/WHY_ASTROCARE.md:23`), демо фронтенда — "22-min comm-delay countdown"
  (`/tmp/astrocare-fe/README.md`, раздел "Demo (60 s)"). Оба — ориентировочные демо-величины
  задержки сигнала Земля-Марс, не единая откалиброванная константа; на сцене называть одно
  число и не противоречить себе.

---

## 4. Сценарий выступления — 4 минуты (блоки по 30 секунд)

Роли: **Спикер** — говорит; **Оператор** — ведёт терминал/браузер. Экран — browser с фронтом
AstroCare + терминал с `curl`.

| # | Время | Кто | Фраза (коротко) | Что на экране |
|---|---|---|---|---|
| 1 | 0:00–0:30 | Спикер | "Марс. До Земли — до 20 минут в одну сторону. Врача по радио не вызвать." | Заставка, 3D-двойник, зелёные зоны |
| 2 | 0:30–1:00 | Спикер | "Три команды, один контракт. Симулятор, мозг, фронт — отдельно собраны, вместе работают." | `docs/INTEGRATION.md` в терминале, три процесса запущены |
| 3 | 1:00–1:30 | Оператор | Запускает нормальный тик (тихий день): `curl -s -X POST localhost:8765/ingest -d @examples/input_nominal.json` | `alertLevel: green`, план дня, доктор говорит "всё штатно" |
| 4 | 1:30–2:00 | Спикер | "Теперь солнечная вспышка." | Оператор инжектит `SOLAR_PARTICLE_EVENT` (astralis-фид, `docs/INTEGRATION.md:13`) |
| 5 | 2:00–2:30 | Оператор | Доза растёт, флаг `RADIATION_CRITICAL` загорается | Зоны skin_immune/skeleton становятся red; карточка `ACUTE_RADIATION_SYNDROME` с `drivers` и `resources` (storm shelter, dosimeter) |
| 6 | 2:30–3:00 | Спикер | "Мозг сам видит, что в укрытии есть/нет нужного." Вызывает `/ask`: "Что делать прямо сейчас?" | `onboardCapability` показывает `full`/`partial`/`none`; ответ `/ask` на экране |
| 7 | 3:00–3:30 | Оператор | Третий сценарий: `HYPERCAPNIC_CABIN`, скруббер CO₂ выбывает | Флаг `CABIN_CO2_HIGH`, зона lungs red, рекомендация доктора — в духе "Contact ground medical now" (как в README.md:141) |
| 8 | 3:30–4:00 | Спикер | "Всё это — локально. Без интернета, без Земли. Каждый порог — в одной таблице, с источником." | `docs/EVIDENCE.md` открыт на экране, одна строка VERIFIED, одна DESIGN DECISION |

Примечание: точный список флагов по сценариям — `docs/INTEGRATION.md:11-18` (таблица
ASTRALIS-сценарий → ожидаемый флаг → зона); конкретный текст "Contact ground medical now" взят
из примера вывода в `README.md:114-144`, не придуман для питча.

---

## 5. Вопросы жюри (10) с ответами

1. **"Это диагноз?"** Нет. `likelyConditions` — ранжирование кандидатов-состояний по
   прозрачной формуле `confidence = min(1, Σ weights / saturation)`, никогда диагноз.
   `src/astro_brain/conditions.py:9` и докстринг класса `LikelyCondition`.

2. **"NEWS2 — это же больничная шкала, при чём тут космос?"** Пороги взяты из RCP NEWS2 2017
   (Chart 1/2) как есть; валидации для астронавтов/микрогравитации не найдено, это прямо
   написано в реестре. `docs/EVIDENCE.md:55`; `README.md:235-238`.

3. **"Почему не настоящий IMM?"** IMM — Monte Carlo модель планирования на всю миссию,
   требующая годы калибровки; наш модуль — его real-time аналог для одного замера, с открытой
   формулой вместо чёрного ящика. `docs/WHY_ASTROCARE.md:50-54`.

4. **"А если модель Ollama не ответит?"** Тогда детерминированный rule-based fallback-текст,
   без разрыва ответа; `doctorSource` честно скажет `"fallback"`. Это типичный, а не крайний
   случай на CPU. `src/astro_brain/doctor/layer.py:1-45` (докстринг семантики `recommend()`);
   `docs/WHY_ASTROCARE.md:28-33`.

5. **"Откуда пороги по радиации?"** Карьерный лимит 600 мЗв и 30-дневный BFO-лимит 250 мГр-экв
   — из NASA-STD-3001 Vol.1 Rev C, §4.8.2 и Table 4.8-1 (VERIFIED, проверено по реальному PDF
   Rev C); а вот сравнение 30-дневной накопленной мЗв-дозы с мГр-экв-лимитом — наше допущение
   (ASSUMPTION), не конверсия единиц. `docs/EVIDENCE.md:10-12`;
   `docs/EVIDENCE_RESEARCH_2026-11-14.md` п.8.

6. **"Вы проверяли свои же источники?"** Да, два раза отдельными проходами: первый аудит
   нашёл и исправил, например, что NASA цитирует NASEM 2021, а не NCRP 2021, и что калорийный
   красный порог NASA — 80%, а не 70% (мы его тоже поправили). `docs/EVIDENCE_RESEARCH_2026-11-14.md`
   §1, §2 пп.1,5; видно по истории коммитов "primary-source audit" → "apply evidence audit
   corrections". Второй — отдельный аудит CliFF/IMM-данных для ресурсов и фазовых приоритетов.
   `docs/PHASE_PRIORS_AND_RESOURCES_RESEARCH_2026-11-14.md`.

7. **"Что если нужного лекарства нет на борту?"** `onboardCapability` помечает `partial`/`none`
   по входному списку `medical_kit`, и рекомендация доктора это учитывает в контексте промпта;
   список ресурсов на условие взят из CliFF Resource Table, но это не полный CRT.
   `src/astro_brain/resources.py:21-36`; `AGENTS.md` §3 (`likelyConditions[].onboardCapability`).

8. **"Как три команды не наступали друг другу на ноги?"** Один документ-контракт (`AGENTS.md`)
   фиксирует вход/выход; остальные два репозитория его не пересчитывают — явное правило "один
   мозг, один контракт" зафиксировано отдельно для обсуждения с командой симулятора.
   `docs/CONTRACT_V02_PROPOSAL.md` §1.

9. **"Это проверено тестами?"** 435 тестов и офлайн QA-прогон 24/24 сценариев по моковым
   данным, без обращения к двум другим репозиториям. `README.md:54,220-221`;
   `src/astro_brain/qa.py` (раздел докстринга про чистые функции `run_scenario`/`evaluate`).

10. **"Это готовый продукт?"** Нет, это хакатон-прототип, не медицинское устройство; это прямо
    написано в README и повторяется в evidence-документах. `README.md:233-239`;
    `docs/WHY_ASTROCARE.md:168-169`.

---

## 6. Чеклист перед сценой

- **Прогрев модели.** В репозитории нет кода для `OLLAMA_KEEP_ALIVE` — это общий параметр
  сервера Ollama (держит модель в памяти между вызовами), а не что-то, задокументированное в
  этом репозитории; если полагаемся на живой ответ LLM на сцене, сделать один "прогревочный"
  запрос через `/ingest` заранее, за ~20–25 секунд до выхода на сцену, чтобы фоновый
  upgrade-поток успел заполнить кэш (`README.md:179-189`, `src/astro_brain/doctor/layer.py:33-41`
  — фоновый поток с `upgrade_timeout_s`, по умолчанию 90 с).
- **Прогон всех трёх сценариев заранее**, вживую, в том порядке, что в разделе 4: тихий день →
  `SOLAR_PARTICLE_EVENT` → `HYPERCAPNIC_CABIN`. Таблица ожидаемых флагов —
  `docs/INTEGRATION.md:11-18`; по `SOLAR_PARTICLE_EVENT` есть наблюдённый прогон, по остальным
  сценариям — "expected until a matching run is captured" (`docs/INTEGRATION.md:19,23`), значит
  проверить своими глазами, а не полагаться на таблицу.
- **Резервный офлайн-режим.** Если на сцене нет сети/модели: `.venv/bin/python -m
  astro_brain.dashboard --simulate --offline` или `ASTRO_DOCTOR_OFFLINE=1`; доктор продолжит
  отвечать rule-based текстом, ничего не упадёт. `README.md:91-98`.
- **Если фронт не подключился:** голый дашборд всё ещё отвечает по HTTP; показываем
  `curl -s localhost:8765/state/all` (общий снимок по всем астронавтам) или
  `curl -s localhost:8765/` (текстовый снимок + статистика доктора) — оба эндпоинта не зависят
  от фронтенда и WebSocket. `AGENTS.md` §4; `src/astro_brain/dashboard.py:18-24`.
- **Проверить формулировку задержки связи** заранее между собой: спикер говорит "до 20 минут"
  (как в `docs/WHY_ASTROCARE.md:23`), а не "22 минуты" из демо-ролика фронтенда — чтобы не
  прозвучало как два разных числа с одной сцены (см. раздел 3, последний пункт).
