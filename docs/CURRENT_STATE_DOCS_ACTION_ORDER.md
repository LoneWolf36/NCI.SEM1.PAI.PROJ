## Final values to use

- Sample: **100,000 patients / 388,375 hospitalization events**
- Logistic Regression: **AUC 0.6309, F1 0.3469**
- CatBoost: **AUC 0.6453, F1 0.3499**
- LightGBM: **AUC 0.6242, F1 0.3009**

## Order of work

### 1. Presentation first

Files:
- `presentation_script_SH.md`
- `dialysis_readmission_presentation.pptx`

Do this:
- replace old metrics
- replace `387,748` with `388,375`
- remove “application or notebook” wording; use notebook only
- add diagnosis-context mention
- add threshold-tuning mention

### 2. Report next

File:
- `Your_Paper__3_.pdf`

Do this:
- replace abstract metrics + event count
- replace results table
- replace old Logistic Regression explanation
- add threshold-selection wording in methodology
- add diagnosis-context wording in feature engineering/methodology
- update old schema names if they appear

### 3. Journals last

Files:
- `JOURNAL_Mohammed_Faizan_Khan_25214501.docx`
- `JOURNAL_Sakshi_Patil_24304166.docx`
- `JOURNAL_Shashank_Yadav_25118692.docx`
- `JOURNAL_Chetan_Panchal_24244058.docx`

Do this in every journal:
- replace old metrics
- replace `387,748` with `388,375`
- replace old schema names like `clean_patient`, `clean_hospitalization`, `derived_readmission`
- update any “default threshold” wording to threshold-tuned wording

## Work split

### Mohammed Faizan Khan
- own final metrics and results wording
- own presentation lead wording
- carry heaviest load
- target hours: **44–46**

### Chetan Panchal
- own DB/schema naming corrections
- own QA / evidence alignment wording
- target hours: **39–41**

### Shashank Yadav
- own dataset / benchmark / methodology updates
- own packaging / presentation support wording
- target hours: **38–40**

### Sakshi Patil
- own cleaning / EDA / report-narration updates
- own wording consistency pass
- target hours: **37–39**

## Replace these old names

| Old | Use instead |
|---|---|
| `clean_patient` | `clean_patient_summary` |
| `clean_hospitalization` | `clean_cl_hospitalization` |
| `clean_hd_adqcy` | `clean_cl_hd_adqcy` |
| `derived_readmission` | `derived_readmission_events` |

## Rule

Do not rewrite whole files.

Patch:
1. metrics
2. event count
3. schema names
4. threshold wording
5. diagnosis-context wording

That is enough to realign most of the drift.
