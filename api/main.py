import os
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from huggingface_hub import hf_hub_download


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "models"


# ============================================================
# HUGGING FACE ARTIFACT CONFIGURATION
# ============================================================

HF_ARTIFACT_REPO = os.getenv(
    "HF_ARTIFACT_REPO",
    ""
)


def get_artifact_path(
    local_path: Path,
    hf_filename: str
) -> Path:
    """
    Return the local artifact if it exists.

    If the artifact does not exist locally and
    HF_ARTIFACT_REPO is configured, download it
    from the public Hugging Face Dataset repository.

    This allows:
        Local development -> local files
        Render deployment -> Hugging Face artifacts
    """

    # --------------------------------------------------------
    # LOCAL DEVELOPMENT
    # --------------------------------------------------------

    if local_path.exists():
        return local_path

    # --------------------------------------------------------
    # CLOUD DEPLOYMENT
    # --------------------------------------------------------

    if HF_ARTIFACT_REPO:
        try:
            downloaded_path = hf_hub_download(
                repo_id=HF_ARTIFACT_REPO,
                filename=hf_filename,
                repo_type="dataset"
            )

            return Path(downloaded_path)

        except Exception as e:
            raise RuntimeError(
                f"Unable to download deployment artifact "
                f"'{hf_filename}' from Hugging Face: {e}"
            )

    # --------------------------------------------------------
    # ARTIFACT NOT AVAILABLE
    # --------------------------------------------------------

    raise FileNotFoundError(
        f"Required artifact is missing locally: {local_path}\n"
        f"Set HF_ARTIFACT_REPO for cloud deployment."
    )


# ============================================================
# REQUIRED ARTIFACTS
# ============================================================

RISK_PATH = get_artifact_path(
    DATA_DIR / "risk_scoring.parquet",
    "data/processed/risk_scoring.parquet"
)

WEEKLY_PATH = get_artifact_path(
    DATA_DIR / "weekly_sales.parquet",
    "data/processed/weekly_sales.parquet"
)

MASTER_PATH = get_artifact_path(
    DATA_DIR / "master_df.parquet",
    "data/processed/master_df.parquet"
)

MODEL_PATH = get_artifact_path(
    MODEL_DIR / "forecast_model_compressed.pkl",
    "models/forecast_model_compressed.pkl"
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Project FORESIGHT API",
    description="Demand Forecasting and Inventory Risk API",
    version="1.0.0"
)


# ============================================================
# LOAD RISK DATA
# ============================================================

try:
    risk_df = pd.read_parquet(RISK_PATH)

except FileNotFoundError as e:
    raise RuntimeError(
        f"Required risk data file not found: {e}"
    )


# ============================================================
# LOAD WEEKLY SALES DATA
# ============================================================

try:
    weekly_sales = pd.read_parquet(WEEKLY_PATH)

    weekly_sales["date"] = pd.to_datetime(
        weekly_sales["date"]
    )

except FileNotFoundError as e:
    raise RuntimeError(
        f"Required weekly sales file not found: {e}"
    )


# ============================================================
# LOAD MASTER DATA
# ============================================================

MASTER_COLUMNS = [
    "date",
    "total_value",
    "profit",
    "customer_id",
    "sku_id",
    "store_id",
    "category"
]

try:
    master_df = pd.read_parquet(
        MASTER_PATH,
        columns=MASTER_COLUMNS
    )

    master_df["date"] = pd.to_datetime(
        master_df["date"]
    )

except FileNotFoundError as e:
    raise RuntimeError(
        f"Required master data file not found: {e}"
    )

except Exception as e:
    raise RuntimeError(
        f"Could not load master data: {e}"
    )


# ============================================================
# VALIDATE MASTER DATA
# ============================================================

missing_master_columns = [
    column
    for column in MASTER_COLUMNS
    if column not in master_df.columns
]

if missing_master_columns:
    raise RuntimeError(
        "master_df.parquet is missing required columns: "
        f"{missing_master_columns}"
    )


# ============================================================
# LOAD TRAINED FORECAST MODEL
# ============================================================

try:
    forecast_model = joblib.load(
        MODEL_PATH
    )

except FileNotFoundError:
    raise RuntimeError(
        f"Forecast model not found: {MODEL_PATH}"
    )

except Exception as e:
    raise RuntimeError(
        f"Could not load forecast model: {e}"
    )


# ============================================================
# MODEL FEATURES
# ============================================================

