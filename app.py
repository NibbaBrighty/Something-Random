import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Property Developer Dashboard", layout="wide")

# ------------------------------------------------------------------
# Helper: load data from a file path or an uploaded BytesIO object
# ------------------------------------------------------------------
def load_data_from_source(source):
    try:
        df = pd.read_pickle(source)
    except Exception as e:
        st.error(f"Failed to load pickle file: {e}")
        st.stop()

    # Find the Transaction Price column
    price_cols = [c for c in df.columns if 'Transaction Price' in c]
    if not price_cols:
        st.error("No column contains 'Transaction Price'. Please check your data.")
        st.stop()
    price_col = price_cols[0]

    # Clean Price
    df['Price'] = (
        df[price_col]
        .astype(str)
        .str.replace(r'[RM,]', '', regex=True)
        .pipe(pd.to_numeric, errors='coerce')
        .fillna(0)
    )

    # Clean Area
    if 'Main Floor Area' not in df.columns:
        st.error("Column 'Main Floor Area' not found. Please check your data.")
        st.stop()
    df['Area'] = pd.to_numeric(df['Main Floor Area'], errors='coerce').fillna(0)

    # Standardize categorical columns
    cols_to_clean = ["State", "District", "Tenure", "Property Type"]
    for col in cols_to_clean:
        if col in df.columns:
            df[col] = df[col].fillna('').astype(str).str.strip()
        else:
            st.warning(f"Column '{col}' not found – skipping cleaning.")

    return df

# ------------------------------------------------------------------
# Main page: Drag & Drop uploader (with fallback to default file)
# ------------------------------------------------------------------
st.title("Property Developer Dashboard")

uploaded_file = st.file_uploader(
    "Drag and drop your pickle file (.pkl) here, or click to browse",
    type=["pkl"],
    label_visibility="visible"
)

if uploaded_file is None:
    # Try to load the default file from the script's folder (portable)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, 'final_dataset.pkl')
    if os.path.exists(default_path):
        with st.spinner("Loading default dataset..."):
            tx = load_data_from_source(default_path)
    else:
        st.error("No file uploaded and 'final_dataset.pkl' not found. Please upload a pickle file.")
        st.stop()
else:
    with st.spinner("Loading uploaded dataset..."):
        tx = load_data_from_source(uploaded_file)

# ------------------------------------------------------------------
# Sidebar Filters (all original logic, unchanged)
# ------------------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    all_states = sorted(tx["State"].unique())
    selected_states = st.multiselect("State", all_states)
    if selected_states:
        available_districts = sorted(tx[tx["State"].isin(selected_states)]["District"].unique())
    else:
        available_districts = sorted(tx["District"].unique())
    selected_districts = st.multiselect("District", available_districts)
    selected_tenure = st.multiselect("Tenure", sorted(tx["Tenure"].unique()))
    selected_types = st.multiselect("Property Type", sorted(tx["Property Type"].unique()))
    max_price = int(tx["Price"].max()) if tx["Price"].max() > 0 else 1000000
    max_budget = st.number_input("Max Budget (RM)", value=max_price)
    analysis = st.selectbox("View", [
        "1. Market Demand",
        "2. Market Concentration",
        "3. Market Value Analysis",
        "4. Price Efficiency",
        "5. Market Risk Assessment",
        "6. Market Valuation Benchmarks"
    ])

# ------------------------------------------------------------------
# Filtering logic
# ------------------------------------------------------------------
filtered_df = tx.copy()
if selected_states:
    filtered_df = filtered_df[filtered_df["State"].isin(selected_states)]
if selected_districts:
    filtered_df = filtered_df[filtered_df["District"].isin(selected_districts)]
if selected_tenure:
    filtered_df = filtered_df[filtered_df["Tenure"].isin(selected_tenure)]
if selected_types:
    filtered_df = filtered_df[filtered_df["Property Type"].isin(selected_types)]
filtered_df = filtered_df[filtered_df["Price"] <= max_budget]

# ------------------------------------------------------------------
# Main Dashboard
# ------------------------------------------------------------------
st.title(analysis)

has_filter = (len(selected_states) > 0) or (len(selected_districts) > 0) or \
             (len(selected_tenure) > 0) or (len(selected_types) > 0)

if not filtered_df.empty and filtered_df['Price'].mean() > 0:
    volatility_metric = (filtered_df['Price'].std() / filtered_df['Price'].mean()) * 100
else:
    volatility_metric = 0.0

if not has_filter:
    st.info("Please select at least one filter in the sidebar (e.g., State or District) to begin analysis.")
elif filtered_df.empty:
    st.warning("No matching data found. Please check your filter criteria.")
