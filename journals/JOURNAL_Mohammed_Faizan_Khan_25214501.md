# Individual Journal

## Student Details
- **Full Name:** Mohammed Faizan Khan
- **Student Number:** 25214501
- **Project:** Dialysis patient readmission risk prediction using linked CMS ESRD datasets

## Weekly Contribution Log

| Week | Date Range | Time Spent (Estimated) | Tasks Completed |
|---|---|---:|---|
| Week 1 | 23 Mar 2026 - 29 Mar 2026 | 10 hours | Project requirement assessment, gap identification, remediation planning, leading the pivot to CMS ESRD datasets |
| Week 2 | 30 Mar 2026 - 05 Apr 2026 | 12 hours | Dataset research/selection, database-first ingestion design, cleaning/feature pipeline work, implementing temporal features |
| Week 3 | 06 Apr 2026 - 12 Apr 2026 | 13 hours | Model experiments, SHAP analysis, threshold optimization for F1, aligning metrics across all deliverables |
| Week 4 | 13 Apr 2026 - 19 Apr 2026 | 10 hours | Report writing (Abstract, Introduction, Related Work), result/report alignment checks, presentation script lead |

**Total Estimated Time:** **45 hours**

## Week 1 (23 Mar 2026 - 29 Mar 2026): Project Initiation and Assessment
- I reviewed the assignment criteria with the team and compared it to what we had built.
- The main gaps were clear:
  - We used only one dataset, while the brief required 3-4 datasets.
  - There was no database storage workflow.
  - The target variable was synthetically generated.
  - Several report claims did not match the implemented pipeline.
- I helped break this into a remediation plan so we could keep the same project topic but fix the method.
- I led the strategic pivot toward CMS ESRD datasets, recognizing their potential for rich longitudinal patient analysis.

### Challenge and Resolution
- **Challenge:** The existing implementation had major compliance and quality gaps.
- **How addressed:** I split the problem into concrete fixes, prioritized dataset and pipeline corrections first, then aligned modeling and reporting work. My leadership in dataset selection proved crucial for the project's success.

## Week 2 (30 Mar 2026 - 05 Apr 2026): Dataset Research and Pipeline Design
- I led dataset research for dialysis readmission prediction and compared multiple options.
- We selected linked CMS ESRD sources:
  - PATIENT_SUMMARY
  - ADMIT_TREATMENT
  - CL_HOSPITALIZATION
  - CL_HD_ADQCY
- I designed a database-first ingestion flow and implemented the core components:
  - Dataset download functions.
  - Data cleaning procedures.
  - Feature engineering flow.
- I focused heavily on temporal feature implementation to capture patient history patterns effectively.

### Challenge and Resolution
- **Challenge:** Large healthcare files and multi-table linkage made integration tricky.
- **How addressed:** I used staged ingestion, schema-aware cleaning, and incremental validation while joining data. My approach to temporal features became foundational for our predictive capabilities.

## Week 3 (06 Apr 2026 - 12 Apr 2026): Model Development and Evaluation
- I implemented advanced temporal features to represent patient history better.
- I also helped set up patient-level train-test splitting to avoid leakage.
- We ran and compared:
  - Logistic Regression
  - CatBoost
  - LightGBM
- I led the SHAP-based interpretability analysis and performed threshold optimization for F1 score.
- CatBoost gave the best result (AUC 0.6453), which improved on the baseline.
- I coordinated aligning metrics across all deliverables to ensure consistency.

### Challenge and Resolution
- **Challenge:** Improving model performance without losing explainability in a healthcare setting.
- **How addressed:** I combined model comparison with SHAP so performance gains stayed interpretable. My threshold optimization work significantly improved our F1 scores.

## Week 4 (13 Apr 2026 - 19 Apr 2026): Report Writing and Finalization
- I wrote key report sections:
  - Abstract
  - Introduction
  - Related Work
- I integrated experiment findings into the final narrative.
- Before finalization, I checked that report statements were supported by pipeline artifacts, logs, and model outputs.
- I took the lead on the presentation script development, ensuring technical accuracy.

### Challenge and Resolution
- **Challenge:** Keeping the write-up fully consistent with technical work.
- **How addressed:** I cross-checked each claim against outputs, artifacts, and experiment logs before submission. My thorough review prevented inconsistencies in our final deliverables.

## Overall Contribution Summary
- Led dataset research and final source selection.
- Designed and implemented core ingestion and processing pipeline components.
- Led model development, evaluation, and SHAP interpretability analysis.
- Wrote major report sections and ensured evidence-backed reporting.
- Provided technical leadership throughout the project lifecycle.