DEFAULT_FEATURE_COLUMNS = [
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


# ============================================================
# GET ACTUAL MODEL FEATURE ORDER
# ============================================================

if hasattr(
    forecast_model,
    "feature_names_in_"
):
    MODEL_FEATURE_COLUMNS = (
        forecast_model
        .feature_names_in_
        .tolist()
    )

else:
    MODEL_FEATURE_COLUMNS = (
        DEFAULT_FEATURE_COLUMNS
    )


# ============================================================
# VALIDATE MODEL FEATURES
# ============================================================

missing_expected_features = [
    feature
    for feature in DEFAULT_FEATURE_COLUMNS
    if feature not in MODEL_FEATURE_COLUMNS
]

if missing_expected_features:
    raise RuntimeError(
        "The loaded forecast model does not contain "
        "the expected forecasting features: "
        f"{missing_expected_features}"
    )

print("\nMODEL FEATURE ORDER:")
print(MODEL_FEATURE_COLUMNS)


# ============================================================
# REQUEST MODEL
# ============================================================

class SKURequest(BaseModel):
    sku_id: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "service": "Project FORESIGHT",
        "status": "running",
        "model": "forecast_model_compressed.pkl"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "risk_records": len(risk_df),
        "weekly_records": len(weekly_sales),
        "master_records": len(master_df),
        "model_loaded": forecast_model is not None,
        "model_features": MODEL_FEATURE_COLUMNS
    }


# ============================================================
# AVAILABLE SKUS
# ============================================================

@app.get("/skus")
def get_skus():

    skus = (
        weekly_sales["sku_id"]
        .dropna()
        .unique()
        .tolist()
    )

    return {
        "total_skus": len(skus),
        "skus": skus
    }


# ============================================================
# FORECAST HISTORY
# ============================================================

@app.get("/forecast/history/{sku_id}")
def forecast_history(
    sku_id: str
):

    sku = sku_id.strip()

    sku_history = (
        weekly_sales[
            weekly_sales["sku_id"] == sku
        ]
        .sort_values("date")
    )

    if sku_history.empty:
        raise HTTPException(
            status_code=404,
            detail=f"SKU {sku} not found"
        )

    columns = [
        "date",
        "quantity"
    ]

    if "promo_count" in sku_history.columns:
        columns.append("promo_count")

    history = sku_history[columns].copy()

    history["date"] = (
        history["date"]
        .dt.strftime("%Y-%m-%d")
    )

    history = history.where(
        pd.notna(history),
        None
    )

    return {
        "sku_id": sku,
        "total_records": len(history),
        "data": history.to_dict(
            orient="records"
        )
    }


# ============================================================
# KPI SUMMARY
# ============================================================

@app.get("/kpi/summary")
def kpi_summary(
    category: str = "ALL",
    sku: str = "ALL"
):

    filtered = master_df

    if category != "ALL":
        filtered = filtered[
            filtered["category"] == category
        ]

    if sku != "ALL":
        filtered = filtered[
            filtered["sku_id"] == sku
        ]

    if filtered.empty:
        return {
            "revenue": 0,
            "profit": 0,
            "customers": 0,
            "products": 0,
            "stores": 0
        }

    revenue = filtered[
        "total_value"
    ].sum()

    profit = filtered[
        "profit"
    ].sum()

    customers = filtered[
        "customer_id"
    ].nunique()

    products = filtered[
        "sku_id"
    ].nunique()

    stores = filtered[
        "store_id"
    ].nunique()

    return {
        "revenue": round(
            float(revenue),
            2
        ),
        "profit": round(
            float(profit),
            2
        ),
        "customers": int(
            customers
        ),
        "products": int(
            products
        ),
        "stores": int(
            stores
        )
    }


# ============================================================
# KPI CATEGORIES
# ============================================================

