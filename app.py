import streamlit as st
import plotly.express as px
import pandas as pd
import Model
import DatabaseConfig as db
import Download

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
        }
        
        .stButton>button {
            background-color:#1E90FF;
            color:white;
            font-size:16px;
            border-radius:8px;
        }

        .stButton>button:hover {
            background-color:#187bcd;
        }
            
        .upload-box {
            background: #ffffff;
            padding: 20px;
            border-radius: 12px;
            border: 2px #4a90e2;
            text-align: left;
            color: #003366;
            font-size: 18px;
            font-weight: 600;
            transition: 0.3s;
        }
        .upload-box:hover {
            border-color: #005bb5;
            background: #f0f6ff;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:  
    st.markdown("<h1 style='color: #003366; font-size: 50px;'>Churn Prediction Dashboard</h1>", unsafe_allow_html=True)
    refresh = st.button("🔄️ Cloud Sync")
    if refresh:
        with st.spinner("☁️ Syncing data from cloud to database..."):
            success, message = Download.load_s3_csvs_to_postgres()

        # Spinner is now CLOSED

        if success:
            st.session_state.refresh_done = True
            st.rerun()
        else:
            st.session_state.refresh_done = False
            st.error(message)
            st.stop()

    if st.session_state.get("refresh_done"):
        st.success("✅ Data synced successfully")
        st.session_state.refresh_done = False


            
        
    st.markdown("<h3 class='upload-box' style='color: #2ECC71;'>📁 Database Tables</h3>", unsafe_allow_html=True)

    # uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    city = st.selectbox(
    "Select table in database:",
    ["-- Select --"]+db.table_names()
        )

    st.write("You selected:", city if city != "-- Select --" else "None")

    if st.button("Submit"):
        df_inpt = db.fetch_data(f'SELECT * FROM {city}')
        df_inpt = db.preprocess_df(df_inpt)
        if df_inpt is not None:

            # df_input = pd.read_csv(uploaded_file)
            df = Model.predict_churn(df_inpt)
            df['Churn'] = df['Churn'].map({0: 'Not Churn', 1: 'Churn'})
            # ---- Pie Chart ----
            if 'Churn' in df.columns:

                churn_count = df["Churn"].value_counts().reset_index()
                churn_count.columns = ["Churn Status", "Count"]
                fig = px.pie(
                    churn_count,
                    names="Churn Status",
                    values="Count",
                    title="Churn vs Not Churn",
                    color_discrete_sequence=["#00A8E8", "#FF5733"]
                )
                fig.update_layout(width=500, height=400)
                fig.update_traces(
                    hovertemplate="<b>%{label}</b><br>"
                                  "Customers: <b>%{value}</b><br>"
                                  "Percentage: <b>%{percent}</b><extra></extra>",
                    pull=[0, 0.1]
                )

                st.plotly_chart(fig)
                st.write("### Accuracy: 92.08%")
            else:
                st.error("Prediction failed.")

        else:
            st.error("Please upload a CSV file before submitting.")


# ----------------- COLUMN 2 (Runs only when df exists) -----------------
with col2:
    if "df" in locals():   # check if df is created
        st.markdown("<h3 style='color: #2ECC71; padding: 15px; text-align: left;'>Churned Customers</h3>", unsafe_allow_html=True)
        st.dataframe(
                    df[df['Churn'] == 'Churn'].reset_index(drop=True),
                    height=340,
                    use_container_width=True
                )

        st.markdown("<h3 style='color: #2ECC71;'>&nbsp;&nbsp;Non-Churned Customers</h3>", unsafe_allow_html=True)
        st.dataframe(
                    df[df['Churn'] == 'Not Churn'].reset_index(drop=True),
                    height=340,
                    use_container_width=True
                )
    