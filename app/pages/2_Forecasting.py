import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.backend import (
    get_skus,
    get_forecast_history,
    get_forecast,
)

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Demand Forecasting",
    page_icon="🔮",
    layout="wide"
)

# =========================================================
# PAGE TITLE
# =========================================================

st.title("🔮 Demand Forecasting")

st.markdown(
    """
    This module uses the trained forecasting model through
    the Project FORESIGHT Streamlit-native backend to generate
    six-week demand forecasts for individual SKUs.
    """
)

st.markdown("---")

# =========================================================
# LOAD SKU LIST
# =========================================================

st.subheader("🎯 Select Product")

try:
    available_skus = get_skus()
except Exception as e:
    st.error(f"❌ Could not load SKU list: {e}")
    st.stop()

if not available_skus:
    st.warning("No SKUs are available.")
    st.stop()

selected_sku = st.selectbox(
    "Select SKU",
    available_skus
)

# =========================================================
# LOAD SELECTED SKU HISTORY
# =========================================================

try:
    sku_history = get_forecast_history(selected_sku)
except Exception as e:
    st.error(f"❌ Could not load historical data: {e}")
    st.stop()

if sku_history.empty:
    st.warning(
        f"No historical demand data found for {selected_sku}."
    )
    st.stop()

sku_history = sku_history.copy()
sku_history["date"] = pd.to_datetime(sku_history["date"])
sku_history = sku_history.sort_values("date").reset_index(drop=True)

# =========================================================
# FORECAST DATASET INFORMATION
# =========================================================

st.subheader("📊 Forecast Dataset")

total_records = len(sku_history)

col1, col2 = st.columns(2)

col1.metric("Selected SKU", selected_sku)
col2.metric("Historical Records", f"{total_records:,}")

# =========================================================
# SHOW SELECTED SKU DATA
# =========================================================

with st.expander("View Historical Demand Data"):
    st.dataframe(
        sku_history,
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# =========================================================
# HISTORICAL DEMAND
# =========================================================

st.subheader(
    f"📈 Historical Demand — {selected_sku}"
)

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    sku_history["date"],
    sku_history["quantity"],
    linewidth=1.8
)

ax.set_xlabel("Date")
ax.set_ylabel("Quantity")
ax.set_title(
    f"Historical Demand Trend for {selected_sku}"
)
ax.grid(alpha=0.3)

plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig, use_container_width=True)
plt.close(fig)

# =========================================================
# FORECAST
# =========================================================

st.markdown("---")
st.subheader("🔮 ML Demand Forecast")

if st.button(
    "Generate 6-Week Forecast",
    type="primary"
):
    with st.spinner(
        f"Generating forecast for {selected_sku}..."
    ):
        try:
            result = get_forecast(selected_sku)

            st.session_state["forecast_result"] = result
            st.session_state["forecast_sku"] = selected_sku

            st.success(
                "✅ Six-week forecast generated successfully."
            )

        except ValueError as e:
            st.error(f"❌ {e}")

        except Exception as e:
            st.error(
                f"❌ Unexpected forecasting error: {e}"
            )

# =========================================================
# DISPLAY FORECAST
# =========================================================

if (
    "forecast_result" in st.session_state
    and
    st.session_state.get("forecast_sku") == selected_sku
):

    result = st.session_state["forecast_result"]

    forecast_dates = result.get(
        "forecast_dates",
        []
    )

    forecast_values = result.get(
        "forecast",
        []
    )

    average_forecast = result.get(
        "average_forecast",
        0
    )

    latest_demand = result.get(
        "latest_demand",
        0
    )

    risk = result.get(
        "risk",
        "UNKNOWN"
    )

    # =====================================================
    # FORECAST SUMMARY
    # =====================================================

    st.markdown("---")
    st.subheader("📌 Forecast Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Latest Demand",
        f"{latest_demand:,.0f}"
    )

    col2.metric(
        "Average Forecast",
        f"{average_forecast:,.2f}"
    )

    col3.metric(
        "Forecast Horizon",
        "6 Weeks"
    )

    col4.metric(
        "Inventory Risk",
        risk
    )

    # =====================================================
    # FORECAST TABLE
    # =====================================================

    st.markdown("---")
    st.subheader("📅 Six-Week Forecast")

    forecast_df = pd.DataFrame({
        "Week": pd.to_datetime(
            forecast_dates
        ).strftime("%Y-%m-%d"),

        "Predicted Demand": forecast_values
    })

    forecast_df["Predicted Demand"] = (
        forecast_df["Predicted Demand"].round(2)
    )

    st.dataframe(
        forecast_df,
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # FORECAST CHART
    # =====================================================

    st.markdown("---")
    st.subheader("📈 Demand Forecast Trend")

    forecast_dates_plot = pd.to_datetime(
        forecast_dates
    )

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        sku_history["date"],
        sku_history["quantity"],
        label="Historical Demand",
        linewidth=1.8
    )

    ax.plot(
        forecast_dates_plot,
        forecast_values,
        marker="o",
        linestyle="--",
        linewidth=2,
        label="ML Forecast"
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Demand")

    ax.set_title(
        f"Demand Forecast for {selected_sku}"
    )

    ax.grid(alpha=0.3)
    ax.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    # =====================================================
    # INVENTORY RECOMMENDATION
    # =====================================================

    st.markdown("---")
    st.subheader("⚠️ Inventory Recommendation")

    if risk == "REORDER NOW":

        st.error(
            """
            🔴 **REORDER NOW**

            This product requires immediate replenishment
            to reduce the risk of stockouts.
            """
        )

    elif risk == "WATCH":

        st.warning(
            """
            🟡 **WATCH**

            Monitor inventory levels closely before taking
            further action.
            """
        )

    elif risk == "MARKDOWN":

        st.info(
            """
            🔵 **MARKDOWN**

            Consider promotional pricing or markdown
            strategies to reduce excess inventory.
            """
        )

    elif risk == "HEALTHY":

        st.success(
            """
            🟢 **HEALTHY**

            Current inventory position appears healthy.
            No immediate inventory intervention is required.
            """
        )

    else:

        st.warning(
            f"Risk status: **{risk}**"
        )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption(
    "Project FORESIGHT • Demand Forecasting powered by Streamlit-native backend"
)