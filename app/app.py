import streamlit as st

st.set_page_config(

    page_title="Project FORESIGHT",

    page_icon="📊",

    layout="wide"

)

st.title("📊 Project FORESIGHT")

st.markdown(
    """
    ## Retail Demand Forecasting and Inventory Optimization

    Welcome to the Project FORESIGHT dashboard.

    This application helps retail businesses:

    - 📈 Analyze sales trends
    - 🔮 Forecast future demand
    - ⚠️ Identify inventory risks
    - 💰 Optimize stock levels
    - 📊 Generate business recommendations
    """
)

st.markdown("---")

st.subheader("📂 Dashboard Pages")

st.info(
    """
    Select a page from the sidebar:

    1. KPI Dashboard
    2. Forecasting
    3. Risk Analysis
    4. Recommendations
    """
)

st.markdown("---")

st.subheader("📌 Project Summary")

col1, col2 = st.columns(2)

with col1:

    st.metric("Stores", 30)

    st.metric("Customers", 10000)

with col2:

    st.metric("Products", 5000)

    st.metric("Years Covered", "2022–2025")

st.markdown("---")

st.success("Use the sidebar to explore the dashboard.")