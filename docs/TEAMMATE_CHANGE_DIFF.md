# Simple Change Diff for Teammates

### Final report facts now aligned to code

- Final sample used in report results: **100,000 patients / 388,375 hospitalization events**
- Final best model in report: **CatBoost**
- Final CatBoost metrics in report: **AUC 0.6453, F1 0.3499**
- Final Logistic Regression metrics in report: **AUC 0.6309, F1 0.3469**
- Final LightGBM metrics in report: **AUC 0.6242, F1 0.3009**

### Notebook files updated

- `notebooks/final_cms_esrd_readmission_workflow.ipynb`
- `notebooks/executed_notebook.ipynb`

## 5. Model/pipeline code changes

### What changed

| File | Main update |
|---|---|
| `scripts/ingest_datasets.py` | Added diagnosis-context fields into `model_feature_mart` |
| `scripts/train_readmission_models.py` | Added diagnosis features, increased boosting rounds, optimized threshold for F1 |
| `outputs/model_runs/train_8df81931-6.json` | Latest final evidence run kept as source of truth |

### Final modeling direction

- Features now cover:
  - demographics
  - treatment history
  - hospitalization history
  - dialysis adequacy
  - diagnosis context
- Evaluation now includes threshold tuning for operational F1.

## 6. Cleanup changes

### What changed

| Before | After |
|---|---|
| Multiple stale run summaries | Only latest final run kept |
| Old run-specific charts | Removed |
| Cache/checkpoint folders | Removed |
| Old legacy notebook/doc files | Removed |

### Final kept output evidence

- `outputs/model_runs/train_8df81931-6.json`
- `outputs/analysis/catboost_feature_importance.csv`
- `outputs/analysis/catboost_feature_importance.png`
- `outputs/analysis/catboost_shap_importance.csv`
- `outputs/analysis/catboost_shap_summary.png`
- `outputs/analysis/model_comparison.png`
- `outputs/analysis/subgroup_f1_by_group.png`
- `outputs/analysis/subgroup_metrics.csv`

## 7. Presentation script changes

### What changed

- Slide 1 now includes **names + student numbers**.
- Script language was rewritten to sound more natural when spoken.
- Slide 5 metrics were updated to the final aligned values.

### File updated

- `docs/presentation_script.md`

## 8. What teammates should use now

If anyone is updating or reviewing deliverables, these are the correct files to use:

- **Report source:** `reports/final_report.tex`
- **Readable report copy:** `reports/FINAL_REPORT.md`
- **Report PDF:** `reports/FINAL_REPORT.pdf`
- **Pipeline figure:** `reports/pipeline.png`
- **Notebook evidence:** `notebooks/final_cms_esrd_readmission_workflow.ipynb`
- **Journals:** `journals/JOURNAL_*.md` and `journals/JOURNAL_*.pdf`
- **Presentation script:** `docs/presentation_script.md`
- **Latest metrics source of truth:** `outputs/model_runs/train_8df81931-6.json`

## 9. Short version

In simple terms: the final pass made the whole submission consistent. The code, notebook, report, journals, figures, and packaged artefacts now line up with one another. The biggest fixes were leakage removal, realistic metric alignment, clearer notebook evidence, stronger report/journal wording, and cleanup of stale outputs.

## 10. If teammates are working from `Current State of Docs/`

Use `docs/CURRENT_STATE_DOCS_DIFF.md` first.

### Minimal action list

- replace old metrics (`0.6531 / 0.3623 / 0.6478 / 0.5135`) with final metrics from `outputs/model_runs/train_8df81931-6.json`
- replace old event count `387,748` with `388,375`
- replace legacy schema names like `clean_patient`, `clean_hospitalization`, `derived_readmission` with current names where relevant
- add threshold-tuning wording where results/method sections are updated
- add diagnosis-context wording where feature engineering is described
- in presentation materials, change “application or notebook” to notebook-only wording

### Work split to follow

- **Mohammed**: final metrics, results wording, main presentation/result ownership, heaviest workload
- **Chetan**: DB/schema wording, QA, interpretability wording
- **Shashank**: dataset validation, benchmark wording, packaging/presentation support
- **Sakshi**: cleaning/EDA/results narration and consistency edits

### Rule

Do not rewrite everything. Patch the stale facts first. Most deviations are targeted number/name updates, not full structural problems.
