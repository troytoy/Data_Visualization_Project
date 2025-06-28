# WTO Import Dashboard – Data Visualization Project

This project is an interactive dashboard built with **Streamlit** and **Plotly**. It visualizes merchandise import data from the **World Trade Organization (WTO)** API for selected countries (China, Germany, and the USA) from 2020 to the present.

---

## Features

- Displays import values by year
- Country selection via sidebar (China, Germany, USA)
- Interactive bar charts with Plotly
- Live data fetched from WTO API

---

## Project Structure

```
Data_Visualization_Project/
├── wto_dashboard.py            # Main Streamlit app
├── requirements.txt            # Required Python packages
├── README.md                   # This file
└── images/
    └── dashboard_snapshot.png  # (Optional) Dashboard screenshot
```

---

## How to Run the Dashboard Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/<your-username>/Data_Visualization_Project.git
   cd Data_Visualization_Project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run wto_dashboard.py
   ```

---

## Dashboard Preview

*_(Snapshot will be added later)_*

You will see a fully interactive dashboard that allows you to select a country and view its merchandise import trends over time.

---

## Tech Stack

- Python 
- Streamlit 
- Plotly 
- WTO API 
- Pandas

---

## License

This project is open source and available under the MIT License.
