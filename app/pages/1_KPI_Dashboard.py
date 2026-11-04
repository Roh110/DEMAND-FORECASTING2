import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.backend import (
    get_categories,
    get_skus_by_category,
    get_kpi_summary,
    get_monthly_revenue,
    get_risk_distribution,
    get_top_categories,
    get_revenue_at_risk,
)

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="KPI Dashboard",
    page_icon="📈",
    layout="wide"
)

# =========================================================
# PAGE TITLE
# =========================================================

st.title("📈 KPI Dashboard")

st.markdown(
    """
    Executive overview of revenue, profitability,
    customer activity and inventory risk.
    """
)

st.markdown("---")

# =========================================================
# DASHBOARD FILTERS
# =========================================================

st.subheader("🎯 Dashboard Filters")

col1, col2 = st.columns(2)

categories = get_categories()

with col1:
    selected_category = st.selectbox(
        "Select Category",
        ["All Categories"] + categories
    )

category_value = (
    "ALL"
    if selected_category == "All Categories"
    else selected_category
)

try:
    sku_options = get_skus_by_category(category_value)
except Exception as e:
    st.error(f"❌ Could not load SKU list: {e}")
    sku_options = []

with col2:
    selected_sku = st.selectbox(
        "Select SKU",
        ["All SKUs"] + sku_options
    )

sku_value = (
    "ALL"
    if selected_sku == "All SKUs"
    else selected_sku
)

# =========================================================
# KPI SUMMARY
# =========================================================

try:
    kpi = get_kpi_summary(category_value, sku_value)
except Exception as e:
    st.error(f"❌ Could not load KPI summary: {e}")
    st.stop()

revenue = float(kpi.get("revenue", 0))
profit = float(kpi.get("profit", 0))
customers = int(kpi.get("customers", 0))
products = int(kpi.get("products", 0))
stores = int(kpi.get("stores", 0))

st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Revenue", f"₹ {revenue / 1e9:.2f} B")
col2.metric("Profit", f"₹ {profit / 1e9:.2f} B")
col3.metric("Customers", f"{customers:,}")
col4.metric("Products", f"{products:,}")
col5.metric("Stores", f"{stores:,}")

# =========================================================
# MONTHLY REVENUE
# =========================================================

st.markdown("---")
st.subheader("📅 Monthly Revenue Trend")

try:
    monthly_df = get_monthly_revenue(
        category_value,
        sku_value
    )
except Exception as e:
    st.error(f"❌ Could not load monthly revenue: {e}")
    monthly_df = pd.DataFrame()

if monthly_df.empty:
    st.warning("No revenue data available for the selected filters.")
else:
    monthly_df = monthly_df.copy()
    monthly_df["month"] = pd.to_datetime(monthly_df["month"])
    monthly_df = monthly_df.sort_values("month")

    fig, ax = plt.subplots(figsize=(14, 5))

    ax.plot(
        monthly_df["month"],
        monthly_df["revenue"],
        linewidth=2
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (₹)")
    ax.set_title("Monthly Revenue")
    ax.grid(alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# =========================================================
# INVENTORY RISK DISTRIBUTION
# =========================================================

st.markdown("---")
st.subheader("⚠️ Inventory Risk Distribution")

try:
    risk_df = get_risk_distribution()
except Exception as e:
    st.error(f"❌ Could not load inventory risk data: {e}")
    risk_df = pd.DataFrame()

if not risk_df.empty:
    risk_lookup = {
        row["action"]: int(row["count"])
        for _, row in risk_df.iterrows()
    }

    total_products = sum(risk_lookup.values())
    markdown_count = risk_lookup.get("MARKDOWN", 0)
    reorder_count = risk_lookup.get("REORDER NOW", 0)
    healthy_count = risk_lookup.get("HEALTHY", 0)
    watch_count = risk_lookup.get("WATCH", 0)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Products", f"{total_products:,}")
    col2.metric("Markdown", f"{markdown_count:,}")
    col3.metric("Reorder Now", f"{reorder_count:,}")
    col4.metric("Healthy", f"{healthy_count:,}")
    col5.metric("Watch", f"{watch_count:,}")

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        risk_df["action"],
        risk_df["count"]
    )

    ax.set_xlabel("Recommended Action")
    ax.set_ylabel("Number of Products")
    ax.set_title("Inventory Action Distribution")

    plt.xticks(rotation=30)
    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# =========================================================
# TOP CATEGORIES
# =========================================================

st.markdown("---")
st.subheader("🛒 Top Categories")

try:
    category_df = get_top_categories(
        category_value,
        sku_value
    )
except Exception as e:
    st.error(f"❌ Could not load category data: {e}")
    category_df = pd.DataFrame()

if not category_df.empty:
    category_df = category_df.sort_values(
        "revenue",
        ascending=False
    )

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.bar(
        category_df["category"],
        category_df["revenue"]
    )

    ax.set_title("Top Revenue Categories")
    ax.set_xlabel("Category")
    ax.set_ylabel("Revenue (₹)")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
else:
    st.warning("No category revenue data available.")

# =========================================================
# TOP REVENUE-AT-RISK PRODUCTS
# =========================================================

st.markdown("---")
st.subheader("🚨 Top Revenue-at-Risk Products")

try:
    revenue_risk_df = get_revenue_at_risk()
except Exception as e:
    st.error(f"❌ Could not load revenue-at-risk data: {e}")
    revenue_risk_df = pd.DataFrame()

if not revenue_risk_df.empty:
    revenue_risk_df = revenue_risk_df.rename(
        columns={
            "sku_id": "SKU",
            "revenue": "Revenue at Risk (₹)"
        }
    )

    revenue_risk_df["Revenue at Risk (₹)"] = (
        revenue_risk_df["Revenue at Risk (₹)"].round(2)
    )

    st.dataframe(
        revenue_risk_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No revenue-at-risk products found.")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption(
    "Project FORESIGHT • KPI Dashboard powered by Streamlit-native backend"
)