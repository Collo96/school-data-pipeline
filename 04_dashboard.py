"""
04_dashboard.py
===============
Phase 4 – ANALYZE / VISUALIZE
Interactive Streamlit dashboard for KCSE student performance.

Run locally:
    streamlit run 04_dashboard.py

Deploy FREE to Streamlit Cloud:
    1. Push this repo to GitHub
    2. Go to https://share.streamlit.io
    3. Connect your repo, set main file = 04_dashboard.py
    4. Add DATABASE_URL in the Secrets section

Add secrets locally in  .streamlit/secrets.toml :
    DATABASE_URL = "postgresql://..."
"""

import os
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KCSE Analytics Dashboard",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏫 KCSE Student Performance Dashboard")
st.caption("Secondary School Data Engineering Project – Live Analytics")


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)   # Cache 10 minutes; re-fetch automatically
def load_data() -> pd.DataFrame:
    """Load data from PostgreSQL (or SQLite fallback)."""
    # Priority 1: Streamlit Cloud secrets
    db_url = st.secrets.get("DATABASE_URL", None) if hasattr(st, "secrets") else None
    # Priority 2: environment variable
    if not db_url:
        db_url = os.environ.get("DATABASE_URL")
    # Priority 3: local SQLite (dev fallback)
    if not db_url:
        sqlite_path = "data/school_pipeline.db"
        if os.path.exists(sqlite_path):
            db_url = f"sqlite:///{sqlite_path}"
        else:
            st.error(
                "No database found. Run the pipeline first:\n"
                "```\npython 00_generate_data.py\n"
                "python 01_extract.py\n"
                "python 02_transform.py\n"
                "python 03_load.py\n```"
            )
            st.stop()

    engine = create_engine(db_url)
    df = pd.read_sql("SELECT * FROM student_results", engine)
    return df


df_all = load_data()


# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("Filters")

counties = st.sidebar.multiselect(
    "County", sorted(df_all["county"].unique()), default=[]
)
genders = st.sidebar.multiselect("Gender", ["M", "F"], default=[])
grades  = st.sidebar.multiselect("Grade", ["A","B","C","D","E"], default=[])
years   = st.sidebar.multiselect(
    "Year", sorted(df_all["year"].unique()), default=[]
)

df = df_all.copy()
if counties: df = df[df["county"].isin(counties)]
if genders:  df = df[df["gender"].isin(genders)]
if grades:   df = df[df["grade"].isin(grades)]
if years:    df = df[df["year"].isin(years)]

if df.empty:
    st.warning("No data matches the current filters. Please adjust your selection.")
    st.stop()


# ── KPI row ───────────────────────────────────────────────────────────────────
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Students",    f"{len(df):,}")
kpi2.metric("Pass Rate",         f"{df['passed'].mean()*100:.1f}%")
kpi3.metric("Mean Score",        f"{df['mean_score'].mean():.1f}")
kpi4.metric("Schools",           df["school"].nunique())
kpi5.metric("Low Attendance",    df["low_attend"].sum())

st.divider()


# ── Row 1: Score distribution + Grade breakdown ───────────────────────────────
col1, col2 = st.columns(2)

with col1:
    fig_hist = px.histogram(
        df, x="mean_score", color="gender",
        nbins=25, barmode="overlay", opacity=0.75,
        color_discrete_map={"M": "#3B8BD4", "F": "#D05538"},
        title="Score Distribution by Gender",
        labels={"mean_score": "Mean Score", "count": "Students"},
    )
    fig_hist.update_layout(showlegend=True, height=320)
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    grade_counts = df["grade"].value_counts().reindex(["A","B","C","D","E"]).reset_index()
    grade_counts.columns = ["grade", "count"]
    fig_grade = px.bar(
        grade_counts, x="grade", y="count",
        color="grade",
        color_discrete_map={"A":"#3B6D11","B":"#1D9E75","C":"#BA7517","D":"#D85A30","E":"#A32D2D"},
        title="Students per Grade",
        labels={"count": "Number of Students"},
    )
    fig_grade.update_layout(showlegend=False, height=320)
    st.plotly_chart(fig_grade, use_container_width=True)


# ── Row 2: County comparison + Scatter ───────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    county_avg = (
        df.groupby("county")
        .agg(avg_score=("mean_score","mean"), students=("student_id","count"))
        .reset_index()
        .sort_values("avg_score", ascending=False)
    )
    county_avg["avg_score"] = county_avg["avg_score"].round(1)
    fig_county = px.bar(
        county_avg, x="county", y="avg_score",
        color="avg_score", color_continuous_scale="Blues",
        title="Average Score by County",
        labels={"avg_score": "Avg Score", "county": "County"},
    )
    fig_county.update_layout(height=340, coloraxis_showscale=False, xaxis_tickangle=-30)
    st.plotly_chart(fig_county, use_container_width=True)

with col4:
    fig_scatter = px.scatter(
        df.sample(min(1000, len(df)), random_state=1),
        x="attendance_pct", y="mean_score",
        color="grade",
        color_discrete_map={"A":"#3B6D11","B":"#1D9E75","C":"#BA7517","D":"#D85A30","E":"#A32D2D"},
        title="Attendance vs Score",
        labels={"attendance_pct":"Attendance (%)", "mean_score":"Mean Score"},
        opacity=0.6,
    )
    fig_scatter.update_traces(marker_size=5)
    fig_scatter.update_layout(height=340)
    st.plotly_chart(fig_scatter, use_container_width=True)


# ── Subject averages ──────────────────────────────────────────────────────────
st.subheader("Subject Performance")
subjects = ["math","english","kiswahili","biology","chemistry"]
subj_means = df[subjects].mean().reset_index()
subj_means.columns = ["subject","average"]
subj_means["average"] = subj_means["average"].round(1)
fig_subj = px.bar(
    subj_means, x="subject", y="average",
    color="average", color_continuous_scale="Teal",
    title="Average Score per Subject (all filtered students)",
    labels={"average":"Average Score"},
)
fig_subj.update_layout(height=280, coloraxis_showscale=False)
st.plotly_chart(fig_subj, use_container_width=True)


# ── Raw data table ────────────────────────────────────────────────────────────
st.subheader("Student Records")
st.caption(f"Showing {min(200, len(df)):,} of {len(df):,} records")
cols_show = ["student_id","name","school","county","gender",
             "mean_score","grade","attendance_pct","passed"]
st.dataframe(
    df[cols_show].head(200).reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)


# ── Download ──────────────────────────────────────────────────────────────────
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇ Download filtered data as CSV",
    data=csv,
    file_name="kcse_filtered.csv",
    mime="text/csv",
)
