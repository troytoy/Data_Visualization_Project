import streamlit as st
import requests
import pandas as pd
import datetime
import plotly.express as px


st.set_page_config(layout="wide")


@st.cache_data
def load_wto_data():
    API_KEY = "228ffb618b6a448ab834a8cea045ae76" 
    url = "https://api.wto.org/timeseries/v1/data"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}
    current_year = datetime.datetime.now().year
    years_range = f"2020-{current_year}"

    params = {
        "i": "ITS_MTV_AM", "r": "156,276,840", "p": "all",
        "ps": years_range, "fmt": "json", "lang": "1",
        "head": "H", "max": "20000"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if "Dataset" in data and data["Dataset"]:
            df = pd.DataFrame(data["Dataset"])[["ReportingEconomy", "ProductOrSector", "Year", "Value"]]
            df['Year'] = pd.to_numeric(df['Year'])
            df['Value'] = pd.to_numeric(df['Value'])
            return df
        else:
            return pd.DataFrame()
    except requests.exceptions.RequestException:
        return pd.DataFrame()


df_original = load_wto_data()


st.title("Interactive WTO Merchandise Imports Dashboard")
st.markdown("Explore import data for China, Germany, and the USA. Use the filters in the sidebar to customize the analysis.")

if df_original.empty:
    st.error("Could not load data from the WTO API. Please check your connection or API key.")
else:
    # --- Sidebar ---
    st.sidebar.header("Dashboard Filters")

 
    all_years = sorted(df_original['Year'].unique())
    all_countries = df_original['ReportingEconomy'].unique()
    all_products = df_original[df_original['ProductOrSector'] != 'Total merchandise']['ProductOrSector'].unique()

    # Widgets in Sidebar
    selected_years = st.sidebar.select_slider(
        "Select Year Range",
        options=all_years,
        value=(all_years[0], all_years[-1])
    )

    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=all_countries,
        default=all_countries
    )

    default_products = list(all_products)[:5]
    selected_products = st.sidebar.multiselect(
        "Select Product Groups",
        options=all_products,
        default=default_products
    )

    df_filtered = df_original[
        (df_original['Year'] >= selected_years[0]) &
        (df_original['Year'] <= selected_years[1]) &
        (df_original['ReportingEconomy'].isin(selected_countries)) &
        (df_original['ProductOrSector'].isin(selected_products))
    ]


    if df_filtered.empty or not selected_countries or not selected_products:
        st.warning("No data available for the selected filters. Please adjust your selection in the sidebar.")
    else:

        st.header("Filtered Analysis")

        # 1. KPI Cards
        total_import_value = df_filtered['Value'].sum()
        num_countries = len(selected_countries)
        num_products = len(selected_products)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Import Value (M USD)", f"${total_import_value:,.0f}")
        col2.metric("Countries Selected", f"{num_countries}")
        col3.metric("Product Groups Selected", f"{num_products}")
        
        st.markdown("---")

        # 2. Time Series
        st.subheader("Import Value Trend Over Time")
        time_series_data = df_filtered.groupby(['Year', 'ReportingEconomy'])['Value'].sum().reset_index()
        fig_line = px.line(
            time_series_data,
            x='Year',
            y='Value',
            color='ReportingEconomy',
            markers=True,
            title='Import Value by Country Over Selected Years',
            labels={'Value': 'Total Import Value (Million USD)'}
        )
        fig_line.update_xaxes(type='category')
        st.plotly_chart(fig_line, use_container_width=True)

        # 3. barchart
        col_bar1, col_bar2 = st.columns(2)

        with col_bar1:
            st.subheader("Comparison by Country")
            country_comparison = df_filtered.groupby('ReportingEconomy')['Value'].sum().reset_index().sort_values('Value', ascending=False)
            fig_bar_country = px.bar(
                country_comparison,
                x='ReportingEconomy',
                y='Value',
                color='ReportingEconomy',
                title='Total Import Value by Country',
                labels={'Value': 'Total Import Value (Million USD)', 'ReportingEconomy': 'Country'},
                text_auto='.2s'
            )
            st.plotly_chart(fig_bar_country, use_container_width=True)

        with col_bar2:
            st.subheader("Comparison by Product Group")
            product_comparison = df_filtered.groupby('ProductOrSector')['Value'].sum().reset_index().sort_values('Value', ascending=False)
            fig_bar_product = px.bar(
                product_comparison,
                x='ProductOrSector',
                y='Value',
                color='ProductOrSector',
                title='Total Import Value by Product Group',
                labels={'Value': 'Total Import Value (Million USD)', 'ProductOrSector': 'Product Group'},
                text_auto='.2s'
            )
            st.plotly_chart(fig_bar_product, use_container_width=True)

        st.markdown("---")

        # 4. Treemap
        st.subheader("Import Composition Treemap")
        st.markdown("This chart shows the breakdown of import values, first by country, then by product group.")
        fig_treemap = px.treemap(
            df_filtered,
            path=[px.Constant("All Countries"), 'ReportingEconomy', 'ProductOrSector'],
            values='Value',
            color='Value',
            hover_data=['Value'],
            color_continuous_scale='Blues',
            title='Hierarchical View of Import Values'
        )
        fig_treemap.update_traces(textinfo="label+percent root")
        st.plotly_chart(fig_treemap, use_container_width=True)

        # 5. table
        with st.expander("View Filtered Raw Data"):
            st.dataframe(df_filtered)