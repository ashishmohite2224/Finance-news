import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from datetime import date, timedelta

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Finance Dashboard 💹",
    page_icon="💰",
    layout="wide",
)

# ==============================
# DARK THEME STYLING
# ==============================
st.markdown("""
    <style>
        body, .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        .css-18e3th9, .css-1d391kg {
            background-color: #0e1117;
        }
        .stButton>button {
            background-color: #007bff;
            color: white;
            border-radius: 10px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        .stMetric {
            background-color: #1a1d23;
            border-radius: 10px;
            padding: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================
# SIDEBAR SETTINGS
# ==============================
st.sidebar.header("⚙️ Dashboard Controls")
ticker = st.sidebar.text_input("Enter Stock Symbol", value="AAPL").upper()
start_date = st.sidebar.date_input("Start Date", date.today() - timedelta(days=365))
end_date = st.sidebar.date_input("End Date", date.today())

# ==============================
# LOAD STOCK DATA
# ==============================
@st.cache_data
def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    data.reset_index(inplace=True)
    return data

data = load_data(ticker, start_date, end_date)

if data.empty:
    st.error("⚠️ No data found. Please check the stock symbol.")
    st.stop()

# ==============================
# HEADER
# ==============================
st.title("💹 Finance Dashboard")
st.markdown(f"### Stock Analysis for **{ticker}**")

# ==============================
# CANDLESTICK CHART
# ==============================
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data['Date'],
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name="Candlestick"
))
fig.update_layout(
    template="plotly_dark",
    title=f"{ticker} Price Chart",
    yaxis_title="Price (USD)",
    xaxis_rangeslider_visible=False,
    height=600
)
st.plotly_chart(fig, use_container_width=True)

# ==============================
# MOVING AVERAGES (MATPLOTLIB)
# ==============================
st.subheader("📊 Technical Indicators")

data['MA20'] = data['Close'].rolling(window=20).mean()
data['MA50'] = data['Close'].rolling(window=50).mean()

fig2, ax = plt.subplots(figsize=(10, 4))
ax.plot(data['Date'], data['Close'], label='Close Price', color='white')
ax.plot(data['Date'], data['MA20'], label='20-Day MA', color='cyan')
ax.plot(data['Date'], data['MA50'], label='50-Day MA', color='magenta')
ax.set_facecolor('#0e1117')
ax.legend()
ax.grid(True, color='#333333')
ax.set_xlabel("Date")
ax.set_ylabel("Price (USD)")
st.pyplot(fig2)

# ==============================
# STOCK STATS
# ==============================
st.subheader("📈 Key Stock Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Current Price", f"${data['Close'].iloc[-1]:.2f}")
with col2:
    st.metric("52 Week High", f"${data['High'].max():.2f}")
with col3:
    st.metric("52 Week Low", f"${data['Low'].min():.2f}")

# ==============================
# PORTFOLIO TRACKER
# ==============================
st.subheader("💼 Portfolio Tracker")

portfolio = st.session_state.get("portfolio", {})

col_add1, col_add2, col_add3 = st.columns([3, 2, 1])
with col_add1:
    new_symbol = st.text_input("Add Stock Symbol (e.g., MSFT)").upper()
with col_add2:
    quantity = st.number_input("Quantity", min_value=0, value=0)
with col_add3:
    add_button = st.button("➕ Add to Portfolio")

if add_button and new_symbol and quantity > 0:
    stock = yf.Ticker(new_symbol)
    price = stock.history(period="1d")['Close'].iloc[-1]
    portfolio[new_symbol] = {"Quantity": quantity, "Price": price}
    st.session_state["portfolio"] = portfolio
    st.success(f"✅ {new_symbol} added to portfolio!")

if portfolio:
    portfolio_df = pd.DataFrame(portfolio).T
    portfolio_df["Total Value"] = portfolio_df["Quantity"] * portfolio_df["Price"]
    total_value = portfolio_df["Total Value"].sum()
    st.write(portfolio_df)
    st.metric("💰 Portfolio Total Value", f"${total_value:,.2f}")
else:
    st.info("Your portfolio is empty. Add some stocks above.")

# ==============================
# TOP GAINERS / LOSERS (NSE)
# ==============================
st.subheader("📈 Market Overview (NSE Top Gainers & Losers)")

@st.cache_data
def get_nse_data():
    try:
        url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json"
        df = pd.read_json(url)
        return df
    except:
        return pd.DataFrame()

market_data = get_nse_data()
if market_data.empty:
    st.info("Live NSE data not available right now.")
else:
    top_gainers = market_data.sort_values(by='ltpChange', ascending=False).head(5)
    top_losers = market_data.sort_values(by='ltpChange').head(5)

    col_g, col_l = st.columns(2)
    with col_g:
        st.write("### 🟢 Top Gainers")
        st.dataframe(top_gainers)
    with col_l:
        st.write("### 🔴 Top Losers")
        st.dataframe(top_losers)

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.markdown(
    "<center>💼 Built with ❤️ using Streamlit | © 2025 Finance Dashboard</center>",
    unsafe_allow_html=True
)
