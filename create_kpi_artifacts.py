from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT FORESIGHT
# KPI DEPLOYMENT ARTIFACT GENERATOR
# ============================================================
#
# Purpose:
# Create small pre-aggregated Parquet files for the Streamlit
# deployment so the deployed KPI Dashboard does NOT need to
# load the 319+ MB master_df.parquet into memory.
#
# Source:
#   data/processed/master_df.parquet
#   data/processed/risk_scoring.parquet
#
# Output:
#   data/deployment/kpi_summary.parquet
#   data/deployment/monthly_revenue.parquet
#   data/deployment/category_revenue.parquet
#   data/deployment/revenue_risk.parquet
#
# ============================================================


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MASTER_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "master_df.parquet"
)

RISK_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "risk_scoring.parquet"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "deployment"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# VALIDATE SOURCE FILES
# ============================================================

print("=" * 60)
print("PROJECT FORESIGHT - KPI ARTIFACT GENERATOR")
print("=" * 60)

print()
print("Checking source files...")

if not MASTER_PATH.exists():
    raise FileNotFoundError(
        f"master_df.parquet not found:\n{MASTER_PATH}"
    )

if not RISK_PATH.exists():
    raise FileNotFoundError(
        f"risk_scoring.parquet not found:\n{RISK_PATH}"
    )

print("✓ master_df.parquet found")
print("✓ risk_scoring.parquet found")


# ============================================================
# LOAD MASTER DATA
# ============================================================

print()
print("=" * 60)
print("Loading master_df.parquet...")
print("=" * 60)

MASTER_COLUMNS = [
    "date",
    "total_value",
    "profit",
    "customer_id",
    "sku_id",
    "store_id",
    "category"
]

master = pd.read_parquet(
    MASTER_PATH,
    columns=MASTER_COLUMNS
)

print(
    f"Loaded {len(master):,} rows."
)


# ============================================================
# BASIC CLEANING
# ============================================================

print()
print("Preparing master data...")

master["date"] = pd.to_datetime(
    master["date"]
)

master["category"] = (
    master["category"]
    .astype(str)
)

master["sku_id"] = (
    master["sku_id"]
    .astype(str)
)

print("✓ Date converted")
print("✓ Category normalized")
print("✓ SKU IDs normalized")


# ============================================================
# 1. KPI SUMMARY
# ============================================================

print()
print("=" * 60)
print("Creating KPI summary...")
print("=" * 60)


# ------------------------------------------------------------
# Overall KPI
# ------------------------------------------------------------

overall = pd.DataFrame(
    [{
        "filter_type": "ALL",
        "category": "ALL",
        "sku": "ALL",
        "revenue": master["total_value"].sum(),
        "profit": master["profit"].sum(),
        "customers": master["customer_id"].nunique(),
        "products": master["sku_id"].nunique(),
        "stores": master["store_id"].nunique()
    }]
)


# ------------------------------------------------------------
# Category-level KPI
# ------------------------------------------------------------

category_summary = (
    master
    .groupby(
        "category",
        as_index=False
    )
    .agg(
        revenue=(
            "total_value",
            "sum"
        ),

        profit=(
            "profit",
            "sum"
        ),

        customers=(
            "customer_id",
            "nunique"
        ),

        products=(
            "sku_id",
            "nunique"
        ),

        stores=(
            "store_id",
            "nunique"
        )
    )
)

category_summary["filter_type"] = (
    "CATEGORY"
)

category_summary["sku"] = (
    "ALL"
)

category_summary = category_summary[
    [
        "filter_type",
        "category",
        "sku",
        "revenue",
        "profit",
        "customers",
        "products",
        "stores"
    ]
]


# ------------------------------------------------------------
# SKU-level KPI
# ------------------------------------------------------------

