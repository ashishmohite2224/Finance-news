import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from textblob import TextBlob
from datetime import datetime

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="📊 Indian Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================
# THEME: GREEN + BLUE PROFESSIONAL + DARK SIDEBAR
# ==============================
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #021C2A 0%, #053B3F 100%);
            color: #EAF6F4;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #011016 0%, #012B33 100%);
            color: #EAF6F4;
        }
        [data-testid="stSidebarNav"] { color: white !important; }
        h1, h2, h3, h4 {
            color: #00F5A0;
            font-weight: 700;
        }
        .stButton>button {
            background-color: #00C3FF !important;
            color: #021C2A !important;
            border-radius: 8px;
            font-weight: 700;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #00F5A0 !important;
            transform: scale(1.05);
        }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }
        [data-testid="stMetricValue"] { color: #00F5A0; font-weight: 700; }
        [data-testid="stMetricLabel"] { color: #EAF6F4; }
    </style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.title("📈 Indian Market Dashboard")
st.write("Live Market Overview • Stock Analysis • Top Movers • Business News • Sentiment Insights")

# ==============================
# API KEYS
# ==============================
NEWSDATA_API_KEY = "pub_0c5f15ab4f13424cbbad70c0c7fe1207"

# ==============================
# FUNCTIONS
# ==============================
@st.cache_data(ttl=1800)
def fetch_nse_data():
    """Fetch sample NSE stock data."""
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json().get("data", [])
        df = pd.DataFrame(data)
        if "symbol" in df.columns and "lastPrice" in df.columns:
            return df[["symbol", "lastPrice", "pChange"]]
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_newsdata(category="business", num_articles=6):
    """Fetch latest Indian market/business news from NewsData.io"""
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&country=in&language=en&category={category}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json().get("results", [])
        return data[:num_articles]
    except Exception:
        return []

def get_stock_data(symbol, period="1mo"):
    try:
        return yf.Ticker(symbol).history(period=period)
    except Exception:
        return pd.DataFrame()

def sentiment_label(text):
    score = TextBlob(text).sentiment.polarity
    if score > 0.1:
        return "🟢 Positive"
    elif score < -0.1:
        return "🔴 Negative"
    else:
        return "⚪ Neutral"

# ==============================
# SIDEBAR NAVIGATION
# ==============================
st.sidebar.title("📍 Navigation")
page = st.sidebar.radio(
    "Go to",
    (
        "🏠 Dashboard",
        "🔎 Stock Search",
        "🚀 Top Movers",
        "📰 Latest News",
        "💬 Sentiment",
        "ℹ️ About"
    ),
)

# ==============================
# DASHBOARD
# ==============================
if page == "🏠 Dashboard":
    st.header("📊 Market Overview")

    col1, col2, col3 = st.columns([1.2, 1.2, 1.6])

    nifty = get_stock_data("^NSEI", "1mo")
    sensex = get_stock_data("^BSESN", "1mo")

    # NIFTY
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("NIFTY 50")
        if not nifty.empty:
            start, end = nifty["Close"].iloc[0], nifty["Close"].iloc[-1]
            growth = ((end - start) / start) * 100
            st.metric("Value", f"₹{end:,.2f}", delta=f"{growth:.2f}%")
            st.line_chart(nifty["Close"], height=160)
        else:
            st.warning("NIFTY data unavailable.")
        st.markdown('</div>', unsafe_allow_html=True)

    # SENSEX
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("SENSEX")
        if not sensex.empty:
            start, end = sensex["Close"].iloc[0], sensex["Close"].iloc[-1]
            growth = ((end - start) / start) * 100
            st.metric("Value", f"₹{end:,.2f}", delta=f"{growth:.2f}%")
            st.line_chart(sensex["Close"], height=160)
        else:
            st.warning("SENSEX data unavailable.")
        st.markdown('</div>', unsafe_allow_html=True)

    # News snapshot
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📰 Latest Market Headlines")
        news = fetch_newsdata("business", 5)
        if news:
            for n in news:
                st.markdown(f"- **{n.get('title','No title')}**")
        else:
            st.info("News unavailable. Please try later.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📄 NSE Snapshot (Sample)")
    df = fetch_nse_data()
    if not df.empty:
        df["pChange"] = pd.to_numeric(df["pChange"], errors="coerce").round(2)
        st.dataframe(df.head(30), use_container_width=True)
    else:
        st.info("NSE data currently unavailable.")

# ==============================
# STOCK SEARCH
# ==============================
elif page == "🔎 Stock Search":
    st.header("🔍 Stock Search & Chart")
    symbol = st.text_input("Enter NSE symbol (e.g., RELIANCE.NS, TCS.NS)", "RELIANCE.NS")
    period = st.selectbox("Select timeframe", ["5d", "1mo", "3mo", "6mo", "1y"], index=1)

    if st.button("Show Data"):
        data = get_stock_data(symbol, period)
        if data.empty:
            st.error("Data not found. Try another stock symbol.")
        else:
            start, end = data["Close"].iloc[0], data["Close"].iloc[-1]
            growth = ((end - start) / start) * 100
            st.metric("Growth", f"{growth:.2f}%")
            st.line_chart(data["Close"], height=350)
            st.dataframe(data.tail(), use_container_width=True)

# ==============================
# TOP MOVERS
# ==============================
elif page == "🚀 Top Movers":
    st.header("🚀 Top Gainers & Losers (NSE)")
    df = fetch_nse_data()
    if df.empty:
        st.info("NSE data not available.")
    else:
        df["pChange"] = pd.to_numeric(df["pChange"], errors="coerce")
        gainers = df.sort_values("pChange", ascending=False).head(10)
        losers = df.sort_values("pChange", ascending=True).head(10)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🏆 Top Gainers")
            st.dataframe(gainers.reset_index(drop=True), use_container_width=True)
        with c2:
            st.subheader("📉 Top Losers")
            st.dataframe(losers.reset_index(drop=True), use_container_width=True)

# ==============================
# LATEST NEWS
# ==============================
elif page == "📰 Latest News":
    st.header("📰 Latest Indian Market & Business News")
    num = st.slider("Number of Articles", 3, 12, 6)
    if st.button("Load News"):
        articles = fetch_newsdata("business", num)
        if not articles:
            st.warning("News unavailable. Please try again later.")
        for i, art in enumerate(articles, start=1):
            st.markdown(f"### {i}. [{art.get('title')}]({art.get('link')})")
            if art.get(
