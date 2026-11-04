from pathlib import Path
import os

import joblib
import pandas as pd
import streamlit as st
from huggingface_hub import hf_hub_download


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "processed"
DEPLOYMENT_DIR = BASE_DIR / "data" / "deployment"
MODEL_DIR = BASE_DIR / "models"


# ============================================================
# HUGGING FACE
# ============================================================

HF_ARTIFACT_REPO = os.getenv(
    "HF_ARTIFACT_REPO",
    "sibamsen07/project-foresight-artifacts"
)


def get_artifact_path(
    local_path: Path,
    hf_filename: str
) -> str:
    """
    Use the local artifact during development.

    If the local artifact does not exist, download the
    corresponding artifact from the Hugging Face Dataset repo.
    """

    if local_path.exists():
        return str(local_path)

    return hf_hub_download(
        repo_id=HF_ARTIFACT_REPO,
        filename=hf_filename,
        repo_type="dataset"
    )


# ============================================================
# RISK DATA
# ============================================================

@st.cache_data
def load_risk_data():

    path = get_artifact_path(
        DATA_DIR / "risk_scoring.parquet",
        "data/processed/risk_scoring.parquet"
    )

    return pd.read_parquet(path)


# ============================================================
# WEEKLY SALES
# ============================================================

@st.cache_data
def load_weekly_sales():

    path = get_artifact_path(
        DATA_DIR / "weekly_sales.parquet",
        "data/processed/weekly_sales.parquet"
    )

    df = pd.read_parquet(path)

    df["date"] = pd.to_datetime(
        df["date"]
    )

    return df


# ============================================================
# FORECAST MODEL
# ============================================================
#
# PRODUCTION MODEL
#
# The original model was approximately 389 MB.
#
# The optimized production model:
#
#     RandomForestRegressor
#     n_estimators = 30
#     max_depth = 12
#     min_samples_leaf = 2
#
# Model size:
#
#     ~1.60 MB
#
# Test performance:
#
#     MAE  = 3.9832
#     RMSE = 13.0601
#     R2   = 0.9823
#
# This model is used for Streamlit deployment because it
# provides excellent forecasting performance while being
# dramatically smaller than the original model.
# ============================================================

@st.cache_resource
def load_forecast_model():

    path = get_artifact_path(
        MODEL_DIR / "rf_30_depth12_leaf2.pkl",
        "models/rf_30_depth12_leaf2.pkl"
    )

    return joblib.load(path)


# ============================================================
# KPI DEPLOYMENT ARTIFACTS
# ============================================================
#
# IMPORTANT:
#
# The deployed application no longer loads:
#
#     master_df.parquet
#
# for KPI operations.
#
# Instead it uses the small pre-aggregated artifacts:
#
#     kpi_summary.parquet
#     monthly_revenue.parquet
#     category_revenue.parquet
#     revenue_risk.parquet
#
# These were generated locally from the original
# 9.96-million-row master dataframe.
# ============================================================


@st.cache_data
def load_kpi_summary_data():

    path = get_artifact_path(
        DEPLOYMENT_DIR / "kpi_summary.parquet",
        "data/deployment/kpi_summary.parquet"
    )

    return pd.read_parquet(path)


@st.cache_data
def load_monthly_revenue_data():

    path = get_artifact_path(
        DEPLOYMENT_DIR / "monthly_revenue.parquet",
        "data/deployment/monthly_revenue.parquet"
    )

    return pd.read_parquet(path)


@st.cache_data
def load_category_revenue_data():

    path = get_artifact_path(
        DEPLOYMENT_DIR / "category_revenue.parquet",
        "data/deployment/category_revenue.parquet"
    )

    return pd.read_parquet(path)


@st.cache_data
def load_revenue_risk_data():

    path = get_artifact_path(
        DEPLOYMENT_DIR / "revenue_risk.parquet",
        "data/deployment/revenue_risk.parquet"
    )

    return pd.read_parquet(path)


# ============================================================
# KPI SUMMARY
# ============================================================

