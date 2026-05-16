"""
01_extract.py
=============
Phase 1 – EXTRACT
Reads raw student data from CSV (or a URL) and validates the schema.
Saves a staging Parquet file for the Transform phase.

Run:
    python 01_extract.py
"""

import os
import logging
import pandas as pd

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/extract.log", mode="a"),
    ],
)
log = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────
RAW_CSV     = "data/raw/kcse_students_2024.csv"
STAGING_OUT = "data/staging/raw_stage.parquet"

# ── Real public data URLs you can swap in ────────────────────────────────────
# Option A – UCI Student Performance (downloads automatically):
#   UCI_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00320/student.zip"
# Option B – Kenya Open Data (manual download needed, save to data/raw/):
#   https://opendata.go.ke  →  Education → KCSE Results

REQUIRED_COLUMNS = [
    "student_id", "name", "school", "county",
    "gender", "math", "english", "kiswahili",
    "biology", "chemistry", "attendance_pct", "year",
]


def extract_from_csv(path: str) -> pd.DataFrame:
    """Load raw student data from a local CSV file."""
    log.info(f"Reading raw data from: {path}")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Raw file not found: {path}\n"
            "Run  python 00_generate_data.py  first, or place your CSV there."
        )
    df = pd.read_csv(path, dtype={"student_id": str, "year": int})
    log.info(f"Loaded  {len(df):,} rows  ×  {len(df.columns)} columns")
    return df


def extract_from_url(url: str) -> pd.DataFrame:
    """Fetch CSV data directly from a URL."""
    log.info(f"Fetching remote data from: {url}")
    df = pd.read_csv(url, dtype={"student_id": str})
    log.info(f"Loaded  {len(df):,} rows  from URL")
    return df


def validate_schema(df: pd.DataFrame) -> bool:
    """Check all required columns are present."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        log.error(f"Schema validation FAILED – missing columns: {missing}")
        return False
    log.info("Schema validation PASSED ✓")
    return True


def profile_raw_data(df: pd.DataFrame) -> None:
    """Log a quick data quality snapshot."""
    nulls = df.isnull().sum()
    log.info("── Data Quality Snapshot ──────────────────────────────")
    log.info(f"  Rows          : {len(df):,}")
    log.info(f"  Columns       : {len(df.columns)}")
    log.info(f"  Duplicate IDs : {df['student_id'].duplicated().sum()}")
    log.info(f"  Null counts   :\n{nulls[nulls > 0].to_string()}")
    log.info(f"  Year range    : {df['year'].min()} – {df['year'].max()}")
    log.info("───────────────────────────────────────────────────────")


def run():
    os.makedirs("data/staging", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # ── Choose your data source here ─────────────────────────────────────────
    df = extract_from_csv(RAW_CSV)
    # df = extract_from_url("https://your-data-source.com/students.csv")

    if not validate_schema(df):
        raise ValueError("Stopping pipeline: schema validation failed.")

    profile_raw_data(df)

    df.to_parquet(STAGING_OUT, index=False)
    log.info(f"Saved staging file → {STAGING_OUT}")
    log.info("Extract phase COMPLETE ✓\n")


if __name__ == "__main__":
    run()
