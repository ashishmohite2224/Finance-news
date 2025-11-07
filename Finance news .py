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
# Custom dark-blue theme CSS
# ==============================
st.markdown(
    """
    <style>
        body { background-color: #0a0f24; color: #f5f5f5; }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(180deg, #0b132b, #1c2541);
            color: white;
        }
        [data-testid="stSidebar"] { background-color: #0b132b; border-right: 1px solid #1c2541; }
        h1, h2, h3 { color: #00bfff; font-weight: 700; }
        .stButton>button {
            background-color: #00bfff !important;
            color: black !important;
            border-radius: 8px;
            font-weight: 700;
        }
        .card {
            background-color: #1c2541;
            border-radius: 10px;
            padding: 16px;
            box-shadow: 0 0 10px rgba(0,191,255,0.08);
            margin-bottom: 18px;
        }
        .stMetric label, .stDataFrame { color: #f5f5f5 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📈 Indian Stock Market Dashboard")
st.caption("NSE & BSE • Growth % • Business News • Sentiment (Dark Blue Theme)")

# ==============================
# NewsAPI key - replace if needed
# ==============================
API_KEY = "a9b91dc9740c491ab00c7b79d40486e4"

# ==============================
# Helper functions
# ==============================

@st.cache_data(ttl=3600)
def fetch_nse_data():
    """
    Fetch NIFTY500 list (sample) from NSE. Returns DataFrame with symbol, lastPrice, pChange.
    Note: NSE blocks frequent scraping; calls may fail if NSE blocks the request.
    """
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        res = requests.get(url, headers=headers, timeout=8)
        res.raise_for_status()
        data = res.json().get("data", [])
        df = pd.DataFrame(data)
        # Keep symbol, lastPrice and pChange if available, else return minimal df
        cols = []
        if "symbol" in df.columns:
            cols.append("symbol")
        if "lastPrice" in df.columns:
            cols.append("lastPrice")
        if "pChange" in df.columns:
            cols.append("pChange")
        if cols:
            return df[cols]
        return df
    except Exception:
        # Return empty DataFrame on failure
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_bse_data():
    """
    Fetch BSE list sample. Returns DataFrame with Security_Name and Scrip_Code if available.
    """
    try:
        url = "https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?flag=Equity"
        res = requests.get(url, timeout=8)
        res.raise_for_status()
        data = res.json().get("Table", [])
        df = pd.DataFrame(data)
        if not df.empty:
            # Normalize column names
            if "Security_Name" in df.columns and "Scrip_Code" in df.columns:
                return df[["Security_Name", "Scrip_Code"]]
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def get_stock_data(symbol: str, period: str = "1mo"):
    """Return historical price DataFrame using yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        return df
    except Exception:
        return pd.DataFrame()

def fetch_news(category: str = "business", num_articles: int = 8):
    """Fetch top headlines for India from NewsAPI."""
    if not API_KEY or API_KEY.strip() == "":
        return []
    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={API_KEY}&pageSize={num_articles}"
    try:
        res = requests.get(url, timeout=8)
        res.raise_for_status()
        return res.json().get("articles", [])
    except Exception:
        return []

def analyze_sentiment(text: str):
    """Return simple sentiment label using TextBlob polarity."""
    try:
        polarity = TextBlob(text).sentiment.polarity
        if polarity > 0:
            return "🟢 Positive"
        elif polarity < 0:
            return "🔴 Negative"
        else:
            return "⚪ Neutral"
    except Exception:
        return "⚪ Neutral"

# ==============================
# Sidebar navigation
# ==============================
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Sections",
    ["Dashboard", "Stock Search", "Top Movers", "Latest News", "Sentiment", "About"],
)

# ==============================
# Page: Dashboard
# ==============================
if page == "Dashboard":
    st.header("Market Overview")
    col1, col2 = st.columns(2)

    indices = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN"}
    for i, (label, symbol) in enumerate(indices.items()):
        with (col
