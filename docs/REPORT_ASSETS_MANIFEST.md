# Report Assets Manifest

This file lists the final assets bundled for sharing with teammates.

## Bundle file

- `report_assets_bundle.zip`

## Included assets

### Pipeline / workflow
- `reports/pipeline.png` — final report-ready workflow diagram
- `reports/pipeline.svg` — vector version of the workflow diagram

### Database schema
- `reports/database_schema.svg` — vector database schema diagram (preferred for reports)
- `reports/database_schema.mmd` — Mermaid source for the database schema

### Performance visuals
- `outputs/analysis/model_comparison.png` — side-by-side comparison of model metrics
- `outputs/analysis/subgroup_f1_by_group.png` — subgroup comparison figure
- `outputs/analysis/catboost_feature_importance.png` — CatBoost feature importance plot
- `outputs/analysis/catboost_shap_summary.png` — SHAP summary visualization

### Diagnostic tables / score files
- `outputs/analysis/catboost_feature_importance.csv`
- `outputs/analysis/catboost_shap_importance.csv`
- `outputs/analysis/subgroup_metrics.csv`
- `outputs/analysis/final_model_scores.csv`
- `outputs/model_runs/train_8df81931-6.json`

## Why this bundle exists

The goal is to give teammates one small package containing the most useful visuals and score artefacts for report discussion, figure selection, and presentation prep without needing to browse the whole repository.
