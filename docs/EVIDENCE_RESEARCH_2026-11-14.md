# AstroCare — проверка источников для docs/EVIDENCE.md

Дата проверки: 2026-11-14  
Проверяющий: исследовательский проход по открытым источникам  
Объект: `abdyrazakov/AstroCare`, текущий `docs/EVIDENCE.md` (v0.2)  
Принцип: источник считается подтверждённым только там, где открыт документ и видна цитата.  
Где документ недоступен (MORD SSP 50260, полный NCRP Commentary No. 32) — это указано явно.

---

## 1. Краткий вывод

- **Подтверждены:** карьерный лимит 600 мЗв и его определение как NASA effective dose; предписание упражнений 2,5 ч/сут × 6 дн/нед; порог PHQ-2 ≥ 3.
- **Исправить атрибуцию:** 600 мЗв — это предложение NASA, рассмотренное и поддержанное **NASEM 2021**, а не NCRP 2021. NCRP Commentary No. 32 (2022) посвящён другой теме.
- **Исправить порог:** калорийный дефицит в NASA — **< 80% EER = red**, а не < 70%.
- **Исправить имена состояний:** в EMCL нет «Hypovolemia» — есть **Hypovolemic Shock**; нет «Hypoxemia»/«Hypoxia» в основном списке — «Hypoxia» есть только в остаточном списке ARCL (ARCL88).
- **Исправить диапазон:** 12–30 µSv/ч не является цитатой; открытые источники дают 0,2–0,5 мЗв/сут (≈8–21 µSv/ч), отдельные периоды до 1,2 мЗв/сут (≈50 µSv/ч).
- **Методическая проблема:** сравнивать накопленную effective dose (мЗв) с 30-суточным BFO-лимитом 250 мГр-экв напрямую нельзя; это не «консервативная аппроксимация».
- **NEWS2:** пороги RCP подтверждены, но валидации для астронавтов/микрогравитации не найдено; нужен честный limitation-абзац.

---

## 2. Таблица по 11 пунктам

