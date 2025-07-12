import streamlit as st
import requests
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_wto_data():
    """
    Loads merchandise import data from the WTO API.
    Data is cached to avoid repeated API calls.
    """
    # IMPORTANT: For production, store API_KEY securely (e.g., Streamlit Secrets)
    # st.secrets["wto_api_key"] or environment variables
    API_KEY = "228ffb618b6a448ab834a8cea045ae76"
    url = "https://api.wto.org/timeseries/v1/data"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}

    current_year = datetime.datetime.now().year
    years_range = f"2020-{current_year}" # Fetch data from 2020 to current year

    params = {
        "i": "ITS_MTV_AM",  # Indicator: Merchandise Trade Value - Annual (Imports)
        "r": "156,276,840", # Reporting Economies: China (156), Germany (276), United States (840)
        "p": "all",         # Partner: All (global imports)
        "ps": years_range,  # Period: Specified year range
        "fmt": "json",      # Format: JSON
        "lang": "1",        # Language: English
        "head": "H",        # Header: Human-readable headers
        "max": "20000"      # Max records
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if "Dataset" in data and data["Dataset"]:
            # Create DataFrame from the 'Dataset' key
            df = pd.DataFrame(data["Dataset"])[["ReportingEconomy", "ProductOrSector", "Year", "Value"]]
            df['Year'] = pd.to_numeric(df['Year'])
            df['Value'] = pd.to_numeric(df['Value'])
            return df
        else:
            st.error("Error: 'Dataset' key not found or is empty in the API response. Please check the API parameters.")
            return pd.DataFrame(columns=["ReportingEconomy", "ProductOrSector", "Year", "Value"])
    except requests.exceptions.RequestException as e:
        st.error(f"Error: Could not retrieve data from the WTO API. Please check the API Key or network connection. Details: {e}")
        return pd.DataFrame(columns=["ReportingEconomy", "ProductOrSector", "Year", "Value"])

def find_latest_valid_year(df):
    """
    Finds the latest year that contains detailed merchandise data
    (i.e., not just 'Total merchandise' and has positive values).
    This ensures analysis is based on the most recent meaningful data.
    """
    if df.empty:
        return None
    years = sorted(df['Year'].unique(), reverse=True)
    for year in years:
        # Filter for data in the current year, excluding 'Total merchandise'
        year_data = df[(df['Year'] == year) & (df['ProductOrSector'] != 'Total merchandise')]
        # Check if there's any detailed product data with a value greater than 0
        if not year_data.empty and year_data['Value'].sum() > 0:
            return year
    return None


st.title("WTO Merchandise Import Analysis (2020-Present)")
st.markdown("""
This dashboard provides an analysis and visualization of merchandise import data from the World Trade Organization (WTO), focusing on three economic superpowers: the United States, China, and Germany. Use the sidebar to navigate through the 10 key analytical questions.
""")

# Load data and determine the latest valid year
df = load_wto_data()

if not df.empty:
    latest_year = find_latest_valid_year(df)

    if latest_year:
        st.success(f"Analysis is based on the latest available year with detailed data: **{latest_year}**")
        # Filter the main DataFrame for the latest year's data
        df_latest = df[df['Year'] == latest_year].copy()
    else:
        st.error("Error: No valid data found for the specified years with detailed product information. Cannot proceed with analysis.")
        df_latest = pd.DataFrame() # Ensure df_latest is an empty DataFrame if no valid year
else:
    st.error("Failed to load data from the source. Please check your internet connection or API key.")
    latest_year = None
    df_latest = pd.DataFrame() # Ensure df_latest is an empty DataFrame if data loading failed


# Sidebar for navigation
st.sidebar.title("Analytical Questions")
question = st.sidebar.radio(
    "Select a question to display:",
    (
        "Q1: Highest Total Import Value",
        "Q2: Top 5 Imported Product Groups",
        "Q3: Top Imported Product Group per Country",
        "Q4: Trend of Total Import Value",
        "Q5: Top 5 Global Import Product Groups",
        "Q6: Evolution of Import Share",
        "Q7: 'Machinery and Transport Equipment' Import Trend",
        "Q8: Import Composition by Country",
        "Q9: Fastest Import Growth Rate",
        "Q10: Heatmap of Import Values"
    )
)

# Display content based on selected question
if not df_latest.empty and latest_year: # Ensure df_latest is not empty and latest_year is found
    # --- Q1: Highest Total Import Value (Choropleth Map) ---
    if question == "Q1: Highest Total Import Value":
        st.header(f"Q1: Which country had the highest total import value in {latest_year}?")
        total_imports = df_latest[df_latest['ProductOrSector'] == 'Total merchandise'].sort_values('Value', ascending=False)

        if not total_imports.empty:
            fig = px.choropleth(
                total_imports,
                locations='ReportingEconomy',      # Column for country names
                locationmode='country names',      # Specifies that 'locations' are country names
                color='Value',                     # Column to determine color intensity
                hover_name='ReportingEconomy',     # Text to display on hover
                color_continuous_scale='Plasma',   # Color scale for the map (changed to Plasma for desired look)
                labels={'Value': 'Import Value (Million USD)'}, # Label for the color bar
                title=f'<b>Total Merchandise Imports by Country ({latest_year})</b>' # Map title
            )

            # Update map layout for better presentation
            fig.update_layout(
                geo=dict(
                    showframe=False,       # Do not show frame around the map
                    showcoastlines=True    # Show coastlines
                ),
                coloraxis_colorbar=dict(title='Million USD'), # Title for the color bar
                title_x=0.5 # Center the main title of the plot
            )

            st.plotly_chart(fig, use_container_width=True)
            st.info("**Insight:** The map clearly shows which countries were the largest importers of goods in the latest available year, highlighting geographical patterns.")
        else:
            st.warning("No data for 'Total merchandise' available for this question in the latest year.")

    # --- Q2: Top 5 Imported Product Groups (Bar Chart) ---
    # Corrected indentation for this elif block
    elif question == "Q2: Top 5 Imported Product Groups":
        st.header(f"Q2: What are the top 5 imported product groups for each country in {latest_year}?")
        top5_products_per_country = (df_latest[df_latest['ProductOrSector'] != 'Total merchandise']
                                     .sort_values('Value', ascending=False)
                                     .groupby('ReportingEconomy').head(5))
        if not top5_products_per_country.empty:
            fig = px.bar(top5_products_per_country,
                         x="Value",
                         y="ProductOrSector",
                         color="ReportingEconomy",
                         barmode='group',
                         orientation='h',
                         text_auto='.2s',
                         title=f'<b>Top 5 Imported Product Groups per Country ({latest_year})</b>',
                         labels={'Value': 'Import Value (Million USD)', 'ProductOrSector': 'Product Group'})
            fig.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig, use_container_width=True)
            st.info("**Insight:** This comparison highlights the different import priorities. The US and Germany focus on machinery, while China's top import is telecom equipment.")
        else:
            st.warning("No detailed product data available for Q2 in the latest year.")

    # --- Q3: Top Imported Product Group per Country (Bar Chart) ---
    # Corrected indentation for this elif block
    elif question == "Q3: Top Imported Product Group per Country":
        st.header(f"Q3: What is the single top imported product group for each country in {latest_year}?")
        top_product_per_country = (df_latest[df_latest['ProductOrSector'] != 'Total merchandise']
                                   .sort_values('Value', ascending=False)
                                   .groupby('ReportingEconomy').first().reset_index())
        if not top_product_per_country.empty:
            fig = px.bar(top_product_per_country,
                         x="Value",
                         y="ReportingEconomy",
                         color="ProductOrSector",
                         orientation='h',
                         text="ProductOrSector",
                         title=f'<b>Top Imported Product Group per Country ({latest_year})</b>',
                         labels={'Value': 'Import Value (Million USD)', 'ReportingEconomy': 'Country'})
            fig.update_traces(textposition='inside', textfont_color='white')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            st.info("**Insight:** This view simplifies the comparison, reinforcing that manufactures and machinery are key import categories for these economic powerhouses.")
        else:
            st.warning("No data available for Q3 in the latest year.")

    # --- Q4: Trend of Total Import Value (Line Chart) ---
    # Corrected indentation for this elif block
    elif question == "Q4: Trend of Total Import Value":
        st.header("Q4: What is the trend of total import value for each country over the years?")
        total_imports_trend = df[df['ProductOrSector'] == 'Total merchandise'].sort_values('Year')
        if not total_imports_trend.empty:
            fig = px.line(total_imports_trend,
                          x='Year',
                          y='Value',
                          color='ReportingEconomy',
                          markers=True,
                          title='<b>Trend of Total Import Value by Country (2020-Present)</b>',
                          labels={'Value': 'Total Import Value (Million USD)', 'Year': 'Year'})
            fig.update_xaxes(type='category') # Treat years as categories to avoid continuous scale issues
            st.plotly_chart(fig, use_container_width=True)
            st.info("**Insight:** The line chart illustrates the import trends for each country, showing how their trade volumes have evolved over the years.")
        else:
            st.warning("No data available to show trend for Q4.")

    # --- Q5: Top 5 Global Import Product Groups (Bar Chart) ---
    # Corrected indentation for this elif block
    elif question == "Q5: Top 5 Global Import Product Groups":
        st.header(f"Q5: What are the top 5 global import product groups in {latest_year}?")
        top_global_products = (df_latest[df_latest['ProductOrSector'] != 'Total merchandise']
                               .groupby("ProductOrSector")['Value'].sum()
                               .nlargest(5).reset_index())
        if not top_global_products.empty:
            fig = px.bar(top_global_products,
                         x='Value',
                         y='ProductOrSector',
                         text_auto='.2s',
                         orientation='h',
                         color='ProductOrSector', # Color by product group
                         title=f'<b>Top 5 Global Imported Product Groups ({latest_year})</b>',
                         labels={'Value': 'Total Import Value (Million USD)', 'ProductOrSector': 'Product Group'})
            fig.update_yaxes(categoryorder='total ascending') # Order bars by value
            st.plotly_chart(fig, use_container_width=True)
            st.info("**Insight:** 'Manufactures' and 'Machinery and transport equipment' stand out as the most significant import categories globally among these nations, indicating their central role in the world's industrial supply chain.")
        else:
            st.warning("No data available for Q5 in the latest year.")

    # --- Q6: Evolution of Import Share (Area Chart) ---
    # Corrected indentation for this elif block
    elif question == "Q6: Evolution of Import Share":
        st.header("Q6: How has the import share of the top 3 global product groups evolved within each country?")
        # Determine top 3 global products from the *full* dataset for consistency over years
        top_3_global = (df[df['ProductOrSector'] != 'Total merchandise']
                        .groupby('ProductOrSector')['Value'].sum().nlargest(3).index.tolist())
        if top_3_global:
            # Filter for these top 3 products across all years
            df_trends = df[df['ProductOrSector'].isin(top_3_global)]
            # Get total merchandise value for each country and year
            df_totals = df[df['ProductOrSector'] == 'Total merchandise'].rename(columns={'Value': 'TotalValue'})
            # Merge to calculate share
            df_merged = pd.merge(df_trends, df_totals[['ReportingEconomy', 'Year', 'TotalValue']], on=['ReportingEconomy', 'Year'])
            df_merged['Share'] = (df_merged['Value'] / df_merged['TotalValue']) * 100
            df_merged = df_merged.sort_values('Year')

            fig = px.area(df_merged,
                          x='Year',
                          y='Share',
                          color='ProductOrSector',
                          facet_col='ReportingEconomy', # Create separate plots for each country
                          title='<b>Evolution of Import Share for Top 3 Global Products</b>',
                          labels={'Share': 'Import Share (%)', 'Year': 'Year'})
            fig.update_xaxes(type='category') # Treat years as categories
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1])) # Clean facet titles
            st.plotly_chart(fig, use_container_width=True)
            st.info("**Insight:** This chart shows how the importance of key global products shifts within each country's import strategy over time. A rising share may indicate a growing reliance on that sector.")
        else:
            st.warning("Could not determine top global products for Q6 or missing data.")

    # --- Q7: 'Machinery and Transport Equipment' Import Trend (Line Chart) ---
    # Corrected indentation for this elif block
    elif question == "Q7: 'Machinery and Transport Equipment' Import Trend":
        st.header("Q7: Which country dominates the import of 'Machinery and Transport Equipment', and what is the trend?")
        top_product_name = 'Machinery and transport equipment'
        df_top_product_trend = df[df['ProductOrSector'] == top_product_name].sort_values('Year')
        if not df_top_product_trend.empty:
            fig = px.line(df_top_product_trend,
                          x='Year',
                          y='Value',
                          color='ReportingEconomy',
                          markers=True,
                          title=f'<b>Import Trend for {top_product_name} (2020-Present)</b>',
                          labels={'Value': 'Import Value (M USD)', 'Year': 'Year'})
            fig.update_xaxes(type='category') # Treat years as categories
            st.plotly_chart(fig, use_container_width=True)
            st.info("**Insight:** The USA is the largest importer of machinery and transport equipment. This direct comparison highlights the competitive landscape for one of the world's most traded product categories.")
        else:
            st.warning(f"No data available for '{top_product_name}' for Q7.")

    # --- Q8: Import Composition by Country (Pie Charts) ---
    # Corrected indentation for this elif block
    elif question == "Q8: Import Composition by Country":
        st.header(f"Q8: What is the percentage share of top import groups for each country in {latest_year}?")
        df_pie = df_latest[df_latest['ProductOrSector'] != 'Total merchandise'].copy()

        # Get the top 4 products across all countries for consistent grouping
        # This ensures 'Others' groups consistently across facets
        all_top_products = df_pie.groupby('ProductOrSector')['Value'].sum().nlargest(4).index.tolist()

        # Group smaller categories into 'Others'
        df_pie['Sector_Grouped'] = df_pie['ProductOrSector'].apply(lambda x: x if x in all_top_products else 'Others')

        if not df_pie.empty:
            fig = px.pie(df_pie,
                         values='Value',
                         names='Sector_Grouped',
                         facet_col='ReportingEconomy', # Create separate pie charts for each country
                         title=f'<b>Import Composition by Country ({latest_year})</b>',
                         color_discrete_sequence=px.colors.qualitative.Pastel) # Use a pastel color sequence
            fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1])) # Clean facet titles
            st.plotly_chart(fig, use_container_width=True)
            st.info("**Insight:** The pie charts provide a clear breakdown of each country's import dependency, illustrating their unique economic structures at a glance.")
        else:
            st.warning("No data available for Q8 in the latest year.")

    # --- Q9: Fastest Import Growth Rate (Bar Chart) ---
    # Corrected indentation for this elif block
    elif question == "Q9: Fastest Import Growth Rate":
        st.header(f"Q9: Which product groups have the fastest import growth rate (2020 vs. {latest_year})?")
        if 2020 in df['Year'].values and latest_year in df['Year'].values:
            # Pivot table to get values for 2020 and latest_year
            df_pivot = (df[df['ProductOrSector'] != 'Total merchandise']
                        .pivot_table(index=['ReportingEconomy', 'ProductOrSector'],
                                     columns='Year',
                                     values='Value')
                        .dropna()) # Drop rows where either year is missing

            if not df_pivot.empty and 2020 in df_pivot.columns and latest_year in df_pivot.columns:
                # Calculate growth rate
                df_pivot['GrowthRate'] = ((df_pivot[latest_year] - df_pivot[2020]) / df_pivot[2020]) * 100
                # Get top 3 growth products per country
                top_growth = df_pivot.reset_index().sort_values('GrowthRate', ascending=False).groupby('ReportingEconomy').head(3)

                fig = px.bar(top_growth,
                             x="GrowthRate",
                             y="ProductOrSector",
                             color="ReportingEconomy",
                             orientation='h',
                             text_auto='.1f', # Display growth rate with 1 decimal place
                             title=f'<b>Top 3 Fastest-Growing Imported Product Groups (2020-{latest_year})</b>',
                             labels={'GrowthRate': 'Growth Rate (%)', 'ProductOrSector': 'Product Group'})
                fig.update_traces(textangle=0, textposition="outside", cliponaxis=False)
                fig.update_yaxes(categoryorder='total ascending')
                st.plotly_chart(fig, use_container_width=True)
                st.info("**Insight:** The dramatic growth in fuel imports for Germany highlights the impact of recent geopolitical events on energy markets. In contrast, the US and China show strong growth in technology-related and industrial sectors.")
            else:
                st.warning("Not enough historical data (e.g., missing 2020 or latest year values) to calculate growth rates for Q9.")
        else:
            st.warning(f"Year 2020 or the latest year ({latest_year}) is not available in the data for Q9.")

    # --- Q10: Heatmap of Import Values ---
    # Corrected indentation for this elif block
    elif question == "Q10: Heatmap of Import Values":
        st.header(f"Q10: How do import values compare across all product groups and countries in {latest_year}?")
        # Get top 10 products for USA (as a reference for heatmap rows)
        top10_usa_products = (df_latest[(df_latest['ReportingEconomy'] == 'United States of America') & (df_latest['ProductOrSector'] != 'Total merchandise')]
                              .nlargest(10, 'Value')['ProductOrSector'].tolist())
        if top10_usa_products:
            # Create a pivot table for heatmap
            heatmap_pivot = (df_latest[df_latest['ProductOrSector'] != 'Total merchandise']
                             .pivot_table(index="ProductOrSector", columns="ReportingEconomy", values="Value", aggfunc="sum"))
            # Reindex to ensure top USA products are at the top, fill NaNs with 0
            heatmap_data = heatmap_pivot.reindex(top10_usa_products).fillna(0)

            fig = px.imshow(heatmap_data,
                            text_auto=True, # Automatically show values on heatmap cells
                            aspect="auto", # Adjust aspect ratio automatically
                            color_continuous_scale='Viridis', # Color scale for heatmap
                            title=f'<b>Heatmap of Import Values for Top US Product Groups ({latest_year})</b>',
                            labels=dict(x="Country", y="Product Group", color="Value (M USD)"))
            fig.update_xaxes(side="top") # Move x-axis labels to the top
            st.plotly_chart(fig, use_container_width=True)
            st.info("**Insight:** The heatmap provides an excellent summary, clearly showing the concentration of import values. It quickly reveals China's leadership in telecom equipment and the close competition between the US and Germany in machinery.")
        else:
            st.warning("Could not determine top 10 products for USA to generate heatmap for Q10.")
else:
    # This else block handles cases where df is empty or latest_year is None
    # The error messages are already handled by load_wto_data and find_latest_valid_year
    # No further action needed here, as appropriate warnings/errors are shown above.
    pass # Keep this pass to make the else block syntactically correct

st.markdown("---")
st.markdown("Data sourced from the World Trade Organization (WTO) API.")