sku_summary = (
    master
    .groupby(
        [
            "category",
            "sku_id"
        ],
        as_index=False
    )
    .agg(
        revenue=(
            "total_value",
            "sum"
        ),

        profit=(
            "profit",
            "sum"
        ),

        customers=(
            "customer_id",
            "nunique"
        ),

        products=(
            "sku_id",
            "nunique"
        ),

        stores=(
            "store_id",
            "nunique"
        )
    )
)

sku_summary["filter_type"] = (
    "SKU"
)

sku_summary = sku_summary.rename(
    columns={
        "sku_id": "sku"
    }
)

sku_summary = sku_summary[
    [
        "filter_type",
        "category",
        "sku",
        "revenue",
        "profit",
        "customers",
        "products",
        "stores"
    ]
]


# ------------------------------------------------------------
# Combine KPI tables
# ------------------------------------------------------------

kpi_summary = pd.concat(
    [
        overall,
        category_summary,
        sku_summary
    ],
    ignore_index=True
)


# Round numeric values
kpi_summary["revenue"] = (
    kpi_summary["revenue"]
    .round(2)
)

kpi_summary["profit"] = (
    kpi_summary["profit"]
    .round(2)
)


# Save
KPI_SUMMARY_PATH = (
    OUTPUT_DIR
    / "kpi_summary.parquet"
)

kpi_summary.to_parquet(
    KPI_SUMMARY_PATH,
    index=False
)

print(
    f"✓ KPI summary created: "
    f"{len(kpi_summary):,} rows"
)


# ============================================================
# 2. MONTHLY REVENUE
# ============================================================

print()
print("=" * 60)
print("Creating monthly revenue...")
print("=" * 60)


master["month"] = (
    master["date"]
    .dt.to_period("M")
    .astype(str)
)


# ------------------------------------------------------------
# Overall monthly revenue
# ------------------------------------------------------------

monthly_all = (
    master
    .groupby(
        "month",
        as_index=False
    )["total_value"]
    .sum()
)

monthly_all["filter_type"] = (
    "ALL"
)

monthly_all["category"] = (
    "ALL"
)

monthly_all["sku"] = (
    "ALL"
)


# ------------------------------------------------------------
# Category monthly revenue
# ------------------------------------------------------------

monthly_category = (
    master
    .groupby(
        [
            "category",
            "month"
        ],
        as_index=False
    )["total_value"]
    .sum()
)

monthly_category["filter_type"] = (
    "CATEGORY"
)

monthly_category["sku"] = (
    "ALL"
)


# ------------------------------------------------------------
# SKU monthly revenue
# ------------------------------------------------------------

monthly_sku = (
    master
    .groupby(
        [
            "category",
            "sku_id",
            "month"
        ],
        as_index=False
    )["total_value"]
    .sum()
)

monthly_sku["filter_type"] = (
    "SKU"
)

monthly_sku = monthly_sku.rename(
    columns={
        "sku_id": "sku"
    }
)


# ------------------------------------------------------------
# Rename revenue column
# ------------------------------------------------------------

monthly_all = monthly_all.rename(
    columns={
        "total_value": "revenue"
    }
)

monthly_category = monthly_category.rename(
    columns={
        "total_value": "revenue"
    }
)

monthly_sku = monthly_sku.rename(
    columns={
        "total_value": "revenue"
    }
)


# ------------------------------------------------------------
# Standardize column order
# ------------------------------------------------------------

monthly_all = monthly_all[
    [
        "filter_type",
        "category",
        "sku",
        "month",
        "revenue"
    ]
]

monthly_category = monthly_category[
    [
        "filter_type",
        "category",
        "sku",
        "month",
        "revenue"
    ]
]

monthly_sku = monthly_sku[
    [
        "filter_type",
        "category",
        "sku",
        "month",
        "revenue"
    ]
]


# ------------------------------------------------------------
# Combine
# ------------------------------------------------------------

monthly_revenue = pd.concat(
    [
        monthly_all,
        monthly_category,
        monthly_sku
    ],
    ignore_index=True
)


