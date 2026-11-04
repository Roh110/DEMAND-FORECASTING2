import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.backend import (
    get_risk_summary,
    get_risk_distribution,
    get_risk_products,
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Inventory Risk Analysis",
    page_icon="⚠️",
    layout="wide"
)

# ============================================================
# LOAD RISK DATA
# ============================================================

try:
    summary = get_risk_summary()
    distribution_df = get_risk_distribution()

except Exception as e:
    st.error(
        f"❌ Unable to load Project FORESIGHT risk data: {e}"
    )
    st.stop()

# ============================================================
# HEADER
# ============================================================

st.title("⚠️ Inventory Risk Analysis")

st.markdown(
    """
    Analyze inventory health, identify products requiring attention,
    and support data-driven inventory decisions using the Project
    FORESIGHT risk-scoring engine.
    """
)

st.divider()

# ============================================================
# RISK SUMMARY
# ============================================================

st.header("📊 Risk Distribution")

total_products = summary["total_products"]
markdown_count = summary["markdown"]
reorder_count = summary["reorder_now"]
healthy_count = summary["healthy"]
watch_count = summary["watch"]

# ============================================================
# SUMMARY METRICS
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Products", f"{total_products:,}")

with col2:
    st.metric("Markdown", f"{markdown_count:,}")

with col3:
    st.metric("Reorder Now", f"{reorder_count:,}")

with col4:
    st.metric("Healthy", f"{healthy_count:,}")

with col5:
    st.metric("Watch", f"{watch_count:,}")

st.divider()

# ============================================================
# PIE CHART
# ============================================================

if not distribution_df.empty:

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.pie(
        distribution_df["count"],
        labels=distribution_df["action"],
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.70,
        labeldistance=1.08
    )

    ax.set_title(
        "Inventory Risk Distribution",
        pad=15
    )

    ax.axis("equal")
    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ============================================================
# DISTRIBUTION TABLE
# ============================================================

st.subheader("📋 Risk Distribution Details")

display_distribution = distribution_df.copy()

if not display_distribution.empty:

    display_distribution["count"] = (
        display_distribution["count"]
        .map(lambda x: f"{x:,}")
    )

    display_distribution["percentage"] = (
        display_distribution["percentage"]
        .map(lambda x: f"{x:.2f}%")
    )

    display_distribution.columns = [
        "Action",
        "Products",
        "Percentage"
    ]

    st.dataframe(
        display_distribution,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ============================================================
# FILTER BY ACTION
# ============================================================

st.header("🔎 Filter by Action")

action_options = (
    distribution_df["action"].tolist()
    if not distribution_df.empty
    else []
)

if action_options:

    selected_action = st.selectbox(
        "Choose Action",
        action_options
    )

    # ========================================================
    # LOAD PRODUCTS FOR SELECTED ACTION
    # ========================================================

    try:
        products_df = get_risk_products(
            selected_action
        )

    except Exception as e:
        st.error(
            f"❌ Unable to load products: {e}"
        )
        products_df = pd.DataFrame()

    st.write(
        f"**Total products: {len(products_df):,}**"
    )

    if not products_df.empty:

        st.dataframe(
            products_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No products found for this action."
        )

st.divider()

# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

st.header("📌 Executive Summary")

if total_products > 0:

    markdown_percentage = (
        markdown_count / total_products * 100
    )

    reorder_percentage = (
        reorder_count / total_products * 100
    )

    watch_percentage = (
        watch_count / total_products * 100
    )

    healthy_percentage = (
        healthy_count / total_products * 100
    )

else:

    markdown_percentage = 0
    reorder_percentage = 0
    watch_percentage = 0
    healthy_percentage = 0

st.markdown(
    f"""
    - **{markdown_percentage:.2f}%** of products require markdown strategies.

    - **{reorder_percentage:.2f}%** of products need immediate replenishment.

    - **{watch_percentage:.2f}%** of products should be monitored closely.

    - **{healthy_percentage:.2f}%** of products are currently classified as healthy.

    - Inventory optimization can help reduce stockouts,
      control excess inventory, and improve profitability.
    """
)

st.divider()

# ============================================================
# KEY BUSINESS INSIGHT
# ============================================================

st.header("💡 Key Business Insight")

st.info(
    f"""
    **Inventory surplus is the dominant risk.**

    {markdown_percentage:.2f}% of products are classified as
    **MARKDOWN**. This suggests that reducing excess inventory
    through promotional campaigns, discounts, or optimized pricing
    should be a major business priority.
    """
)

st.warning(
    f"""
    **Replenishment is also a significant priority.**

    {reorder_percentage:.2f}% of products are classified as
    **REORDER NOW**. These products should be prioritized to
    reduce potential stockout risk.
    """
)

st.warning(
    f"""
    **The proportion of healthy inventory is relatively low.**

    Only {healthy_percentage:.2f}% of products are currently
    classified as **HEALTHY**. Inventory policies should therefore
    be reviewed regularly.
    """
)

st.success(
    """
    **Overall recommendation:** Prioritize excess-inventory reduction
    while simultaneously protecting the availability of products
    requiring immediate replenishment.
    """
)

st.divider()

# ============================================================
# RECOMMENDED ACTIONS
# ============================================================

st.header("💡 Recommended Actions")

st.success(
    f"""
    ✅ **Immediately reorder products marked as REORDER NOW.**

    There are **{reorder_count:,} products** requiring immediate
    replenishment to reduce the risk of stockouts.
    """
)

st.warning(
    f"""
    ⚠️ **Monitor WATCH products carefully.**

    There are **{watch_count:,} products** that require closer
    inventory monitoring before taking further action.
    """
)

st.info(
    f"""
    📦 **Launch promotional campaigns or markdown strategies
    for MARKDOWN products.**

    There are **{markdown_count:,} products** classified as
    markdown candidates. Promotional pricing can help reduce
    excess inventory.
    """
)

st.success(
    f"""
    💰 **Maintain the current stock strategy for HEALTHY products.**

    There are **{healthy_count:,} healthy products** that currently
    do not require major inventory intervention.
    """
)

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Project FORESIGHT • Inventory Risk Analysis powered by Streamlit-native backend"
)