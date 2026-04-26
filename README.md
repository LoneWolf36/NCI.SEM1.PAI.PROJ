# Programming for AI Project — Final Working Repository

## Project focus

**Predict 30-day hospital readmission risk in dialysis / ESRD patients using linked CMS ESRD public-use tables, with a database-first workflow and comparative machine learning evaluation.**

## Locked dataset stack

This repository uses four CMS ESRD Population PUF datasets:

1. `PATIENT_SUMMARY` — patient demographics and diagnosis context
2. `ADMIT_TREATMENT` — treatment history and dialysis setting context
3. `CL_HOSPITALIZATION` — hospitalization events used to derive the real 30-day readmission target
4. `CL_HD_ADQCY` — dialysis adequacy features including Kt/V

All four datasets exceed the assignment scale requirement and are programmatically ingested into SQLite before preprocessing and modeling.

## Implemented workflow

1. Download CMS ESRD ZIP datasets into `data/downloads/`
2. Ingest raw data into SQLite via `scripts/ingest_datasets.py`
3. Build clean tables, derived event tables, and `model_feature_mart`
4. Train Logistic Regression, CatBoost, and LightGBM via `scripts/train_readmission_models.py`
5. Save model metrics and artifacts to SQLite and `outputs/`
6. Present results in `reports/final_report.tex`, `reports/FINAL_REPORT.md`, and `notebooks/final_cms_esrd_readmission_workflow.ipynb`

## Key evidence

- SQLite database: `dialysis_readmission.db`
- Raw row counts verified in database:
  - `raw_patient_summary`: 3,197,683
  - `raw_admit_treatment`: 7,720,441
  - `raw_cl_hospitalization`: 3,899,711
  - `raw_cl_hd_adqcy`: 32,250,552
- Derived analytical cohort: `derived_readmission_events` = 3,098,950 rows
- Final modeling mart: `model_feature_mart` = 3,098,950 rows
- Latest model summary: `outputs/model_runs/train_8df81931-6.json`

## Main files

- `scripts/ingest_datasets.py` — ingestion, cleaning, derivation, and feature-mart creation
- `scripts/train_readmission_models.py` — model training, metrics, and artifact generation
- `notebooks/final_cms_esrd_readmission_workflow.ipynb` — executed final notebook artifact
- `reports/final_report.tex` — IEEE LaTeX report source
- `reports/FINAL_REPORT.md` — synchronized Markdown report source
- `reports/FINAL_REPORT.pdf` — generated report PDF
- `docs/DATA_DICTIONARY.md` — data dictionary for raw, clean, derived, and modeling tables
- `docs/SUBMISSION_CHECKLIST.md` — delivery checklist aligned to current repo state
- `docs/REQUIREMENTS_VERIFICATION.md` — evidence-based requirement verification

## Quick run

### Rebuild derived tables and verify DB

```bash
.venv/bin/python scripts/ingest_datasets.py --skip-download
```

### Train models

```bash
.venv/bin/python scripts/train_readmission_models.py --db-path dialysis_readmission.db --output-dir outputs/model_runs --artifacts-dir outputs/analysis --max-patients 100000
```

### Execute notebook artifact

```bash
.venv/bin/jupyter-execute --inplace --timeout=-1 notebooks/final_cms_esrd_readmission_workflow.ipynb
```

### Regenerate report PDF

```bash
.venv/bin/python reports/build_report_pdf.py
```

### Regenerate journal PDFs

```bash
.venv/bin/python journals/convert_journals.py
```

## Submission note

Repository now aligns with the locked CMS ESRD direction. The only major deliverable not generated inside this repo is the final presentation video file, which still needs to be recorded/exported separately.
