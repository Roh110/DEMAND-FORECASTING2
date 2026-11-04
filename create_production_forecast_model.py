from pathlib import Path
import time

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# PROJECT FORESIGHT
# PRODUCTION FORECAST MODEL COMPARISON
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

WEEKLY_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "weekly_sales.parquet"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONFIGURATION
# ============================================================

FEATURES = [
    "promo_count",
    "has_promo",
    "year",
    "month",
    "quarter",
    "weekofyear",
    "lag_1",
    "lag_2",
    "lag_4",
    "lag_8",
    "rolling_mean_4",
    "rolling_mean_8",
    "rolling_std_4",
    "expanding_mean"
]

TARGET = "quantity"


# ============================================================
# MODEL CANDIDATES
# ============================================================

CANDIDATES = {

    "rf_50_depth20_leaf2": {
        "n_estimators": 50,
        "max_depth": 20,
        "min_samples_leaf": 2
    },

    "rf_50_depth15_leaf2": {
        "n_estimators": 50,
        "max_depth": 15,
        "min_samples_leaf": 2
    },

    "rf_30_depth15_leaf2": {
        "n_estimators": 30,
        "max_depth": 15,
        "min_samples_leaf": 2
    },

    "rf_30_depth12_leaf2": {
        "n_estimators": 30,
        "max_depth": 12,
        "min_samples_leaf": 2
    }
}


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("PROJECT FORESIGHT")
print("PRODUCTION FORECAST MODEL COMPARISON")
print("=" * 70)

print()
print("Loading weekly_sales.parquet...")

if not WEEKLY_PATH.exists():

    raise FileNotFoundError(
        f"weekly_sales.parquet not found:\n{WEEKLY_PATH}"
    )

weekly_sales = pd.read_parquet(
    WEEKLY_PATH
)

print(
    f"Loaded {len(weekly_sales):,} rows."
)


# ============================================================
# VALIDATE COLUMNS
# ============================================================

required_columns = (
    FEATURES
    + [TARGET]
)

missing_columns = [
    column
    for column in required_columns
    if column not in weekly_sales.columns
]

if missing_columns:

    raise ValueError(
        "Missing required columns:\n"
        + "\n".join(missing_columns)
    )

print("✓ All required columns found")


# ============================================================
# SORT DATA
# ============================================================

if "date" in weekly_sales.columns:

    weekly_sales["date"] = pd.to_datetime(
        weekly_sales["date"]
    )

    weekly_sales = (
        weekly_sales
        .sort_values("date")
        .reset_index(drop=True)
    )


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================
#
# EXACTLY MATCHES ORIGINAL NOTEBOOK:
#
# train_size = int(len(weekly_sales) * 0.8)
# train = weekly_sales.iloc[:train_size]
# test = weekly_sales.iloc[train_size:]
#
# ============================================================

train_size = int(
    len(weekly_sales) * 0.8
)

train = weekly_sales.iloc[
    :train_size
]

test = weekly_sales.iloc[
    train_size:
]

print()
print("=" * 70)
print("TRAIN / TEST SPLIT")
print("=" * 70)

print(
    f"Train rows: {len(train):,}"
)

print(
    f"Test rows:  {len(test):,}"
)


# ============================================================
# FEATURES / TARGET
# ============================================================

X_train = train[
    FEATURES
]

y_train = train[
    TARGET
]

X_test = test[
    FEATURES
]

y_test = test[
    TARGET
]


print()
print(
    f"Features: {len(FEATURES)}"
)

print(
    f"Target: {TARGET}"
)


# ============================================================
# RESULTS STORAGE
# ============================================================

results = []


# ============================================================
# TRAIN CANDIDATES
# ============================================================

for name, params in CANDIDATES.items():

    print()
    print("=" * 70)
    print(f"TRAINING: {name}")
    print("=" * 70)

    print(
        "Parameters:",
        params
    )

    start_time = time.time()


    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    model = RandomForestRegressor(

        n_estimators=params[
            "n_estimators"
        ],

        max_depth=params[
            "max_depth"
        ],

        min_samples_leaf=params[
            "min_samples_leaf"
        ],

        random_state=42,

        n_jobs=-1
    )


    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    model.fit(
        X_train,
        y_train
    )


    training_time = (
        time.time()
        - start_time
    )


    # --------------------------------------------------------
    # PREDICT
    # --------------------------------------------------------

    predictions = model.predict(
        X_test
    )


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )


    # --------------------------------------------------------
    # SAVE TEMP MODEL
    # --------------------------------------------------------

    model_path = (
        MODEL_DIR
        / f"{name}.pkl"
    )

    joblib.dump(
        model,
        model_path,
        compress=3
    )


    # --------------------------------------------------------
    # FILE SIZE
    # --------------------------------------------------------

    size_mb = (
        model_path.stat().st_size
        / 1024
        / 1024
    )


    # --------------------------------------------------------
    # MAX TREE DEPTH
    # --------------------------------------------------------

    tree_depths = [
        estimator.tree_.max_depth
        for estimator
        in model.estimators_
    ]

    average_tree_depth = (
        np.mean(tree_depths)
    )

    maximum_tree_depth = (
        np.max(tree_depths)
    )


    # --------------------------------------------------------
    # STORE RESULT
    # --------------------------------------------------------

    results.append({

        "model":
            name,

        "n_estimators":
            params["n_estimators"],

        "max_depth":
            params["max_depth"],

        "min_samples_leaf":
            params["min_samples_leaf"],

        "MAE":
            mae,

        "RMSE":
            rmse,

        "R2":
            r2,

        "size_MB":
            size_mb,

        "training_seconds":
            training_time,

        "avg_tree_depth":
            average_tree_depth,

        "max_tree_depth":
            maximum_tree_depth
    })


    # --------------------------------------------------------
    # PRINT RESULT
    # --------------------------------------------------------

    print()
    print(
        f"MAE:              {mae:.4f}"
    )

    print(
        f"RMSE:             {rmse:.4f}"
    )

    print(
        f"R²:               {r2:.4f}"
    )

    print(
        f"Model size:       {size_mb:.2f} MB"
    )

    print(
        f"Training time:    {training_time:.2f} sec"
    )

    print(
        f"Average depth:    {average_tree_depth:.2f}"
    )

    print(
        f"Maximum depth:    {maximum_tree_depth}"
    )


# ============================================================
# RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(
    results
)


results_df = (
    results_df
    .sort_values(
        by="RMSE"
    )
    .reset_index(drop=True)
)


print()
print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_path = (
    MODEL_DIR
    / "production_model_comparison.csv"
)

results_df.to_csv(
    results_path,
    index=False
)


# ============================================================
# SELECT PRODUCTION MODEL
# ============================================================
#
# We don't automatically choose simply by lowest RMSE.
#
# We want a model that:
#
# 1. Has good forecasting performance
# 2. Is substantially smaller
# 3. Is suitable for Streamlit Cloud
#
# For now, display the candidates and let us inspect them
# before replacing the current production model.
# ============================================================

print()
print("=" * 70)
print("FILES CREATED")
print("=" * 70)

for path in sorted(
    MODEL_DIR.glob(
        "rf_*.pkl"
    )
):

    size_mb = (
        path.stat().st_size
        / 1024
        / 1024
    )

    print(
        f"{path.name:<35}"
        f"{size_mb:>10.2f} MB"
    )


print()
print("=" * 70)
print("COMPARISON COMPLETE")
print("=" * 70)

print()
print(
    "IMPORTANT:"
)

print(
    "No existing production model was replaced."
)

print(
    "Review the metrics above before selecting "
    "the replacement model."
)

print("=" * 70)