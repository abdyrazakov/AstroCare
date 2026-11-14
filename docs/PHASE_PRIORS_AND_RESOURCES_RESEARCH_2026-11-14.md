# AstroCare — IMM phase priors и ресурсы по состояниям

Дата: 2026-11-14  
Статус: исследовательский deliverable, не патч кода.  
Назначение: данные для будущих `phase_priors.py` и `resources.py`, без изменения логики.

---

## 1. Краткий вывод

- IMM различает три механизма возникновения: **SA / SAS** (space adaptation, один раз за полёт, onset в первые ~5 суток), **general** (Poisson, постоянный rate на протяжении миссии) и **SPE/EVA** (привязка к событию, а не к календарной фазе).
- Для `PHASE_1_ACUTE_ADAPTATION` обоснованно относятся только SA-состояния; для `PHASE_2_LONG_DURATION` — general-состояния и «late»-варианты. EVA/SPE нельзя жёстко привязать к фазе без расписания EVA/SPE.
- Публичных **числовых IMM-частот строго по фазам** нет. Есть per-mission sample output (NASA-STD-3001 Table E.2-1), per-condition incidence rate/proportion в CliFF и правило IMM о first-5-days для SA. Поэтому phase split ниже — **DERIVED**, кроме SA-пропорций.
- Table E.2-1 нельзя трактовать как распределение вероятностей: сумма 48 значений = **101.808 per mission**. Это sample output / ожидаемые события, а не вероятности, которые должны суммироваться в 1.
- Для SANS опубликованная IP = **0.2593** (7/27 person-missions; 95% CI 0.1111–0.4628), model mean Beta = **0.2789**. Onset — в первые 5–7 суток, но состояние сохраняется до конца полёта. Поэтому SANS — P1 по onset, не P2.
- Для CO₂-induced headache rate = **1.5168 events/person-year** (69/45.49), это general-состояние, не SA.
- CliFF Resource Table (RT) — это не полный Capability Resource Table (CRT). Полный CRT находится в Excel/IMPACT-MD; в PDF есть только RT и CRT prose. Поэтому `resources.py` может быть построен по RT, но не выдавать себя за полный CRT.
- SANS в CliFF имеет **CRT prose без RT**: space anticipation glasses, repeat testing, офтальмологическое обследование. Отдельного списка расходников нет.
- CO₂-headache в EMCL/ICL называется **`Headache - CO2` (ICL64)**, а не `Hypercapnia`. SANS называется **`Spaceflight Associated Neuro-Ocular Syndrome (SANS)` (ICL100)**; прежнее имя — `VIIP`.

---

## 2. Методика

- Фаза 1 принята как **5 суток** (IMM: SA onset within first 5 days; CliFF SANS говорит first 5–7 days). Фаза 2 — остальные **175 суток** 180-суточной миссии. Для Table E.2-1 это assumption: в самой таблице длительность миссии не указана; если sample output не 180 суток, split нужно пересчитать.
- Для incidence rate: `phase_1 = rate × 5/365`, `phase_2 = rate × 175/365`, единица — events/person.
- Для incidence proportion: значение остаётся events/person at risk; phase assignment определяется механизмом (SA → P1; late → P2).
- Для SPE: значение **0.05 на событие SPE**, а не на год. Фаза зависит от того, когда произошёл SPE; складывать P1 и P2 нельзя.
- `VERIFIED` — значение и механизм прямо в источнике; `DERIVED` — рассчитано из опубликованного rate/proportion и правила фаз; `NOT FOUND` — числовых данных нет.
- Все derived-значения округлены; в коде лучше хранить исходный rate/proportion и считать phase split функцией, а не заранее округлять.

---

## 3. Phase priors по текущим condition codes

Единицы различаются: `rate` — events/person за фазу; `proportion` — events/person at risk за событие/фазу. Не смешивать в одном агрегате без нормализации.

