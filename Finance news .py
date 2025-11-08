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
    page_title="Finance Dashboard",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# DARK THEME STYLING
# ==============================
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stApp {
            background-color: #0e1117;
        }
        .css-18e3th9 {
            background-color: #0e1117;
        }
        .stMarkdown, .stText, .stHeader, .stDataFrame {
            color: #fafafa;
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
    </style>
""", unsafe_allow_html=True)

# ==============================
# SIDEBAR SETTINGS
# ==============================
st.sidebar.header("📈 Stock Dashboard Settings")

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
# DASHBOARD HEADER
# ==============================
st.title("💹 Finance Dashboard")
st.markdown(f"### Stock Analysis for **{ticker}**")

# ==============================
# PRICE CHART (PLOTLY)
# ==============================
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data['Date'],
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name='Candlestick'
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
# TECHNICAL INDICATORS
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
ax.set_ylabel("Price")
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
# DATAFRAME DISPLAY
# ==============================
st.subheader("📅 Stock Data Table")
st.dataframe(data.tail(10))