monthly_revenue["revenue"] = (
    monthly_revenue["revenue"]
    .round(2)
)


# Save
MONTHLY_REVENUE_PATH = (
    OUTPUT_DIR
    / "monthly_revenue.parquet"
)

monthly_revenue.to_parquet(
    MONTHLY_REVENUE_PATH,
    index=False
)

print(
    f"✓ Monthly revenue created: "
    f"{len(monthly_revenue):,} rows"
)


# ============================================================
# 3. CATEGORY REVENUE
# ============================================================

print()
print("=" * 60)
print("Creating category revenue...")
print("=" * 60)


category_revenue = (
    master
    .groupby(
        "category",
        as_index=False
    )["total_value"]
    .sum()
)


category_revenue = category_revenue.rename(
    columns={
        "total_value": "revenue"
    }
)


category_revenue["revenue"] = (
    category_revenue["revenue"]
    .round(2)
)


category_revenue = (
    category_revenue
    .sort_values(
        "revenue",
        ascending=False
    )
    .reset_index(drop=True)
)


# Save
CATEGORY_REVENUE_PATH = (
    OUTPUT_DIR
    / "category_revenue.parquet"
)

category_revenue.to_parquet(
    CATEGORY_REVENUE_PATH,
    index=False
)

print(
    f"✓ Category revenue created: "
    f"{len(category_revenue):,} rows"
)


# ============================================================
# 4. REVENUE AT RISK
# ============================================================

print()
print("=" * 60)
print("Creating revenue-at-risk...")
print("=" * 60)


risk = pd.read_parquet(
    RISK_PATH,
    columns=[
        "sku_id",
        "recommended_action"
    ]
)


risk["sku_id"] = (
    risk["sku_id"]
    .astype(str)
)


# ------------------------------------------------------------
# Find REORDER NOW SKUs
# ------------------------------------------------------------

reorder_skus = (
    risk.loc[
        risk["recommended_action"]
        == "REORDER NOW",
        "sku_id"
    ]
    .dropna()
    .unique()
)


print(
    f"REORDER NOW SKUs: "
    f"{len(reorder_skus):,}"
)


# ------------------------------------------------------------
# Calculate revenue for those SKUs
# ------------------------------------------------------------

revenue_risk = (
    master[
        master["sku_id"]
        .isin(reorder_skus)
    ]
    .groupby(
        "sku_id",
        as_index=False
    )["total_value"]
    .sum()
)


revenue_risk = revenue_risk.rename(
    columns={
        "total_value": "revenue"
    }
)


revenue_risk = (
    revenue_risk
    .sort_values(
        "revenue",
        ascending=False
    )
    .head(100)
    .reset_index(drop=True)
)


revenue_risk["revenue"] = (
    revenue_risk["revenue"]
    .round(2)
)


# Save
REVENUE_RISK_PATH = (
    OUTPUT_DIR
    / "revenue_risk.parquet"
)

revenue_risk.to_parquet(
    REVENUE_RISK_PATH,
    index=False
)

print(
    f"✓ Revenue-at-risk created: "
    f"{len(revenue_risk):,} rows"
)


# ============================================================
# CLEANUP
# ============================================================

print()
print("Cleaning temporary objects...")

del risk
del monthly_all
del monthly_category
del monthly_sku
del category_summary
del sku_summary
del overall
del category_revenue
del revenue_risk
del kpi_summary
del master

print("✓ Cleanup complete")


# ============================================================
# FINAL FILE REPORT
# ============================================================

print()
print("=" * 60)
print("ALL KPI ARTIFACTS CREATED SUCCESSFULLY")
print("=" * 60)

for file in sorted(
    OUTPUT_DIR.glob("*.parquet")
):

    size_mb = (
        file.stat().st_size
        / 1024
        / 1024
    )

    print(
        f"{file.name:<30}"
        f"{size_mb:>10.2f} MB"
    )

print("=" * 60)
print("Done.")
print("=" * 60)