| code | EMCL/ICL | measure | phase 1 | phase 2 | status | basis |
|---|---|---|---:|---:|---|---|
| `HYPOVOLEMIA` | ICL116 Traumatic Hypovolemic Shock | rate 0.000641/person-year | 8.78e-6 | 3.073e-4 | **DERIVED** | CliFF: fixed rate 0.000641; general split 5/365 + 175/365 |
| `SEPSIS` | ICL84 Sepsis | rate 0.0024/person-year | 3.288e-5 | 1.151e-3 | **DERIVED** | CliFF: fixed rate 0.0024; general split |
| `ACUTE_RADIATION_SYNDROME` | ICL4 Acute Radiation Syndrome | conditional proportion 0.05 per SPE | 0.05 if SPE in P1 | 0.05 if SPE in P2 | **VERIFIED (conditional)** | CliFF: 5% disease given SPE exposure; phase depends on SPE timing |
| `CARDIAC_ARRHYTHMIA` | ICL10 Atrial Fibrillation/Atrial Flutter | rate 0.0004729/person-year total | 6.478e-6 | 2.267e-4 | **DERIVED** | CliFF: total mean 0.0004729; male 0.0007107, female 0.0002343 |
| `SLEEP_DISORDER` (SAS insomnia) | ICL95 Space Adaptation – Insomnia | proportion 0.4721 | 0.4721 | 0 | **VERIFIED** | CliFF: 381/807 = 0.4721189; SA, occurrence 24–120 h, peak 24 h |
| `SLEEP_DISORDER` (late insomnia) | Table E.2-1 Late Insomnia | 13.85 per mission (scale as printed) | 0 | 13.85 | **DERIVED** | Table E.2-1; late condition, P2 only |
| `SANS` | ICL100 Spaceflight Associated Neuro-Ocular Syndrome | proportion 0.2789 (model mean) | 0.2789 | 0 (onset) | **VERIFIED** | CliFF: 7/27 person-missions, observed IP 0.2593, model mean 0.2789; onset first 5–7 days; persists |
| `CO2_HEADACHE` | ICL64 Headache – CO2 | rate 1.5168/person-year | 0.02078 | 0.7272 | **DERIVED** | CliFF: 69/45.49 = 1.5168169; general split |
| `RESPIRATORY_INFECTION` | ICL81/82 Respiratory Tract Infection | rate 0.7694/person-year | 0.01054 | 0.3689 | **DERIVED** | CliFF: 35/45.49 = 0.7693999; general split |
| `DEPRESSION` | ICL15 BHP – Depression | rate male 0.0029 / female 0.0036 per person-year | male 3.973e-5; female 4.932e-5 | male 1.390e-3; female 1.726e-3 | **DERIVED** | CliFF: fixed rates by sex; general split |
| `HYPOXEMIA` | нет в EMCL/ICL (только ARCL88 Hypoxia) | — | — | — | **NOT FOUND** | Нет CliFF/incidence для Hypoxemia как условия |
| `NUTRITIONAL_DEFICIT` | нет в EMCL/ICL | — | — | — | **NOT FOUND** | Нет CliFF/incidence; это не medical condition IMM |

### 3.1. Важное различие единиц

- `HYPOVOLEMIA`, `SEPSIS`, `CARDIAC_ARRHYTHMIA`, `DEPRESSION`, `CO2_HEADACHE`, `RESPIRATORY_INFECTION` — **rates**; phase values — ожидаемое число событий на человека за фазу.
- `SLEEP_DISORDER` SAS и `SANS` — **proportions**; phase values — вероятность/доля людей с onset в фазе, не число событий на год.
- `ACUTE_RADIATION_SYNDROME` — **conditional proportion per SPE**; не rate и не phase probability.
- `Late Insomnia` из Table E.2-1 — sample output в неясной шкале; не смешивать с 0.4721 SAS insomnia.

---

## 4. Table E.2-1: phase allocation

Ниже — все 48 состояний из NASA-STD-3001 Vol.1 Rev C, Table E.2-1, с механической разбивкой. Это **sample output**, не калиброванная вероятность. Значения `P1/P2` — в тех же единицах, что и столбец `Per mission`; для general-состояний применён exposure split 5/175 суток.

Правило:
- `SA → P1`: 100% в P1.
- `Late → P2`: 100% в P2.
- `General split`: `P1 = value × 5/180`, `P2 = value × 175/180`.

| # | Condition | Per mission | Regime | P1 | P2 | Status |
|---|---|---:|---|---:|---:|---|
| 1 | Late Insomnia | 13.85 | Late → P2 | 0.0000 | 13.8500 | DERIVED |
| 2 | Skin Abrasion | 9.86 | General split | 0.2739 | 9.5861 | DERIVED |
| 3 | Skin Rash | 9.83 | General split | 0.2731 | 9.5569 | DERIVED |
| 4 | Eye Abrasion | 7.42 | General split | 0.2061 | 7.2139 | DERIVED |
| 5 | Late Headache | 5.25 | Late → P2 | 0.0000 | 5.2500 | DERIVED |
| 6 | Space Motion Sickness (SAS) | 4.37 | SA → P1 | 4.3700 | 0.0000 | DERIVED |
| 7 | Diarrhea | 3.53 | General split | 0.0981 | 3.4319 | DERIVED |
| 8 | Nasal Congestion | 3.51 | SA → P1 | 3.5100 | 0.0000 | DERIVED |
| 9 | Respiratory Infection | 3.46 | General split | 0.0961 | 3.3639 | DERIVED |
| 10 | Back Injury | 3.41 | General split | 0.0947 | 3.3153 | DERIVED |
| 11 | Barotrauma (Ear/Sinus Block) | 3.28 | General split | 0.0911 | 3.1889 | DERIVED |
| 12 | Back Pain (SAS) | 3.15 | SA → P1 | 3.1500 | 0.0000 | DERIVED |
| 13 | Insomnia (SAS) | 2.70 | SA → P1 | 2.7000 | 0.0000 | DERIVED |
| 14 | Shoulder Sprain/Strain | 2.43 | General split | 0.0675 | 2.3625 | DERIVED |
| 15 | CO2 Headache | 2.15 | General split | 0.0597 | 2.0903 | DERIVED |
| 16 | Headache (SAS) | 2.11 | SA → P1 | 2.1100 | 0.0000 | DERIVED |
| 17 | SANS | 2.08 | SA → P1 | 2.0800 | 0.0000 | DERIVED |
| 18 | Urinary Tract Infection | 1.44 | General split | 0.0400 | 1.4000 | DERIVED |
| 19 | Skin Infection | 1.38 | General split | 0.0383 | 1.3417 | DERIVED |
| 20 | Elbow Sprain/Strain | 1.32 | General split | 0.0367 | 1.2833 | DERIVED |
| 21 | Ankle Sprain/Strain | 1.22 | General split | 0.0339 | 1.1861 | DERIVED |
| 22 | Allergic Reaction | 1.18 | General split | 0.0328 | 1.1472 | DERIVED |
| 23 | Pharyngitis | 1.17 | General split | 0.0325 | 1.1375 | DERIVED |
| 24 | Constipation | 1.02 | SA → P1 | 1.0200 | 0.0000 | DERIVED |
| 25 | Neck Injury | 0.99 | General split | 0.0275 | 0.9625 | DERIVED |
| 26 | Mouth Ulcer | 0.96 | General split | 0.0267 | 0.9333 | DERIVED |
| 27 | Dental Caries | 0.88 | General split | 0.0244 | 0.8556 | DERIVED |
| 28 | Knee Sprain/Strain | 0.78 | General split | 0.0217 | 0.7583 | DERIVED |
| 29 | Paresthesia [EVA] | 0.65 | General split | 0.0181 | 0.6319 | DERIVED |
| 30 | Indigestion | 0.64 | General split | 0.0178 | 0.6222 | DERIVED |
| 31 | Eye Chemical Burn | 0.64 | General split | 0.0178 | 0.6222 | DERIVED |
| 32 | Sinusitis | 0.64 | General split | 0.0178 | 0.6222 | DERIVED |
| 33 | Hearing Loss | 0.57 | General split | 0.0158 | 0.5542 | DERIVED |
| 34 | Wrist Sprain/Strain | 0.55 | General split | 0.0153 | 0.5347 | DERIVED |
| 35 | Eye Infection | 0.53 | General split | 0.0147 | 0.5153 | DERIVED |
| 36 | Hip Sprain/Strain | 0.45 | General split | 0.0125 | 0.4375 | DERIVED |
| 37 | Gastroenteritis | 0.42 | General split | 0.0117 | 0.4083 | DERIVED |
| 38 | Fingernail Delamination [EVA] | 0.40 | General split | 0.0111 | 0.3889 | DERIVED |
| 39 | Otitis Externa | 0.32 | General split | 0.0089 | 0.3111 | DERIVED |
| 40 | Otitis Media | 0.30 | General split | 0.0083 | 0.2917 | DERIVED |
| 41 | Hemorrhoids | 0.22 | General split | 0.0061 | 0.2139 | DERIVED |
| 42 | Lower Extremity Stress Fracture | 0.13 | General split | 0.0036 | 0.1264 | DERIVED |
| 43 | Urinary Retention | 0.11 | SA → P1 | 0.1100 | 0.0000 | DERIVED |
| 44 | Skin Laceration | 0.11 | General split | 0.0031 | 0.1069 | DERIVED |
| 45 | Influenza | 0.11 | General split | 0.0031 | 0.1069 | DERIVED |
| 46 | Finger Dislocation | 0.11 | General split | 0.0031 | 0.1069 | DERIVED |
| 47 | Shingles | 0.11 | General split | 0.0031 | 0.1069 | DERIVED |
| 48 | Dental Abscess | 0.068 | General split | 0.0019 | 0.0661 | DERIVED |

