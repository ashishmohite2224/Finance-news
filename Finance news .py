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
    initial_sidebar_state="expanded",
)

# ==============================
# Theme / CSS - Professional Dark Navy + Teal
# ==============================
st.markdown(
    """
    <style>
        /* App background and sidebar */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #071021 0%, #0b2540 100%);
            color: #EAF6F4;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #071021 0%, #0b2540 100%);
            color: #EAF6F4;
            border-right: 1px solid rgba(93,214,192,0.08);
        }

        /* Headings */
        h1, h2, h3, h4 { color: #5dd6c0; font-weight:700; }

        /* Buttons */
        .stButton>button {
            background-color: #5dd6c0 !important;
            color: #071021 !important;
            border-radius: 8px !important;
            padding: 0.45rem 0.8rem !important;
            font-weight: 700 !important;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            transition: 0.15s;
        }

        /* Cards & tables */
        .card {
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.35);
        }
        div[data-testid="stDataFrame"] {
            background: rgba(255,255,255,0.02);
            border-radius: 8px;
            padding: 8px;
        }

        /* Metric colors */
        [data-testid="stMetricValue"] { color: #5dd6c0; font-weight:700; }
        [data-testid="stMetricLabel"] { color: #EAF6F4; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================
# Title & small header row
# ==============================
st.title("📈 Indian Market Dashboard")
st.write("Professional dashboard • Live NSE/BSE stocks • Growth % • Gainers/Losers • Business News • Sentiment")

# ==============================
# API Key (NewsAPI) - Insert your own if needed
# ==============================
API_KEY = "a9b91dc9740c491ab00c7b79d40486e4"  # replace if needed

# ==============================
# Cached helper functions
# ==============================
@st.cache_data(ttl=1800)
def fetch_nse_data():
    """Fetch sample NSE list (NIFTY 500). Returns DataFrame or empty DF."""
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=8)
        res.raise_for_status()
        data = res.json().get("data", [])
        df = pd.DataFrame(data)
        cols = [c for c in ["symbol", "lastPrice", "pChange"] if c in df.columns]
        if cols:
            return df[cols]
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=1800)
def fetch_bse_data():
    """Fetch sample BSE scrip list. Returns DataFrame or empty DF."""
    try:
        url = "https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?flag=Equity"
        res = requests.get(url, timeout=8)
        res.raise_for_status()
        data = res.json().get("Table", [])
        df = pd.DataFrame(data)
        if not df.empty and {"Security_Name", "Scrip_Code"}.issubset(df.columns):
            return df[["Security_Name", "Scrip_Code"]]
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_news(category="business", num_articles=6):
    """Fetch news from NewsAPI (India)"""
    if not API_KEY:
        return []
    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={API_KEY}&pageSize={num_articles}"
    try:
        res = requests.get(url, timeout=8)
        res.raise_for_status()
        return res.json().get("articles", [])
    except Exception:
        return []

