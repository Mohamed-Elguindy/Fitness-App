# Phase 1 Chunking Experiment Report

This report compares local chunking strategies after lightweight PDF preprocessing.

## Environment

- Token counter: `tiktoken:text-embedding-3-small`
- Local embedding model: `BAAI/bge-small-en-v1.5`
- Hybrid target tokens: `750`
- Semantic break percentile: `85`
- Minimum chunk tokens after merge: `50`
- Local semantic splitter: `fallback:could not load BAAI/bge-small-en-v1.5`
- Hybrid JSONL export: `/home/runner/work/Fitness-App/Fitness-App/agentic-fitness-app/experiments/reports/phase1_hybrid_chunks.jsonl`

## Source PDFs

| Corpus | File | Pages | Parser | Title |
|---|---|---:|---|---|
| nutrition | `dummy_test_file_2.pdf` | 18 | `pdfplumber-layout` | Creatine is one of the most popular nutritional ergogenic aids for athletes. Studies have consistently shown that creatine supplementation increases intramuscular creatine concentr |
| nutrition | `s12970-017-0173-z.pdf` | 18 | `pdfplumber-layout` | International Society of Sports Nutrition Position Stand: Safety and Efficacy of Creatine Supplementation in Exercise, Sport, and Medicine |
| nutrition | `s12970-017-0174-y.pdf` | 19 | `pdfplumber-layout` | International Society of Sports Nutrition Position Stand: Diets and Body Composition |
| nutrition | `s12970-017-0177-8.pdf` | 25 | `pdfplumber-layout` | International Society of Sports Nutrition Position Stand: Protein and Exercise |
| nutrition | `s12970-017-0189-4.pdf` | 21 | `pdfplumber-layout` | International Society of Sports Nutrition Position Stand: Nutrient Timing |
| training | `ACSM-Progression-models-in-resistance-training-for-healthy-adults-2009.pdf` | 22 | `pdfplumber-layout` | Progression Models in Resistance Training for Healthy Adults |
| training | `Effects of Resistance Training Frequency on Measures of Muscle Hypertrophy - A Systematic Review and Meta-Analysis.pdf` | 9 | `pdfplumber-layout` | Effects of Resistance Training Frequency on Measures of Muscle Hypertrophy: A Systematic Review and Meta-Analysis |
| training | `hukin-81-199.pdf` | 12 | `pdfplumber-layout` | A Systematic Review of the Effects of Different Resistance Training Volumes on Muscle Hypertrophy |
| training | `ijerph-17-01285.pdf` | 27 | `pdfplumber-layout` | A Systematic Review with Meta-Analysis of the Effect of Resistance Training on Whole-Body Muscle Growth in Healthy Adult Males |
| training | `oajsm-7-115.pdf` | 8 | `pdfplumber-layout` | Diagnosis and Prevention of Overtraining Syndrome: An Opinion on Education Strategies |

## Strategy Summary

| Strategy | Chunks | Avg Tokens | Min | Under 50 | P90 | Max |
|---|---:|---:|---:|---:|---:|---:|
| fixed | 220 | 1352 | 559 | 0 | 1838 | 2760 |
| structure | 143 | 1417 | 75 | 0 | 2050 | 3445 |
| hybrid | 273 | 696 | 52 | 0 | 745 | 2345 |

## Per-Corpus Summary

| Strategy | Corpus | Chunks | Avg Tokens | Min | Under 50 | P90 | Max |
|---|---|---:|---:|---:|---:|---:|---:|
| fixed | nutrition | 139 | 1307 | 559 | 0 | 1763 | 1860 |
| fixed | training | 81 | 1429 | 563 | 0 | 1960 | 2760 |
| structure | nutrition | 92 | 1413 | 128 | 0 | 1934 | 2297 |
| structure | training | 51 | 1424 | 75 | 0 | 2606 | 3445 |
| hybrid | nutrition | 177 | 691 | 87 | 0 | 745 | 756 |
| hybrid | training | 96 | 706 | 52 | 0 | 745 | 2345 |

## Sample Chunks

### fixed

**nutrition sample**

- Source: `dummy_test_file_2.pdf`
- Section: `full text`
- Tokens: `1246`

> Kreider et al. Journal of the International Society of Sports Nutrition (2017) 14:18 DOI 10.1186/s12970-017-0173-z REVIEW Open Access International Society of Sports Nutrition position stand: safety and efficacy of creatine supplementation in exercise, sport, and medicine Richard B. Kreider1*, Douglas S. Kalman2, Jose Antonio3, Tim N. Ziegenfuss4, Robert Wildman5, Rick Collins6, Darren G. Candow7, Susan M. Kleiner8, Anthony L. Almada9 and Hector L. Lopez4,10 Abstract Creatine is one of the most popular nutritional ergogenic aids for athletes. Studies have consistently shown that creatine supplementation increases intramuscular creatine concentrations which may help explain the observed improvements in high intensity exercise performance lea...