Сумма всех `Per mission` = **101.808**. Это ещё один аргумент не называть столбец вероятностью и не нормировать его вслепую.

---

## 5. Resources по состояниям

### 5.1. Ограничение источника

В CliFF PDF находится **Resource Table (RT)**: `Resource`, `Units Required Best Case`, `Units Required Worst Case`, `Units Available At Start Of Mission`, `Consumable`, `Essential`, `Rationale`.  
Полный **CRT** (capabilities + resource parameters + necessity + alternatives) в PDF не опубликован; HRP-48036 прямо говорит, что CRT data живёт в отдельном Excel/IMPACT-MD. Поэтому таблица ниже — RT, а не полный CRT.

Формат: `item (best/worst)`, только `Essential = Yes`. `0/1` означает «в best case не требуется, в worst case — 1 единица».

### 5.2. `HYPOVOLEMIA` — ICL116 Traumatic Hypovolemic Shock

Источник: `Traumatic Hypovolemic Shock Cliff`, 5/11/2020, RT p.7–9.

- Дыхание/дыхательные пути: Ambu bag and mask (0/1); Endotracheal Stylet (0/1); Endotracheal Tube 7.0/8.0 (0/1); EtCO2 Monitor with EMMA adapter (0/1); King Supraglottic Airway Tube (0/1); Laryngoscope blade (0/1); Laryngoscope handle (0/1); Nasal Airway 6/7 mm (0/1); Oral Airway (0/1); PEEP Valve (0/1); SGA Cue Card (0/1); Suction Cartridge (0/1); Suction device (0/1); Suction device syringe (0/1); Suction tip mouth (0/1); Suction Tubing Endotracheal (0/1); T-adapter (0/1); Variable Oxygen System (0/1); VOS Intubated Patient Hardware (0/1).
- Циркуляция/мониторинг: Adrenaline 1:10000 10 mL (0/4); Blood Oximeter (1/1); Blood Pressure Cuff (1/1); Blood Pressure Monitor (1/1); ECG Monitor (1/1); Pack of 12 ECG electrodes (1/1); IV administration set (1/1); IV Catheter 18G/20G/22G (1/1); IV Fluid 1 L (2/4); Stethoscope (1/1).
- Медикаменты/расходники: Ketamine 50 mg/mL 10 mL (0/0.3); Valium 5 mg/mL 2 mL (0/1); Needle 23G (0/6); Syringe 3cc (1/6); Syringe 10cc (0/1); Syringe 35cc (0/1).

### 5.3. `SEPSIS` — ICL84 Sepsis

Источник: `Sepsis Cliff`, 5/11/2020, RT p.9–11.