| # | flag / threshold | value | source (открывается) | section / page | status | цитата / что найдено |
|---|---|---|---|---|---|---|
| 1 | NCRP 2021 attribution / происхождение 600 мЗв | 600 мЗв приписаны NCRP 2021 | [NASA-STD-3001 Vol.1 Rev C](https://www.nasa.gov/wp-content/uploads/2023/11/nasa-std-3001-vol-1-rev-c-with-signature.pdf); [NASEM 2021, doi:10.17226/26155](https://doi.org/10.17226/26155); [NCRP Commentary No. 32](https://ncrponline.org/shop/commentaries/commentary-no-32-evaluation-of-a-sex-specific-difference-in-lung-cancer-radiation-risk-projection-with-a-focus-on-application-to-space-activities-2022/) | §4.8.2, p.39 (Rationale); NASEM Box 3-1; NCRP abstract | **CONFLICT** | NASA: *“For background on setting the limit for this standard, refer to National Academies of Sciences, Engineering, and Medicine 2021. Space Radiation and Astronaut Health: Managing and Communicating Cancer Risks.”* NCRP Commentary No. 32 (2022) — про половые различия риска рака лёгких, не про 600 мЗв. |
| 2 | radiation_dose_career_msv input provenance | NASA effective dose, мЗв | [NASA-STD-3001 Vol.1 Rev C](https://www.nasa.gov/wp-content/uploads/2023/11/nasa-std-3001-vol-1-rev-c-with-signature.pdf) | §4.8.2, p.39 | **VERIFIED** (определение); provenance данных — ещё аудит | *“An individual crewmember’s total career effective radiation dose due to spaceflight radiation exposure shall be less than 600 mSv. This limit is universal for all ages and sexes.”* Note: доза считается через NASA Q (NASA cancer model 2012) и параметры 35-летней женщины для обоих полов. |
| 3 | ISS background context | 12–30 µSv/ч | [Shavers et al. 2023, PMC10919966](https://pmc.ncbi.nlm.nih.gov/articles/PMC10919966/); [NASA/JSC acute effects](https://three.jsc.nasa.gov/articles/SeedAcuteEffects.pdf); [Atwell/NAIRAS](https://wrmiss.org/workshops/seventeenth/Atwell.pdf) | Results; текст; слайды | **CONFLICT** (точный диапазон не подтверждён) | Shavers: *“Effective doses usually accumulate at a rate of ∼0.2 to ∼0.5 mSv or more each day of a mission.”* → 8–21 µSv/ч. NASA/JSC: *“typical exposures on the ISS are in the range of 0.5 to 1.2 mSv per day”* → 21–50 µSv/ч. Atwell: *“The exposure rate on ISS ≈ 18-20 µSv/hr.”* Ни один источник не даёт 12–30 µSv/ч. |
| 4 | EXERCISE_DEFICIT | <50% предписанных минут; предписание 2,5 ч/сут, 6 дн/нед | [NASA SP-20250000273](https://www.nasa.gov/wp-content/uploads/2025/02/sp-20250000273.pdf); [NTRS 20110016265](https://ntrs.nasa.gov/citations/20110016265); [Hackney et al. 2015](https://journals.lww.com/nsca-jscr/Fulltext/2015/12000/The_Astronaut_Athlete___Optimizing_Human.35.aspx) | “Current exercise practices”; Abstract/Conclusions; текст | **VERIFIED** (предписание); **NOT FOUND** (официальный порог <50%) | NASA: *“recommended 2.5 hours a day/6 days a week of exercise with 30-60 minutes of resistive training and average 27 minutes of metabolic/aerobic training…”* NTRS: *“2.5 h blocks, six days a week, which includes 1.5 h for resistive training and 1 h for aerobic exercise.”* Официального порога «недовыполнения» не найдено; MORD SSP 50260 публично не открывается. |
| 5 | CALORIC_DEFICIT | в репо <70%; норма NASA — <80% = red | [JSC-63555 (2005), NTRS 20200001703](https://ntrs.nasa.gov/api/citations/20200001703/downloads/20200001703.pdf); [JSC 67378 (2020)](https://ntrs.nasa.gov/api/citations/20205008306/downloads/JSC67378%20Expl%20Nutr%20Reqs%20042020.pdf); [NASA-STD-3001 Vol.2, 7.1.1.3](https://www.nasa.gov/reference/7-0-habit-ability-functions-vol-2/) | “Energy intake operating bands”; Energy Intake; [V2 7003] | **CONFLICT** | JSC-63555: *“90-100% green; 80-90% yellow; <80% red”* (% от EER). То есть 70% — ниже красной зоны NASA; менять на 80% red / 80–90% yellow. Исторически: Apollo–Shuttle ~70%, ISS ~80% (NTRS 20150000512). |
| 6 | HYPOVOLEMIA | имя условия EMCL | [NTRS 20160011168, Table 2 (EMCL JSC-65722)](https://ntrs.nasa.gov/api/citations/20160011168/downloads/20160011168.pdf); [SMEMCL 2011, NTRS 20110008645](https://ntrs.nasa.gov/api/citations/20110008645/downloads/20110008645.pdf); [HRP-48036 Rev B, ICL/ARCL](https://ntrs.nasa.gov/api/citations/20240004774/downloads/HRP-48036%20RevB_ExMC%20Evidence%20Library%20Methods.pdf) | Table 2; priority list; ICL116 / ARCL | **NOT FOUND** (точного “Hypovolemia”); ближайшее — **“Hypovolemic Shock”** | EMCL Table 2: *“Hypovolemic Shock”*. ICL 1.0: **ICL116 “Traumatic Hypovolemic Shock”**, CNES-синоним *“Acute Hypovolemia”*. Отдельного условия “Hypovolemia” нет. |
| 7 | HYPOXEMIA | EMCL “Hypoxia” | [NTRS 20160011168, Table 2](https://ntrs.nasa.gov/api/citations/20160011168/downloads/20160011168.pdf); [NASA Appendix E, Table E.2-2](https://www.nasa.gov/reference/appendix-e-health-and-medical-care-technical-requirements/); [HRP-48036 Rev B, Appendix G](https://ntrs.nasa.gov/api/citations/20240004774/downloads/HRP-48036%20RevB_ExMC%20Evidence%20Library%20Methods.pdf) | Table 2; Table E.2-2; ARCL88 | **NOT FOUND** | В EMCL Table 2 и Appendix E нет “Hypoxemia”/“Hypoxia”. **“Hypoxia” есть только как ARCL88** в *All Remaining Conditions List* (остаточный список, не основной ICL). Ближайшие основные: *Respiratory tract infection (lower/upper)*, *Altitude sickness*. |
| 8 | RADIATION_30DAY_LIMIT | yellow ≥125 мЗв; red ≥250 мЗв | [NASA-STD-3001 Vol.1, Table 4.8-1](https://www.nasa.gov/wp-content/uploads/2023/11/nasa-std-3001-vol-1-rev-c-with-signature.pdf) | Table 4.8-1, p.40; Table 4.8-2 | **ASSUMPTION → несостоятельно** | Table 4.8-1: *“Blood-forming Organs# — 250 mGy-Eq”* (30-day). Это organ dose equivalent, не effective dose. Прямое сравнение мЗв с мГр-экв — разные величины; «консервативной аппроксимацией» не является. |
| 9 | nominal mock cumulative doses | 15 мЗв/30 сут; 120 мЗв карьера | [Shavers et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10919966/); [Simonsen 2025, NTRS 20250006168](https://ntrs.nasa.gov/api/citations/20250006168/downloads/ASCEND%20Simonsen%20draft%201.pdf) | Results; §III | **ASSUMPTION → правдоподобный верхний край** | 15/30 = 0,5 мЗв/сут; 120/240 = 0,5 мЗв/сут. Shavers: типично 0,2–0,5 мЗв/сут. Simonsen: ~40–90 мЗв за 6 мес; максимум multi-mission у США ~240–290 мЗв. 0,5 мЗв/сут — верхняя граница, но не «типичное» значение. |
| 10 | LOW_MOOD / PHQ-2 | PHQ-2 ≥3 | [Kroenke, Spitzer, Williams 2003, PMID 14583691](https://pubmed.ncbi.nlm.nih.gov/14583691/); [OCHMO Behavioral Health Brief](https://www.nasa.gov/wp-content/uploads/2023/03/behavioral-health-technical-brief-ochmo.pdf) | Abstract; “In-Flight Psychological and Neurobehavioral Monitoring” | **VERIFIED** (порог PHQ-2); in-flight стандарт PHQ-2 — **NOT FOUND** | Kroenke: *“a PHQ-2 score > or =3 had a sensitivity of 83% and a specificity of 92% for major depression… identified a PHQ-2 score of 3 as the optimal cutpoint for screening purposes.”* NASA: *“Cognitive testing is currently fulfilled by the monthly administration of the Spaceflight Cognitive Assessment Tool for Windows (WinSCAT).”* |
| 11 | NEWS2 и невесомость | NEWS2 | [RCP NEWS2 2017](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Recommendations, p.xvi; §3 | **NOT FOUND** (валидации для астронавтов/микрогравитации) | RCP: *“We recommend that the routine clinical assessment of all adult patients (aged 16 years or more) should be standardised across the NHS…”* В отчёте нет astronaut/spaceflight/microgravity. В PubMed/NTRS валидации NEWS2 у астронавтов не найдено. |

---

## 3. По пунктам: что именно проверено

### 1. NCRP 2021 → на самом деле NASEM 2021

Открыт NASA-STD-3001 Vol.1 Rev C (approved 2023-09-15), §4.8.2, p.39. В Rationale прямым текстом:

> “For background on setting the limit for this standard, refer to National Academies of Sciences, Engineering, and Medicine 2021. Space Radiation and Astronaut Health: Managing and Communicating Cancer Risks. Washington, DC: The National Academies Press. https://doi.org/10.17226/26155.”

В NASEM Box 3-1 указано, что 600 мЗв — это **предложение NASA** (white paper OCHMO), которое комитет NASEM рассмотрел и рекомендовал. Источник — NASA, не NCRP.

NCRP Commentary No. 32 (2022) имеет другую тему: “Evaluation of a Sex-Specific Difference in Lung Cancer Radiation Risk Projection (with a Focus on Application to Space Activities)”. Это не документ о 600 мЗв.

Отдельно: в сноске к Table 4.8-1 NASA действительно ссылается на **NCRP Report No. 132 (2000)** — но только для органных лимитов (lens, skin, BFO, circulatory), а не для карьерных 600 мЗв. Вероятно, отсюда и путаница «NCRP 2021».

**Вывод:** атрибуцию NCRP 2021 убрать, поставить NASEM 2021; сам лимит 600 мЗв остаётся верным.

### 2. radiation_dose_career_msv — это NASA effective dose

§4.8.2, p.39:

> “An individual crewmember’s total career effective radiation dose due to spaceflight radiation exposure shall be less than 600 mSv. This limit is universal for all ages and sexes.”

Note:

> “The NASA effective dose for determining the threshold limit is calculated using the NASA Q (based on the NASA cancer model of 2012…), 35-year-old female model parameters (tissue weighting factors, phantom etc.), for both males and females. Individual crewmember REID calculations are calculated using the appropriate NASA Q … sex and age model parameters.”

Это подтверждает, что в поле `radiation_dose_career_msv` должна подаваться именно NASA effective dose, а не ICRP effective dose, не absorbed dose и не произвольный «мЗв». Равенство вашего симулятора этой величине документом не подтверждается — это отдельный аудит data pipeline.

### 3. ISS background 12–30 µSv/ч — точный диапазон не подтверждён

Проверены три источника:

- Shavers et al. 2023 (PMC10919966): *“Effective doses usually accumulate at a rate of ∼0.2 to ∼0.5 mSv or more each day of a mission.”* → 8–21 µSv/ч. Также: personal badges обычно <0,3 мГр/сут, иногда >0,4 мГр/сут.
- NASA/JSC (three.jsc.nasa.gov, со ссылкой на NCRP-153, 2006): *“typical exposures on the International Space Station (ISS) are in the range of 0.5 to 1.2 mSv per day”* → 21–50 µSv/ч.
- Atwell/NAIRAS: *“The exposure rate on ISS ≈ 18-20 µSv/hr.”*

Диапазон 12–30 µSv/ч (0,29–0,72 мЗв/сут) не является цитатой ни из одного источника; он попадает между «типичным» и «design envelope».

**Рекомендация для EVIDENCE:** “0,2–0,5 мЗв/сут (≈8–21 µSv/ч), отдельные периоды до 1,2 мЗв/сут (≈50 µSv/ч)”; отдельно указать, что 12–30 было инженерным envelope, а не измеренным диапазоном.

### 4. EXERCISE_DEFICIT — предписание подтверждено, порог 50% — ваше решение

NASA SP-20250000273:

> “recommended 2.5 hours a day/6 days a week of exercise with 30-60 minutes of resistive training and average 27 minutes of metabolic/aerobic training, with the remaining time allocated for crew setup and cleanup.”

NTRS 20110016265:

> “In-flight countermeasure sessions are scheduled in 2.5 h blocks, six days a week, which includes 1.5 h for resistive training and 1 h for aerobic exercise.”

Этого достаточно, чтобы подтвердить 2,5 ч × 6 дн/нед, включая setup/cleanup.

**MORD SSP 50260** не открыт: публичной копии нет, в открытых источниках только ссылки на него (например, MEDB 5.3). Официального порога «<50% предписанного = недовыполнение» в NASA-документах не найдено; это design decision, а не норматив.

### 5. CALORIC_DEFICIT — реальный конфликт: 70% vs 80%

JSC-63555 (2005), Table “Energy intake operating bands”:

> “90-100% green; 80-90% yellow; <80% red” (% от EER).

JSC 67378 (2020) для exploration даёт EER с activity factor 1,11 (и 1,25, если exercise как на ISS), но не отменяет operating bands. NASA-STD-3001 Vol.2 [V2 7003] даёт 3 035 ккал/сут (average) и EER-формулы с AF 1,25.

Исторические данные: Apollo–Shuttle ~70% от расчётной нормы, ISS ~80% (NTRS 20150000512; NASA “Human Adaptation to Spaceflight: The Role of Nutrition”).

**Вывод:** ваш порог <70% пропускает состояния, которые NASA относит к красной зоне (<80%). Рекомендация: red <80%, yellow 80–90%, green 90–100%. Если хотите оставить 70% как «тяжёлый дефицит», это должна быть отдельная явно прототипная строка, а не «норма NASA».

### 6. HYPOVOLEMIA — точного имени нет; есть Hypovolemic Shock

- EMCL Table 2 (воспроизведена в NTRS 20160011168, IAC-16): **“Hypovolemic Shock”**.
- SMEMCL 2011 (NTRS 20110008645): **“Hypovolemic Shock”**.
- ICL 1.0 (HRP-48036 Rev B): **ICL116 “Traumatic Hypovolemic Shock”**, в колонке CNES — синоним **“Acute Hypovolemia”**.

Отдельного условия «Hypovolemia» в EMCL/ICL нет.

**Вывод:** либо переименовать флаг в `HYPOVOLEMIC_SHOCK`, либо в EVIDENCE написать: «Hypovolemia = CNES-синоним для ICL116 Traumatic Hypovolemic Shock; отдельного EMCL-условия нет». Текущая формулировка «EMCL condition name» неверна.

### 7. HYPOXEMIA — в EMCL/ICL нет; “Hypoxia” только в ARCL

В EMCL Table 2 и NASA Appendix E Table E.2-2 нет ни “Hypoxemia”, ни “Hypoxia”. Есть *Altitude Sickness*, *Respiratory Infection*, *Chest Injury/Pneumothorax*, *Smoke Inhalation*, *Choking/Obstructed Airway*.

В HRP-48036 Rev B “Hypoxia” появляется только как **ARCL88** в *Appendix G: All Remaining Conditions List* — это остаточный/справочный список, не основной ICL.

**Вывод:** текущая строка EVIDENCE «HYPOXEMIA | EMCL “Hypoxia”» неверна. Варианты:
1. переименовать в `RESPIRATORY_INFECTION_LOWER` / `ALTITUDE_SICKNESS`, если сценарий про инфекцию/гипоксию;
2. оставить `HYPOXEMIA` как физиологический флаг, но указать: «EMCL provenance: none; ARCL88 Hypoxia only; weights ours».

### 8. RADIATION_30DAY_LIMIT — это разные величины

Table 4.8-1, p.40: **BFO 30-day limit = 250 mGy-Eq**. В Rationale к §4.8.2 сказано, что органные лимиты считаются “using mGy-eq calculations”, а Table 4.8-2 задаёт RBE для нейтронов и др.

- `мЗв` — effective dose (сумма по органам с tissue weighting factors, стохастический риск).
- `мГр-экв` — органная поглощённая доза × RBE (неканцерогенные эффекты).

Это не взаимозаменяемые единицы. Прямое численное сравнение 250 мЗв с 250 мГр-экв **нельзя назвать консервативной аппроксимацией**: для типичного поля BFO мГр-экв может быть больше effective dose, поэтому red-порог сработает позже реального BFO-лимита — риск недооценки, а не перестраховки.

**Что делать:**
1. Запросить у data-equivalent **`bfo_dose_mgy_eq_30d`** напрямую.
2. Если его нет — **`bfo_absorbed_dose_mgy_30d` + спектр/quality factor**, и считать мГр-экв по Table 4.8-2.
3. Если доступна только effective dose — не маркировать это как «30-day BFO limit»; оставить как отдельный screening-показатель с явной оговоркой или убрать флаг до появления BFO-дозы.

### 9. Mock-значения 15 мЗв/30 сут и 120 мЗв/240 сут

- 15/30 = 0,5 мЗв/сут; 120/240 = 0,5 мЗв/сут.
- Shavers 2023: типично 0,2–0,5 мЗв/сут.
- Simonsen 2025: ~40–90 мЗв за типичную 6-месячную экспедицию; максимальные multi-mission дозы у американских астронавтов ~240–290 мЗв.

0,5 мЗв/сут — верхняя граница типичного диапазона, но не измеренная история конкретного crewmember. Для мока это нормально, если в EVIDENCE явно написано «synthetic upper-bound fixture, not a measured crew history». 120 мЗв также = 20% от 600 мЗв, поэтому карьерный warning (300 мЗв) этот мок не проверяет; для warning нужен отдельный fixture.

### 10. PHQ-2 ≥3 — подтверждено; в полёте NASA использует WinSCAT

Kroenke et al. 2003 (Med Care 41(11):1284–92; PMID 14583691):

> “a PHQ-2 score > or =3 had a sensitivity of 83% and a specificity of 92% for major depression… identified a PHQ-2 score of 3 as the optimal cutpoint for screening purposes.”

Это валидный земной primary-care screen, не диагностический инструмент и не «in-flight standard».

OCHMO Behavioral Health Brief:

> “Cognitive testing is currently fulfilled by the monthly administration of the Spaceflight Cognitive Assessment Tool for Windows (WinSCAT). A preflight baseline is obtained for each astronaut and is then compared using a monthly in-flight test.”

В исследованиях/аналогах также используются PVT, BDI-II, PANAS, POMS-SF, Cognition + AMS. PHQ-2 как операционного стандарта NASA не найден.

**Для `mood_score`:** либо реализовать PHQ-2 буквально (2 пункта, 0–3 каждый, cutoff ≥3) и называть это PHQ-2 screen, либо оставить ad hoc 1–10, но переименовать в «subjective mood (unvalidated)» и не ссылаться на Kroenke как на валидацию вашей шкалы.

### 11. NEWS2 и невесомость — валидации нет

RCP NEWS2 2017 — отчёт для взрослых пациентов NHS (aged 16+), validated in terrestrial acute-illness settings (ED, prehospital):

> “We recommend that the routine clinical assessment of all adult patients (aged 16 years or more) should be standardised across the NHS…”

В отчёте нет astronaut/spaceflight/microgravity. В PubMed/NTRS/NASA валидации NEWS/NEWS2 у астронавтов или в микрогравитации не найдено.

**Вывод:** NEWS2 можно использовать как вспомогательный тренд/adjunct, но не как «валидированный для экипажа» инструмент. Сами пороги HR/SpO2/BP и т.д. остаются VERIFIED по RCP — не меняйте их статус; добавьте отдельную строку про spaceflight applicability = NOT FOUND.

---

## 4. Что конкретно поправить в docs/EVIDENCE.md

Не менять `CAREER_EFFECTIVE_DOSE_LIMIT_MSV = 600` — он верный. Изменения:

1. **`NCRP 2021 attribution`** → статус **CONFLICT**; source: NASA-STD-3001 Rev C §4.8.2 Rationale + NASEM 2021 (doi:10.17226/26155). Note: “600 mSv is NASA’s proposed standard, reviewed/endorsed by NASEM 2021; NCRP Commentary No. 32 (2022) is unrelated. NCRP Report 132 (2000) is cited only for Table 4.8-1 organ limits.”
2. **`radiation_dose_career_msv input provenance`** → **VERIFIED (definition)**; note: “NASA effective dose per §4.8.2 Note (NASA Q 2012, 35-y-o female parameters); actual pipeline equivalence not audited.”
3. **`ISS background context`** → **CONFLICT**; value: “0.2–0.5 mSv/day (≈8–21 µSv/h), episodes up to 1.2 mSv/day (≈50 µSv/h)”; sources: Shavers 2023 + NASA/JSC acute effects + Atwell. Note: “12–30 µSv/h was a derived envelope, not a quoted measured range.”
4. **`EXERCISE_DEFICIT`** → **VERIFIED (prescription)**; value: “2.5 h/day × 6 d/week”; note: “<50% is a design decision; no official NASA underperformance cutoff found; MORD SSP 50260 not publicly opened.”
5. **`CALORIC_DEFICIT`** → **CONFLICT**; value: “red <80% of EER; yellow 80–90%; green 90–100%”; source: JSC-63555 (2005), Table “Energy intake operating bands”; note: “70% is below NASA’s red band and is not a NASA cutoff.”
6. **`HYPOVOLEMIA`** → **NOT FOUND (exact)**; note: “EMCL Table 2 has ‘Hypovolemic Shock’; ICL116 ‘Traumatic Hypovolemic Shock’, CNES synonym ‘Acute Hypovolemia’; no standalone ‘Hypovolemia’ condition. Rename or document synonym.”
7. **`HYPOXEMIA`** → **NOT FOUND**; note: “No ‘Hypoxemia’/‘Hypoxia’ in EMCL Table 2 or NASA Appendix E; ‘Hypoxia’ only ARCL88 (All Remaining Conditions List). Nearest primary: Respiratory tract infection (lower/upper), Altitude sickness.”
8. **`RADIATION_30DAY_LIMIT`** → оставить **ASSUMPTION**, но добавить: “not a valid unit conversion; direct mSv-to-mGy-Eq comparison is not conservative; request bfo_dose_mgy_eq_30d or bfo_absorbed_dose_mgy_30d + spectrum/RBE.”
9. **`nominal mock cumulative doses`** → **ASSUMPTION**; note: “0.5 mSv/day is the upper end of the typical 0.2–0.5 mSv/day ISS range; synthetic upper-bound fixture, not measured crew history; 120 mSv = 20% of career limit.”
10. **`LOW_MOOD`** → разделить: PHQ-2 ≥3 — **VERIFIED** (Kroenke 2003); текущая ad hoc 1–10 шкала — **DESIGN DECISION**; note: “NASA operational cognitive monitoring uses monthly WinSCAT; no PHQ-2 operational standard found.”
11. **NEWS2 rows** → оставить пороги **VERIFIED** по RCP; добавить отдельную строку: **`NEWS2 spaceflight validation` → NOT FOUND**; note с limitation-абзацем.

---

## 5. Предлагаемые строки для вставки в docs/EVIDENCE.md

```md
| NCRP 2021 attribution | origin of universal 600 mSv recommendation | [NASA-STD-3001 Rev C §4.8.2 Rationale](https://www.nasa.gov/wp-content/uploads/2023/11/nasa-std-3001-vol-1-rev-c-with-signature.pdf); [NASEM 2021](https://doi.org/10.17226/26155) | §4.8.2 p.39; NASEM Box 3-1 | CONFLICT | NASA cites NASEM 2021, not NCRP 2021. NCRP Commentary No. 32 (2022) is about sex-specific lung-cancer risk; NCRP Report 132 (2000) is cited only for Table 4.8-1 organ limits. |
| radiation_dose_career_msv input provenance | NASA effective dose (mSv) | [NASA-STD-3001 Rev C §4.8.2 Note](https://www.nasa.gov/wp-content/uploads/2023/11/nasa-std-3001-vol-1-rev-c-with-signature.pdf) | §4.8.2 p.39 | VERIFIED (definition) | NASA Q (2012 cancer model), 35-y-o female parameters for both sexes. Pipeline equivalence still needs audit. |
| ISS background context | 0.2–0.5 mSv/day (≈8–21 µSv/h); episodes up to 1.2 mSv/day (≈50 µSv/h) | [Shavers et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10919966/); [NASA/JSC acute effects](https://three.jsc.nasa.gov/articles/SeedAcuteEffects.pdf); [Atwell/NAIRAS](https://wrmiss.org/workshops/seventeenth/Atwell.pdf) | Results; text | CONFLICT | 12–30 µSv/h was a derived envelope, not a quoted measured range. |
| EXERCISE_DEFICIT | 2.5 h/day × 6 d/week; <50% = design decision | [NASA SP-20250000273](https://www.nasa.gov/wp-content/uploads/2025/02/sp-20250000273.pdf); [NTRS 20110016265](https://ntrs.nasa.gov/citations/20110016265) | Current exercise practices; Abstract | VERIFIED (prescription); NOT FOUND (official <50% cutoff) | No NASA underperformance threshold found; MORD SSP 50260 not publicly opened. |
| CALORIC_DEFICIT | red <80% of EER; yellow 80–90%; green 90–100% | [JSC-63555 (2005)](https://ntrs.nasa.gov/api/citations/20200001703/downloads/20200001703.pdf); [JSC 67378 (2020)](https://ntrs.nasa.gov/api/citations/20205008306/downloads/JSC67378%20Expl%20Nutr%20Reqs%20042020.pdf) | Energy intake operating bands | CONFLICT | 70% is below NASA’s red band and is not a NASA cutoff. |
| HYPOVOLEMIA | EMCL “Hypovolemic Shock” | [NTRS 20160011168 Table 2](https://ntrs.nasa.gov/api/citations/20160011168/downloads/20160011168.pdf); [NTRS 20110008645](https://ntrs.nasa.gov/api/citations/20110008645/downloads/20110008645.pdf); [HRP-48036 Rev B](https://ntrs.nasa.gov/api/citations/20240004774/downloads/HRP-48036%20RevB_ExMC%20Evidence%20Library%20Methods.pdf) | Table 2; ICL116 | NOT FOUND (exact) | No standalone “Hypovolemia”; ICL116 “Traumatic Hypovolemic Shock”, CNES synonym “Acute Hypovolemia”. |
| HYPOXEMIA | no primary EMCL/ICL name | [NTRS 20160011168 Table 2](https://ntrs.nasa.gov/api/citations/20160011168/downloads/20160011168.pdf); [NASA Appendix E](https://www.nasa.gov/reference/appendix-e-health-and-medical-care-technical-requirements/); [HRP-48036 Rev B App. G](https://ntrs.nasa.gov/api/citations/20240004774/downloads/HRP-48036%20RevB_ExMC%20Evidence%20Library%20Methods.pdf) | Table 2; Table E.2-2; ARCL88 | NOT FOUND | “Hypoxia” only in ARCL88 (All Remaining Conditions List). Nearest primary: Respiratory tract infection (lower/upper), Altitude sickness. |
| RADIATION_30DAY_LIMIT | yellow ≥125 mSv; red ≥250 mSv | [NASA-STD-3001 Table 4.8-1](https://www.nasa.gov/wp-content/uploads/2023/11/nasa-std-3001-vol-1-rev-c-with-signature.pdf) | Table 4.8-1 p.40 | ASSUMPTION | Not a unit conversion; direct mSv-to-mGy-Eq comparison is not conservative. Request bfo_dose_mgy_eq_30d or bfo_absorbed_dose_mgy_30d + spectrum/RBE. |
| nominal mock cumulative doses | 15 mSv/30 days; 120 mSv career | [Shavers et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10919966/); [Simonsen 2025](https://ntrs.nasa.gov/api/citations/20250006168/downloads/ASCEND%20Simonsen%20draft%201.pdf) | Results; §III | ASSUMPTION | 0.5 mSv/day is upper end of typical 0.2–0.5 mSv/day; synthetic upper-bound fixture, not measured crew history. |
| LOW_MOOD / PHQ-2 | PHQ-2 ≥3 | [Kroenke et al. 2003](https://pubmed.ncbi.nlm.nih.gov/14583691/) | Abstract | VERIFIED (PHQ-2) | Sensitivity 83%, specificity 92%; optimal cutpoint 3. NASA operational cognitive monitoring uses monthly WinSCAT; no PHQ-2 operational standard found. |
| NEWS2 spaceflight validation | none found | [RCP NEWS2 2017](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) | Recommendations p.xvi; §3 | NOT FOUND | NEWS2 validated for terrestrial adult acute illness; not validated in astronauts/microgravity. SpO2, BP, temperature and consciousness may be confounded. |
```

---

## 6. Ограничения проверки

- **MORD SSP 50260** не открыт: публичной копии не найдено; предписание упражнений подтверждено через NASA SP-20250000273 и NTRS 20110016265, но не через сам MORD.
- **Полный NCRP Commentary No. 32** не открыт (paywall); проверены название, год и abstract на странице NCRP. Для вывода о конфликте этого достаточно, поскольку NASA-STD-3001 сам ссылается на NASEM 2021.
- **Оригинальный JSC-65722 (EMCL Rev C)** не открыт как отдельный PDF; использованы NTRS 20160011168 (Table 2 воспроизводит EMCL), NTRS 20110008645 (SMEMCL 2011) и HRP-48036 Rev B (ICL/ARCL).
- **NEWS2**: отсутствие валидации для космоса установлено поиском по PubMed/NTRS/NASA и чтением RCP-отчёта; это не формальный систематический обзор.
- **PHQ-2**: порог подтверждён по PubMed abstract; полный текст Kroenke 2003 не открывался.

---

## 7. Ссылки (все проверены на доступность)

- NASA-STD-3001 Vol.1 Rev C — https://www.nasa.gov/wp-content/uploads/2023/11/nasa-std-3001-vol-1-rev-c-with-signature.pdf
- NASA-STD-3001 Vol.2, 7.0 Habitability — https://www.nasa.gov/reference/7-0-habit-ability-functions-vol-2/
- NASA Appendix E — https://www.nasa.gov/reference/appendix-e-health-and-medical-care-technical-requirements/
- NASEM 2021 — https://doi.org/10.17226/26155
- NCRP Commentary No. 32 — https://ncrponline.org/shop/commentaries/commentary-no-32-evaluation-of-a-sex-specific-difference-in-lung-cancer-radiation-risk-projection-with-a-focus-on-application-to-space-activities-2022/
- NCRP Report No. 132 — https://ncrponline.org/shop/reports/report-no-132-radiation-protection-guidance-for-activities-in-low-earth-orbit-2000/
- Shavers et al. 2023 — https://pmc.ncbi.nlm.nih.gov/articles/PMC10919966/
- NASA/JSC acute effects — https://three.jsc.nasa.gov/articles/SeedAcuteEffects.pdf
- Atwell/NAIRAS — https://wrmiss.org/workshops/seventeenth/Atwell.pdf
- NASA SP-20250000273 — https://www.nasa.gov/wp-content/uploads/2025/02/sp-20250000273.pdf
- NTRS 20110016265 — https://ntrs.nasa.gov/citations/20110016265
- Hackney et al. 2015 — https://journals.lww.com/nsca-jscr/Fulltext/2015/12000/The_Astronaut_Athlete___Optimizing_Human.35.aspx
- JSC-63555 (2005) — https://ntrs.nasa.gov/api/citations/20200001703/downloads/20200001703.pdf
- JSC 67378 (2020) — https://ntrs.nasa.gov/api/citations/20205008306/downloads/JSC67378%20Expl%20Nutr%20Reqs%20042020.pdf
- NTRS 20150000512 (nutrition evidence) — https://ntrs.nasa.gov/api/citations/20150000512/downloads/20150000512.pdf
- EMCL Table 2 (NTRS 20160011168) — https://ntrs.nasa.gov/api/citations/20160011168/downloads/20160011168.pdf
- SMEMCL 2011 (NTRS 20110008645) — https://ntrs.nasa.gov/api/citations/20110008645/downloads/20110008645.pdf
- HRP-48036 Rev B (ICL/ARCL) — https://ntrs.nasa.gov/api/citations/20240004774/downloads/HRP-48036%20RevB_ExMC%20Evidence%20Library%20Methods.pdf
- Simonsen 2025 — https://ntrs.nasa.gov/api/citations/20250006168/downloads/ASCEND%20Simonsen%20draft%201.pdf
- Kroenke et al. 2003 — https://pubmed.ncbi.nlm.nih.gov/14583691/
- OCHMO Behavioral Health Brief — https://www.nasa.gov/wp-content/uploads/2023/03/behavioral-health-technical-brief-ochmo.pdf
- RCP NEWS2 2017 — https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf
