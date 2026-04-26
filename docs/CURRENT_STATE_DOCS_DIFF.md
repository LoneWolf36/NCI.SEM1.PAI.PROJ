## Live codebase state to use

- Sample used in final aligned materials: **100,000 patients / 388,375 hospitalization events**
- Final metrics:
  - Logistic Regression: **AUC 0.6309, F1 0.3469**
  - CatBoost: **AUC 0.6453, F1 0.3499**
  - LightGBM: **AUC 0.6242, F1 0.3009**
- Current workflow includes:
  - diagnosis context features (`hospital_admit_diag`, `hospital_discharge_diag`)
  - patient-level split
  - threshold optimization for F1
  - current clean/derived table names such as `clean_patient_summary` and `derived_readmission_events`

---

## High-severity deviations

### 1. `presentation_script_SH.md`

| Ref | Current wording | Deviation from codebase | Exact replacement values |
|---|---|---|---|
| lines 86-92 | Uses **387,748** events and old metrics **0.6531 / 0.3623 / 0.6478 / 0.5135** | Final run is **388,375** events and **0.6453 / 0.3499 / 0.6242 / 0.6309** | Replace with: `CatBoost AUC 0.6453, F1 0.3499; LightGBM AUC 0.6242, F1 0.3009; Logistic Regression AUC 0.6309, F1 0.3469; Events: 388,375`. Proof: `outputs/model_runs/train_8df81931-6.json`. |
| line 92 | Says Logistic Regression was nearly random and missed almost all positives | No longer true in final aligned run; LR is still weaker than CatBoost but much more competitive after threshold tuning | Replace with: `Logistic Regression reaches the highest recall after threshold tuning, but its ranking quality remains weaker than CatBoost.` Proof: `reports/final_report.tex` lines 251-253. |
| lines 122-139 | Says “open the application or notebook” and describes a demo that implies an application | Current codebase has a notebook and scripts; no separate application artifact is part of final repo | Replace with: `open the notebook`. Proof: `notebooks/final_cms_esrd_readmission_workflow.ipynb` is the only demo artifact. |
| line 172 | Repeats CatBoost **AUC 0.6531** in conclusion | Stale final headline metric | Replace with: `0.6453`. Proof: `outputs/model_runs/train_8df81931-6.json`. |
| line 189 | Presenter reminder still highlights **0.6531** | Stale final metric | Replace with: `0.6453`. Proof: `outputs/model_runs/train_8df81931-6.json`. |

### 2. `dialysis_readmission_presentation.pptx`

| Ref | Current wording | Deviation from codebase | Exact replacement values |
|---|---|---|---|
| slide5 lines 89-100 in extracted text | CatBoost AUC **0.6531**, F1 **0.3623**, recall **57.1%**, **387,748** events | Final run is CatBoost **0.6453**, F1 **0.3499**, recall **48.5%**, **388,375** events | Replace with: `CatBoost AUC 0.6453, F1 0.3499, Recall 48.5%; Events: 388,375`. Proof: `outputs/model_runs/train_8df81931-6.json`. |
| slide9 lines 147-154 | Repeats “CatBoost (AUC 0.6531)” | Stale headline metric | Replace with: `CatBoost (AUC 0.6453)`. Proof: `outputs/model_runs/train_8df81931-6.json`. |
| slide4 lines 60-87 | Methodology slide shows ingest/clean/engineer/label/train only | Current workflow also includes diagnosis context and threshold optimization | Add: `Diagnosis context features` and `Threshold optimization for F1`. Proof: `scripts/train_readmission_models.py` lines 72-82, 100-110. |

### 3. `Your_Paper__3_.pdf`