- Дыхание/дыхательные пути: Adrenaline 1:10000 10 mL (0/4); Ambu bag and mask (0/1); Endotracheal Stylet (0/1); Endotracheal Tube 7.0/8.0 (0/1); EtCO2 Monitor (0/1); King SGA Tube (0/1); Laryngoscope blade (0/1); Laryngoscope handle (0/1); Nasal Airway (0/1); Oral Airway (0/1); PEEP Valve (0/1); SGA Cue Card (0/1); Suction Cartridge (0/1); Suction device (0/1); Suction device syringe (0/1); Suction tip (0/1); Suction Tubing (0/1); T-adapter (0/1); Variable Oxygen System (0/1); VOS Intubated Hardware (0/1).
- Циркуляция/мониторинг: Blood Oximeter (1/1); Blood Pressure Cuff (1/1); Blood Pressure Monitor (1/1); ECG Monitor (1/1); Pack of 12 ECG electrodes (1/1); IV administration set (1/1); IV Catheter (1/1); IV Fluid 1 L (2/4); Stethoscope (1/1); Ultrasound gel (2/2); Ultrasound machine (1/1).
- Медикаменты/расходники: Ertapenem 1 g (1/3); Ketamine (0/0.3); Lidocaine 1% 10 mL (1/1); Needle 23G (1/6); Needle 25G (1/1); Syringe 3cc (1/10); Syringe 10cc (0/1); Syringe 35cc (0/1); Tylenol 325 mg (12/24); Valium (0/1).

### 5.4. `ACUTE_RADIATION_SYNDROME` — ICL4

Источник: `Acute Radiation Syndrome Cliff`, 5/11/2020, RT p.6–7.

- Bacitracin 500 units/g (0/0.25); Blood Oximeter (1/1); Blood Pressure Cuff (1/1); Blood Pressure Monitor (1/1); Dilaudid 2 mg/mL (0/12); ECG Monitor (0/1); Ertapenem 1 g (0/3); IV administration set (0/1); IV Catheter (0/1); IV Fluid 1 L (0/4); Lidocaine 1% (0/3); Motrin 400 mg (3/0); Needle 23G (0/25); Pack of 12 ECG electrodes (0/1); Promethazine 25 mg/mL (0/18); Stethoscope (0/1); Syringe 3cc (0/25); Valium (0/2); Variable Oxygen System (0/1); Zofran 8 mg (2/2).

### 5.5. `CARDIAC_ARRHYTHMIA` — ICL10 Atrial Fibrillation/Atrial Flutter

Источник: `Atrial Fibrillation/ Atrial Flutter Cliff`, 5/11/2020, RT p.6.

- Aspirin 325 mg (0/3); Blood Oximeter (1/1); Blood Pressure Cuff (1/1); Blood Pressure Monitor (1/1); ECG Monitor (1/1); Lopressor (Metoprolol) 50 mg (0/12); Pack of 12 ECG electrodes (1/1); Variable Oxygen System (0/1).

### 5.6. `SLEEP_DISORDER` — ICL95 Space Adaptation – Insomnia

Источник: `Insomnia (space adaptation) Cliff`, 5/11/2020, RT p.5.

- Zolpidem (Ambien) 5 mg (1/2).
- В комментарии к RT сказано, что нужны и Ambien, и Sonata, выбор индивидуальный; в таблице Sonata отдельной строкой не выделена. Это **расхождение текста и RT**, его нельзя молча исправлять.

### 5.7. `DEPRESSION` — ICL15 BHP – Depression

Источник: `Depression Cliff`, 5/11/2020, RT p.5.

- Abilify (Aripiprazole) 5 mg (0/30); Psychotherapy (1/1); Zoloft (Sertraline) 50 mg (60/60).

### 5.8. `CO2_HEADACHE` — ICL64 Headache – CO2

Источник: `Headache (CO2 induced) Cliff`, 5/11/2020, RT p.8.

- Blood Pressure Cuff (0/1); Blood Pressure Monitor (0/1); Tylenol (Acetaminophen) 325 mg (0/4).
- В комментарии к RT, не в таблице: при кластерных головных болях или подозрении на локальный CO₂ нужен атмосферный пробоотбор `CSA-CP` и портативный CO₂ monitor (`CDM`). Это environmental diagnostic, а не расходник из RT.

