# Dataset Acquisition Plan — CMS ESRD Readmission Pipeline

## Locked decision

We are preserving the original topic as closely as possible.

We are **not** using the county-level California pivot as the main project direction.

We are replacing the weak synthetic-label workflow with a linked CMS ESRD multi-table workflow.

## Final research question

**Can machine learning predict 30-day hospital readmission risk in dialysis / ESRD patients using linked CMS ESRD patient, treatment, hospitalization, and dialysis adequacy data?**

## Final dataset stack

### Dataset 1 — Patient summary

- **Source:** CMS ESRD Population PUF
- **File:** `patient_summary.zip`
- **Direct URL:** `https://downloads.cms.gov/files/patient_summary.zip`
- **Rows verified:** 3,197,683
- **Type:** patient-level summary table
- **Role:** demographics and diagnosis context
- **Key fields observed:** `pat_id`, `state`, `age_range`, `race`, `gender`, `ethnicity`, `primdiag`, `primcause`, `netnumb`

### Dataset 2 — Admit / treatment history

- **Source:** CMS ESRD Population PUF
- **File:** `admit_treatment.zip`
- **Direct URL:** `https://downloads.cms.gov/files/admit_treatment.zip`
- **Rows verified:** 7,720,441
- **Type:** patient-treatment episode table
- **Role:** treatment modality and dialysis-setting history
- **Key fields observed:** `pat_id`, `prov_nbr`, `Admit_Date`, `Admit_Reason`, `Discharge_Date`, `Discharge_Reason`, `Treatment_Start_Date`, `Dialysis_Setting`, `Treatment_Type`, `Dialysis_Type`, `Modality`

### Dataset 3 — Hospitalization events / target source

- **Source:** CMS ESRD Population PUF
- **File:** `cl_hospitalization.zip`
- **Direct URL:** `https://downloads.cms.gov/files/cl_hospitalization.zip`
- **Rows verified:** 3,899,711
- **Type:** patient hospitalization events table
- **Role:** derive true 30-day readmission outcome
- **Key fields observed:** `pat_id`, `prov_nbr`, `clinical_month_year`, `modality`, `Hospitalizations`, `Hospital_Admit_Date`, `Hospital_Discharge_Date`, `Hospital_Discharge_Diag`, `Hospital_Admit_Diag`, `Length_of_Stay`

### Dataset 4 — Dialysis adequacy measures

- **Source:** CMS ESRD Population PUF
- **File:** `cl_hd_adqcy.zip`
- **Direct URL:** `https://downloads.cms.gov/files/cl_hd_adqcy.zip`
- **Rows:** not yet fully counted locally, but CMS documentation confirms it is part of the ESRD Population PUF clinical tables and therefore well above assignment scale
- **Type:** patient-facility-month dialysis adequacy table
- **Role:** dialysis-specific feature source closer to original report claims
- **Documented fields:** `PAT_ID`, `PROV_NBR`, `CLNCL_MO_YR`, `MODALITY`, `Hd_ktv`, `hd_ktv_coll_date`, `hd_ktv_method`

## Why this stack is coherent

All four tables belong to the same CMS ESRD ecosystem.

This is the key difference versus the earlier loose dataset mix.

1. `PATIENT_SUMMARY` gives patient demographics and diagnosis context.
2. `ADMIT_TREATMENT` gives treatment and dialysis-setting history.
3. `CL_HOSPITALIZATION` gives actual hospitalization events and enables readmission derivation.
4. `CL_HD_ADQCY` gives dialysis-specific adequacy features such as Kt/V.

This is a **real linked patient-level multi-table project**, not a side-by-side dataset bundle.

## Verified linkage evidence

### Patient overlap

- hospitalization unique patients: **855,823**
- hospitalization overlap with `patient_summary`: **826,117 / 855,823**
- hospitalization overlap with `admit_treatment`: **855,505 / 855,823**

### Patient-provider pair overlap

- hospitalization ↔ admit-treatment unique pair overlap: **1,010,096 / 1,011,138**
- overlap rate: **~99.9%**

## Verified target feasibility

Using `CL_HOSPITALIZATION` only:

- rows with usable admit/discharge dates: **3,098,950**
- rows with nonnegative follow-up gap: **2,250,000**
- estimated 30-day readmission rate from next-admission gaps: **~25.18%**

This is the strongest reason this stack should become the project core.

## Unit of analysis

Preferred final modelling unit:

- **index hospitalization / discharge event**

Target:

- **readmitted within 30 days after discharge** (`0/1`)

## Integration keys

- `pat_id`
- `prov_nbr`
- event timing fields based on relative study days
- modality where relevant

## Database-first design

### Raw tables

```sql
CREATE TABLE raw_patient_summary (...);
CREATE TABLE raw_admit_treatment (...);
CREATE TABLE raw_cl_hospitalization (...);
CREATE TABLE raw_cl_hd_adqcy (...);
```

### Clean tables

```sql
CREATE TABLE clean_patient_summary (...);
CREATE TABLE clean_admit_treatment (...);
CREATE TABLE clean_cl_hospitalization (...);
CREATE TABLE clean_cl_hd_adqcy (...);
```

### Derived tables

```sql
CREATE TABLE derived_readmission_events (...);
CREATE TABLE derived_patient_features (...);
CREATE TABLE model_feature_mart (...);
CREATE TABLE model_runs (...);
CREATE TABLE evaluation_metrics (...);
CREATE TABLE figure_registry (...);
```

## Core engineered features

### From `PATIENT_SUMMARY`

- age bucket
- sex / gender
- race / ethnicity
- primary diagnosis cause categories

### From `ADMIT_TREATMENT`

- dialysis setting
- treatment type
- dialysis modality history
- time since treatment start
- prior admission / discharge patterns

### From `CL_HOSPITALIZATION`

- index length of stay
- hospitalization type
- prior hospitalization count
- gap since previous hospitalization
- discharge diagnosis group

### From `CL_HD_ADQCY`

- Kt/V value
- Kt/V availability flag
- adequacy method
- most recent or rolling adequacy summary before index discharge

## Modelling target

Primary target:

- **30-day readmission classification**

Secondary analysis:

- time-to-next-admission distribution
- subgroup analysis by modality / diagnosis / adequacy status

## Model direction

### Keep strong

- CatBoost
- Logistic Regression baseline
- Random Forest / XGBoost as secondary comparator if helpful
- SHAP explainability
- repeated-run stability analysis

### Keep cautious

- TFT only if a real sequential setup is implemented from longitudinal CMS tables

## What we are explicitly rejecting

- synthetic readmission labels
- old Kaggle dialysis dataset as final core target source
- fake patient-level joins across unrelated datasets
- county-level California pivot as the final main story if CMS ESRD path works

## Immediate execution plan

1. Ingest the 4 CMS ESRD tables into SQLite
2. Normalize IDs and date fields
3. Build the derived hospitalization cohort with true 30-day readmission label
4. Join patient, treatment, and adequacy features
5. Save final modelling mart to database
6. Train baseline + CatBoost model
7. Rewrite report and presentation around the exact CMS workflow

## Risk notes

### Risk 1 — CMS clinical tables are large
- **Mitigation:** chunked ingestion into SQLite and indexed joins

### Risk 2 — some fields use relative study dates
- **Mitigation:** use relative gaps and event ordering; absolute calendar dates are not required for readmission gap derivation

### Risk 3 — not every hospitalized patient has every linked table populated
- **Mitigation:** report join coverage explicitly and design transparent missing-value handling

### Risk 4 — TFT may still be weak
- **Mitigation:** keep CatBoost as core and treat TFT as optional rather than guaranteed
