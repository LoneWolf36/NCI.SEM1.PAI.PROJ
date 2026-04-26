# Data Dictionary

## Scope

This dictionary documents the main source, transformed, and modeling tables used in the CMS ESRD 30-day readmission project.

## 1. Source datasets

| Dataset | Raw table | Purpose | Key linkage fields |
|---|---|---|---|
| `PATIENT_SUMMARY` | `raw_patient_summary` | Patient demographics and diagnosis context | `pat_id` |
| `ADMIT_TREATMENT` | `raw_admit_treatment` | Treatment history, modality, dialysis setting | `pat_id`, `prov_nbr` |
| `CL_HOSPITALIZATION` | `raw_cl_hospitalization` | Hospitalization events and readmission target derivation | `pat_id`, `prov_nbr` |
| `CL_HD_ADQCY` | `raw_cl_hd_adqcy` | Dialysis adequacy measures such as Kt/V | `pat_id`, `prov_nbr` |

## 2. Clean tables

### `clean_patient_summary`

| Column | Meaning |
|---|---|
| `pat_id` | Patient identifier |
| `state` | State of residence |
| `age_range` | Age bucket |
| `race` | Reported race |
| `gender` | Reported gender |
| `ethnicity` | Reported ethnicity |
| `primdiag` | Primary diagnosis text |
| `primcause` | Primary ESRD cause |
| `netnumb` | ESRD network number |

### `clean_admit_treatment`

| Column | Meaning |
|---|---|
| `pat_id` | Patient identifier |
| `prov_nbr` | Normalized 6-digit provider number |
| `admit_date` | Treatment admission date (relative integer) |
| `admit_reason` | Admission reason |
| `discharge_date` | Treatment discharge date (relative integer) |
| `discharge_reason` | Discharge reason |
| `treatment_start_date` | Treatment start date (relative integer) |
| `dialysis_setting` | Setting of dialysis care |
| `treatment_type` | Treatment type |
| `sessions_per_week` | Sessions per week where available |
| `dialysis_type` | Dialysis type |
| `modality` | Dialysis modality |
| `treatment_event_date` | Coalesced event date used for temporal feature engineering |

### `clean_cl_hospitalization`

| Column | Meaning |
|---|---|
| `pat_id` | Patient identifier |
| `prov_nbr` | Normalized 6-digit provider number |
| `clinical_month_year` | Clinical month-year key |
| `modality` | Dialysis modality at event |
| `hospitalization_type` | Hospitalization type/class |
| `hospital_admit_date` | Hospital admission date (relative integer) |
| `hospital_discharge_date` | Hospital discharge date (relative integer) |
| `hospital_discharge_diag` | Discharge diagnosis |
| `hospital_admit_diag` | Admission diagnosis |
| `length_of_stay` | Length of stay in days |
| `facility_to_hospital` | Facility-to-hospital indicator |
| `advanced_directives` | Advanced directives flag |
| `transplant_referral` | Referral flag |
| `transplant_wait_list` | Waitlist flag |
| `presumptive_diag_to_hospitalization` | Presumptive diagnosis flag |

### `clean_cl_hd_adqcy`

| Column | Meaning |
|---|---|
| `pat_id` | Patient identifier |
| `prov_nbr` | Normalized 6-digit provider number |
| `clncl_mo_yr` | Clinical month-year key |
| `modality` | Dialysis modality |
| `hd_ktv` | Hemodialysis adequacy value (Kt/V) |
| `hd_ktv_coll_date` | Kt/V collection date |
| `hd_ktv_method` | Kt/V calculation method |
| `hd_weight_pre` | Pre-dialysis weight, where available |
| `hd_weight_pre_uom` | Unit of measure for pre-dialysis weight |

## 3. Derived tables

### `derived_readmission_events`

Event-level hospitalization table used to derive the primary target.

| Column | Meaning |
|---|---|
| `pat_id` | Patient identifier |
| `prov_nbr` | Provider number |
| `clinical_month_year` | Clinical month-year key |
| `modality` | Hospitalization modality context |
| `hospitalization_type` | Hospitalization type/class |
| `hospital_admit_date` | Index admission date |
| `hospital_discharge_date` | Index discharge date |
| `hospital_admit_diag` | Admission diagnosis |
| `hospital_discharge_diag` | Discharge diagnosis |
| `length_of_stay` | Stay length in days |
| `next_hospital_admit_date` | Next observed admission for same patient |
| `previous_hospital_discharge_date` | Previous discharge for same patient |
| `hospitalization_sequence` | Chronological event number per patient |
| `gap_to_next_admit_days` | Days from discharge to next admission |
| `gap_from_previous_discharge_days` | Days since previous discharge |
| `readmitted_30d` | Binary target: 1 if next admission occurs within 30 days |

