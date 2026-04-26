# Individual Journal

## Student Details
- **Full Name:** Shashank Yadav
- **Student Number:** 25118692
- **Filename Note:** File kept as `JOURNAL_Shaskank_Yadav_25118692.md` for compatibility with conversion script.
- **Project:** Dialysis patient readmission risk prediction using linked CMS ESRD datasets

## Weekly Contribution Log

| Week | Date Range | Time Spent (Estimated) | Tasks Completed |
|---|---|---:|---|
| Week 1 | 23 Mar 2026 - 29 Mar 2026 | 8 hours | Compliance review, remediation planning, replacement dataset evaluation |
| Week 2 | 30 Mar 2026 - 05 Apr 2026 | 12 hours | Dataset acquisition/validation, schema checks, linkage validation, resilient download support |
| Week 3 | 06 Apr 2026 - 12 Apr 2026 | 10 hours | Model framework setup, patient-level split implementation, tuning and comparison |
| Week 4 | 13 Apr 2026 - 19 Apr 2026 | 9 hours | Presentation support, methodology documentation, artifact packaging |

**Total Estimated Time:** **39 hours**

## Week 1 (23 Mar 2026 - 29 Mar 2026): Project Evaluation and Planning
- I took part in the project compliance evaluation during the first week.
- We flagged the critical issues early:
  - Only one dataset was used, not the required 3-4 datasets.
  - No database storage layer existed.
  - The target variable was synthetically generated.
  - Report and implementation were misaligned.
- I helped draft the remediation plan and shortlist replacement datasets.
- I focused particularly on evaluating dataset quality and availability for our use case.

### Challenge and Resolution
- **Challenge:** Broad requirement failures needed to become executable engineering tasks.
- **How addressed:** I converted each issue into milestones: data sources, storage architecture, model protocol, and documentation alignment. My dataset evaluation work informed key project decisions.

## Week 2 (30 Mar 2026 - 05 Apr 2026): Dataset Acquisition and Validation
- I acquired and validated CMS ESRD datasets for pipeline use.
- Validation checks included:
  - Verified download URLs for all four datasets.
  - Confirmed row counts and schema compatibility.
  - Validated linkage via patient/provider IDs.
- I implemented resilient download mechanisms with resume support to reduce rerun failures.
- I worked closely with the database team to ensure schema compatibility.

### Challenge and Resolution
- **Challenge:** Large dataset retrieval and preprocessing created reliability risks.
- **How addressed:** I added resilient download behavior and validation checkpoints before any downstream modeling. My validation work prevented data quality issues from affecting later stages.

## Week 3 (06 Apr 2026 - 12 Apr 2026): Model Implementation and Comparison
- I built the model comparison workflow across:
  - Logistic Regression
  - CatBoost
  - LightGBM
- I implemented patient-level train-test splitting and supported hyperparameter tuning.
- Result was clear: CatBoost and LightGBM outperformed Logistic Regression, with CatBoost best overall.
- I collaborated with team members to integrate our modeling work with their analysis.

### Challenge and Resolution
- **Challenge:** Keep model comparison fair while avoiding optimistic bias.
- **How addressed:** I standardized evaluation protocol and enforced patient-level partitioning to prevent leakage. My framework supported consistent evaluation across all models.

## Week 4 (13 Apr 2026 - 19 Apr 2026): Presentation Preparation and Documentation
- I supported final presentation development by organizing key result visualizations and helping with the presentation script.
- I contributed to the report methodology section.
- I also helped package final code artifacts for submission.
- I coordinated with team members to ensure all deliverables were properly documented.

### Challenge and Resolution
- **Challenge:** Keep code artifacts, report method, and presentation narrative consistent.
- **How addressed:** I cross-checked outputs and documentation before assembling the final submission package. My packaging work ensured smooth submission.

## Overall Contribution Summary
- Acquired and validated core CMS ESRD datasets.
- Improved reliability of the dataset download workflow.
- Contributed to model benchmarking and evaluation rigor.
- Supported final documentation and presentation readiness.
- Ensured data quality and pipeline reliability throughout the project.