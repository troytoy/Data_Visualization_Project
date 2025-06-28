import streamlit as st
import requests
import pandas as pd
import datetime
import plotly.express as px

# --- Page config ---
st.set_page_config(page_title="WTO Import Comparison Dashboard", layout="wide")

# --- Header ---
st.title("🌐 WTO Import Comparison Dashboard")
st.markdown("Compare merchandise import values across countries by year using data from the WTO API")

# --- WTO API Setup ---
API_KEY = "228ffb618b6a448ab834a8cea045ae76"
url = "https://api.wto.org/timeseries/v1/data"
headers = {"Ocp-Apim-Subscription-Key": API_KEY}

# --- Year Range ---
current_year = datetime.datetime.now().year
year_list = list(reversed(range(2015, current_year + 1)))
selected_year = st.sidebar.selectbox("Select Year", year_list)

# --- Country Selection ---
country_map = {
    "China": "CN",
    "Germany": "DE",
    "United States": "US"
}
selected_countries = st.sidebar.multiselect("Select Countries to Compare", list(country_map.keys()), default=["China", "Germany", "United States"])

# --- Fetch Data ---
@st.cache_data
def fetch_data(reporter_code):
    params = {
        "i": "6",  # Import
        "r": reporter_code,
        "pc": "TOTAL",
        "ps": str(selected_year),
        "freq": "A",
        "px": "HS",
        "type": "C",
        "fmt": "json"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        dataset = response.json().get("Dataset", [])
        df = pd.DataFrame([{
            "Country": country_name,
            "Year": int(d["Year"]),
            "Value (Million USD)": d["Value"]
        } for d in dataset])
        return df
    else:
        return pd.DataFrame()

# --- Load data for selected countries ---
dfs = []
for country_name in selected_countries:
    code = country_map[country_name]
    df = fetch_data(code)
    dfs.append(df)

# --- Combine all ---
final_df = pd.concat(dfs, ignore_index=True)

# --- Show data ---
if final_df.empty:
    st.warning("No data available for the selected countries and year.")
else:
    st.subheader(f"📈 Import Value Comparison ({selected_year})")
    st.dataframe(final_df)

    # --- Line Chart ---
    fig = px.line(final_df, x="Year", y="Value (Million USD)", color="Country",
                  markers=True, title=f"Import Trends in {selected_year}")
    st.plotly_chart(fig, use_container_width=True)

    # --- Summary Table ---
    summary = final_df.groupby("Country")["Value (Million USD)"].sum().reset_index()
    st.subheader("📊 Summary: Total Import Value")
    st.dataframe(summary)
