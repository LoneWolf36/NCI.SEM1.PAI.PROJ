"""CMS ESRD multi-table ingestion pipeline.

Assignment fit:
- 4 structured datasets
- datasets stored in SQLite before processing
- cleaned tables + derived modelling tables stored back in SQLite

Main workflow:
1. download CMS ESRD Population PUF ZIP files
2. ingest raw CSVs into SQLite in chunks
3. create cleaned tables
4. derive 30-day readmission target from hospitalization events
5. join patient / treatment / adequacy features into a modelling mart

Default run ingests full tables. Use --sample-rows for smoke tests.
"""

from __future__ import annotations

import argparse
import sqlite3
import time
import zipfile
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


DB_PATH = Path("dialysis_readmission.db")
DOWNLOAD_DIR = Path("data") / "downloads"
CHUNK_SIZE = 100_000
USER_AGENT = "Mozilla/5.0 (compatible; PAI-project-bot/1.0)"


DATASETS = {
    "patient_summary": {
        "url": "https://downloads.cms.gov/files/patient_summary.zip",
        "raw_table": "raw_patient_summary",
    },
    "admit_treatment": {
        "url": "https://downloads.cms.gov/files/admit_treatment.zip",
        "raw_table": "raw_admit_treatment",
    },
    "cl_hospitalization": {
        "url": "https://downloads.cms.gov/files/cl_hospitalization.zip",
        "raw_table": "raw_cl_hospitalization",
    },
    "cl_hd_adqcy": {
        "url": "https://downloads.cms.gov/files/cl_hd_adqcy.zip",
        "raw_table": "raw_cl_hd_adqcy",
    },
}


