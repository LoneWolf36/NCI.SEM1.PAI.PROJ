# Requirements Verification

Reference assignment: `Description_Programming_for_AI_final.docx`

This file is intentionally evidence-based. It records what is currently satisfied in the repository and what still remains outside the repo.

## 1. Project objective and scope

| Requirement | Status | Evidence |
|---|---|---|
| Clear research/application question | ✅ Met | `reports/final_report.tex`, `reports/FINAL_REPORT.md`, `README.md` |
| Novel framing / justified significance | ✅ Met | Framed around linked ESRD readmission pipeline, not synthetic labels |
| Three or four datasets used | ✅ Met | `scripts/ingest_datasets.py`, SQLite raw tables |
| Each dataset >= 1,000 rows | ✅ Met | DB counts: 3.2M / 7.7M / 3.9M / 32.3M |
| Database-first storage before processing | ✅ Met | `scripts/ingest_datasets.py`, `dialysis_readmission.db` |
| Programmatic preprocessing, transformation, analysis, visualisation | ✅ Met | `scripts/ingest_datasets.py`, `scripts/train_readmission_models.py`, `outputs/analysis/` |
| Processed outputs stored programmatically where relevant | ✅ Met | `derived_*`, `model_feature_mart`, `model_runs`, `evaluation_metrics` |
| Coherent end-to-end workflow | ✅ Met | Scripts + DB + executed notebook + pipeline diagram |

## 2. Report deliverable

| Requirement | Status | Evidence |
|---|---|---|
| Around 3,000 words | ✅ Met | `reports/final_report.tex` maintained near assignment target |
| IEEE conference format source | ✅ Met | `reports/final_report.tex` uses `IEEEtran` |
| Required sections present | ✅ Met | Abstract, Introduction, Related Work, Methodology, Results and Evaluation, Conclusions and Future Work, Bibliography |
| In-text citations present | ✅ Met | `reports/final_report.tex` uses `\cite{...}`; `reports/FINAL_REPORT.md` has numbered citations |
| Pipeline diagram included | ✅ Met | `reports/pipeline.png`, `reports/pipeline.svg`, report references |
| Report PDF generated | ✅ Met | `reports/FINAL_REPORT.pdf` |

## 3. Code artefact deliverable

| Requirement | Status | Evidence |
|---|---|---|
| Code archive / reviewable assets | ✅ Met | `code_artifact.zip` |
| Program code included | ✅ Met | `scripts/ingest_datasets.py`, `scripts/train_readmission_models.py`, `notebooks/final_cms_esrd_readmission_workflow.ipynb` |
| Data-processing scripts included | ✅ Met | same as above |
| Data dictionary included where appropriate | ✅ Met | `docs/DATA_DICTIONARY.md` |
| System configuration details included | ✅ Met | `scripts/requirements.txt`, `README.md` |

## 4. Journal deliverable

| Requirement | Status | Evidence |
|---|---|---|
| One journal per member | ✅ Met | 4 `journals/JOURNAL_*.pdf` files |
| Full name and student number included | ✅ Met | journal markdown/PDF content |
| Tasks included | ✅ Met | weekly logs |
| Time spent included | ✅ Met | explicit hours per week |
| Challenges included | ✅ Met | challenge sections |
| How challenges were addressed | ✅ Met | resolution sections |

## 5. Remaining external submission item

| Requirement | Status | Note |
|---|---|---|
| Final presentation video (`.mp4`) | ⏳ Pending outside repo | Script exists as `docs/presentation_script.md`, but final recorded/exported video must still be produced separately |

## Conclusion

The repository now satisfies the core technical, report, code-artifact, and journal requirements with evidence in source files, generated outputs, and supporting documentation. The main remaining submission item outside the repo is the final recorded presentation video.
