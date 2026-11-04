import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.backend import (
    get_risk_summary,
    get_risk_distribution,
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Business Recommendations",
    page_icon="💡",
    layout="wide"
)

# ============================================================
# LOAD DATA
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
# EXTRACT VALUES
# ============================================================

total_products = summary["total_products"]
markdown_count = summary["markdown"]
reorder_count = summary["reorder_now"]
healthy_count = summary["healthy"]
watch_count = summary["watch"]

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

# ============================================================
# HEADER
# ============================================================

st.title("💡 Business Recommendations")

st.markdown(
    """
    Use inventory risk insights to identify immediate actions,
    optimize stock levels, reduce excess inventory, and improve
    overall business performance.
    """
)

st.divider()

# ============================================================
# RECOMMENDATION SUMMARY
# ============================================================

st.header("📌 Recommendation Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🔴 Reorder Immediately",
        f"{reorder_count:,}",
        f"{reorder_percentage:.2f}%"
    )

with col2:
    st.metric(
        "🟡 Watch Closely",
        f"{watch_count:,}",
        f"{watch_percentage:.2f}%"
    )

with col3:
    st.metric(
        "🟢 Healthy Products",
        f"{healthy_count:,}",
        f"{healthy_percentage:.2f}%"
    )

with col4:
    st.metric(
        "🔵 Markdown Required",
        f"{markdown_count:,}",
        f"{markdown_percentage:.2f}%"
    )

st.divider()

# ============================================================
# RECOMMENDATION DISTRIBUTION
# ============================================================

st.header("📊 Recommendation Distribution")

if not distribution_df.empty:

    fig, ax = plt.subplots(figsize=(10, 5))

    bars = ax.bar(
        distribution_df["action"],
        distribution_df["count"]
    )

    for bar in bars:

        height = bar.get_height()

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height):,}",
            ha="center",
            va="bottom",
            fontsize=10
        )

    ax.set_xlabel("Inventory Action")
    ax.set_ylabel("Number of Products")
    ax.set_title("Inventory Recommendation Distribution")

    plt.xticks(rotation=0)
    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.divider()

# ============================================================
# PRIORITY ACTIONS
# ============================================================

st.header("📋 Priority Actions")

st.success(
    f"""
    ✅ **Immediately reorder products marked as REORDER NOW.**

    There are **{reorder_count:,} products ({reorder_percentage:.2f}%)**
    requiring immediate replenishment. Prioritizing these products
    can help reduce potential stockout risk.
    """
)

st.warning(
    f"""
    ⚠️ **Monitor WATCH products carefully.**

    There are **{watch_count:,} products ({watch_percentage:.2f}%)**
    that require closer inventory monitoring before further action
    is taken.
    """
)

st.info(
    f"""
    📦 **Reduce excess inventory through markdown strategies.**

    There are **{markdown_count:,} products ({markdown_percentage:.2f}%)**
    classified as MARKDOWN candidates. Promotional campaigns,
    discounts, and optimized pricing can help improve inventory
    turnover.
    """
)

st.success(
    f"""
    💰 **Maintain the current stock strategy for HEALTHY products.**

    There are **{healthy_count:,} products ({healthy_percentage:.2f}%)**
    currently classified as healthy and not requiring major
    inventory intervention.
    """
)

st.divider()

# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

st.header("📌 Executive Summary")

st.markdown(
    f"""
    - **{markdown_percentage:.2f}%** of products require
      markdown strategies.

    - **{reorder_percentage:.2f}%** of products need
      immediate replenishment.

    - **{watch_percentage:.2f}%** of products should
      be monitored closely.

    - **{healthy_percentage:.2f}%** of products are
      currently classified as healthy.

    - Inventory optimization should balance **excess-inventory
      reduction** with **stockout prevention**.
    """
)

st.divider()

# ============================================================
# KEY BUSINESS INSIGHTS
# ============================================================

st.header("💡 Key Business Insights")

if markdown_percentage >= 50:

    st.info(
        f"""
        **Inventory surplus is the dominant business risk.**

        **{markdown_percentage:.2f}%** of products are classified
        as MARKDOWN. This indicates a substantial amount of inventory
        may require promotional pricing, discounts, or other
        inventory-reduction strategies.

        **Business priority:** Improve inventory turnover and
        reduce carrying costs.
        """
    )

else:

    st.info(
        f"""
        **Markdown inventory remains an important consideration.**

        **{markdown_percentage:.2f}%** of products are classified
        as MARKDOWN and should be reviewed for inventory-reduction
        opportunities.
        """
    )

if reorder_percentage >= 15:

    st.warning(
        f"""
        **Replenishment is a significant operational priority.**

        **{reorder_percentage:.2f}%** of products are classified
        as REORDER NOW.

        **Business priority:** Protect product availability and
        reduce the probability of stockouts.
        """
    )

else:

    st.warning(
        f"""
        **Replenishment requirements should continue to be monitored.**

        **{reorder_percentage:.2f}%** of products are classified
        as REORDER NOW.
        """
    )

if healthy_percentage < 20:

    st.warning(
        f"""
        **The proportion of healthy inventory is relatively low.**

        Only **{healthy_percentage:.2f}%** of products are currently
        classified as HEALTHY.

        **Business priority:** Regularly review inventory policies,
        demand forecasts, and replenishment strategies.
        """
    )

else:

    st.success(
        f"""
        **A reasonable portion of inventory is currently healthy.**

        **{healthy_percentage:.2f}%** of products are classified
        as HEALTHY and currently require no major intervention.
        """
    )

# ============================================================
# OVERALL BUSINESS PRIORITY
# ============================================================

st.divider()
st.header("🎯 Overall Business Priority")

if markdown_percentage >= 50 and reorder_percentage >= 15:

    st.success(
        """
        **Balance excess-inventory reduction with stockout prevention.**

        The inventory portfolio shows two simultaneous priorities:
        reducing excess inventory through markdown strategies while
        ensuring products requiring immediate replenishment remain
        available.
        """
    )

elif markdown_percentage >= 50:

    st.info(
        """
        **Prioritize excess-inventory reduction.**

        The dominant inventory risk is surplus stock. Promotional
        campaigns, optimized pricing, and inventory turnover
        strategies should receive priority.
        """
    )

elif reorder_percentage >= 15:

    st.warning(
        """
        **Prioritize replenishment and stock availability.**

        A significant proportion of products require immediate
        replenishment. Procurement and stock allocation should
        focus on reducing potential stockouts.
        """
    )

else:

    st.success(
        """
        **Maintain balanced inventory management.**

        Continue monitoring inventory levels while maintaining
        current replenishment and stock-control strategies.
        """
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Project FORESIGHT • Business Recommendations powered by Streamlit-native backend"
)