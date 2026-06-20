import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

st.set_page_config(page_title="Property Developer Dashboard", layout="wide")

def load_data_from_source(source):
    try:
        df = pd.read_pickle(source)
    except Exception as e:
        st.error(f"Failed to load pickle file: {e}")
        sys.exit()

    price_cols = [c for c in df.columns if 'Transaction Price' in c]
    if not price_cols:
        st.error("No column contains 'Transaction Price'. Please check your data.")
        sys.exit()
    price_col = price_cols[0]

    df['Price'] = (
        df[price_col]
        .astype(str)
        .str.replace(r'[RM,]', '', regex=True)
        .pipe(pd.to_numeric, errors='coerce')
        .fillna(0)
    )

    if 'Main Floor Area' not in df.columns:
        st.error("Column 'Main Floor Area' not found. Please check your data.")
        sys.exit()
    df['Area'] = pd.to_numeric(df['Main Floor Area'], errors='coerce').fillna(0)

    cols_to_clean = ["State", "District", "Tenure", "Property Type"]
    for col in cols_to_clean:
        if col in df.columns:
            df[col] = df[col].fillna('').astype(str).str.strip()
        else:
            st.warning(f"Column '{col}' not found – skipping cleaning.")
    return df

st.title("Property Developer Dashboard")

uploaded_file = st.file_uploader(
    "Drag and drop your pickle file (.pkl) here, or click to browse",
    type=["pkl"],
    label_visibility="visible"
)

if uploaded_file is None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, 'final_dataset.pkl')
    if os.path.exists(default_path):
        with st.spinner("Loading default dataset..."):
            tx = load_data_from_source(default_path)
    else:
        st.error("No file uploaded and 'final_dataset.pkl' not found. Please upload a pickle file.")
        sys.exit()
else:
    with st.spinner("Loading uploaded dataset..."):
        tx = load_data_from_source(uploaded_file)

# Safety check: if tx is still not defined, abort
if 'tx' not in locals():
    st.error("Data could not be loaded.")
    sys.exit()

# ------------------------------------------------------------
# Sidebar Filters (unchanged)
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# Filtering logic
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# Dashboard (same as before – omitted for brevity, but you can paste the full analysis blocks)
# ------------------------------------------------------------
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

    # ... (copy all the analysis elif blocks from previous full code) ...
    # They are identical – paste them here.

    # Strategic insights
    if not filtered_df.empty:
        st.divider()
        st.markdown("#### Strategic Insights")
        best_district = filtered_df.groupby("District").size().idxmax()
        st.info(f"**Market Signal:** Within the selected range, **{best_district}** exhibits the highest transaction activity and strongest market absorption capacity. We recommend prioritizing this area for further due diligence.")