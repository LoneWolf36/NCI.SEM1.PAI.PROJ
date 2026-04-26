# Project Submission: Data-Driven Prediction of 30-Day Readmissions in ESRD Patients

This repository contains the codebase and outputs for predicting 30-day hospital readmissions among End-Stage Renal Disease (ESRD) dialysis patients using linked CMS records.

## Directory Structure

*   `docs/`: Contains the `DATA_DICTIONARY.md` explaining the structure of source, transformed, and derived tables.
*   `notebooks/`: Contains the Jupyter notebooks for the analytical workflow.
*   `outputs/`: Stores the generated figures, evaluation metrics, and feature importance/SHAP value analyses.
*   `reports/`: Contains the final project report, presentation video, and architecture diagrams.
*   `scripts/`: Python scripts for automated data ingestion and model training/evaluation.

## Instructions

1.  **Environment Setup**: Set up the Python environment using `scripts/requirements.txt`.
2.  **Data Ingestion**: The raw CMS data is not included in this repository due to its large size. Please run `scripts/ingest_datasets.py` to automatically download the raw CMS datasets into a local `data/` directory and ingest the linked tables.
3.  **Model Training**: Run `scripts/train_readmission_models.py` or use the provided Jupyter notebook in `notebooks/` to reproduce the model evaluation, temporal feature engineering, and SHAP explainability workflows.
