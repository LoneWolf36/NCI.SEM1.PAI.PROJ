# Individual Journal

## Student Details
- **Full Name:** Chetan Panchal
- **Student Number:** 24244058
- **Project:** Dialysis patient readmission risk prediction using linked CMS ESRD datasets

## Weekly Contribution Log

| Week | Date Range | Time Spent (Estimated) | Tasks Completed |
|---|---|---:|---|
| Week 1 | 23 Mar 2026 - 29 Mar 2026 | 9 hours | Requirement-gap assessment, strategic realignment decisions, DB schema design |
| Week 2 | 30 Mar 2026 - 05 Apr 2026 | 11 hours | Database-first pipeline design, schema/index setup, raw/clean/derived table workflow |
| Week 3 | 06 Apr 2026 - 12 Apr 2026 | 10 hours | SHAP analysis, subgroup performance analysis, temporal feature support, metric refinement |
| Week 4 | 13 Apr 2026 - 19 Apr 2026 | 10 hours | Integration QA, report claim verification, artifact and presentation preparation |

**Total Estimated Time:** **40 hours**

## Week 1 (23 Mar 2026 - 29 Mar 2026): Project Assessment and Direction Setting
- I joined the assignment-compliance review and focused on architecture gaps.
- The major issues were:
  - Only one dataset was in use, not the required 3-4 datasets.
  - No database-first implementation was present.
  - The target was synthetically generated instead of derived from real data.
  - Report statements and implementation were out of sync.
- I contributed to the realignment decision to move to linked CMS ESRD datasets.
- I took the lead on initial database schema design, laying groundwork for the pipeline.

### Challenge and Resolution
- **Challenge:** Correct architecture without changing project objective or scope.
- **How addressed:** I helped define a staged migration plan centered on a database-first path, with particular attention to schema design for scalability.

## Week 2 (30 Mar 2026 - 05 Apr 2026): Database Pipeline Development
- Most of my week went into database-first infrastructure.
- I designed and implemented:
  - SQLite schema design.
  - Raw data storage for four CMS ESRD datasets.
  - Clean table structures with indexing.
  - Derived tables for readmission events and patient features.
- This became the base for downstream modeling and reproducibility.
- I worked closely with the team to ensure the pipeline supported their modeling needs.

### Challenge and Resolution
- **Challenge:** Build a schema efficient enough for large healthcare data and repeated analytics queries.
- **How addressed:** I used normalized structures, targeted indexing, and strict separation of raw, clean, and derived stages. My design choices enabled faster query performance for the team.

## Week 3 (06 Apr 2026 - 12 Apr 2026): Advanced Analysis and Interpretation
- I expanded the analysis layer in four areas:
  - SHAP-based interpretability analysis.
  - Subgroup performance analysis by demographics.
  - Temporal feature engineering support.
  - Evaluation metric refinements.
- Main interpretability finding: prior hospitalization count and recent hospitalization activity were major predictors.
- I collaborated with team members to ensure analysis aligned with their work.

### Challenge and Resolution
- **Challenge:** Translate model behavior into signals that are both actionable and understandable.
- **How addressed:** I combined SHAP evidence with subgroup analysis to keep insights technical but still clear. My work supported the team's interpretation efforts.

## Week 4 (13 Apr 2026 - 19 Apr 2026): Final Integration and Quality Assurance
- I ran final integration checks across pipeline and reporting artifacts.
- I reviewed report sections for technical correctness and verified each claim against implementation evidence.
- I also helped prepare the final code artifact package and presentation materials.
- I coordinated with team members to ensure all components worked together seamlessly.

### Challenge and Resolution
- **Challenge:** Prevent mismatch between documentation and actual code/results at submission time.
- **How addressed:** I used an evidence-first QA pass on the report and deliverables before final submission. My systematic review caught several inconsistencies.

## Overall Contribution Summary
- Designed and implemented the core database-first pipeline.
- Contributed interpretability and subgroup analysis work.
- Supported evaluation rigor and delivery quality.
- Helped keep the final report and artifacts technically accurate.
- Facilitated team coordination and integration efforts.