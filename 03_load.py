"""
03_load.py  -  Phase 3: Load clean data into PostgreSQL (Neon.tech)
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
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger(__name__)

PROCESSED_IN = "data/processed/students_clean.parquet"

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
    COUNT(*)                                        AS total_students,
    ROUND(AVG(mean_score)::NUMERIC, 2)              AS avg_score,
    ROUND(SUM(passed)::NUMERIC / COUNT(*) * 100, 1) AS pass_rate_pct,
    ROUND(AVG(attendance_pct)::NUMERIC, 1)          AS avg_attendance,
    SUM(low_attend)                                 AS low_attend_count
FROM student_results
GROUP BY county, year
ORDER BY avg_score DESC;
"""


def get_engine():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        db_url = "sqlite:///data/school_pipeline.db"
        log.warning("DATABASE_URL not set - using local SQLite")
    engine = create_engine(db_url.replace("postgresql://", "postgresql+psycopg://"), echo=False)
    host = db_url.split("@")[-1] if "@" in db_url else db_url
    log.info(f"Connected to: {host}")
    return engine


def clear_existing(engine):
    """Drop view and table with CASCADE so we can reload cleanly."""
    with engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS county_summary CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS student_results CASCADE"))
        conn.commit()
    log.info("Cleared existing tables")


def setup_schema(engine):
    with engine.connect() as conn:
        conn.execute(text(CREATE_STUDENTS_TABLE))
        conn.execute(text(CREATE_SUMMARY_VIEW))
        conn.commit()
    log.info("Schema ready")


def load_students(df: pd.DataFrame, engine):
    df.to_sql(
        name="student_results",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi",
    )
    log.info(f"Loaded {len(df):,} rows into student_results")


def verify_load(engine):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM student_results")).scalar()
    log.info(f"Verification: {result:,} rows in database")


def run():
    log.info("Loading processed data ...")
    df = pd.read_parquet(PROCESSED_IN)
    log.info(f"Shape: {df.shape}")

    engine = get_engine()
    clear_existing(engine)
    setup_schema(engine)
    load_students(df, engine)
    verify_load(engine)
    log.info("Load phase COMPLETE")


if __name__ == "__main__":
    run()
