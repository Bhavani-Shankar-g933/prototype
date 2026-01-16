import streamlit as st
import plotly.express as px
import pandas as pd
import Model
import DatabaseConfig as db
import Download

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Churn Prediction Dashboard",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    background-color: #f9f9f9;
}

.stButton>button {
    background-color:#1E90FF;
    color:white;
    font-size:15px;
    border-radius:8px;
    padding: 6px 14px;
    font-weight: bold;
}
.stButton>button:hover {
    background-color:#187bcd;
}

h1 {
    color:#003366;
    margin-bottom: 15px;
}

.stMetricLabel {
    font-weight: bold;
    color:#003366;
}

.stMetricValue {
    font-size: 22px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LAYOUT ----------------
left_col, right_col = st.columns([1, 1])

# ================= LEFT COLUMN =================
with left_col:

    # Dashboard title
    st.markdown("""
        <h1 style="background: linear-gradient(90deg, #1E90FF, #003366);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: bold;
                font-size: 36px;">
        <img src="https://cdn-icons-png.flaticon.com/512/679/679948.png" width="40" style="vertical-align: middle; margin-right:10px;">
        Churn Prediction Dashboard
        </h1>
        """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

    # Cloud Sync button
    refresh = st.button("🔄 Cloud Sync")
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

    if refresh:
        with st.spinner("☁️ Syncing data from cloud to database..."):
            success, message = Download.load_s3_csvs_to_postgres()
        if success:
            st.success("✅ Data synced successfully")
            st.rerun()
        else:
            st.error(message)
            st.stop()

    # Table selection
    st.markdown("### 📁 Database Tables")
    st.markdown("<div style='margin-top:5px'></div>", unsafe_allow_html=True)

    city = st.selectbox(
        "Select table in database:",
        ["-- Select --"] + db.table_names()
    )

    st.markdown("<div style='margin-top:5px'></div>", unsafe_allow_html=True)

    # Submit button
    submit_clicked = st.button("Submit")
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

    # Model prediction & accuracy
    if submit_clicked and city != "-- Select --":
        df_input = db.fetch_data(f"SELECT * FROM {city}")
        df_input = db.preprocess_df(df_input)

        if df_input is not None:
            df = Model.predict_churn(df_input)
            df["Churn"] = df["Churn"].map({0: "Not Churn", 1: "Churn"})
            st.markdown("<span style='color:#2ECC71; font-weight:bold;'>🎯 Model Accuracy: 92.08%</span>", unsafe_allow_html=True)
        else:
            st.error("Failed to load data")

# ================= RIGHT COLUMN =================
with right_col:

    st.markdown("<div style='margin-top:30px'></div>", unsafe_allow_html=True)

    if "df" in locals():
        st.markdown("<h2 style='color:#003366; font-weight:bold;'>🔵 Churn Distribution</h2>", unsafe_allow_html=True)
        # st.markdown("<> 🔵 Churn Distribution")

        # Metrics with colors matching pie chart
        total_customers = len(df)
        churn_count_num = (df["Churn"] == "Churn").sum()
        not_churn_count = (df["Churn"] == "Not Churn").sum()

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.markdown(f"<h4 style='color:#003366; font-weight:bold;'>Total<br>{total_customers}</h4>", unsafe_allow_html=True)
        metric_col2.markdown(f"<h4 style='color:#E74C3C; font-weight:bold;'>Churn<br>{churn_count_num}</h4>", unsafe_allow_html=True)
        metric_col3.markdown(f"<h4 style='color:#2ECC71; font-weight:bold;'>Not Churn<br>{not_churn_count}</h4>", unsafe_allow_html=True)

        # Pie chart / donut chart
        churn_count = df["Churn"].value_counts().reset_index()
        churn_count.columns = ["Churn Status", "Count"]

        donut_fig = px.pie(
            churn_count,
            names="Churn Status",
            values="Count",
            hole=0.4,
            color_discrete_map={
                "Churn": "#E74C3C",
                "Not Churn": "#2ECC71"
            }
        )

        donut_fig.update_layout(
            height=350,
            width=None,
            font=dict(size=12, color="#003366"),
            margin=dict(t=50, b=25, l=25, r=25),
            legend_title_text="Status",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        donut_fig.update_traces(
            textinfo="percent+label",
            textposition="inside",
            hovertemplate="<b>%{label}</b><br>Customers: %{value}<br>Percentage: %{percent}<extra></extra>"
        )

        st.plotly_chart(donut_fig, use_container_width=True)

# ================= DATA TABLES (FULL WIDTH) =================
st.markdown("---")
st.markdown("## 👥 Customer Segments")

if "df" in locals():
    # Churned customers - full width
    with st.expander("🔴 Churned Customers", expanded=True):
        st.dataframe(df[df["Churn"] == "Churn"].reset_index(drop=True), height=320, use_container_width=True)

    # Non-Churned customers - full width
    with st.expander("🟢 Non-Churned Customers"):
        st.dataframe(df[df["Churn"] == "Not Churn"].reset_index(drop=True), height=320, use_container_width=True)