def get_kpi_summary(
    category="ALL",
    sku="ALL"
):

    df = load_kpi_summary_data()

    filtered = df[
        (df["category"] == category)
        & (df["sku"] == sku)
    ]

    if filtered.empty:

        return {
            "revenue": 0,
            "profit": 0,
            "customers": 0,
            "products": 0,
            "stores": 0
        }

    row = filtered.iloc[0]

    return {
        "revenue": round(
            float(row["revenue"]),
            2
        ),

        "profit": round(
            float(row["profit"]),
            2
        ),

        "customers": int(
            row["customers"]
        ),

        "products": int(
            row["products"]
        ),

        "stores": int(
            row["stores"]
        )
    }


# ============================================================
# CATEGORIES
# ============================================================

def get_categories():

    df = load_kpi_summary_data()

    categories = (
        df.loc[
            df["filter_type"] == "CATEGORY",
            "category"
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return sorted(categories)


# ============================================================
# SKUS
# ============================================================

def get_skus():

    df = load_kpi_summary_data()

    skus = (
        df.loc[
            df["filter_type"] == "SKU",
            "sku"
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return sorted(skus)


def get_skus_by_category(category):

    df = load_kpi_summary_data()

    sku_rows = df[
        df["filter_type"] == "SKU"
    ]

    if category != "ALL":

        sku_rows = sku_rows[
            sku_rows["category"] == category
        ]

    return sorted(
        sku_rows["sku"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


# ============================================================
# MONTHLY REVENUE
# ============================================================

def get_monthly_revenue(
    category="ALL",
    sku="ALL"
):

    df = load_monthly_revenue_data()

    filtered = df[
        (df["category"] == category)
        & (df["sku"] == sku)
    ]

    if filtered.empty:

        return pd.DataFrame(
            columns=[
                "month",
                "revenue"
            ]
        )

    result = (
        filtered[
            [
                "month",
                "revenue"
            ]
        ]
        .sort_values("month")
        .reset_index(drop=True)
    )

    result["revenue"] = (
        result["revenue"]
        .round(2)
    )

    return result


# ============================================================
# TOP CATEGORIES
# ============================================================

def get_top_categories(
    category="ALL",
    sku="ALL"
):

    df = load_kpi_summary_data()

    # --------------------------------------------------------
    # ALL categories / ALL SKUs
    # --------------------------------------------------------

    if category == "ALL" and sku == "ALL":

        result = df[
            df["filter_type"] == "CATEGORY"
        ][
            [
                "category",
                "revenue"
            ]
        ].copy()

        result = (
            result
            .sort_values(
                "revenue",
                ascending=False
            )
            .head(10)
            .reset_index(drop=True)
        )

        result["revenue"] = (
            result["revenue"]
            .round(2)
        )

        return result


    # --------------------------------------------------------
    # Specific category
    # --------------------------------------------------------

    if category != "ALL" and sku == "ALL":

        result = df[
            (df["filter_type"] == "CATEGORY")
            & (df["category"] == category)
        ][
            [
                "category",
                "revenue"
            ]
        ].copy()

        result["revenue"] = (
            result["revenue"]
            .round(2)
        )

        return result.reset_index(drop=True)


    # --------------------------------------------------------
    # Specific SKU
    #
    # The original implementation groups by category.
    # A SKU belongs to one category, so we retrieve that
    # category from the pre-aggregated SKU row.
    # --------------------------------------------------------

    sku_rows = df[
        (df["filter_type"] == "SKU")
        & (df["sku"] == sku)
    ]

    if sku_rows.empty:

        return pd.DataFrame(
            columns=[
                "category",
                "revenue"
            ]
        )

    result = sku_rows[
        [
            "category",
            "revenue"
        ]
    ].copy()

    result["revenue"] = (
        result["revenue"]
        .round(2)
    )

    return result.reset_index(drop=True)


# ============================================================
# REVENUE AT RISK
# ============================================================

def get_revenue_at_risk():

    df = load_revenue_risk_data()

    if df.empty:

        return pd.DataFrame(
            columns=[
                "sku_id",
                "revenue"
            ]
        )

    result = (
        df[
            [
                "sku_id",
                "revenue"
            ]
        ]
        .sort_values(
            "revenue",
            ascending=False
        )
        .head(10)
        .reset_index(drop=True)
    )

    result["revenue"] = (
        result["revenue"]
        .round(2)
    )

    return result


# ============================================================
# RISK SUMMARY
# ============================================================

def get_risk_summary():

    risk_df = load_risk_data()

    counts = (
        risk_df["recommended_action"]
        .value_counts()
        .to_dict()
    )

    return {

        "total_products":
            len(risk_df),

        "markdown":
            int(
                counts.get(
                    "MARKDOWN",
                    0
                )
            ),

        "reorder_now":
            int(
                counts.get(
                    "REORDER NOW",
                    0
                )
            ),

        "healthy":
            int(
                counts.get(
                    "HEALTHY",
                    0
                )
            ),

        "watch":
            int(
                counts.get(
                    "WATCH",
                    0
                )
            )
    }


# ============================================================
# RISK DISTRIBUTION
# ============================================================

def get_risk_distribution():

    risk_df = load_risk_data()

    counts = (
        risk_df["recommended_action"]
        .value_counts()
    )

    total = len(risk_df)

    if total == 0:

        return pd.DataFrame(
            columns=[
                "action",
                "count",
                "percentage"
            ]
        )

    result = pd.DataFrame({

        "action":
            counts.index.astype(str),

        "count":
            counts.values
    })

    result["percentage"] = (
        result["count"]
        / total
        * 100
    ).round(2)

    return result


# ============================================================
# RISK PRODUCTS
# ============================================================

def get_risk_products(action):

    action = action.strip().upper()

    valid_actions = [
        "MARKDOWN",
        "REORDER NOW",
        "HEALTHY",
        "WATCH"
    ]

    if action not in valid_actions:

        raise ValueError(
            "Invalid risk action."
        )

    risk_df = load_risk_data()

    return risk_df[
        risk_df["recommended_action"]
        == action
    ].copy()


# ============================================================
# FORECAST HISTORY
# ============================================================

def get_forecast_history(sku_id):

    weekly_sales = load_weekly_sales()

    sku = sku_id.strip()

    history = (
        weekly_sales[
            weekly_sales["sku_id"]
            == sku
        ]
        .sort_values("date")
        .copy()
    )

    if history.empty:

        raise ValueError(
            f"SKU {sku} not found"
        )

    columns = [
        "date",
        "quantity"
    ]

    if "promo_count" in history.columns:

        columns.append(
            "promo_count"
        )

    return history[columns]


# ============================================================
# FORECAST GENERATION
# ============================================================

def generate_forecast(
    sku_history,
    horizon=6
):

    model = load_forecast_model()

    history = (
        sku_history
        .sort_values("date")
        .copy()
    )

    values = (
        history["quantity"]
        .astype(float)
        .tolist()
    )

    dates = (
        history["date"]
        .tolist()
    )

    if len(history) < 8:

        raise ValueError(
            "At least 8 weeks of history are required."
        )

    if "promo_count" in history.columns:

        recent_promo_count = (
            history["promo_count"]
            .tail(8)
            .mean()
        )

    else:

        recent_promo_count = 0


    forecast_values = []
    forecast_dates = []


    # --------------------------------------------------------
    # USE THE FEATURES STORED INSIDE THE MODEL
    # --------------------------------------------------------

    if hasattr(
        model,
        "feature_names_in_"
    ):

        model_features = (
            model
            .feature_names_in_
            .tolist()
        )

    else:

        model_features = [
            "rolling_mean_4",
            "rolling_std_4",
            "lag_1",
            "lag_2",
            "weekofyear",
            "expanding_mean",
            "rolling_mean_8",
            "lag_4",
            "lag_8",
            "promo_count",
            "month",
            "year",
            "quarter",
            "has_promo"
        ]


    # ========================================================
    # ITERATIVE FORECAST
    # ========================================================

    for _ in range(horizon):

        next_date = (
            pd.Timestamp(dates[-1])
            + pd.Timedelta(weeks=1)
        )

        lag_1 = values[-1]
        lag_2 = values[-2]
        lag_4 = values[-4]
        lag_8 = values[-8]

        recent_values = pd.Series(
            values
        )

        rolling_mean_4 = (
            recent_values
            .tail(4)
            .mean()
        )

        rolling_std_4 = (
            recent_values
            .tail(4)
            .std()
        )

        if pd.isna(
            rolling_std_4
        ):

            rolling_std_4 = 0.0

        rolling_mean_8 = (
            recent_values
            .tail(8)
            .mean()
        )

        expanding_mean = (
            recent_values
            .mean()
        )

        weekofyear = int(
            next_date
            .isocalendar()
            .week
        )

        month = int(
            next_date.month
        )

        year = int(
            next_date.year
        )

        quarter = int(
            next_date.quarter
        )

        promo_count = float(
            recent_promo_count
        )

        has_promo = int(
            promo_count > 0
        )


        # ----------------------------------------------------
        # FEATURE ROW
        # ----------------------------------------------------

        feature_row = pd.DataFrame([
            {

                "rolling_mean_4":
                    rolling_mean_4,

                "rolling_std_4":
                    rolling_std_4,

                "lag_1":
                    lag_1,

                "lag_2":
                    lag_2,

                "weekofyear":
                    weekofyear,

                "expanding_mean":
                    expanding_mean,

                "rolling_mean_8":
                    rolling_mean_8,

                "lag_4":
                    lag_4,

                "lag_8":
                    lag_8,

                "promo_count":
                    promo_count,

                "month":
                    month,

                "year":
                    year,

                "quarter":
                    quarter,

                "has_promo":
                    has_promo
            }
        ])


        # ----------------------------------------------------
        # REORDER COLUMNS TO MATCH TRAINING
        # ----------------------------------------------------

        feature_row = (
            feature_row[
                model_features
            ]
        )


        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------

        prediction = (
            model
            .predict(feature_row)[0]
        )

        prediction = max(
            0,
            float(prediction)
        )

        prediction = round(
            prediction,
            2
        )


        # ----------------------------------------------------
        # UPDATE HISTORY FOR NEXT ITERATION
        # ----------------------------------------------------

        values.append(
            prediction
        )

        dates.append(
            next_date
        )

        forecast_values.append(
            prediction
        )

        forecast_dates.append(
            next_date.strftime(
                "%Y-%m-%d"
            )
        )


    return (
        forecast_dates,
        forecast_values
    )


# ============================================================
# COMPLETE FORECAST RESULT
# ============================================================

def get_forecast(sku_id):

    risk_df = load_risk_data()

    history = get_forecast_history(
        sku_id
    )

    sku = sku_id.strip()


    # --------------------------------------------------------
    # FIND RISK ACTION
    # --------------------------------------------------------

    sku_risk = risk_df[
        risk_df["sku_id"]
        == sku
    ]

    if sku_risk.empty:

        risk_action = "UNKNOWN"

    else:

        risk_action = str(
            sku_risk.iloc[0][
                "recommended_action"
            ]
        )


    # --------------------------------------------------------
    # LATEST DEMAND
    # --------------------------------------------------------

    latest_demand = float(
        history.iloc[-1]["quantity"]
    )


    # --------------------------------------------------------
    # GENERATE FORECAST
    # --------------------------------------------------------

    (
        forecast_dates,
        forecast_values
    ) = generate_forecast(
        history
    )


    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {

        "sku_id":
            sku,

        "latest_demand":
            round(
                latest_demand,
                2
            ),

        "forecast_horizon_weeks":
            6,

        "forecast_dates":
            forecast_dates,

        "forecast":
            forecast_values,

        "average_forecast":
            round(
                sum(forecast_values)
                / len(forecast_values),
                2
            ),

        "risk":
            risk_action
    }