# PDF Realignment Instructions

These instructions detail the exact changes required to align `PAI-Final_Report_Draft.pdf` with the source-of-truth `reports/FINAL_REPORT.md`.

## 1. Abstract & Global Stats
Replace all instances of stale performance metrics and event counts.

| Metric | Old (PDF) | **New (Final)** |
| :--- | :--- | :--- |
| **Total Hospitalization Events** | 387,748 | **388,375** |
| **CatBoost AUC** | 0.6531 | **0.6453** |
| **CatBoost F1-Score** | 0.3623 | **0.3499** |

## 2. Methodology Updates (Section III)
The PDF lacks the description of threshold optimization, which is key to the final results.

**Action:** In Section III.C (Model Training and Evaluation), insert the following text:
> "**Threshold Selection:** We tune the decision threshold on the training split to maximize F1, then reuse that threshold on the held-out test split."

## 3. Model Performance Narrative (Section IV.A)
The PDF incorrectly characterizes the baseline model as having failed.

**Action:** Replace the second paragraph of Section IV.A with:
> "Logistic Regression reaches the highest recall after threshold tuning, but its ranking quality remains weaker than CatBoost. CatBoost delivers the best overall balance of AUC, Average Precision, and F1, which makes it the most defensible choice for risk ranking."

## 4. Table I (Performance Comparison)
Replace the entire table with these final values:

| Model | AUC | Avg Prec | Accuracy | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 0.6309 | 0.2937 | 0.6053 | 0.2479 | 0.5780 | 0.3469 |
| **LightGBM** | 0.6242 | 0.2751 | 0.7409 | 0.2946 | 0.3075 | 0.3009 |
| **CatBoost** | 0.6453 | 0.3000 | 0.6729 | 0.2735 | 0.4853 | 0.3499 |

## 5. Figure Re-alignment
Re-order and update the figures to follow the sequence in the final report.

1.  **Figure 1:** Pipeline Workflow (`reports/pipeline.png`).
2.  **Figure 2:** Model Performance Comparison (Insert `outputs/analysis/model_comparison.png`).
3.  **Figure 3:** F1-score by Demographic Subgroup (`outputs/analysis/subgroup_f1_by_group.png`).
4.  **Figure 4:** CatBoost Feature Importance (`outputs/analysis/catboost_feature_importance.png`).
5.  **Figure 5:** CatBoost SHAP Analysis (`outputs/analysis/catboost_shap_summary.png`).

## 6. Minor Text Adjustments
- **Research Question:** Remove the parenthetical "(i.e. data mining)".
- **Section III.A:** Add "admission diagnosis, discharge diagnosis" to the list of hospitalization features.