**training sample**

- Source: `ACSM-Progression-models-in-resistance-training-for-healthy-adults-2009.pdf`
- Section: `full text`
- Tokens: `1209`

> SPECIAL COMMUNICATIONS Progression Models in Resistance Training for Healthy Adults POSITION STAND This pronouncement was written for the American College of Sports Medicine by Nicholas A. Ratamess, Ph.D.; Brent A. Alvar, Ph.D.; Tammy K. Evetoch, Ph.D., FACSM; Terry J. Housh, Ph.D., FACSM (Chair); W. Ben Kibler, M.D., FACSM; William J. Kraemer, Ph.D., FACSM; and N. Travis Triplett, Ph.D. SUMMARY withpriorones,recommendationsshouldbeappliedincontextandshouldbe contingent upon an individual’s target goals, physical capacity, and training In order to stimulate further adaptation toward specific training goals, status. Key Words: strength, power, local muscular endurance, fitness, progressive resistance training (RT) protocols are necessary. Th...

### structure

**nutrition sample**

- Source: `dummy_test_file_2.pdf`
- Section: `front matter`
- Tokens: `128`

> Kreider et al. Journal of the International Society of Sports Nutrition (2017) 14:18 DOI 10.1186/s12970-017-0173-z REVIEW Open Access International Society of Sports Nutrition position stand: safety and efficacy of creatine supplementation in exercise, sport, and medicine Richard B. Kreider1*, Douglas S. Kalman2, Jose Antonio3, Tim N. Ziegenfuss4, Robert Wildman5, Rick Collins6, Darren G. Candow7, Susan M. Kleiner8, Anthony L. Almada9 and Hector L. Lopez4,10

**training sample**

- Source: `ACSM-Progression-models-in-resistance-training-for-healthy-adults-2009.pdf`
- Section: `front matter`
- Tokens: `1511`

> SPECIAL COMMUNICATIONS Progression Models in Resistance Training for Healthy Adults POSITION STAND This pronouncement was written for the American College of Sports Medicine by Nicholas A. Ratamess, Ph.D.; Brent A. Alvar, Ph.D.; Tammy K. Evetoch, Ph.D., FACSM; Terry J. Housh, Ph.D., FACSM (Chair); W. Ben Kibler, M.D., FACSM; William J. Kraemer, Ph.D., FACSM; and N. Travis Triplett, Ph.D. SUMMARY withpriorones,recommendationsshouldbeappliedincontextandshouldbe contingent upon an individual’s target goals, physical capacity, and training In order to stimulate further adaptation toward specific training goals, status. Key Words: strength, power, local muscular endurance, fitness, progressive resistance training (RT) protocols are necessary. Th...

### hybrid

**nutrition sample**

- Source: `dummy_test_file_2.pdf`
- Section: `front matter`
- Tokens: `128`

> Kreider et al. Journal of the International Society of Sports Nutrition (2017) 14:18 DOI 10.1186/s12970-017-0173-z REVIEW Open Access International Society of Sports Nutrition position stand: safety and efficacy of creatine supplementation in exercise, sport, and medicine Richard B. Kreider1*, Douglas S. Kalman2, Jose Antonio3, Tim N. Ziegenfuss4, Robert Wildman5, Rick Collins6, Darren G. Candow7, Susan M. Kleiner8, Anthony L. Almada9 and Hector L. Lopez4,10

**training sample**

- Source: `ACSM-Progression-models-in-resistance-training-for-healthy-adults-2009.pdf`
- Section: `front matter`
- Tokens: `711`

> SPECIAL COMMUNICATIONS Progression Models in Resistance Training for Healthy Adults POSITION STAND This pronouncement was written for the American College of Sports Medicine by Nicholas A. Ratamess, Ph.D.; Brent A. Alvar, Ph.D.; Tammy K. Evetoch, Ph.D., FACSM; Terry J. Housh, Ph.D., FACSM (Chair); W. Ben Kibler, M.D., FACSM; William J. Kraemer, Ph.D., FACSM; and N. Travis Triplett, Ph.D. SUMMARY withpriorones,recommendationsshouldbeappliedincontextandshouldbe contingent upon an individual’s target goals, physical capacity, and training In order to stimulate further adaptation toward specific training goals, status. Key Words: strength, power, local muscular endurance, fitness, progressive resistance training (RT) protocols are necessary. Th...

## Initial Read

- References and back-matter sections are filtered before chunk creation.
- Micro-chunks under 50 tokens are merged into the previous chunk when possible.
- Hybrid chunks keep section metadata and split oversized sections with local embedding similarity when the BGE model is available.
- If the local embedding model cannot load, the script falls back to sentence-boundary splitting.