### 5.9. `SANS` — ICL100

Источник: `ICL100_Space Flight Associated Neuro-Ocular Syndrome (Sans) Cliff`, 9/19/2022, CRT prose p.6.

- Формальной RT нет.
- Treatment: `space anticipation glasses` и repeat testing; при вариабельной гиперопии нужны либо индивидуальные линзы, либо переменная power lens.
- Diagnosis: history/physical, fundoscopy, vision, OCT, intraocular pressure, focused neurological exam, ophthalmic ultrasound.
- Нет preventive/curative treatment; CNES: NONE.

### 5.10. Справочно: `RESPIRATORY_INFECTION` — ICL81/82

Источник: `Respiratory Infection Cliff`, 5/11/2020, RT p.6.

- Benzonatate 100 mg (10/20); Blood Oximeter (1/1); Dextromethorphan 15 mg (10/20); Stethoscope (1/1); Zithromax (Azithromycin) 250 mg (0/6).
- Это не `HYPOXEMIA`; использовать как ресурс для Hypoxemia нельзя.

### 5.11. `HYPOXEMIA` и `NUTRITIONAL_DEFICIT`

- `HYPOXEMIA`: CliFF/RT нет, в EMCL/ICL условия нет (есть только ARCL88 Hypoxia). Ресурсы не выдумывать.
- `NUTRITIONAL_DEFICIT`: CliFF/RT нет, это не condition IMM. Ресурсы не выдумывать.

---

## 6. CO₂: имена и пороги

- EMCL/ICL имя: **`Headache - CO2` (ICL64)**, не `Hypercapnia`.
- NASA-STD-3001 Vol.2 Rev C [V2 6004]: average 1-hour ppCO₂ in habitable volume **≤ 3 mmHg**.
- Предыдущее требование допускало **3.8–7.5 mmHg**; снижено до 3 mmHg по operational/research data.
- OCHMO-TB-004: у 19 из 49 астронавтов (≈38.7%) были headaches; чтобы держать риск headache <1%, average 7-day CO₂ <2.5 mmHg; текущий ISS range 1–9 mmHg.
- Исторические ассоциации: headaches 2.8–4.5 mmHg, усиление с fatigue/malaise/flushing; >4.5 mmHg — fatigue, malaise, decreased sleep, nausea; 4.5–5.0 mmHg — 5th cranial nerve dysesthesia; 3.5 mmHg — chronic cough, poor sleep, blurred vision, frontal headaches.
- OCHMO связывает часть symptoms с fluid shift/CO₂ retention, а не только с измеренным ppCO₂; SANS и headaches — самые частые in-flight symptoms.
- Для flags: `CO2_ELEVATED`/`CO2_CRITICAL` можно строить от 3 mmHg (standard) и 4.5 mmHg (symptom-associated), но это **design thresholds**, пока правило не утверждено.

---

## 7. Предлагаемая data-only схема

Ниже — не патч, а форма, которую можно один-в-один перенести в `phase_priors.py`. Исходные rate/proportion лучше хранить отдельно от рассчитанных phase values.

```python
PHASE_PRIORS = {
    "HYPOVOLEMIA": {
        "emcl": "ICL116 Traumatic Hypovolemic Shock",
        "measure": "rate",
        "unit": "events/person",
        "phase_1": 8.78e-6,
        "phase_2": 3.073e-4,
        "basis": "0.000641/person-year × 5/365 and 175/365",
        "status": "DERIVED",
    },
    "SEPSIS": {
        "emcl": "ICL84 Sepsis",
        "measure": "rate",
        "unit": "events/person",
        "phase_1": 3.288e-5,
        "phase_2": 1.151e-3,
        "basis": "0.0024/person-year × 5/365 and 175/365",
        "status": "DERIVED",
    },
    "ACUTE_RADIATION_SYNDROME": {
        "emcl": "ICL4 Acute Radiation Syndrome",
        "measure": "conditional_proportion",
        "unit": "per SPE exposure",
        "phase_1": 0.05,
        "phase_2": 0.05,
        "basis": "0.05 given SPE; phase depends on SPE timing",
        "status": "VERIFIED_CONDITIONAL",
    },
    "CARDIAC_ARRHYTHMIA": {
        "emcl": "ICL10 Atrial Fibrillation/Atrial Flutter",
        "measure": "rate",
        "unit": "events/person",
        "phase_1": 6.478e-6,
        "phase_2": 2.267e-4,
        "basis": "total mean 0.0004729/person-year; sex-specific male 0.0007107, female 0.0002343",
        "status": "DERIVED",
    },
    "SLEEP_DISORDER_SAS_INSOMNIA": {
        "emcl": "ICL95 Space Adaptation – Insomnia",
        "measure": "proportion",
        "unit": "events/person at risk",
        "phase_1": 0.4721,
        "phase_2": 0.0,
        "basis": "381/807 = 0.4721189; SA; occurrence 24–120 h",
        "status": "VERIFIED",
    },
    "SLEEP_DISORDER_LATE_INSOMNIA": {
        "emcl": "Table E.2-1 Late Insomnia",
        "measure": "sample_per_mission",
        "unit": "as printed",
        "phase_1": 0.0,
        "phase_2": 13.85,
        "basis": "late condition; Table E.2-1",
        "status": "DERIVED",
    },
    "SANS": {
        "emcl": "ICL100 Spaceflight Associated Neuro-Ocular Syndrome",
        "measure": "proportion",
        "unit": "events/person at risk",
        "phase_1": 0.2789,
        "phase_2": 0.0,
        "basis": "model mean 0.2789; observed IP 0.2593 (7/27); onset first 5–7 days, persists",
        "status": "VERIFIED",
    },
    "CO2_HEADACHE": {
        "emcl": "ICL64 Headache – CO2",
        "measure": "rate",
        "unit": "events/person",
        "phase_1": 0.02078,
        "phase_2": 0.7272,
        "basis": "69/45.49 = 1.5168169/person-year; general split",
        "status": "DERIVED",
    },
    "RESPIRATORY_INFECTION": {
        "emcl": "ICL81/82 Respiratory Tract Infection",
        "measure": "rate",
        "unit": "events/person",
        "phase_1": 0.01054,
        "phase_2": 0.3689,
        "basis": "35/45.49 = 0.7693999/person-year; general split",
        "status": "DERIVED",
    },
    "DEPRESSION": {
        "emcl": "ICL15 BHP – Depression",
        "measure": "rate",
        "unit": "events/person",
        "phase_1": {"male": 3.973e-5, "female": 4.932e-5},
        "phase_2": {"male": 1.390e-3, "female": 1.726e-3},
        "basis": "male 0.0029, female 0.0036/person-year; general split",
        "status": "DERIVED",
    },
    "HYPOXEMIA": None,
    "NUTRITIONAL_DEFICIT": None,
}
```

Для `resources.py` предлагается такая форма:

```python
RESOURCES_BY_CONDITION = {
    "HYPOVOLEMIA": {
        "emcl": "ICL116 Traumatic Hypovolemic Shock",
        "cliff": "Traumatic Hypovolemic Shock Cliff, 5/11/2020, RT p.7–9",
        "essential": {
            "Ambu bag and mask": (0, 1),
            "Adrenaline 1:10000 10 mL": (0, 4),
            "IV Fluid 1 L": (2, 4),
            "IV Catheter 18G/20G/22G": (1, 1),
            "Endotracheal Tube 7.0/8.0": (0, 1),
            "Variable Oxygen System": (0, 1),
        },
        "status": "VERIFIED_RT",
    },
    "SANS": {
        "emcl": "ICL100 Spaceflight Associated Neuro-Ocular Syndrome",
        "cliff": "ICL100 SANS Cliff, 9/19/2022, CRT prose p.6",
        "essential": {
            "space anticipation glasses": None,
            "repeat ophthalmic testing": None,
        },
        "note": "no formal RT; counts not published",
        "status": "VERIFIED_CRT_PROSE",
    },
}
```

Полные списки RT — в разделах 5.2–5.10; в `resources.py` их можно сгруппировать по capability (`airway`, `circulation`, `medications`, `diagnostics`) без изменения чисел.

---

## 8. Ограничения и открытые вопросы

1. **Нет публичного per-phase числового IMM output.** Все P1/P2, кроме SA-пропорций, — derived.
2. **Table E.2-1 scale не указана.** Значения выглядят как expected events per mission, потому что сумма 101.808; нельзя автоматически превращать в вероятность.
3. **SANS incidence расходится:** Table E.2-1 даёт 2.08 per mission, CliFF 2022 — 0.2593 observed IP / 0.2789 model mean. Разные определения и эпохи; для SANS использовать CliFF 2022.
4. **SANS onset vs duration:** onset в P1, но состояние персистирует в P2; `phase_2 = 0` означает «нет новых onset», а не «нет случаев».
5. **EVA/SPE не привязаны к фазе.** Paresthesia, fingernail delamination, ARS требуют отдельного EVA/SPE-расписания.
6. **RT ≠ CRT.** Полный CRT в PDF отсутствует; `resources.py` по RT не должен обещать capability-level полноту.
7. **Sonata vs Zolpidem:** текст RT говорит, что нужны оба, таблица содержит только Zolpidem. Нужен отдельный source check перед кодом.
8. **CO₂ flag thresholds** (3 mmHg vs 4.5 mmHg) — design decision; в EVIDENCE.md пока нет утверждённого правила.
9. **`HYPOVOLEMIA` — не EMCL-имя.** В коде можно оставить code, но в `emcl` поле писать `ICL116 Traumatic Hypovolemic Shock`.

---

## 9. Источники

- NASA-STD-3001 Vol.1 Rev C, Appendix E, Table E.2-1 — sample IMM output, 48 conditions.
- NASA-STD-3001 Vol.2 Rev C, [V2 6004] — 1-hour ppCO₂ ≤ 3 mmHg.
- OCHMO-TB-004 Carbon Dioxide, Rev B, 11/10/2022 — historical CO₂ symptoms, 19/49 headaches, <3 mmHg.
- IMM 2015, NTRS 20150018879 — SA first 5 days, general Poisson, SPE/EVA mechanics, Appendix condition names.
- HRP-48036 Rev B, ExMC Evidence Library Methods — ICL/ARCL names, SAS/EVA/Environmental categories, CRT/RT distinction.
- `Traumatic Hypovolemic Shock Cliff`, 5/11/2020.
- `Sepsis Cliff`, 5/11/2020.
- `Acute Radiation Syndrome Cliff`, 5/11/2020.
- `Atrial Fibrillation/ Atrial Flutter Cliff`, 5/11/2020.
- `Insomnia (space adaptation) Cliff`, 5/11/2020.
- `Depression Cliff`, 5/11/2020.
- `Headache (CO2 induced) Cliff`, 5/11/2020.
- `Respiratory Infection Cliff`, 5/11/2020.
- `ICL100_Space Flight Associated Neuro-Ocular Syndrome (Sans) Cliff`, 9/19/2022.

### 9.1. Локальные копии

- `/tmp/opencode/astro/std3001.txt` — NASA-STD-3001 Vol.1 Rev C, Table E.2-1.
- `/tmp/opencode/astro/imm2015.txt` — IMM 2015, NTRS 20150018879.
- `/tmp/opencode/astro/hrp48036.txt` — HRP-48036 Rev B.
- `/tmp/opencode/astro/co2_brief.txt` — OCHMO-TB-004, Rev B.
- `/tmp/opencode/astro/cliff_hypovolemic.txt`
- `/tmp/opencode/astro/sepsis2.txt`
- `/tmp/opencode/astro/cliff_ars.txt`
- `/tmp/opencode/astro/cliff_af.txt`
- `/tmp/opencode/astro/cliff_insomnia.txt`
- `/tmp/opencode/astro/cliff_depression.txt`
- `/tmp/opencode/astro/cliff_co2.txt`
- `/tmp/opencode/astro/cliff_resp.txt`
- `/tmp/opencode/astro/cliff_sans.txt`

### 9.2. URL

- OCHMO-TB-004: https://www.nasa.gov/ochmo-tb-004-carbon-dioxide-2/
- CO₂ technical brief: https://www.nasa.gov/wp-content/uploads/2023/03/co2-technical-brief-ochmo.pdf
