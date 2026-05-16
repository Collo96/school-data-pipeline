"""
02_transform.py
===============
Phase 2 – TRANSFORM
Clean, enrich, and validate the raw student data:
  • Fill missing subject scores with school-level medians
  • Compute mean_score, KCSE grade, pass/fail flag
  • Standardise string columns
  • Remove duplicate and out-of-range records

Run:
    python 02_transform.py
"""

import logging
import pandas as pd
import numpy as np
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/transform.log", mode="a"),
    ],
)
log = logging.getLogger(__name__)

STAGING_IN  = "data/staging/raw_stage.parquet"
PROCESSED_OUT = "data/processed/students_clean.parquet"

SUBJECTS = ["math", "english", "kiswahili", "biology", "chemistry"]
VALID_YEARS = (2020, 2024)


# ── Transformation steps ─────────────────────────────────────────────────────

def standardise_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and normalise case for string columns."""
    df["county"] = df["county"].str.strip().str.title()
    df["school"] = df["school"].str.strip().str.title()
    df["gender"] = df["gender"].str.strip().str.upper()
    df["name"]   = df["name"].str.strip().str.title()
    log.info("String standardisation done ✓")
    return df


def fill_missing_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute NULL subject scores using the SCHOOL-LEVEL median.
    This preserves local academic context better than a global median.
    Falls back to county median if the school has no valid values.
    """
    null_before = df[SUBJECTS].isnull().sum().sum()
    for subj in SUBJECTS:
        # School-level median
        df[subj] = df.groupby("school")[subj].transform(
            lambda x: x.fillna(x.median())
        )
        # County-level fallback for any remaining NULLs
        df[subj] = df.groupby("county")[subj].transform(
            lambda x: x.fillna(x.median())
        )
    null_after = df[SUBJECTS].isnull().sum().sum()
    log.info(f"Null imputation: {null_before} → {null_after} missing values")
    return df


def clip_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Clip scores to valid range [0, 100]."""
    for subj in SUBJECTS:
        df[subj] = df[subj].clip(0, 100)
    log.info("Score clipping to [0, 100] done ✓")
    return df


def compute_mean_score(df: pd.DataFrame) -> pd.DataFrame:
    """Add mean_score: average of all five subjects."""
    df["mean_score"] = df[SUBJECTS].mean(axis=1).round(2)
    return df


def assign_grade(score: float) -> str:
    """KCSE-style grade from A (≥75) to E (<40)."""
    if score >= 75: return "A"
    elif score >= 60: return "B"
    elif score >= 50: return "C"
    elif score >= 40: return "D"
    else:            return "E"


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add grade, passed flag, and low-attendance flag."""
    df["grade"]      = df["mean_score"].apply(assign_grade)
    df["passed"]     = (df["mean_score"] >= 50).astype(int)
    df["low_attend"] = (df["attendance_pct"] < 80).astype(int)
    log.info("Derived columns added: grade, passed, low_attend ✓")
    return df


def remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicates and records with out-of-range year."""
    before = len(df)
    df = df.drop_duplicates(subset="student_id")
    df = df[df["year"].between(*VALID_YEARS)]
    df = df[df["gender"].isin(["M", "F"])]
    after = len(df)
    log.info(f"Row filter: {before:,} → {after:,} (removed {before - after:,})")
    return df


def quality_check(df: pd.DataFrame) -> None:
    """Final quality gate before saving."""
    assert df.isnull().sum().sum() == 0,  "Still has nulls after transform!"
    assert df["mean_score"].between(0, 100).all(), "mean_score out of range!"
    assert df["student_id"].is_unique, "Duplicate student_ids found!"
    log.info("Quality checks PASSED ✓")


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    os.makedirs("data/processed", exist_ok=True)

    log.info("Loading staging data …")
    df = pd.read_parquet(STAGING_IN)
    log.info(f"Input shape: {df.shape}")

    df = standardise_strings(df)
    df = fill_missing_scores(df)
    df = clip_scores(df)
    df = compute_mean_score(df)
    df = add_derived_columns(df)
    df = remove_invalid_rows(df)

    quality_check(df)

    df.to_parquet(PROCESSED_OUT, index=False)
    log.info(f"Clean data saved → {PROCESSED_OUT}")
    log.info(f"Final shape      : {df.shape}")
    log.info(f"Grade breakdown  :\n{df['grade'].value_counts().sort_index().to_string()}")
    log.info(f"Pass rate        : {df['passed'].mean()*100:.1f}%")
    log.info("Transform phase COMPLETE ✓\n")


if __name__ == "__main__":
    run()
