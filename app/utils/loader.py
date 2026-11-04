import pandas as pd
import streamlit as st
from pathlib import Path


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# =========================================================
# PROCESSED DATA DIRECTORY
# =========================================================

DATA_DIR = PROJECT_ROOT / "data" / "processed"


# =========================================================
# DATA PATHS
# =========================================================

MASTER_PATH = DATA_DIR / "master_df.parquet"

RISK_PATH = DATA_DIR / "risk_scoring.parquet"

WEEKLY_PATH = DATA_DIR / "weekly_sales.parquet"


# =========================================================
# LOAD MASTER DATA
# =========================================================

@st.cache_data
def load_master_data():

    return pd.read_parquet(
        MASTER_PATH
    )


# =========================================================
# LOAD RISK DATA
# =========================================================

@st.cache_data
def load_risk_data():

    return pd.read_parquet(
        RISK_PATH
    )


# =========================================================
# LOAD WEEKLY SALES
# =========================================================

@st.cache_data
def load_weekly_sales():

    return pd.read_parquet(
        WEEKLY_PATH
    )


# =========================================================
# LOAD ALL DATA
# Used by KPI / Risk / Recommendation pages
# =========================================================

@st.cache_data
def load_data():

    master_df = load_master_data()

    risk_df = load_risk_data()

    weekly_sales = load_weekly_sales()

    return (
        master_df,
        risk_df,
        weekly_sales
    )