# Project Direction Realignment

## Decision

Direction now locked as:

**keep the original dialysis / readmission topic, but replace the weak synthetic-data core with linked CMS ESRD public-use tables.**

## Blunt assessment

The earlier repo state was not submission-safe because:

- notebooks generated a synthetic readmission label
- actual code did not show a real multi-dataset linked workflow
- county-level California pivot drifted too far from the existing report

The better answer was not topic drift.

The better answer was **better datasets**.

## Final research question

**Can machine learning predict 30-day hospital readmission risk in dialysis / ESRD patients using linked CMS ESRD patient, treatment, hospitalization, and dialysis adequacy data?**

## Why this is better

1. **Much closer to the report**
   - dialysis / ESRD patients remain the subject
   - hospitalization / readmission remains the outcome area
   - patient-level framing remains intact

2. **Real target**
   - readmission can be derived from true hospitalization events
   - no synthetic label creation

3. **Genuine multi-dataset coherence**
   - CMS tables link by `pat_id` and `prov_nbr`
   - treatment, hospitalization, and dialysis adequacy live in one consistent ESRD ecosystem

4. **Assignment fit**
   - 4 structured datasets
   - all well above 1,000 rows
   - database-first ingestion feasible
   - programmatic preprocessing, modelling, visualization, and DB write-back feasible

## Final dataset stack

### Dataset 1 — Patient summary
**PATIENT_SUMMARY**

- Source: CMS ESRD Population PUF
- Granularity: patient
- Role: demographics and high-level diagnosis context
- Example fields:
  - `pat_id`
  - `state`
  - `age_range`
  - `race`
  - `gender`
  - `ethnicity`
  - `primdiag`
  - `primcause`

### Dataset 2 — Treatment history
**ADMIT_TREATMENT**

- Source: CMS ESRD Population PUF
- Granularity: patient-treatment episode
- Role: treatment modality and dialysis setting history
- Example fields:
  - `pat_id`
  - `prov_nbr`
  - `Admit_Date`
  - `Discharge_Date`
  - `Dialysis_Setting`
  - `Treatment_Type`
  - `Dialysis_Type`
  - `Modality`

### Dataset 3 — Hospitalization events / target source
**CL_HOSPITALIZATION**

- Source: CMS ESRD Population PUF
- Granularity: patient-facility-month hospitalization events
- Role: derive the true 30-day readmission target
- Example fields:
  - `pat_id`
  - `prov_nbr`
  - `clinical_month_year`
  - `Hospital_Admit_Date`
  - `Hospital_Discharge_Date`
  - `Hospital_Discharge_Diag`
  - `Hospital_Admit_Diag`
  - `Length_of_Stay`

### Dataset 4 — Dialysis adequacy clinical features
**CL_HD_ADQCY**

- Source: CMS ESRD Population PUF
- Granularity: patient-facility-month hemodialysis adequacy record
- Role: provide dialysis-specific features closer to original report claims
- Example documented fields:
  - `pat_id`
  - `prov_nbr`
  - `clncl_mo_yr`
  - `modality`
  - `hd_ktv`
  - `hd_ktv_coll_date`
  - `hd_ktv_method`

## Unit of analysis

Preferred final modelling unit:

- **index hospitalization / discharge event for an ESRD dialysis patient**

Target:

- **readmitted within 30 days after discharge: yes / no**

## Integration logic

1. Ingest all 4 raw CMS tables into SQLite.
2. Normalize column names, patient IDs, provider IDs, and relative date fields.
3. Clean hospitalization events and sort chronologically per patient.
4. Derive next-admission gap and create the 30-day readmission label.
5. Aggregate or attach treatment-history features from `ADMIT_TREATMENT`.
6. Attach dialysis adequacy features from `CL_HD_ADQCY`.
7. Attach patient-level demographics from `PATIENT_SUMMARY`.
8. Store the final modelling cohort back into the database.

## What is now out of scope

- county-level California readmission burden modeling
- synthetic patient-level readmission labels
- claiming Kaggle hemodialysis data as the final core dataset
- forced UCI diabetes readmission anchor if CMS ESRD stack works

## Model implications

### CatBoost
- remains strong fit
- tabular mixed clinical + treatment + adequacy features

### TFT
- no longer automatic core model
- may be retained only if a defensible sequential setup is built from the CMS timeline
- should not be claimed as core novelty unless actually supported by the final implementation

## Immediate execution order

1. Rewrite dataset acquisition plan to CMS ESRD stack
2. Build final ingestion script for CMS ESRD tables
3. Create raw / clean / derived database schema
4. Build readmission cohort with true 30-day label
5. Train baseline + CatBoost models
6. Decide whether TFT remains exploratory or is dropped
7. Rewrite report around the implemented CMS pipeline
