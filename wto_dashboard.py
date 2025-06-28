import streamlit as st
import requests
import pandas as pd
import datetime
import plotly.express as px

# --- Config ---
st.set_page_config(page_title="WTO Import Dashboard", layout="wide")

# --- Header ---
st.title("🌐 WTO Import Dashboard")
st.markdown("Visualize merchandise import data from WTO API")

# --- API Setup ---
API_KEY = "228ffb618b6a448ab834a8cea045ae76"  # Replace with your own key if rate-limited
url = "https://api.wto.org/timeseries/v1/data"
headers = {"Ocp-Apim-Subscription-Key": API_KEY}

# --- Parameters ---
current_year = datetime.datetime.now().year
years_range = list(range(2020, current_year + 1))

countries = {
    "China": "CN",
    "Germany": "DE",
    "United States": "US"
}

reporter = st.selectbox("Select Reporter Country", list(countries.keys()))
reporter_code = countries[reporter]

params = {
    "i": "6",  # Import
    "r": reporter_code,
    "pc": "TOTAL",
    "ps": ",".join(str(y) for y in years_range),
    "freq": "A",
    "px": "HS",
    "type": "C",
    "fmt": "json"
}

# --- Data Fetch ---
@st.cache_data
def fetch_data():
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()["Dataset"]
        df = pd.DataFrame([{
            "Year": int(d["Year"]),
            "Value (Million USD)": d["Value"]
        } for d in data])
        return df
    else:
        st.error("Failed to fetch data from WTO API")
        return pd.DataFrame()

df = fetch_data()

# --- Show Data ---
st.subheader(f"📊 Merchandise Imports of {reporter} (2020-{current_year})")
st.dataframe(df)

# --- Plot ---
fig = px.bar(df, x="Year", y="Value (Million USD)",
             title=f"Import Value of {reporter} by Year",
             text_auto=True)
st.plotly_chart(fig, use_container_width=True)