| Ref | Current wording | Deviation from codebase | Exact replacement values |
|---|---|---|---|
| page 1 lines 19-31 | Abstract uses CatBoost **0.6531**, F1 **0.3623**, **387,748** events | Final truth is **0.6453**, **0.3499**, **388,375** events | Replace with: `CatBoost performs best (AUC: 0.6453, F1: 0.3499) on 388,375 hospitalization events`. Proof: `reports/final_report.tex` lines 47-48. |
| page 3/4 results section | Old full model table: LR **0.5135/0.0219 recall**, LightGBM **0.6478/0.3582**, CatBoost **0.6531/0.3623** | Entire table is stale | Replace with: `Logistic Regression: 0.6309 / 0.2937 / 0.6053 / 0.2479 / 0.5780 / 0.3469; LightGBM: 0.6242 / 0.2751 / 0.7409 / 0.2946 / 0.3075 / 0.3009; CatBoost: 0.6453 / 0.3000 / 0.6729 / 0.2735 / 0.4853 / 0.3499`. Proof: `reports/final_report.tex` lines 263-265. |
| methodology section | No explicit threshold-selection step | Current code explicitly tunes threshold for F1 | Add: `Threshold Selection: We tune the decision threshold on the training split to maximize F1, then reuse that threshold on the held-out test split.` Proof: `scripts/train_readmission_models.py` lines 100-110. |
| dataset/method wording | Does not clearly reflect diagnosis-context feature additions | Current code/report do include diagnosis context | Add: `Hospitalization Features: Length of stay, admission diagnosis, discharge diagnosis where present, gap from previous discharge, and counts of recent hospitalizations.` Proof: `scripts/ingest_datasets.py` lines 420-434. |
| schema wording | Legacy names appear in older wording style | Current codebase uses `clean_patient_summary`, `clean_admit_treatment`, `clean_cl_hospitalization`, `derived_readmission_events` | Replace with: `clean_patient_summary`, `clean_admit_treatment`, `clean_cl_hospitalization`, `derived_readmission_events`. Proof: `scripts/ingest_datasets.py` lines 180-290. |

### 4. `JOURNAL_Mohammed_Faizan_Khan_25214501.docx`

| Ref | Current wording | Deviation from codebase | Exact replacement values |
|---|---|---|---|
| extracted lines 83-99 | Uses `clean_patient`, `clean_hospitalization`, `derived_readmission` | Current schema names differ | Replace with: `clean_patient_summary`, `clean_cl_hospitalization`, `derived_readmission_events`. Proof: `scripts/ingest_datasets.py` lines 180-290. |
| extracted line 106 | Says feature mart had **1,938,740** hospitalization events | Current modeling evidence uses **388,375** sampled events and DB cohort is 3,098,950 discharges | Replace with: `388,375 sampled events`. Proof: `outputs/model_runs/train_8df81931-6.json`. |
| extracted lines 131-168 | Old metrics table with **0.6531 / 0.3623 / 0.5135 / 0.6478** | Stale metrics | Replace with: `CatBoost AUC 0.6453, F1 0.3499; LightGBM AUC 0.6242, F1 0.3009; Logistic Regression AUC 0.6309, F1 0.3469`. Proof: `outputs/model_runs/train_8df81931-6.json`. |
| extracted lines 194-205 | Claims CatBoost **0.6531 / 0.3623** on **387,748** held-out events | Stale | Replace with: `CatBoost AUC 0.6453, F1 0.3499 on 388,375 events`. Proof: `outputs/model_runs/train_8df81931-6.json`. |

### 5. `JOURNAL_Shashank_Yadav_25118692.docx`

| Ref | Current wording | Deviation from codebase | Exact replacement values |
|---|---|---|---|
| extracted lines 91-126 | Old test-event count **387,748** and old metric table | Stale | Replace with: `388,375 events` and `CatBoost AUC 0.6453, F1 0.3499; LightGBM AUC 0.6242, F1 0.3009; Logistic Regression AUC 0.6309, F1 0.3469`. Proof: `outputs/model_runs/train_8df81931-6.json`. |
| extracted line 126 | Says LR weakness is at the “default decision threshold” | Current final pipeline uses threshold optimization | Replace with: `Logistic Regression reaches the highest recall after threshold tuning, but its ranking quality remains weaker than CatBoost.` Proof: `reports/final_report.tex` lines 251-253. |
| extracted lines 142-151 / 167-172 / 209 | Repeats old CatBoost metrics **0.6531 / 0.3623** | Stale | Replace with: `0.6453 / 0.3499`. Proof: `outputs/model_runs/train_8df81931-6.json`. |