@app.get("/kpi/categories")
def kpi_categories():

    categories = (
        master_df["category"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    categories = sorted(
        categories
    )

    return {
        "total_categories": len(
            categories
        ),
        "categories": categories
    }


# ============================================================
# KPI SKUS BY CATEGORY
# ============================================================

@app.get("/kpi/skus/{category}")
def kpi_skus(
    category: str
):

    if category == "ALL":
        filtered = master_df

    else:
        filtered = master_df[
            master_df["category"] == category
        ]

    skus = (
        filtered["sku_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    skus = sorted(
        skus
    )

    return {
        "category": category,
        "total_skus": len(
            skus
        ),
        "skus": skus
    }


# ============================================================
# KPI MONTHLY REVENUE
# ============================================================

@app.get("/kpi/monthly-revenue")
def kpi_monthly_revenue(
    category: str = "ALL",
    sku: str = "ALL"
):

    filtered = master_df

    if category != "ALL":
        filtered = filtered[
            filtered["category"] == category
        ]

    if sku != "ALL":
        filtered = filtered[
            filtered["sku_id"] == sku
        ]

    if filtered.empty:
        return {
            "data": []
        }

    monthly = (
        filtered
        .assign(
            month=(
                filtered["date"]
                .dt.to_period("M")
                .astype(str)
            )
        )
        .groupby("month")[
            "total_value"
        ]
        .sum()
        .reset_index()
        .rename(
            columns={
                "total_value": "revenue"
            }
        )
    )

    monthly["revenue"] = (
        monthly["revenue"]
        .round(2)
    )

    return {
        "data": monthly.to_dict(
            orient="records"
        )
    }


# ============================================================
# KPI TOP CATEGORIES
# ============================================================

@app.get("/kpi/top-categories")
def kpi_top_categories(
    category: str = "ALL",
    sku: str = "ALL"
):

    filtered = master_df

    if category != "ALL":
        filtered = filtered[
            filtered["category"] == category
        ]

    if sku != "ALL":
        filtered = filtered[
            filtered["sku_id"] == sku
        ]

    if filtered.empty:
        return {
            "data": []
        }

    top_categories = (
        filtered
        .groupby("category")[
            "total_value"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
        .rename(
            columns={
                "total_value": "revenue"
            }
        )
    )

    top_categories["revenue"] = (
        top_categories["revenue"]
        .round(2)
    )

    return {
        "data": top_categories.to_dict(
            orient="records"
        )
    }


# ============================================================
# KPI REVENUE AT RISK
# ============================================================

@app.get("/kpi/revenue-risk")
def kpi_revenue_risk():

    risk_skus = (
        risk_df.loc[
            risk_df[
                "recommended_action"
            ] == "REORDER NOW",
            "sku_id"
        ]
        .dropna()
        .unique()
    )

    if len(risk_skus) == 0:
        return {
            "data": []
        }

    filtered = master_df[
        master_df["sku_id"].isin(
            risk_skus
        )
    ]

    revenue_risk = (
        filtered
        .groupby("sku_id")[
            "total_value"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
        .rename(
            columns={
                "total_value": "revenue"
            }
        )
    )

    revenue_risk["revenue"] = (
        revenue_risk["revenue"]
        .round(2)
    )

    return {
        "data": revenue_risk.to_dict(
            orient="records"
        )
    }


# ============================================================
# RISK SUMMARY
# ============================================================

@app.get("/risk/summary")
def risk_summary():

    counts = (
        risk_df[
            "recommended_action"
        ]
        .value_counts()
        .to_dict()
    )

    total_products = len(
        risk_df
    )

    return {
        "total_products": total_products,
        "markdown": int(
            counts.get(
                "MARKDOWN",
                0
            )
        ),
        "reorder_now": int(
            counts.get(
                "REORDER NOW",
                0
            )
        ),
        "healthy": int(
            counts.get(
                "HEALTHY",
                0
            )
        ),
        "watch": int(
            counts.get(
                "WATCH",
                0
            )
        )
    }


# ============================================================
# RISK DISTRIBUTION
# ============================================================

@app.get("/risk/distribution")
def risk_distribution():

    counts = (
        risk_df[
            "recommended_action"
        ]
        .value_counts()
        .to_dict()
    )

    total_products = len(
        risk_df
    )

    if total_products == 0:
        return []

    distribution = []

    for action, count in counts.items():

        distribution.append(
            {
                "action": str(
                    action
                ),
                "count": int(
                    count
                ),
                "percentage": round(
                    (
                        count
                        / total_products
                    )
                    * 100,
                    2
                )
            }
        )

    return distribution


# ============================================================
# RISK PRODUCTS
# ============================================================

@app.get("/risk/products/{action}")
def get_risk_products(
    action: str
):

    action = action.strip().upper()

    valid_actions = [
        "MARKDOWN",
        "REORDER NOW",
        "HEALTHY",
        "WATCH"
    ]

    if action not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid action. "
                "Choose from: "
                f"{', '.join(valid_actions)}"
            )
        )

    filtered = (
        risk_df[
            risk_df[
                "recommended_action"
            ] == action
        ]
        .copy()
    )

    filtered = filtered.where(
        pd.notna(filtered),
        None
    )

    return {
        "action": action,
        "total_products": len(
            filtered
        ),
        "products": filtered.to_dict(
            orient="records"
        )
    }


# ============================================================
# FORECAST FUNCTION
# ============================================================

def generate_forecast(
    sku_history,
    horizon=6
):

    history = (
        sku_history
        .sort_values("date")
        .copy()
    )

    # ========================================================
    # HISTORICAL DEMAND
    # ========================================================

    values = (
        history["quantity"]
        .astype(float)
        .tolist()
    )

    # ========================================================
    # HISTORICAL DATES
    # ========================================================

    dates = (
        history["date"]
        .tolist()
    )

    # ========================================================
    # RECENT PROMOTION INFORMATION
    # ========================================================

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

    # ========================================================
    # RECURSIVE FORECAST
    # ========================================================

    for _ in range(horizon):

        # ----------------------------------------------------
        # NEXT DATE
        # ----------------------------------------------------

        next_date = (
            pd.Timestamp(
                dates[-1]
            )
            + pd.Timedelta(
                weeks=1
            )
        )

        # ----------------------------------------------------
        # LAG FEATURES
        # ----------------------------------------------------

        lag_1 = values[-1]
        lag_2 = values[-2]
        lag_4 = values[-4]
        lag_8 = values[-8]

        # ----------------------------------------------------
        # ROLLING FEATURES
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # EXPANDING MEAN
        # ----------------------------------------------------

        expanding_mean = (
            recent_values
            .mean()
        )

        # ----------------------------------------------------
        # CALENDAR FEATURES
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # PROMOTION FEATURES
        # ----------------------------------------------------

        promo_count = float(
            recent_promo_count
        )

        has_promo = int(
            promo_count > 0
        )

        # ====================================================
        # CREATE FEATURE ROW
        # ====================================================

        feature_row = pd.DataFrame(
            [
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
            ]
        )

        # ====================================================
        # CRITICAL:
        # REORDER FEATURES ACCORDING TO MODEL
        # ====================================================

        try:

            feature_row = (
                feature_row[
                    MODEL_FEATURE_COLUMNS
                ]
            )

        except KeyError as e:

            raise RuntimeError(
                "Required model feature is missing "
                f"from forecast input: {e}"
            )

        # ====================================================
        # MODEL PREDICTION
        # ====================================================

        try:

            prediction = (
                forecast_model
                .predict(
                    feature_row
                )[0]
            )

        except Exception as e:

            raise RuntimeError(
                "Forecast model prediction failed: "
                f"{e}"
            )

        # ----------------------------------------------------
        # PREVENT NEGATIVE DEMAND
        # ----------------------------------------------------

        prediction = max(
            0,
            float(prediction)
        )

        prediction = round(
            prediction,
            2
        )

        # ----------------------------------------------------
        # RECURSIVE FORECASTING
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
# PREDICT
# ============================================================

@app.post("/predict")
def predict(
    request: SKURequest
):

    # ========================================================
    # CLEAN SKU INPUT
    # ========================================================

    sku = request.sku_id.strip()

    # ========================================================
    # GET SKU HISTORY
    # ========================================================

    sku_history = (
        weekly_sales[
            weekly_sales["sku_id"] == sku
        ]
        .sort_values("date")
    )

    # ========================================================
    # SKU VALIDATION
    # ========================================================

    if sku_history.empty:

        raise HTTPException(
            status_code=404,
            detail=f"SKU {sku} not found"
        )

    # ========================================================
    # MINIMUM HISTORY VALIDATION
    # ========================================================

    if len(sku_history) < 8:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Not enough historical data "
                f"for SKU {sku}. "
                f"At least 8 weeks are required."
            )
        )

    # ========================================================
    # CURRENT RISK
    # ========================================================

    sku_risk = (
        risk_df[
            risk_df["sku_id"] == sku
        ]
    )

    if sku_risk.empty:

        risk_action = "UNKNOWN"

    else:

        risk_action = str(
            sku_risk
            .iloc[0]
            ["recommended_action"]
        )

    # ========================================================
    # LATEST DEMAND
    # ========================================================

    latest_demand = float(
        sku_history
        .iloc[-1]
        ["quantity"]
    )

    # ========================================================
    # GENERATE ML FORECAST
    # ========================================================

    try:

        (
            forecast_dates,
            forecast_values
        ) = generate_forecast(
            sku_history,
            horizon=6
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Forecast generation failed: {e}"
            )
        )

    # ========================================================
    # AVERAGE FORECAST
    # ========================================================

    average_forecast = round(
        sum(
            forecast_values
        )
        /
        len(
            forecast_values
        ),
        2
    )

    # ========================================================
    # API RESPONSE
    # ========================================================

    return {
        "sku_id": sku,

        "latest_demand": round(
            latest_demand,
            2
        ),

        "forecast_horizon_weeks": 6,

        "forecast_dates":
            forecast_dates,

        "forecast":
            forecast_values,

        "average_forecast":
            average_forecast,

        "risk":
            risk_action
    }