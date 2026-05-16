"""
03_load.py
==========
Phase 3 – LOAD
Loads the clean student data into a PostgreSQL database.

Free cloud PostgreSQL options:
  • Neon.tech  → https://neon.tech     (512 MB free, serverless)
  • Supabase   → https://supabase.com  (500 MB free, full Postgres)

Set DATABASE_URL as an environment variable before running:
    export DATABASE_URL="postgresql://user:pass@host:5432/school_db"
    python 03_load.py

Or create a .env file (never commit to Git!):
    DATABASE_URL=postgresql://user:pass@...neon.tech/school_db?sslmode=require
"""

import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/load.log", mode="a"),
    ],
)
log = logging.getLogger(__name__)

PROCESSED_IN = "data/processed/students_clean.parquet"

# ── DDL for the main fact table ───────────────────────────────────────────────
CREATE_STUDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS student_results (
    student_id      VARCHAR(25)  PRIMARY KEY,
    name            VARCHAR(120),
    school          VARCHAR(120),
    county          VARCHAR(80),
    gender          CHAR(1),
    math            NUMERIC(5,2),
    english         NUMERIC(5,2),
    kiswahili       NUMERIC(5,2),
    biology         NUMERIC(5,2),
    chemistry       NUMERIC(5,2),
    attendance_pct  NUMERIC(5,2),
    mean_score      NUMERIC(5,2),
    grade           CHAR(1),
    passed          SMALLINT,
    low_attend      SMALLINT,
    year            SMALLINT,
    loaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_SUMMARY_VIEW = """
CREATE OR REPLACE VIEW county_summary AS
SELECT
    county,
    year,
    COUNT(*)                                    AS total_students,
    ROUND(AVG(mean_score)::NUMERIC, 2)          AS avg_score,
    ROUND(SUM(passed)::NUMERIC / COUNT(*) * 100, 1) AS pass_rate_pct,
    ROUND(AVG(attendance_pct)::NUMERIC, 1)      AS avg_attendance,
    SUM(low_attend)                             AS low_attend_count
FROM student_results
GROUP BY county, year
ORDER BY avg_score DESC;
"""


def get_engine():
    """Create SQLAlchemy engine from DATABASE_URL environment variable."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        # Fallback: local SQLite for development (no server needed)
        log.warning("DATABASE_URL not set – using local SQLite (dev mode)")
        db_url = "sqlite:///data/school_pipeline.db"
    engine = create_engine(db_url, echo=False)
    log.info(f"Connected to: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    return engine


def setup_schema(engine) -> None:
    """Create tables and views if they don't already exist."""
    with engine.connect() as conn:
        conn.execute(text(CREATE_STUDENTS_TABLE))
        # SQLite doesn't support CREATE OR REPLACE VIEW — wrap safely
        try:
            conn.execute(text(CREATE_SUMMARY_VIEW))
        except Exception:
            pass
        conn.commit()
    log.info("Schema ready ✓")


def load_students(df: pd.DataFrame, engine) -> None:
    """Write clean data to the database (replace full load each run)."""
    df.to_sql(
        name="student_results",
        con=engine,
        if_exists="replace",   # ← change to "append" for incremental loads
        index=False,
        chunksize=500,
        method="multi",
    )
    log.info(f"Loaded {len(df):,} rows into student_results ✓")


def verify_load(engine) -> None:
    """Run a quick count to confirm the load succeeded."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM student_results")).scalar()
    log.info(f"Verification: {result:,} rows found in student_results ✓")


def run():
    os.makedirs("logs", exist_ok=True)

    log.info("Loading processed data …")
    df = pd.read_parquet(PROCESSED_IN)
    log.info(f"Shape: {df.shape}")

    engine = get_engine()
    setup_schema(engine)
    load_students(df, engine)
    verify_load(engine)

    log.info("Load phase COMPLETE ✓\n")


if __name__ == "__main__":
    run()
