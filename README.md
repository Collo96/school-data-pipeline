# 🏫 Secondary School Data Engineering Project
**KCSE Student Performance Pipeline — Extract → Transform → Load → Deploy**

A complete, beginner-friendly data engineering prototype built around Kenya Certificate of Secondary Education (KCSE) student data.

---

## 📁 Project Structure

```
school-pipeline/
├── 00_generate_data.py     # Generate synthetic KCSE student data
├── 01_extract.py           # Phase 1: Ingest raw CSV data
├── 02_transform.py         # Phase 2: Clean & enrich data
├── 03_load.py              # Phase 3: Load into PostgreSQL
├── 04_dashboard.py         # Phase 4: Streamlit analytics dashboard
├── run_pipeline.py         # Run all phases at once
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition
├── docker-compose.yml      # Local dev with PostgreSQL
├── .github/workflows/      # Automated daily ETL on GitHub Actions
│   └── etl.yml
└── data/
    ├── raw/                # Input: raw CSV files
    ├── staging/            # Intermediate: Parquet after extraction
    └── processed/          # Output: clean Parquet before DB load
```

---

## 🗂 Raw Data Sources (real, free)

| Source | What it contains | Link |
|--------|----------------|------|
| **Kenya Open Data** | KNEC KCSE results by school & county | [opendata.go.ke](https://opendata.go.ke) |
| **UCI Student Performance** | Math & Portuguese grades, demographics | [UCI Repository](https://archive.ics.uci.edu/dataset/320/student+performance) |
| **Kaggle Student Exams** | Score data with socioeconomic factors | [Kaggle](https://www.kaggle.com/datasets/whenamancodes/student-performance) |
| **This project** | Synthetic KCSE-style data (auto-generated) | `python 00_generate_data.py` |

---

## 🚀 Quick Start (Local, 5 minutes)

### 1. Clone & install dependencies
```bash
git clone https://github.com/your-username/school-data-pipeline
cd school-data-pipeline
pip install -r requirements.txt
```

### 2. Run the full pipeline
```bash
python 00_generate_data.py    # Creates data/raw/kcse_students_2024.csv
python 01_extract.py          # Validates & stages the data
python 02_transform.py        # Cleans, enriches, adds grades
python 03_load.py             # Loads into SQLite (local dev)
```

Or run everything at once:
```bash
python run_pipeline.py
```

### 3. Launch the dashboard
```bash
streamlit run 04_dashboard.py
# Open: http://localhost:8501
```

---

## ☁️ Cloud Deployment (FREE)

### Step 1 – Push to GitHub
```bash
git init && git add . && git commit -m "Initial pipeline"
git remote add origin https://github.com/you/school-pipeline.git
git push -u origin main
```

### Step 2 – Free PostgreSQL on Neon.tech
1. Sign up at [neon.tech](https://neon.tech) (free, no credit card)
2. Create a new project → copy the **Connection String**
3. It looks like: `postgresql://user:pass@ep-xxx.neon.tech/school_db?sslmode=require`

### Step 3 – Deploy dashboard on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repo
3. Set main file: `04_dashboard.py`
4. Under **Settings → Secrets**, add:
   ```toml
   DATABASE_URL = "postgresql://..."
   ```
5. Click Deploy → your dashboard is live! 🎉

### Step 4 – Add DATABASE_URL to GitHub Secrets (for automated ETL)
1. GitHub repo → Settings → Secrets → Actions → New secret
2. Name: `DATABASE_URL`, Value: your Neon connection string
3. The pipeline runs automatically every day at 9 AM EAT

---

## 🐳 Docker (local with real PostgreSQL)
```bash
docker compose up --build
# Dashboard: http://localhost:8501
```

---

## 📊 Pipeline Overview

```
Raw CSV Files  →  Extract  →  [Validate Schema]  →  Staging (Parquet)
                                                           ↓
                                                      Transform
                                              [Clean, Enrich, Grade]
                                                           ↓
                                                    Processed Parquet
                                                           ↓
                                               Load → PostgreSQL DB
                                                           ↓
                                              Streamlit Dashboard ← Users
```

---

## 🔧 Key Technologies

| Tool | Purpose | Cost |
|------|---------|------|
| Python + Pandas | ETL processing | Free |
| SQLAlchemy | Database ORM | Free |
| PostgreSQL (Neon) | Cloud database | Free (512 MB) |
| Streamlit | Dashboard | Free |
| Plotly | Charts | Free |
| GitHub Actions | Automation | Free (2000 min/month) |
| Docker | Containerisation | Free |

---

## 📚 Learning Objectives

By completing this project, you will understand:
- ✅ What raw data looks like and where it comes from
- ✅ How to ingest (Extract) data from CSV / URL sources
- ✅ How to clean and enrich (Transform) data with Pandas
- ✅ How to store (Load) clean data into a relational database
- ✅ How to build an interactive analytics dashboard
- ✅ How to automate a pipeline with GitHub Actions
- ✅ How to deploy a full stack to the cloud for free

---

## 🇰🇪 Designed For

Kenyan secondary school data engineering education.
The synthetic data mirrors KCSE grading (A–E) and includes all 47 counties.
