"""
00_generate_data.py
===================
Generates synthetic but realistic KCSE-style student performance data
for secondary school data engineering practice.

Data Source Options (real, free):
  1. Kenya Open Data Portal  → https://opendata.go.ke  (Education section)
  2. UCI Student Performance → https://archive.ics.uci.edu/dataset/320
  3. Kaggle Student Exams    → https://www.kaggle.com/datasets/whenamancodes/student-performance
  4. This script             → generates a realistic synthetic dataset

Usage:
    python 00_generate_data.py
    # Creates: data/raw/kcse_students_2024.csv
"""

import pandas as pd
import numpy as np
import random
import os

# ── Seed for reproducibility ────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

N_STUDENTS = 5_000

# ── Kenyan counties and sample schools ──────────────────────────────────────
COUNTIES_SCHOOLS = {
    "Nyeri":      ["Alliance High", "Nyeri High", "Tetu Girls"],
    "Nairobi":    ["Nairobi School", "Kenya High", "Upper Hill", "Starehe Boys"],
    "Kiambu":     ["Thika High", "Kiambu High", "Chania Girls"],
    "Meru":       ["Meru High", "Mt Kenya Academy", "Nkubu High"],
    "Kisumu":     ["Kisumu Boys", "Kisumu Girls", "Lwak Girls"],
    "Mombasa":    ["Coast High", "Shimba Hills", "Shimo la Tewa"],
    "Nakuru":     ["Nakuru High", "Rift Valley Academy", "Menengai High"],
    "Kakamega":   ["Kakamega High", "St. Peters", "Butere Girls"],
    "Machakos":   ["Machakos Boys", "St. Josephs", "Mbooni Girls"],
    "Bomet":      ["St. Patricks Iten", "Bomet High"],
    "Embu":       ["Embu High", "St. Marys Kibiri"],
    "Kilifi":     ["Kilifi High", "Bahari Girls"],
}

# ── Kenyan first names ───────────────────────────────────────────────────────
MALE_NAMES   = ["Kamau","Mwangi","Kipchoge","Mutua","Otieno","Omondi",
                "Kariuki","Njoroge","Koech","Cheruiyot","Baraza","Wafula",
                "Simiyu","Juma","Limo","Ndirangu","Gitahi","Irungu"]
FEMALE_NAMES = ["Wanjiku","Achieng","Chebet","Njeri","Wambui","Atieno",
                "Moraa","Nyambura","Cheptoo","Jebet","Nekesa","Wasike",
                "Adhiambo","Muthoni","Wangari","Chelangat"]
SURNAMES     = ["Mwangi","Kamau","Njoroge","Otieno","Koech","Mutua",
                "Omondi","Wafula","Kariuki","Kipchoge","Juma","Limo","Baraza"]

SUBJECTS = ["math","english","kiswahili","biology","chemistry"]


def school_performance_mean(school: str) -> float:
    """Top schools score higher on average."""
    top_schools = {"Alliance High","Kenya High","Nairobi School","Starehe Boys",
                   "Nyeri High","Meru High","St. Patricks Iten"}
    return 72.0 if school in top_schools else 58.0


def generate_scores(mean: float, n_subjects: int = 5) -> list:
    """Generate correlated subject scores centred on a student mean."""
    student_ability = np.random.normal(mean, 10)
    scores = []
    for _ in range(n_subjects):
        raw = student_ability + np.random.normal(0, 8)
        scores.append(float(np.clip(raw, 20, 100).round(1)))
    return scores


def inject_nulls(scores: list, null_prob: float = 0.04) -> list:
    """Randomly set some scores to None to simulate missing data."""
    return [None if random.random() < null_prob else s for s in scores]


def generate_dataset(n: int = N_STUDENTS) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        gender = random.choice(["M", "F"])
        fname  = random.choice(MALE_NAMES if gender == "M" else FEMALE_NAMES)
        sname  = random.choice(SURNAMES)
        county = random.choice(list(COUNTIES_SCHOOLS.keys()))
        school = random.choice(COUNTIES_SCHOOLS[county])
        year   = random.choice([2022, 2023, 2024])

        attend = round(random.gauss(88, 10), 1)
        attend = max(40, min(100, attend))

        perf_mean = school_performance_mean(school)
        # Low-attendance students score worse
        if attend < 75:
            perf_mean -= 12
        scores = generate_scores(perf_mean)
        scores = inject_nulls(scores)

        rows.append({
            "student_id":     f"KE-{year}-{i:05d}",
            "name":           f"{fname} {sname}",
            "school":         school,
            "county":         county,
            "gender":         gender,
            "math":           scores[0],
            "english":        scores[1],
            "kiswahili":      scores[2],
            "biology":        scores[3],
            "chemistry":      scores[4],
            "attendance_pct": attend,
            "year":           year,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    print(f"Generating {N_STUDENTS:,} synthetic student records …")
    df = generate_dataset()
    out = "data/raw/kcse_students_2024.csv"
    df.to_csv(out, index=False)
    print(f"✓ Saved {len(df):,} rows → {out}")
    print(f"  Columns : {list(df.columns)}")
    print(f"  Nulls   : {df.isnull().sum().sum()} total missing values")
    print(f"  Schools : {df['school'].nunique()} unique schools")
    print(f"  Counties: {df['county'].nunique()} counties")
    print(df.head(3).to_string(index=False))
