import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from textblob import TextBlob
from datetime import datetime

# ==============================
# Page configuration
# ==============================
st.set_page_config(
    page_title="📊 Indian Market Dashboard",
    page_icon="📈",
    layout="wide",
)

# ==============================
# 🎨 Custom Professional Theme (Dark Navy + Teal Blue)
# ==============================
st.markdown(
    """
    <style>
        /* Base Layout */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0b0f1a 0%, #121b2f 100%);
            color: #EAEAEA;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b1a2f 0%, #14294b 100%);
            color: white;
            border-right: 1px solid #1e3a5f;
        }
        /* Headings */
        h1, h2, h3, h4, h5 {
            color: #5dd6c0;
            font-weight: 700;
        }
        /* Buttons */
        .stButton>button {
            background-color: #5dd6c0 !important;
            color: #0a0f24 !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            padding: 0.5rem 1rem !important;
            border: none !important;
        }
        .stButton>button:hover {
            background-color: #4ac8b3 !important;
            color: white !important;
            transform: scale(1.03);
            transition: 0.2s;
        }
        /* Cards */
        .card {
            background-color: rgba(255,255,255,0.06);
            backdrop-filter: blur(8px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        /* Tables */
        div[data-testid="stDataFrame"] {
            background: rgba(255,255,255,0.03);
            border-radius: 10px;
            color: white !important;
        }
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #5dd6c0;
            font-weight: 700;
        }
        [data-testid="stMetricDelta"] {
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================
# Title
# ==============================
st.title("📈 Indian Stock Market Dashboard")
st.caption("Live NSE & BSE Data • Growth % • Gainers/Losers • Business News • Sentiment")

# ==============================
# API key
# ==============================
API_KEY = "a9b91dc9740c491ab00c7b79d40486e4"

# ==============================
# Helper Functions
# ==============================
@st.cache_data(ttl=3600)
def fetch_nse_data():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=8)
        data = res.json().get("data", [])
        df = pd.DataFrame(data)
        cols = [c for c in ["symbol", "lastPrice", "pChange"] if c in df.columns]
        return df[cols] if cols else df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_bse_data():
    try:
        url = "https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?flag=Equity"
        res = requests.get(url, timeout=8)
        data = res.json().get("Table", [])
        df = pd.DataFrame(data)
        if not df.empty and {"Security_Name", "Scrip_Code"}.issubset(df.columns):
            return df[["Security_Name", "Scrip_Code"]]
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def get_stock_data(symbol, period="1mo"):
    try:
        df = yf.Ticker(symbol).history(period=period)
        return df
    except Exception:
        return pd.DataFrame()

def fetch_news(category="business", num_articles=8):
    if not API_KEY:
        return []
    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={API_KEY}&pageSize={num_articles}"
    try:
        res = requests.get(url, timeout=8)
        return res.json().get("articles", [])
    except Exception:
        return []

def analyze_sentiment(text):
    try:
        score = TextBlob(text).sentiment.polarity
        if score > 0: return "🟢 Positive"
        elif score < 0: return "🔴 Negative"
        else: return "⚪ Neutral"
    except Exception:
        return "⚪ Neutral"

# ==============================
# Sidebar Navigation
# ==============================
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Stock Search", "Top Movers", "Latest News", "Sentiment", "About"]
)

# ==============================
# 1️⃣ Dashboard
# ==============================
if page == "Dashboard":
    st.header("Market Overview")

    cols = st.columns(2)
    indices = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN"}
    for i, (label, symbol) in enumerate(indices.items()):
        with cols[i]:
            st.markdown(f"#### {label}")
            df = get_stock_data(symbol, "1mo")
            if not df.empty:
                start, end = df["Close"].iloc[0], df["Close"].iloc[-1]
                growth = ((end - start) / start) * 100
                st.metric(label="Index Value", value=f"₹{end:,.2f}", delta=f"{growth:.2f}%")
                st.line_chart(df["Close"], height=230)
            else:
                s
