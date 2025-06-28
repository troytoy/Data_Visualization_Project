# WTO Merchandise Imports Dashboard

This project provides an analysis and visualization of merchandise import data from the World Trade Organization (WTO). It focuses on three economic superpowers: China, Germany, and the United States, for the period from 2020 to the present.

The data is fetched live from the WTO API and presented through two distinct, interactive web dashboards built with Streamlit.

---

## Dashboards Overview

This repository contains two different Streamlit dashboards, each offering a unique way to explore the data.

### 1. Guided Analysis Dashboard (`wto_dashboard_final.py`)

This dashboard is designed to walk users through a curated analysis by answering 10 specific analytical questions. It's a "story-telling" approach, perfect for users who want to see key insights and trends that have been pre-identified.

**Features:**
- Navigate through 10 pre-defined questions using a simple radio button in the sidebar.
- Each question presents a unique chart and a written insight.
- Covers topics like:
  - Highest total import value by country.
  - Top 5 imported product groups.
  - Import composition and growth rates.
  - A heatmap comparison of key product imports.

(Suggestion: Replace this line with an actual screenshot of your dashboard)

---

### 2. Interactive Exploratory Dashboard (`Interactive WTO Merchandise Imports Dashboard.py`)

This dashboard provides a fully interactive, "sandbox" environment for users who want to explore the data freely and create their own analyses.

**Features:**
- **Dynamic Filters**: Users can filter the data by:
  - Year Range (Slider)
  - Countries (Multi-select)
  - Product Groups (Multi-select)
- **Real-time Updates**: All charts and metrics on the dashboard update instantly based on the selected filters.
- **Visualizations include:**
  - KPI Cards showing high-level summaries.
  - A dynamic time-series line chart.
  - Bar charts for comparing countries and products.
  - An interactive treemap for exploring import composition.
  - A raw data table for detailed inspection.

(Suggestion: Replace this line with an actual screenshot of your dashboard)

---

## Technology Stack

- **Language**: Python  
- **Dashboarding**: Streamlit  
- **Data Manipulation**: Pandas  
- **Data Visualization**: Plotly Express  
- **API Communication**: Requests  

---

## Setup and Installation

Follow these steps to set up and run the dashboards on your local machine.

### 1. Prerequisites

- Python 3.8 or newer

### 2. Clone or Download the Repository

Download the project files to your local machine.

### 3. Create a Virtual Environment (Recommended)

It is highly recommended to create a virtual environment to manage project dependencies.

```bash
# Create a virtual environment
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.env\Scriptsctivate
```

### 4. Install Dependencies

Create a `requirements.txt` file with the following content:

```
streamlit
pandas
plotly
requests
```

Then, install the required packages using pip:

```bash
pip install -r requirements.txt
```

### 5. API Key

The scripts use a hardcoded API key for the WTO data source for immediate testing.

**Note:** For production or public-facing applications, it is strongly recommended to use a more secure method like Streamlit Secrets to manage your API keys.

---

## How to Run the Dashboards

Make sure your virtual environment is activated and you are in the project's root directory.

To run the **Guided Analysis Dashboard**:

```bash
streamlit run wto_dashboard_final.py
```

To run the **Interactive Exploratory Dashboard**:

> Note: File names with spaces can be tricky in the command line. You might need to enclose the name in quotes.

```bash
streamlit run "Interactive WTO Merchandise Imports Dashboard.py"
```

Your web browser will automatically open a new tab with the running dashboard.
