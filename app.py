import streamlit as st
import requests
import pandas as pd
import time

# Page setup
st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="📈",
    layout="wide"
)

BASE_URL = "https://api.coingecko.com/api/v3"


def format_big_number(number):
    #  A Function I Use to make numbers readable (Mio/Mrd)
    if number is None:
        return "N/A"
    
    value = float(number)
    
    if value >= 1000000000: # Billion
        formatted = value / 1000000000
        return f"€ {formatted:.2f} Mrd."
    elif value >= 1000000: # Million
        formatted = value / 1000000
        return f"€ {formatted:.2f} Mio."
    else:
        return f"€ {value:,.2f}"

# The API functions 

@st.cache_data(ttl=600) # Cache for 10 mins so I don't get banned by API, due to the free limit
def get_coins_list():
    url = f"{BASE_URL}/coins/markets"
    # Parameters for the API
    params = {
        "vs_currency": "eur",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        # Check if request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print("Error loading coins") 
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []

@st.cache_data(ttl=300)
def get_coin_history(coin_id, days):
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "eur",
        "days": days
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # I used 3 dataframes for the charts
        # 1. Prices
        prices_data = data['prices']
        df_prices = pd.DataFrame(prices_data, columns=['timestamp', 'price'])
        df_prices['timestamp'] = pd.to_datetime(df_prices['timestamp'], unit='ms')
        df_prices = df_prices.set_index('timestamp')
        
        # 2. Market Caps
        caps_data = data['market_caps']
        df_caps = pd.DataFrame(caps_data, columns=['timestamp', 'market_cap'])
        df_caps['timestamp'] = pd.to_datetime(df_caps['timestamp'], unit='ms')
        df_caps = df_caps.set_index('timestamp')
        
        # 3. Volumes
        vol_data = data['total_volumes']
        df_vol = pd.DataFrame(vol_data, columns=['timestamp', 'volume'])
        df_vol['timestamp'] = pd.to_datetime(df_vol['timestamp'], unit='ms')
        df_vol = df_vol.set_index('timestamp')
        
        return df_prices, df_caps, df_vol
        
    except Exception as e:
        return None, None, None

@st.cache_data(ttl=300)
def get_global_data():
    try:
        response = requests.get(f"{BASE_URL}/global", timeout=10)
        if response.status_code == 200:
            return response.json()['data']
    except:
        return None

# --- MAIN APP ---

def main():
    # Sidebar Info
    st.sidebar.title("Navigation")
    st.sidebar.info("Developed by Bassel Abdelmottaleb for HBKU application.")
    
    # Load Data
    coins_data = get_coins_list()
    
    if len(coins_data) == 0:
        st.warning("Could not load data. Please refresh later.")
        return

    # Creates a list of names for the dropdown
    coin_names = []
    coin_names.append("Global Overview")
    
    for coin in coins_data:
        coin_names.append(coin['name'])
    
    # Selection Widget
    selection = st.sidebar.selectbox("Choose View", coin_names)
    
    st.sidebar.write("---")
    
    # Timeframe selection
    days_option = st.sidebar.radio("Timeframe", ["7 Days", "30 Days", "90 Days"])
    
    # Convert string "7 Days" to integer 7
    days_int = 7
    if days_option == "30 Days":
        days_int = 30
    elif days_option == "90 Days":
        days_int = 90
        
    # --- GLOBAL VIEW LOGIC ---
    if selection == "Global Overview":
        st.title("Global Crypto Market")
        
        global_stats = get_global_data()
        
        if global_stats:
            # Step-by-step extraction of data (easier to read)
            total_mcap = global_stats['total_market_cap']['eur']
            total_vol = global_stats['total_volume']['eur']
            btc_percentage = global_stats['market_cap_percentage']['btc']
            
            # Columns for metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Market Cap", format_big_number(total_mcap))
            col2.metric("Volume (24h)", format_big_number(total_vol))
            col3.metric("BTC Dominance", f"{btc_percentage:.1f} %")
        
        st.write("---")
        st.subheader("Top 100 Rankings")
        
        # Prepare Dataframe for display
        df = pd.DataFrame(coins_data)
        
        # Only show important columns
        simple_df = df[['name', 'symbol', 'current_price', 'price_change_percentage_24h', 'market_cap']]
        
        st.dataframe(
            simple_df, 
            hide_index=True,
            use_container_width=True
        )
    
    else:
        # Finds the selected coin in the list
        selected_coin = None
        for coin in coins_data:
            if coin['name'] == selection:
                selected_coin = coin
                break
        
        if selected_coin:
            st.title(f"{selected_coin['name']} ({selected_coin['symbol'].upper()})")
            
            # Display Image
            st.image(selected_coin['image'], width=64)
            
            # Current Stats
            price = selected_coin['current_price']
            change = selected_coin['price_change_percentage_24h']
            high = selected_coin['high_24h']
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Current Price", f"€ {price}")
            c2.metric("24h Change", f"{change} %", delta=change)
            c3.metric("24h High", f"€ {high}")
            
            st.write("---")
            
            # Charts
            st.subheader(f"History ({days_int} Days)")
            
            # Unpacks the 3 dataframes
            df_price, df_cap, df_vol = get_coin_history(selected_coin['id'], days_int)
            
            if df_price is not None:
                tab1, tab2 = st.tabs(["Price Chart", "Volume & Cap"])
                
                with tab1:
                    st.line_chart(df_price['price'])
                
                with tab2:
                    st.bar_chart(df_vol['volume'])
                    st.area_chart(df_cap['market_cap'])
            else:
                st.warning("Could not load chart data. API limit might be reached.")

if __name__ == "__main__":
    main()
