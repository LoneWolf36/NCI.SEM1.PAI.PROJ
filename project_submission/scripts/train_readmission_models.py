"""Train readmission models from SQLite feature mart.

Designed for the CMS ESRD pipeline created by `ingest_datasets.py`.

Key choices:
- patient-level split to reduce leakage across repeated hospitalizations
- conservative feature set that avoids direct future leakage
- Logistic Regression baseline + CatBoost main model + LightGBM challenger
- metrics written back to SQLite `model_runs` and `evaluation_metrics`
- subgroup analysis + CatBoost interpretation artefacts
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

try:
    from catboost import CatBoostClassifier, Pool
except Exception:  # pragma: no cover - optional at runtime
    CatBoostClassifier = None
    Pool = None

try:
    from lightgbm import LGBMClassifier
except Exception:  # pragma: no cover - optional at runtime
    LGBMClassifier = None


SAFE_NUMERIC_FEATURES = [
    "length_of_stay",
    "gap_from_previous_discharge_days",
    "prior_hospitalizations",
    "prior_30d_hospitalizations",
    "prior_180d_hospitalizations",
    "prior_treatment_records",
    "recent_30d_treatment_records",
    "recent_90d_treatment_records",
    "days_since_last_treatment",
    "prior_hemodialysis_flag",
    "prior_center_hemo_flag",
    "recent_hd_ktv",
    "mean_prior_hd_ktv",
    "recent_3m_hd_ktv_mean",
    "recent_6m_hd_ktv_range",
    "hd_ktv_recent_vs_history_delta",
    "prior_hd_ktv_measurements",
]

SAFE_CATEGORICAL_FEATURES = [
    "hospitalization_modality",
    "hospitalization_type",
    "hospital_admit_diag",
    "hospital_discharge_diag",
    "state",
    "age_range",
    "race",
    "gender",
    "ethnicity",
    "primdiag",
    "primcause",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train readmission models from SQLite feature mart")
    parser.add_argument("--db-path", default="dialysis_readmission.db")
    parser.add_argument("--output-dir", default="outputs/model_runs")
    parser.add_argument("--min-positive", type=int, default=50)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--max-patients",
        type=int,
        default=None,
        help="Optional cap on unique patients for faster training runs",
    )
    parser.add_argument(
        "--artifacts-dir",
        default="outputs/analysis",
        help="Directory for subgroup, importance, and SHAP artefacts",
    )
    parser.add_argument(
        "--shap-sample-size",
        type=int,
        default=1000,
        help="Max test rows to use for CatBoost SHAP artefacts",
    )
    parser.add_argument(
        "--subgroup-min-rows",
        type=int,
        default=250,
        help="Minimum subgroup rows to report subgroup metrics",
    )
    parser.add_argument(
        "--subgroup-min-positives",
        type=int,
        default=25,
        help="Minimum subgroup positives to report subgroup metrics",
    )
    return parser.parse_args()


def load_feature_mart(
    conn: sqlite3.Connection,
    max_patients: int | None = None,
    random_state: int = 42,
) -> pd.DataFrame:
    if max_patients is None:
        return pd.read_sql_query("SELECT * FROM model_feature_mart", conn)

    patient_level = pd.read_sql_query(
        "SELECT pat_id, MAX(readmitted_30d) AS readmitted_30d FROM model_feature_mart GROUP BY pat_id",
        conn,
    )
    if max_patients >= len(patient_level):
        return pd.read_sql_query("SELECT * FROM model_feature_mart", conn)

    sampled_patients, _ = train_test_split(
        patient_level,
        train_size=max_patients,
        random_state=random_state,
        stratify=patient_level["readmitted_30d"],
    )
    conn.execute("DROP TABLE IF EXISTS selected_patients_temp")
    sampled_patients[["pat_id"]].to_sql("selected_patients_temp", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_selected_patients_temp_pat_id ON selected_patients_temp(pat_id)")
    df = pd.read_sql_query(
        """
        SELECT m.*
        FROM model_feature_mart m
        INNER JOIN selected_patients_temp s USING (pat_id)
        """,
        conn,
    )
    conn.execute("DROP TABLE IF EXISTS selected_patients_temp")
    conn.commit()
    return df


def pick_existing_features(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric = [col for col in SAFE_NUMERIC_FEATURES if col in df.columns and df[col].notna().any()]
    categorical = [col for col in SAFE_CATEGORICAL_FEATURES if col in df.columns and df[col].notna().any()]
    return numeric, categorical


def split_by_patient(
    df: pd.DataFrame,
    test_size: float,
    random_state: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    patient_level = df.groupby("pat_id", as_index=False)["readmitted_30d"].max()
    train_patients, test_patients = train_test_split(
        patient_level,
        test_size=test_size,
        random_state=random_state,
        stratify=patient_level["readmitted_30d"],
    )
    train_df = df[df["pat_id"].isin(train_patients["pat_id"])].copy()
    test_df = df[df["pat_id"].isin(test_patients["pat_id"])].copy()
    return train_df, test_df


def maybe_sample_patients(
    df: pd.DataFrame,
    max_patients: int | None,
    random_state: int,
) -> pd.DataFrame:
    if max_patients is None:
        return df

    patient_level = df.groupby("pat_id", as_index=False)["readmitted_30d"].max()
    if max_patients >= len(patient_level):
        return df

    sampled_patients, _ = train_test_split(
        patient_level,
        train_size=max_patients,
        random_state=random_state,
        stratify=patient_level["readmitted_30d"],
    )
    return df[df["pat_id"].isin(sampled_patients["pat_id"])].copy()


def compute_metrics(y_true: pd.Series, y_prob: np.ndarray, threshold: float = 0.5) -> dict[str, float]:
    y_pred = (y_prob >= threshold).astype(int)
    metrics = {
        "auc": float(roc_auc_score(y_true, y_prob)),
        "average_precision": float(average_precision_score(y_true, y_prob)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "positive_rate": float(np.mean(y_true)),
        "predicted_positive_rate": float(np.mean(y_pred)),
    }
    return metrics


def compute_subgroup_metrics(
    df: pd.DataFrame,
    y_prob: np.ndarray,
    subgroup_cols: list[str],
    min_rows: int,
    min_positives: int,
) -> pd.DataFrame:
    scored = df.copy()
    scored["y_prob"] = y_prob
    rows: list[dict[str, object]] = []

    for col in subgroup_cols:
        if col not in scored.columns:
            continue
        for value, group in scored.groupby(col, dropna=False):
            if len(group) < min_rows:
                continue
            positive_rows = int(group["readmitted_30d"].sum())
            negative_rows = int(len(group) - positive_rows)
            if positive_rows < min_positives or negative_rows < min_positives:
                continue
            metrics = compute_metrics(group["readmitted_30d"], group["y_prob"].to_numpy())
            rows.append(
                {
                    "subgroup_column": col,
                    "subgroup_value": "missing" if pd.isna(value) else str(value),
                    "rows": int(len(group)),
                    "positive_rows": positive_rows,
                    **metrics,
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "subgroup_column",
                "subgroup_value",
                "rows",
                "positive_rows",
                "auc",
                "average_precision",
                "accuracy",
                "precision",
                "recall",
                "f1",
                "positive_rate",
                "predicted_positive_rate",
            ]
        )
    return pd.DataFrame(rows).sort_values(["subgroup_column", "f1"], ascending=[True, False])


def save_bar_plot(df: pd.DataFrame, label_col: str, value_col: str, path: Path, title: str, top_n: int = 15) -> None:
    if df.empty:
        return
    plot_df = df.nlargest(top_n, value_col).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(plot_df[label_col], plot_df[value_col], color="#2563eb")
    ax.set_title(title)
    ax.set_xlabel(value_col.replace("_", " ").title())
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def train_logistic_regression(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    numeric_features: list[str],
    categorical_features: list[str],
    random_state: int,
) -> tuple[Pipeline, dict[str, float], dict[str, object]]:
    preprocess = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                    ]
                ),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocess", preprocess),
            (
                "classifier",
                LogisticRegression(
                    max_iter=500,
                    solver="saga",
                    class_weight="balanced",
                    random_state=random_state,
                ),
            ),
        ]
    )

    feature_cols = numeric_features + categorical_features
    model.fit(train_df[feature_cols], train_df["readmitted_30d"])
    test_prob = model.predict_proba(test_df[feature_cols])[:, 1]
    metrics = compute_metrics(test_df["readmitted_30d"], test_prob)
    params = {
        "model_type": "LogisticRegression",
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "class_weight": "balanced",
        "solver": "saga",
    }
    return model, metrics, params


def train_catboost(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    numeric_features: list[str],
    categorical_features: list[str],
    random_state: int,
) -> tuple[CatBoostClassifier, dict[str, float], dict[str, object]]:
    if CatBoostClassifier is None:
        raise RuntimeError("catboost is not installed in this environment")

    feature_cols = numeric_features + categorical_features
    X_train = train_df[feature_cols].copy()
    X_test = test_df[feature_cols].copy()

    for col in categorical_features:
        X_train[col] = X_train[col].fillna("missing").astype(str)
        X_test[col] = X_test[col].fillna("missing").astype(str)

    for col in numeric_features:
        X_train[col] = pd.to_numeric(X_train[col], errors="coerce")
        X_test[col] = pd.to_numeric(X_test[col], errors="coerce")

    cat_features = [X_train.columns.get_loc(col) for col in categorical_features]
    model = CatBoostClassifier(
        loss_function="Logloss",
        eval_metric="AUC",
        iterations=1000,
        learning_rate=0.05,
        depth=6,
        random_seed=random_state,
        verbose=False,
        auto_class_weights="Balanced",
    )
    model.fit(X_train, train_df["readmitted_30d"], cat_features=cat_features)
    
    # Find optimal F1 threshold on training set
    train_prob = model.predict_proba(X_train)[:, 1]
    thresholds = np.linspace(0.1, 0.9, 81)
    f1_scores = [f1_score(train_df["readmitted_30d"], (train_prob >= t).astype(int), zero_division=0) for t in thresholds]
    best_t = thresholds[np.argmax(f1_scores)]
    
    test_prob = model.predict_proba(X_test)[:, 1]
    # Use optimal threshold for test metrics
    metrics = compute_metrics(test_df["readmitted_30d"], test_prob, best_t)
    params = {
        "model_type": "CatBoostClassifier",
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "iterations": 300,
        "learning_rate": 0.05,
        "depth": 6,
        "auto_class_weights": "Balanced",
    }
    return model, metrics, params


def train_lightgbm(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    numeric_features: list[str],
    categorical_features: list[str],
    random_state: int,
) -> tuple[object, dict[str, float], dict[str, object]]:
    if LGBMClassifier is None:
        raise RuntimeError("lightgbm is not installed in this environment")

    feature_cols = numeric_features + categorical_features
    X_train = train_df[feature_cols].copy()
    X_test = test_df[feature_cols].copy()

    for col in categorical_features:
        X_train[col] = X_train[col].fillna("missing").astype("category")
        X_test[col] = X_test[col].fillna("missing").astype("category")

    for col in numeric_features:
        X_train[col] = pd.to_numeric(X_train[col], errors="coerce")
        X_test[col] = pd.to_numeric(X_test[col], errors="coerce")

    model = LGBMClassifier(
        objective="binary",
        n_estimators=1000,
        learning_rate=0.05,
        num_leaves=63,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
        verbosity=-1,
    )
    model.fit(X_train, train_df["readmitted_30d"], categorical_feature=categorical_features)
    
    # Find optimal F1 threshold on training set
    train_prob = model.predict_proba(X_train)[:, 1]
    thresholds = np.linspace(0.1, 0.9, 81)
    f1_scores = [f1_score(train_df["readmitted_30d"], (train_prob >= t).astype(int), zero_division=0) for t in thresholds]
    best_t = thresholds[np.argmax(f1_scores)]
    
    test_prob = model.predict_proba(X_test)[:, 1]
    # Use optimal threshold for test metrics
    metrics = compute_metrics(test_df["readmitted_30d"], test_prob, best_t)
    params = {
        "model_type": "LGBMClassifier",
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "n_estimators": 300,
        "learning_rate": 0.05,
        "num_leaves": 63,
        "class_weight": "balanced",
    }
    return model, metrics, params


def save_catboost_artifacts(
    model: CatBoostClassifier,
    test_df: pd.DataFrame,
    numeric_features: list[str],
    categorical_features: list[str],
    artifacts_dir: Path,
    run_id: str,
    shap_sample_size: int,
) -> dict[str, str]:
    if Pool is None:
        return {}

    feature_cols = numeric_features + categorical_features
    X_test = test_df[feature_cols].copy()
    for col in categorical_features:
        X_test[col] = X_test[col].fillna("missing").astype(str)
    for col in numeric_features:
        X_test[col] = pd.to_numeric(X_test[col], errors="coerce")

    sample_size = min(shap_sample_size, len(X_test))
    X_sample = X_test.head(sample_size).copy()
    y_sample = test_df["readmitted_30d"].head(sample_size)
    cat_features = [X_sample.columns.get_loc(col) for col in categorical_features]
    pool = Pool(X_sample, y_sample, cat_features=cat_features)

    importance_df = pd.DataFrame(
        {
            "feature": feature_cols,
            "importance": model.get_feature_importance(),
        }
    ).sort_values("importance", ascending=False)
    importance_csv = artifacts_dir / f"catboost_feature_importance_{run_id}.csv"
    importance_df.to_csv(importance_csv, index=False)
    importance_png = artifacts_dir / f"catboost_feature_importance_{run_id}.png"
    save_bar_plot(importance_df, "feature", "importance", importance_png, "CatBoost feature importance")

    shap_values = model.get_feature_importance(pool, type="ShapValues")
    shap_df = pd.DataFrame(
        {
            "feature": feature_cols,
            "mean_abs_shap": np.abs(shap_values[:, :-1]).mean(axis=0),
        }
    ).sort_values("mean_abs_shap", ascending=False)
    shap_csv = artifacts_dir / f"catboost_shap_summary_{run_id}.csv"
    shap_df.to_csv(shap_csv, index=False)
    shap_png = artifacts_dir / f"catboost_shap_summary_{run_id}.png"
    save_bar_plot(shap_df, "feature", "mean_abs_shap", shap_png, "CatBoost mean |SHAP|")

    return {
        "feature_importance_csv": str(importance_csv),
        "feature_importance_png": str(importance_png),
        "shap_csv": str(shap_csv),
        "shap_png": str(shap_png),
    }


def save_subgroup_artifacts(
    test_df: pd.DataFrame,
    y_prob: np.ndarray,
    artifacts_dir: Path,
    run_id: str,
    min_rows: int,
    min_positives: int,
) -> dict[str, str]:
    subgroup_cols = ["age_range", "race", "gender", "hospitalization_modality"]
    subgroup_df = compute_subgroup_metrics(test_df, y_prob, subgroup_cols, min_rows, min_positives)
    if subgroup_df.empty:
        return {}

    subgroup_csv = artifacts_dir / f"subgroup_metrics_{run_id}.csv"
    subgroup_df.to_csv(subgroup_csv, index=False)

    plot_df = subgroup_df[subgroup_df["subgroup_column"] == "race"].copy()
    subgroup_png = artifacts_dir / f"subgroup_f1_race_{run_id}.png"
    if not plot_df.empty:
        save_bar_plot(plot_df, "subgroup_value", "f1", subgroup_png, "Race subgroup F1", top_n=12)
        return {
            "subgroup_csv": str(subgroup_csv),
            "subgroup_png": str(subgroup_png),
        }

    return {"subgroup_csv": str(subgroup_csv)}


def write_run_metadata(
    conn: sqlite3.Connection,
    run_id: str,
    model_name: str,
    params: dict[str, object],
    notes: str,
) -> None:
    conn.execute(
        "INSERT INTO model_runs (run_id, model_name, notes, created_at) VALUES (?, ?, ?, ?)",
        (run_id, model_name, json.dumps({"params": params, "notes": notes}), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()


def write_metrics(conn: sqlite3.Connection, run_id: str, metrics: dict[str, float]) -> None:
    conn.execute(
        """
        INSERT INTO evaluation_metrics (run_id, split, auc, accuracy, precision, recall, f1, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            "test",
            metrics["auc"],
            metrics["accuracy"],
            metrics["precision"],
            metrics["recall"],
            metrics["f1"],
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()


def save_run_summary(output_dir: Path, run_id: str, payload: dict[str, object]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{run_id}.json"
    path.write_text(json.dumps(payload, indent=2))
    return path


def main() -> None:
    args = parse_args()
    conn = sqlite3.connect(args.db_path)
    try:
        artifacts_dir = Path(args.artifacts_dir)
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        df = load_feature_mart(conn, args.max_patients, args.random_state)
        if df.empty:
            raise RuntimeError("model_feature_mart is empty. Run ingest_datasets.py first.")

        numeric_features, categorical_features = pick_existing_features(df)
        feature_cols = numeric_features + categorical_features
        if not feature_cols:
            raise RuntimeError("No usable features found in model_feature_mart")

        df = df[["pat_id", "readmitted_30d"] + feature_cols].copy()
        df["readmitted_30d"] = pd.to_numeric(df["readmitted_30d"], errors="coerce").fillna(0).astype(int)

        positive_rows = int(df["readmitted_30d"].sum())
        if positive_rows < args.min_positive:
            raise RuntimeError(
                f"Too few positive examples for stable training: {positive_rows}. "
                f"Need at least {args.min_positive}. Run on fuller ingestion output."
            )

        train_df, test_df = split_by_patient(df, args.test_size, args.random_state)

        results: dict[str, object] = {
            "dataset": {
                "rows": int(len(df)),
                "patients": int(df["pat_id"].nunique()),
                "positive_rows": positive_rows,
                "positive_rate": float(df["readmitted_30d"].mean()),
                "train_rows": int(len(train_df)),
                "test_rows": int(len(test_df)),
            },
            "features": {
                "numeric": numeric_features,
                "categorical": categorical_features,
            },
            "models": {},
        }

        lr_model, lr_metrics, lr_params = train_logistic_regression(
            train_df,
            test_df,
            numeric_features,
            categorical_features,
            args.random_state,
        )
        lr_run_id = f"lr_{uuid.uuid4().hex[:10]}"
        write_run_metadata(conn, lr_run_id, "logistic_regression", lr_params, "Patient-level split baseline")
        write_metrics(conn, lr_run_id, lr_metrics)
        results["models"]["logistic_regression"] = {"run_id": lr_run_id, "metrics": lr_metrics}

        if CatBoostClassifier is not None:
            cb_model, cb_metrics, cb_params = train_catboost(
                train_df,
                test_df,
                numeric_features,
                categorical_features,
                args.random_state,
            )
            cb_run_id = f"cat_{uuid.uuid4().hex[:10]}"
            write_run_metadata(conn, cb_run_id, "catboost", cb_params, "Patient-level split core model")
            write_metrics(conn, cb_run_id, cb_metrics)
            feature_cols = numeric_features + categorical_features
            X_test_cb = test_df[feature_cols].copy()
            for col in categorical_features:
                X_test_cb[col] = X_test_cb[col].fillna("missing").astype(str)
            for col in numeric_features:
                X_test_cb[col] = pd.to_numeric(X_test_cb[col], errors="coerce")
            cb_test_prob = cb_model.predict_proba(X_test_cb)[:, 1]
            cb_artifacts = {}
            try:
                cb_artifacts.update(
                    save_subgroup_artifacts(
                        test_df,
                        cb_test_prob,
                        artifacts_dir,
                        cb_run_id,
                        args.subgroup_min_rows,
                        args.subgroup_min_positives,
                    )
                )
                cb_artifacts.update(
                    save_catboost_artifacts(
                        cb_model,
                        test_df,
                        numeric_features,
                        categorical_features,
                        artifacts_dir,
                        cb_run_id,
                        args.shap_sample_size,
                    )
                )
            except Exception as exc:  # keep training result even if artefact generation fails
                cb_artifacts["artifact_error"] = str(exc)
            results["models"]["catboost"] = {"run_id": cb_run_id, "metrics": cb_metrics, "artifacts": cb_artifacts}
        else:
            results["models"]["catboost"] = {"status": "skipped", "reason": "catboost unavailable"}

        if LGBMClassifier is not None:
            lgbm_model, lgbm_metrics, lgbm_params = train_lightgbm(
                train_df,
                test_df,
                numeric_features,
                categorical_features,
                args.random_state,
            )
            lgbm_run_id = f"lgbm_{uuid.uuid4().hex[:10]}"
            write_run_metadata(conn, lgbm_run_id, "lightgbm", lgbm_params, "Patient-level split challenger model")
            write_metrics(conn, lgbm_run_id, lgbm_metrics)
            results["models"]["lightgbm"] = {"run_id": lgbm_run_id, "metrics": lgbm_metrics}
        else:
            results["models"]["lightgbm"] = {"status": "skipped", "reason": "lightgbm unavailable"}

        summary_path = save_run_summary(Path(args.output_dir), f"train_{uuid.uuid4().hex[:10]}", results)
        print(json.dumps(results, indent=2))
        print(f"Saved summary: {summary_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