### `derived_patient_features`

Patient-level aggregate table used for cross-event feature enrichment.

| Column | Meaning |
|---|---|
| `pat_id` | Patient identifier |
| `state`, `age_range`, `race`, `gender`, `ethnicity`, `primdiag`, `primcause`, `netnumb` | Demographic / diagnostic context |
| `ever_hemodialysis` | Whether patient ever had hemodialysis |
| `ever_center_hemo` | Whether patient ever had center-based hemodialysis |
| `treatment_records` | Count of treatment records |
| `first_treatment_start_date` | Earliest treatment start |
| `last_treatment_start_date` | Latest treatment start |
| `mean_hd_ktv`, `min_hd_ktv`, `max_hd_ktv` | Aggregate Kt/V statistics |
| `hd_ktv_measurements` | Count of adequacy measurements |
| `hospitalization_count` | Number of hospitalization events |
| `mean_length_of_stay`, `max_length_of_stay` | Stay aggregates |
| `patient_readmit_30d_rate` | Average event-level readmission rate for patient |

## 4. Final modeling table

### `model_feature_mart`

This is the main event-level analytical table used for model training.

| Column | Meaning |
|---|---|
| `pat_id` | Patient identifier |
| `prov_nbr` | Provider number |
| `hospitalization_sequence` | Event number for patient |
| `clinical_month_year` | Clinical month-year key |
| `hospitalization_modality` | Modality associated with hospitalization |
| `hospitalization_type` | Hospitalization type |
| `hospital_admit_date` | Admission date |
| `hospital_discharge_date` | Discharge date |
| `length_of_stay` | Stay duration in days |
| `gap_from_previous_discharge_days` | Time since prior discharge |
| `gap_to_next_admit_days` | Time to next admission |
| `readmitted_30d` | Primary target variable |
| `prior_hospitalizations` | Count of earlier hospitalizations |
| `prior_30d_hospitalizations` | Count of prior hospitalizations in previous 30 days |
| `prior_180d_hospitalizations` | Count of prior hospitalizations in previous 180 days |
| `state`, `age_range`, `race`, `gender`, `ethnicity`, `primdiag`, `primcause` | Demographic / diagnosis features |
| `prior_treatment_records` | Number of treatment records before current event |
| `recent_30d_treatment_records` | Treatment records in prior 30 days |
| `recent_90d_treatment_records` | Treatment records in prior 90 days |
| `days_since_last_treatment` | Recency of most recent treatment |
| `prior_hemodialysis_flag` | Historical hemodialysis flag |
| `prior_center_hemo_flag` | Historical center-hemodialysis flag |
| `recent_hd_ktv` | Most recent Kt/V before event |
| `mean_prior_hd_ktv` | Mean historical Kt/V before event |
| `recent_3m_hd_ktv_mean` | Mean Kt/V over recent 3 months |
| `recent_6m_hd_ktv_range` | Kt/V range over recent 6 months |
| `hd_ktv_recent_vs_history_delta` | Difference between recent and historical Kt/V |
| `prior_hd_ktv_measurements` | Count of prior Kt/V measurements |

## 5. Tracking and evaluation tables

| Table | Purpose |
|---|---|
| `model_runs` | Stores model run metadata and parameter JSON |
| `evaluation_metrics` | Stores test metrics per run |
| `figure_registry` | Reserved registry for figure outputs |

## 6. Output artifacts

| Path pattern | Meaning |
|---|---|
| `outputs/model_runs/train_*.json` | Serialized training summaries and metrics |
| `outputs/analysis/catboost_feature_importance_*.csv/.png` | Feature importance artifacts |
| `outputs/analysis/catboost_shap_summary_*.csv/.png` | SHAP summary artifacts |
| `outputs/analysis/subgroup_metrics_*.csv` | Subgroup evaluation metrics |
| `outputs/analysis/subgroup_f1_race_*.png` | Race subgroup visualization |

## 7. Notes

- Date fields are represented as relative integer values from the CMS ESRD source system rather than calendar dates.
- Linkage is centered on `pat_id`, with `prov_nbr` used where provider-level context matters.
- `readmitted_30d` is derived from sequential hospitalization events, not synthetically generated.