else:
    st.markdown("#### Strategic Development Overview")
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("Market Volume", f"{len(filtered_df):,}")
        col2.metric("Avg. Transaction (RM)", f"{filtered_df['Price'].mean():,.0f}")
        col3.metric("Volatility Index", f"{volatility_metric:.1f}%")

    # Analysis sections
    if analysis == "1. Market Demand":
        st.subheader("Market Demand by District")
        demand_df = filtered_df.groupby("District").size().reset_index(name="Transaction Count")
        fig = px.bar(
            demand_df,
            x="District",
            y="Transaction Count",
            labels={"District": "District Area", "Transaction Count": "Total Transactions"},
            color="Transaction Count",
            color_continuous_scale="Blues"
        )
        fig.update_layout(
            xaxis_title="District (Area)",
            yaxis_title="Total Transaction Volume",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.write("Note: This chart shows the transaction activity in each area. The higher the transaction volume, the stronger the market absorption capacity.")

    elif analysis == "2. Market Concentration":
        st.subheader("Market Concentration by District")
        df_count = filtered_df.groupby("District").size().reset_index(name="Count")
        df_count = df_count.sort_values(by="Count", ascending=False)
        if len(df_count) > 10:
            top_10 = df_count.head(10).copy()
            others_count = df_count.iloc[10:]['Count'].sum()
            others_df = pd.DataFrame({'District': ['Others'], 'Count': [others_count]})
            df_count = pd.concat([top_10, others_df])
        fig = px.pie(df_count, values="Count", names="District",
                     title="Market Share Contribution by District",
                     hole=0.4,
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
        st.write("Note: For clarity, only the top 10 market clusters are displayed, with the remaining areas grouped under 'Others'.")

    elif analysis == "3. Market Value Analysis":
        st.subheader("Market Value Analysis: Price vs Area")
        clean_df = filtered_df[
            (filtered_df['Price'] > 0) &
            (filtered_df['Area'] > 0) &
            (filtered_df['Area'] < 50000) &
            (filtered_df['Property Type'].notna()) &
            (filtered_df['Property Type'] != '') &
            (filtered_df['Property Type'] != 'nan')
        ].copy()
        if not clean_df.empty:
            fig = px.scatter(
                clean_df,
                x="Area",
                y="Price",
                color="Property Type",
                hover_data=["District", "Tenure"],
                title="Property Price vs. Floor Area",
                template="plotly_white"
            )
            fig.update_layout(xaxis_title="Floor Area (sqft)", yaxis_title="Transaction Price (RM)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Insufficient data available for this analysis under current filters.")

    elif analysis == "4. Price Efficiency":
        efficiency_df = filtered_df[filtered_df['Area'] > 0].copy()
        efficiency_df['PricePerSqft'] = efficiency_df['Price'] / efficiency_df['Area']
        avg_efficiency = efficiency_df.groupby("District")['PricePerSqft'].mean().reset_index()
        avg_efficiency = avg_efficiency[avg_efficiency['PricePerSqft'] < 5000]
        fig = px.bar(avg_efficiency.sort_values(by='PricePerSqft'),
                     x="District", y="PricePerSqft",
                     title="Average Price per sqft (RM) by District",
                     color="PricePerSqft",
                     color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
        st.write("Note: This chart shows the average price per sqft (RM/sqft). The lower the value, the higher the relative value for money.")

    elif analysis == "5. Market Risk Assessment":
        risk_df = filtered_df.groupby("District").agg({'Price': ['mean', 'std', 'count']})
        risk_df.columns = ['AvgPrice', 'StdDev', 'Count']
        risk_df['Volatility'] = risk_df['StdDev'] / risk_df['AvgPrice'].replace(0, 1)
        mean_vol = risk_df['Volatility'].mean()
        std_vol = risk_df['Volatility'].std()
        safe_std = std_vol if std_vol > 0 else 1e-6
        risk_df['Z_Score'] = (risk_df['Volatility'] - mean_vol) / safe_std

        def get_risk_label(z):
            if z > 0.5:
                return "High"
            elif z < -0.5:
                return "Low"
            else:
                return "Medium"
        risk_df['Risk Level'] = risk_df['Z_Score'].apply(get_risk_label)

        st.subheader("Market Risk vs. Return Matrix")
        fig = px.scatter(
            risk_df, x="AvgPrice", y="Count", color="Risk Level",
            size="Volatility", hover_name=risk_df.index,
            color_discrete_map={"High": "#FF4B4B", "Medium": "#FFA500", "Low": "#00CC96"},
            title="District Liquidity vs. Price Value"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            risk_df[['Count', 'AvgPrice', 'Z_Score', 'Risk Level']]
            .sort_values(by='Z_Score', ascending=False)
            .style.format({"AvgPrice": "RM {:,.0f}", "Z_Score": "{:.2f}"}),
            use_container_width=True
        )

        st.markdown("""
        #### Risk Assessment Criteria
        We use **Z-Score** to measure price volatility deviations:
        - **High Risk**: $Z > 0.5$ (Price volatility significantly higher than market average)
        - **Medium Risk**: $-0.5 \le Z \le 0.5$ (Standard market benchmark)
        - **Low Risk**: $Z < -0.5$ (Stable price movement, lower liquidity risk)
        """)

    elif analysis == "6. Market Valuation Benchmarks":
        ranking = filtered_df.groupby("District")["Price"].mean().reset_index()
        ranking.columns = ["District", "Average Transaction Price (RM)"]
        ranking = ranking.sort_values(by="Average Transaction Price (RM)", ascending=False).reset_index(drop=True)
        ranking.index = ranking.index + 1
        st.dataframe(
            ranking.style.format({"Average Transaction Price (RM)": "RM {:,.0f}"}),
            use_container_width=True
        )

    # Strategic insights summary
    if not filtered_df.empty:
        st.divider()
        st.markdown("#### Strategic Insights")
        best_district = filtered_df.groupby("District").size().idxmax()
        st.info(f"**Market Signal:** Within the selected range, **{best_district}** exhibits the highest transaction activity and strongest market absorption capacity. We recommend prioritizing this area for further due diligence.")