# crypto-dashboard

A real-time dashboard built with Python and Streamlit to analyze cryptocurrency market trends.

## Project Overview
I developed this application to demonstrate practical data handling skills using Python. It interacts with the CoinGecko API to fetch live market data and visualizes historical price actions over different timeframes.

Key Engineering Features:
Latency Handling: Implemented `@st.cache_data` decorators to efficiently manage API rate limits (preventing HTTP 429 errors).
Robust Error Handling: Uses `try-except` blocks to ensure the app remains stable even if the external API endpoint times out.
Data Transformation: Raw JSON data is cleaned and transformed into Pandas DataFrames for accurate time-series visualization.

## Setup & Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
