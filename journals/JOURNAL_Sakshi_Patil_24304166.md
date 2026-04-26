# Individual Journal

## Student Details
- **Full Name:** Sakshi Patil
- **Student Number:** 24304166
- **Project:** Dialysis patient readmission risk prediction using linked CMS ESRD datasets

## Weekly Contribution Log

| Week | Date Range | Time Spent (Estimated) | Tasks Completed |
|---|---|---:|---|
| Week 1 | 23 Mar 2026 - 29 Mar 2026 | 8 hours | Compliance assessment, project realignment strategy |
| Week 2 | 30 Mar 2026 - 05 Apr 2026 | 11 hours | Data ingestion implementation, cleaning pipeline, linkage verification |
| Week 3 | 06 Apr 2026 - 12 Apr 2026 | 10 hours | Temporal feature improvements, subgroup analysis support, SHAP contribution |
| Week 4 | 13 Apr 2026 - 19 Apr 2026 | 9 hours | Results analysis, visualizations, report sections on evaluation and future work |

**Total Estimated Time:** **38 hours**

## Week 1 (23 Mar 2026 - 29 Mar 2026): Project Assessment and Realignment
- I joined the compliance review and checked our work against the assignment expectations.
- We found three big issues quickly:
  - We were using synthetic data instead of required real datasets.
  - There was no database integration.
  - Report claims did not match the implemented system.
- I helped define a realistic transition plan to move to linked CMS ESRD datasets.
- I focused on ensuring our realignment strategy would be executable within our timeline.

### Challenge and Resolution
- **Challenge:** We had to pivot fast without breaking project continuity.
- **How addressed:** I pushed for minimum critical changes first: real data, database integration, and evidence-backed reporting. My strategic thinking helped us stay on track.

## Week 2 (30 Mar 2026 - 05 Apr 2026): Data Pipeline Implementation
- I implemented core ingestion pieces:
  - Robust download functions with retry handling.
  - Data cleaning routines for each dataset.
  - Feature engineering flow support.
- I also verified patient ID overlap and linkage behavior across datasets to confirm integration quality.
- I collaborated with team members to ensure our pipeline met their modeling requirements.

### Challenge and Resolution
- **Challenge:** Data consistency across multiple files and tables was a constant risk.
- **How addressed:** I added repeated checks for linkage keys and download reliability to catch silent errors early. My validation work prevented downstream issues.

## Week 3 (06 Apr 2026 - 12 Apr 2026): Feature Engineering and Model Enhancement
- I led feature enhancements with a focus on temporal patient-history signals.
- I implemented subgroup analysis support and contributed to the SHAP interpretation pipeline.
- A strong pattern showed up: prior hospitalization count and recent hospitalization activity were major predictors.
- I worked closely with the modeling team to ensure our features supported their work.

### Challenge and Resolution
- **Challenge:** Build clinically meaningful features without introducing leakage.
- **How addressed:** I followed patient-level split principles and used time-aware feature construction. My approach enhanced model performance while maintaining validity.

## Week 4 (13 Apr 2026 - 19 Apr 2026): Results Analysis and Report Contribution
- I analyzed model outputs and subgroup behavior in detail.
- I created the visualizations used in the final report.
- I wrote major sections:
  - Results and Evaluation
  - Conclusions and Future Work
- I also helped turn SHAP findings into clear discussion points for the report.
- I coordinated with team members to ensure our results section accurately reflected our work.

### Challenge and Resolution
- **Challenge:** Explaining technical model behavior in a healthcare context people can follow.
- **How addressed:** I tied metrics, subgroup visuals, and SHAP explanations into one coherent narrative. My communication work made our findings accessible.

## Overall Contribution Summary
- Implemented key data pipeline functionality.
- Improved feature engineering with temporal signals.
- Led result interpretation and reporting quality work.
- Supported evidence-based final conclusions.
- Facilitated team communication and result synthesis.