def download_file(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0 and zipfile.is_zipfile(destination):
        print(f"Using cached download: {destination}")
        return destination

    temp_path = destination.with_suffix(destination.suffix + ".part")

    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            existing_bytes = temp_path.stat().st_size if temp_path.exists() else 0
            headers = {"User-Agent": USER_AGENT}
            if existing_bytes > 0:
                headers["Range"] = f"bytes={existing_bytes}-"

            print(
                f"Downloading {url} -> {destination} (attempt {attempt}/3, resume_bytes={existing_bytes:,})"
            )
            with requests.get(
                url,
                headers=headers,
                stream=True,
                timeout=(30, 1800),
            ) as response:
                response.raise_for_status()
                append_mode = existing_bytes > 0 and response.status_code == 206
                if existing_bytes > 0 and response.status_code == 200:
                    temp_path.unlink(missing_ok=True)
                mode = "ab" if append_mode else "wb"
                with temp_path.open(mode) as handle:
                    for chunk in response.iter_content(chunk_size=256 * 1024):
                        if chunk:
                            handle.write(chunk)

            if not zipfile.is_zipfile(temp_path):
                raise ValueError(f"Downloaded file is not a valid ZIP: {temp_path}")

            temp_path.replace(destination)
            return destination
        except Exception as exc:  # retry on transient network failures
            last_error = exc
            if attempt < 3:
                time.sleep(3 * attempt)
            else:
                raise

    if last_error:
        raise last_error
    return destination


def normalize_columns(columns: Iterable[str]) -> list[str]:
    return [
        col.strip()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("__", "_")
        .lower()
        for col in columns
    ]


def ingest_zip_csv_to_sql(
    conn: sqlite3.Connection,
    zip_path: Path,
    table_name: str,
    sample_rows: int | None = None,
) -> int:
    print(f"Ingesting {zip_path.name} -> {table_name}")
    total_rows = 0
    first = True

    reader = pd.read_csv(
        zip_path,
        compression="zip",
        dtype=str,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    )

    for chunk in reader:
        chunk.columns = normalize_columns(chunk.columns)
        if sample_rows is not None:
            remaining = sample_rows - total_rows
            if remaining <= 0:
                break
            chunk = chunk.iloc[:remaining].copy()

        total_rows += len(chunk)
        chunk.to_sql(table_name, conn, if_exists="replace" if first else "append", index=False)
        first = False
        print(f"  rows ingested: {total_rows:,}")

        if sample_rows is not None and total_rows >= sample_rows:
            break

    return total_rows


def table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    pragma = pd.read_sql_query(f"PRAGMA table_info({table_name})", conn)
    return set(pragma["name"].tolist())


def create_indexes(conn: sqlite3.Connection) -> None:
    statements = [
        "CREATE INDEX IF NOT EXISTS idx_raw_patient_summary_pat_id ON raw_patient_summary(pat_id)",
        "CREATE INDEX IF NOT EXISTS idx_raw_admit_treatment_pat_id ON raw_admit_treatment(pat_id)",
        "CREATE INDEX IF NOT EXISTS idx_raw_admit_treatment_prov_nbr ON raw_admit_treatment(prov_nbr)",
        "CREATE INDEX IF NOT EXISTS idx_raw_cl_hospitalization_pat_id ON raw_cl_hospitalization(pat_id)",
        "CREATE INDEX IF NOT EXISTS idx_raw_cl_hospitalization_prov_nbr ON raw_cl_hospitalization(prov_nbr)",
        "CREATE INDEX IF NOT EXISTS idx_raw_cl_hd_adqcy_pat_id ON raw_cl_hd_adqcy(pat_id)",
        "CREATE INDEX IF NOT EXISTS idx_raw_cl_hd_adqcy_prov_nbr ON raw_cl_hd_adqcy(prov_nbr)",
    ]
    for statement in statements:
        conn.execute(statement)
    conn.commit()


def create_clean_tables(conn: sqlite3.Connection) -> None:
    print("Creating clean tables")

    conn.executescript(
        """
        DROP TABLE IF EXISTS clean_patient_summary;
        CREATE TABLE clean_patient_summary AS
        SELECT
            TRIM(pat_id) AS pat_id,
            NULLIF(TRIM(state), '') AS state,
            NULLIF(TRIM(age_range), '') AS age_range,
            NULLIF(TRIM(race), '') AS race,
            NULLIF(TRIM(gender), '') AS gender,
            NULLIF(TRIM(ethnicity), '') AS ethnicity,
            NULLIF(TRIM(primdiag), '') AS primdiag,
            NULLIF(TRIM(primcause), '') AS primcause,
            NULLIF(TRIM(netnumb), '') AS netnumb
        FROM raw_patient_summary
        WHERE NULLIF(TRIM(pat_id), '') IS NOT NULL;

        DROP TABLE IF EXISTS clean_admit_treatment;
        CREATE TABLE clean_admit_treatment AS
        SELECT
            TRIM(pat_id) AS pat_id,
            printf('%06d', CAST(TRIM(prov_nbr) AS INTEGER)) AS prov_nbr,
            CAST(NULLIF(TRIM(admit_date), '') AS INTEGER) AS admit_date,
            NULLIF(TRIM(admit_reason), '') AS admit_reason,
            CAST(NULLIF(TRIM(discharge_date), '') AS INTEGER) AS discharge_date,
            NULLIF(TRIM(discharge_reason), '') AS discharge_reason,
            CAST(NULLIF(TRIM(treatment_start_date), '') AS INTEGER) AS treatment_start_date,
            NULLIF(TRIM(dialysis_setting), '') AS dialysis_setting,
            NULLIF(TRIM(treatment_type), '') AS treatment_type,
            NULLIF(TRIM(sessions_per_week), '') AS sessions_per_week,
            NULLIF(TRIM(dialysis_type), '') AS dialysis_type,
            NULLIF(TRIM(modality), '') AS modality,
            COALESCE(
                CAST(NULLIF(TRIM(treatment_start_date), '') AS INTEGER),
                CAST(NULLIF(TRIM(admit_date), '') AS INTEGER),
                CAST(NULLIF(TRIM(discharge_date), '') AS INTEGER)
            ) AS treatment_event_date
        FROM raw_admit_treatment
        WHERE NULLIF(TRIM(pat_id), '') IS NOT NULL;

        DROP TABLE IF EXISTS clean_cl_hospitalization;
        CREATE TABLE clean_cl_hospitalization AS
        SELECT
            TRIM(pat_id) AS pat_id,
            printf('%06d', CAST(TRIM(prov_nbr) AS INTEGER)) AS prov_nbr,
            CAST(NULLIF(TRIM(clinical_month_year), '') AS INTEGER) AS clinical_month_year,
            NULLIF(TRIM(modality), '') AS modality,
            NULLIF(TRIM(hospitalizations), '') AS hospitalization_type,
            CAST(NULLIF(TRIM(hospital_admit_date), '') AS INTEGER) AS hospital_admit_date,
            CAST(NULLIF(TRIM(hospital_discharge_date), '') AS INTEGER) AS hospital_discharge_date,
            NULLIF(TRIM(hospital_discharge_diag), '') AS hospital_discharge_diag,
            NULLIF(TRIM(hospital_admit_diag), '') AS hospital_admit_diag,
            CAST(NULLIF(TRIM(length_of_stay), '') AS INTEGER) AS length_of_stay,
            LOWER(NULLIF(TRIM(facility2hospital), '')) AS facility_to_hospital,
            LOWER(NULLIF(TRIM(advanced_directives), '')) AS advanced_directives,
            LOWER(NULLIF(TRIM(transplant_referral), '')) AS transplant_referral,
            LOWER(NULLIF(TRIM(transplant_wait_list), '')) AS transplant_wait_list,
            LOWER(NULLIF(TRIM(presump_diag2hospitalization), '')) AS presumptive_diag_to_hospitalization
        FROM raw_cl_hospitalization
        WHERE NULLIF(TRIM(pat_id), '') IS NOT NULL;
        """
    )

    hd_cols = table_columns(conn, "raw_cl_hd_adqcy")
    select_parts = [
        "TRIM(pat_id) AS pat_id",
        "printf('%06d', CAST(TRIM(prov_nbr) AS INTEGER)) AS prov_nbr",
    ]

    optional_map = {
        "clncl_mo_yr": "CAST(NULLIF(TRIM(clncl_mo_yr), '') AS INTEGER) AS clncl_mo_yr",
        "clinical_month_year": "CAST(NULLIF(TRIM(clinical_month_year), '') AS INTEGER) AS clncl_mo_yr",
        "modality": "NULLIF(TRIM(modality), '') AS modality",
        "hd_ktv": "CAST(NULLIF(TRIM(hd_ktv), '') AS REAL) AS hd_ktv",
        "hd_ktv_coll_date": "CAST(NULLIF(TRIM(hd_ktv_coll_date), '') AS INTEGER) AS hd_ktv_coll_date",
        "hd_ktv_method": "NULLIF(TRIM(hd_ktv_method), '') AS hd_ktv_method",
        "hd_weight_pre": "CAST(NULLIF(TRIM(hd_weight_pre), '') AS REAL) AS hd_weight_pre",
        "hd_weight_pre_uom": "NULLIF(TRIM(hd_weight_pre_uom), '') AS hd_weight_pre_uom",
    }
    for col, expression in optional_map.items():
        if col in hd_cols:
            select_parts.append(expression)

    conn.execute("DROP TABLE IF EXISTS clean_cl_hd_adqcy")
    conn.execute(
        f"""
        CREATE TABLE clean_cl_hd_adqcy AS
        SELECT
            {', '.join(select_parts)}
        FROM raw_cl_hd_adqcy
        WHERE NULLIF(TRIM(pat_id), '') IS NOT NULL
        """
    )

    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_clean_patient_summary_pat_id ON clean_patient_summary(pat_id);
        CREATE INDEX IF NOT EXISTS idx_clean_admit_treatment_pat_id ON clean_admit_treatment(pat_id);
        CREATE INDEX IF NOT EXISTS idx_clean_admit_treatment_pat_prov ON clean_admit_treatment(pat_id, prov_nbr);
        CREATE INDEX IF NOT EXISTS idx_clean_admit_treatment_pat_event_date ON clean_admit_treatment(pat_id, treatment_event_date);
        CREATE INDEX IF NOT EXISTS idx_clean_cl_hospitalization_pat_id ON clean_cl_hospitalization(pat_id);
        CREATE INDEX IF NOT EXISTS idx_clean_cl_hospitalization_pat_prov ON clean_cl_hospitalization(pat_id, prov_nbr);
        CREATE INDEX IF NOT EXISTS idx_clean_cl_hd_adqcy_pat_id ON clean_cl_hd_adqcy(pat_id);
        CREATE INDEX IF NOT EXISTS idx_clean_cl_hd_adqcy_pat_prov ON clean_cl_hd_adqcy(pat_id, prov_nbr);
        CREATE INDEX IF NOT EXISTS idx_clean_cl_hd_adqcy_pat_month ON clean_cl_hd_adqcy(pat_id, clncl_mo_yr);
        """
    )
    conn.commit()


def derive_readmission_events(conn: sqlite3.Connection) -> None:
    print("Deriving readmission events")
    conn.executescript(
        """
        DROP TABLE IF EXISTS derived_readmission_events;
        CREATE TABLE derived_readmission_events AS
        WITH ordered AS (
            SELECT
                pat_id,
                prov_nbr,
                clinical_month_year,
                modality,
                hospitalization_type,
                hospital_admit_date,
                hospital_discharge_date,
                hospital_admit_diag,
                hospital_discharge_diag,
                length_of_stay,
                LEAD(hospital_admit_date) OVER (
                    PARTITION BY pat_id
                    ORDER BY hospital_admit_date, hospital_discharge_date, prov_nbr
                ) AS next_hospital_admit_date,
                LAG(hospital_discharge_date) OVER (
                    PARTITION BY pat_id
                    ORDER BY hospital_admit_date, hospital_discharge_date, prov_nbr
                ) AS previous_hospital_discharge_date,
                ROW_NUMBER() OVER (
                    PARTITION BY pat_id
                    ORDER BY hospital_admit_date, hospital_discharge_date, prov_nbr
                ) AS hospitalization_sequence
            FROM clean_cl_hospitalization
            WHERE hospital_admit_date IS NOT NULL
              AND hospital_discharge_date IS NOT NULL
        )
        SELECT
            *,
            next_hospital_admit_date - hospital_discharge_date AS gap_to_next_admit_days,
            hospital_admit_date - previous_hospital_discharge_date AS gap_from_previous_discharge_days,
            CASE
                WHEN next_hospital_admit_date IS NOT NULL
                 AND (next_hospital_admit_date - hospital_discharge_date) BETWEEN 0 AND 30 THEN 1
                ELSE 0
            END AS readmitted_30d
        FROM ordered;

        CREATE INDEX IF NOT EXISTS idx_derived_readmission_pat_id ON derived_readmission_events(pat_id);
        CREATE INDEX IF NOT EXISTS idx_derived_readmission_target ON derived_readmission_events(readmitted_30d);
        """
    )
    conn.commit()


def derive_patient_features(conn: sqlite3.Connection) -> None:
    print("Deriving patient-level feature aggregates")
    conn.executescript(
        """
        DROP TABLE IF EXISTS derived_patient_features;
        CREATE TABLE derived_patient_features AS
        WITH treatment AS (
            SELECT
                pat_id,
                MAX(CASE WHEN lower(COALESCE(dialysis_type, '')) LIKE '%hemo%' THEN 1 ELSE 0 END) AS ever_hemodialysis,
                MAX(CASE WHEN lower(COALESCE(modality, '')) LIKE '%center%' OR lower(COALESCE(modality, '')) LIKE '%hemo%' THEN 1 ELSE 0 END) AS ever_center_hemo,
                COUNT(*) AS treatment_records,
                MIN(treatment_start_date) AS first_treatment_start_date,
                MAX(treatment_start_date) AS last_treatment_start_date
            FROM clean_admit_treatment
            GROUP BY pat_id
        ),
        adequacy AS (
            SELECT
                pat_id,
                AVG(hd_ktv) AS mean_hd_ktv,
                MIN(hd_ktv) AS min_hd_ktv,
                MAX(hd_ktv) AS max_hd_ktv,
                COUNT(hd_ktv) AS hd_ktv_measurements
            FROM clean_cl_hd_adqcy
            GROUP BY pat_id
        ),
        hospital AS (
            SELECT
                pat_id,
                COUNT(*) AS hospitalization_count,
                AVG(length_of_stay) AS mean_length_of_stay,
                MAX(length_of_stay) AS max_length_of_stay,
                AVG(readmitted_30d) AS patient_readmit_30d_rate
            FROM derived_readmission_events
            GROUP BY pat_id
        )
        SELECT
            p.pat_id,
            p.state,
            p.age_range,
            p.race,
            p.gender,
            p.ethnicity,
            p.primdiag,
            p.primcause,
            p.netnumb,
            t.ever_hemodialysis,
            t.ever_center_hemo,
            t.treatment_records,
            t.first_treatment_start_date,
            t.last_treatment_start_date,
            a.mean_hd_ktv,
            a.min_hd_ktv,
            a.max_hd_ktv,
            a.hd_ktv_measurements,
            h.hospitalization_count,
            h.mean_length_of_stay,
            h.max_length_of_stay,
            h.patient_readmit_30d_rate
        FROM clean_patient_summary p
        LEFT JOIN treatment t USING (pat_id)
        LEFT JOIN adequacy a USING (pat_id)
        LEFT JOIN hospital h USING (pat_id);

        CREATE INDEX IF NOT EXISTS idx_derived_patient_features_pat_id ON derived_patient_features(pat_id);
        """
    )
    conn.commit()


def create_model_feature_mart(conn: sqlite3.Connection) -> None:
    print("Creating model feature mart")
    conn.executescript(
        """
        DROP TABLE IF EXISTS model_feature_mart;
        CREATE TABLE model_feature_mart AS
        SELECT
            e.pat_id,
            e.prov_nbr,
            e.hospitalization_sequence,
            e.clinical_month_year,
            e.modality AS hospitalization_modality,
            e.hospitalization_type,
            e.hospital_admit_date,
            e.hospital_discharge_date,
            e.hospital_admit_diag,
            e.hospital_discharge_diag,
            e.length_of_stay,
            e.gap_from_previous_discharge_days,
            e.gap_to_next_admit_days,
            e.readmitted_30d,
            CASE WHEN e.hospitalization_sequence > 1 THEN e.hospitalization_sequence - 1 ELSE 0 END AS prior_hospitalizations,
            (
                SELECT COUNT(*)
                FROM derived_readmission_events h
                WHERE h.pat_id = e.pat_id
                  AND h.hospital_discharge_date IS NOT NULL
                  AND h.hospital_discharge_date < e.hospital_admit_date
                  AND h.hospital_discharge_date >= e.hospital_admit_date - 30
            ) AS prior_30d_hospitalizations,
            (
                SELECT COUNT(*)
                FROM derived_readmission_events h
                WHERE h.pat_id = e.pat_id
                  AND h.hospital_discharge_date IS NOT NULL
                  AND h.hospital_discharge_date < e.hospital_admit_date
                  AND h.hospital_discharge_date >= e.hospital_admit_date - 180
            ) AS prior_180d_hospitalizations,
            p.state,
            p.age_range,
            p.race,
            p.gender,
            p.ethnicity,
            p.primdiag,
            p.primcause,
            (
                SELECT COUNT(*)
                FROM clean_admit_treatment t
                WHERE t.pat_id = e.pat_id
                  AND t.treatment_event_date IS NOT NULL
                  AND t.treatment_event_date <= e.hospital_discharge_date
            ) AS prior_treatment_records,
            (
                SELECT COUNT(*)
                FROM clean_admit_treatment t
                WHERE t.pat_id = e.pat_id
                  AND t.treatment_event_date IS NOT NULL
                  AND t.treatment_event_date < e.hospital_admit_date
                  AND t.treatment_event_date >= e.hospital_admit_date - 30
            ) AS recent_30d_treatment_records,
            (
                SELECT COUNT(*)
                FROM clean_admit_treatment t
                WHERE t.pat_id = e.pat_id
                  AND t.treatment_event_date IS NOT NULL
                  AND t.treatment_event_date < e.hospital_admit_date
                  AND t.treatment_event_date >= e.hospital_admit_date - 90
            ) AS recent_90d_treatment_records,
            (
                SELECT e.hospital_admit_date - MAX(t.treatment_event_date)
                FROM clean_admit_treatment t
                WHERE t.pat_id = e.pat_id
                  AND t.treatment_event_date IS NOT NULL
                  AND t.treatment_event_date < e.hospital_admit_date
            ) AS days_since_last_treatment,
            (
                SELECT MAX(CASE WHEN lower(COALESCE(t.dialysis_type, '')) LIKE '%hemo%' THEN 1 ELSE 0 END)
                FROM clean_admit_treatment t
                WHERE t.pat_id = e.pat_id
                  AND t.treatment_event_date IS NOT NULL
                  AND t.treatment_event_date <= e.hospital_discharge_date
            ) AS prior_hemodialysis_flag,
            (
                SELECT MAX(
                    CASE
                        WHEN lower(COALESCE(t.modality, '')) LIKE '%center%'
                          OR lower(COALESCE(t.modality, '')) LIKE '%hemo%'
                        THEN 1 ELSE 0
                    END
                )
                FROM clean_admit_treatment t
                WHERE t.pat_id = e.pat_id
                  AND t.treatment_event_date IS NOT NULL
                  AND t.treatment_event_date <= e.hospital_discharge_date
            ) AS prior_center_hemo_flag,
            (
                SELECT a.hd_ktv
                FROM clean_cl_hd_adqcy a
                WHERE a.pat_id = e.pat_id
                  AND a.clncl_mo_yr IS NOT NULL
                  AND e.clinical_month_year IS NOT NULL
                  AND a.clncl_mo_yr <= e.clinical_month_year
                  AND a.hd_ktv IS NOT NULL
                ORDER BY a.clncl_mo_yr DESC
                LIMIT 1
            ) AS recent_hd_ktv,
            (
                SELECT AVG(a.hd_ktv)
                FROM clean_cl_hd_adqcy a
                WHERE a.pat_id = e.pat_id
                  AND a.clncl_mo_yr IS NOT NULL
                  AND e.clinical_month_year IS NOT NULL
                  AND a.clncl_mo_yr <= e.clinical_month_year
                  AND a.hd_ktv IS NOT NULL
            ) AS mean_prior_hd_ktv,
            (
                SELECT AVG(a.hd_ktv)
                FROM clean_cl_hd_adqcy a
                WHERE a.pat_id = e.pat_id
                  AND a.clncl_mo_yr IS NOT NULL
                  AND e.clinical_month_year IS NOT NULL
                  AND (
                        (CAST(e.clinical_month_year / 100 AS INTEGER) * 12 + (e.clinical_month_year % 100))
                      - (CAST(a.clncl_mo_yr / 100 AS INTEGER) * 12 + (a.clncl_mo_yr % 100))
                  ) BETWEEN 0 AND 2
                  AND a.hd_ktv IS NOT NULL
            ) AS recent_3m_hd_ktv_mean,
            (
                SELECT MAX(a.hd_ktv) - MIN(a.hd_ktv)
                FROM clean_cl_hd_adqcy a
                WHERE a.pat_id = e.pat_id
                  AND a.clncl_mo_yr IS NOT NULL
                  AND e.clinical_month_year IS NOT NULL
                  AND (
                        (CAST(e.clinical_month_year / 100 AS INTEGER) * 12 + (e.clinical_month_year % 100))
                      - (CAST(a.clncl_mo_yr / 100 AS INTEGER) * 12 + (a.clncl_mo_yr % 100))
                  ) BETWEEN 0 AND 5
                  AND a.hd_ktv IS NOT NULL
            ) AS recent_6m_hd_ktv_range,
            (
                (
                    SELECT AVG(a.hd_ktv)
                    FROM clean_cl_hd_adqcy a
                    WHERE a.pat_id = e.pat_id
                      AND a.clncl_mo_yr IS NOT NULL
                      AND e.clinical_month_year IS NOT NULL
                      AND (
                            (CAST(e.clinical_month_year / 100 AS INTEGER) * 12 + (e.clinical_month_year % 100))
                          - (CAST(a.clncl_mo_yr / 100 AS INTEGER) * 12 + (a.clncl_mo_yr % 100))
                      ) BETWEEN 0 AND 2
                      AND a.hd_ktv IS NOT NULL
                )
                -
                (
                    SELECT AVG(a.hd_ktv)
                    FROM clean_cl_hd_adqcy a
                    WHERE a.pat_id = e.pat_id
                      AND a.clncl_mo_yr IS NOT NULL
                      AND e.clinical_month_year IS NOT NULL
                      AND a.clncl_mo_yr <= e.clinical_month_year
                      AND a.hd_ktv IS NOT NULL
                )
            ) AS hd_ktv_recent_vs_history_delta,
            (
                SELECT COUNT(a.hd_ktv)
                FROM clean_cl_hd_adqcy a
                WHERE a.pat_id = e.pat_id
                  AND a.clncl_mo_yr IS NOT NULL
                  AND e.clinical_month_year IS NOT NULL
                  AND a.clncl_mo_yr <= e.clinical_month_year
                  AND a.hd_ktv IS NOT NULL
            ) AS prior_hd_ktv_measurements
        FROM derived_readmission_events e
        LEFT JOIN clean_patient_summary p USING (pat_id)
        WHERE e.hospital_admit_date IS NOT NULL
          AND e.hospital_discharge_date IS NOT NULL;

        CREATE INDEX IF NOT EXISTS idx_model_feature_mart_target ON model_feature_mart(readmitted_30d);
        CREATE INDEX IF NOT EXISTS idx_model_feature_mart_pat_id ON model_feature_mart(pat_id);
        """
    )
    conn.commit()


def create_tracking_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS model_runs (
            run_id TEXT,
            model_name TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS evaluation_metrics (
            run_id TEXT,
            split TEXT,
            auc REAL,
            accuracy REAL,
            precision REAL,
            recall REAL,
            f1 REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS figure_registry (
            figure_name TEXT,
            file_path TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()


def print_verification(conn: sqlite3.Connection) -> None:
    print("\nVerification summary")
    table_counts = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
        conn,
    )
    for table_name in table_counts["name"]:
        count = pd.read_sql_query(f"SELECT COUNT(*) AS n FROM {table_name}", conn).iloc[0]["n"]
        print(f"  {table_name}: {count:,}")

    if "derived_readmission_events" in table_counts["name"].tolist():
        stats = pd.read_sql_query(
            """
            SELECT
                COUNT(*) AS rows_total,
                AVG(readmitted_30d) AS readmit_rate,
                SUM(CASE WHEN gap_to_next_admit_days BETWEEN 0 AND 30 THEN 1 ELSE 0 END) AS positive_rows
            FROM derived_readmission_events
            """,
            conn,
        )
        print("\nDerived target stats")
        print(stats.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest CMS ESRD datasets into SQLite")
    parser.add_argument("--db-path", default=str(DB_PATH), help="SQLite database path")
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=None,
        help="Ingest only the first N rows from each dataset for smoke testing",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Use already downloaded ZIP files from data/downloads",
    )
    parser.add_argument(
        "--rebuild-derived-only",
        action="store_true",
        help="Skip download/raw ingest and rebuild derived tables from existing clean tables",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = Path(args.db_path)
    conn = sqlite3.connect(db_path)

    try:
        if not args.rebuild_derived_only:
            for dataset_name, config in DATASETS.items():
                zip_path = DOWNLOAD_DIR / f"{dataset_name}.zip"
                if not args.skip_download:
                    download_file(config["url"], zip_path)
                elif not zip_path.exists():
                    raise FileNotFoundError(f"Missing cached file: {zip_path}")

                ingest_zip_csv_to_sql(
                    conn=conn,
                    zip_path=zip_path,
                    table_name=config["raw_table"],
                    sample_rows=args.sample_rows,
                )

            create_indexes(conn)
            create_clean_tables(conn)

        derive_readmission_events(conn)
        derive_patient_features(conn)
        create_model_feature_mart(conn)
        create_tracking_tables(conn)
        print_verification(conn)
        print(f"\nPipeline complete. Database saved to: {db_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