### 6. `JOURNAL_Chetan_Panchal_24244058.docx`

| Ref | Current wording | Deviation from codebase | Exact replacement values |
|---|---|---|---|
| extracted lines 81-95 | Uses legacy schema names `clean_patient`, `clean_hospitalization`, `derived_readmission` | Current schema names differ | Replace with: `clean_patient_summary`, `clean_cl_hospitalization`, `derived_readmission_events`. Proof: `scripts/ingest_datasets.py` lines 180-290. |
| extracted lines 120-139 / 169-199 / 209 | Old metrics table and repeated old CatBoost values | Stale | Replace with: `CatBoost AUC 0.6453, F1 0.3499; LightGBM AUC 0.6242, F1 0.3009; Logistic Regression AUC 0.6309, F1 0.3469`. Proof: `outputs/model_runs/train_8df81931-6.json`. |
| extracted lines 107-109 | Describes `derived_readmission` table | Current derived table is `derived_readmission_events` | Replace with: `derived_readmission_events`. Proof: `scripts/ingest_datasets.py` lines 293-343. |

### 7. `JOURNAL_Sakshi_Patil_24304166.docx`

| Ref | Current wording | Deviation from codebase | Exact replacement values |
|---|---|---|---|
| extracted lines 79-99 | Says cleaning outputs are `clean_patient`, `clean_hospitalization`, `clean_hd_adqcy` | Current schema names differ | Replace with: `clean_patient_summary`, `clean_cl_hospitalization`, `clean_cl_hd_adqcy`. Proof: `scripts/ingest_datasets.py` lines 180-290. |
| extracted lines 117-122 / 137-166 | Old CatBoost / LightGBM / Logistic Regression metrics | Stale | Replace with: `CatBoost AUC 0.6453, F1 0.3499; LightGBM AUC 0.6242, F1 0.3009; Logistic Regression AUC 0.6309, F1 0.3469`. Proof: `outputs/model_runs/train_8df81931-6.json`. |
| extracted line 137 | Explains Logistic Regression using old 80.85% accuracy narrative | No longer true in final aligned run | Replace with: `Logistic Regression reaches the highest recall after threshold tuning, but its ranking quality remains weaker than CatBoost.` Proof: `reports/final_report.tex` lines 251-253. |

---

## Medium-severity deviations

| File | Issue | Exact replacement values |
|---|---|---|
| `presentation_script_SH.md` | No explicit diagnosis-context mention in methodology/results | Add: `Diagnosis context features (admission/discharge diagnosis)`. Proof: `scripts/ingest_datasets.py` lines 420-434. |
| `dialysis_readmission_presentation.pptx` | No threshold-tuning mention | Add: `Threshold optimization for F1`. Proof: `scripts/train_readmission_models.py` lines 100-110. |
| all 4 journal `.docx` files | Mention `SQLAlchemy` in implementation stack | Replace with: `sqlite3 and pandas`. Proof: `scripts/ingest_datasets.py` lines 18-28, `scripts/train_readmission_models.py` lines 13-20. |

---

## Low-severity / still aligned

These are mostly still consistent with the current codebase:

- Four CMS datasets used
- Database-first framing
- 18.28% readmission prevalence
- Patient-level split importance
- SHAP / subgroup analysis themes
- Triage-not-autonomous-decision framing

---

## Journal realism check

### Is the current-state journal split realistic?

### Final workload split

| Person | Total hours | Emphasis |
|---|---:|---|
| Mohammed Faizan Khan | **45** | Feature engineering, evaluation design, metrics alignment, report core sections, presentation lead |
| Chetan Panchal | **40** | DB architecture, schema, QA, interpretability, final verification |
| Shashank Yadav | **39** | Dataset acquisition, validation, model benchmarking, packaging, presentation support |
| Sakshi Patil | **38** | Cleaning, EDA, visualizations, results narration, report editing |

Proof: `journals/JOURNAL_*.md` files updated with exact hours and task descriptions.