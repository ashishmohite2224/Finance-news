import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from textblob import TextBlob
from datetime import datetime

# ==============================
# Page Config
# ==============================
st.set_page_config(
    page_title="📊 Indian Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================
# Professional Theme (Blue + Dark Mode)
# ==============================
st.markdown("""
    <style>
        /* Background */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #041427 0%, #0a2f5b 100%);
            color: #EAF6F4;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #061b33 0%, #082c54 100%);
            color: #EAF6F4;
        }
        h1, h2, h3, h4 {
            color: #58d1f5;
            font-weight: 700;
        }
        .stButton>button {
            background-color: #58d1f5 !important;
            color: #041427 !important;
            border-radius: 8px;
            font-weight: 700;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #89e0ff !important;
            transform: scale(1.03);
        }
        .card {
            background: rgba(255,255,255,0.04);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }
        [data-testid="stMetricValue"] { color: #58d1f5; font-weight: 700; }
        [data-testid="stMetricLabel"] { color: #EAF6F4; }
    </style>
""", unsafe_allow_html=True)

# ==============================
# App Header
# ==============================
st.title("📈 Indian Market Dashboard")
st.write("Live Market Overview • Stock Analysis • Top Movers • Business News • Sentiment Insights")

# ==============================
# NewsAPI Key
# ==============================
API_KEY = "a9b91dc9740c491ab00c7b79d40486e4"  # your API key

# ==============================
# Cached Data Fetchers
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
def fetch_news(category="business", num_articles=6):
    """Fetch Indian business news from NewsAPI"""
    if not API_KEY:
        return []
    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={API_KEY}&pageSize={num_articles}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json().get("articles", [])
    except Exception:
        return []

def get_stock_data(symbol, period="1mo"):
    """Get stock data using yfinance"""
    try:
        df = yf.Ticker(symbol).history(period=period)
        return df
    except Exception:
        return pd.DataFrame()

def sentiment_label(text):
    """Simple sentiment analysis"""
    score = TextBlob(text).sentiment.polarity
    if score > 0.1:
        return "🟢 Positive"
    elif score < -0.1:
        return "🔴 Negative"
    else:
        return "⚪ Neutral"

# ==============================
# Sidebar Navigation
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
# Dashboard
# ==============================
if page == "🏠 Dashboard":
    st.header("Market Overview")

    col1, col2, col3 = st.columns([1.2, 1.2, 1.6])

    nifty = get_stock_data("^NSEI", "1mo")
    sensex = get_stock_data("^BSESN", "1mo")

    # NIFTY
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 NIFTY 50")
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
        st.subheader("📈 SENSEX")
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
        st.subheader("📰 Latest Business Headlines")
        news = fetch_news("business", 5)
        if news:
            for n in news:
                st.markdown(f"- **{n.get('title','No title')}**")
        else:
            st.info("No latest news found.")
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
# Stock Search
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
# Top Movers
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
# Latest News
# ==============================
elif page == "📰 Latest News":
    st.header("📰 Latest Business News")
    num = st.slider("Number of Articles", 3, 12, 6)
    if st.button("Load News"):
        articles = fetch_news("business", num)
        if not articles:
            st.warning("No news available (API limit).")
        for i, art in enumerate(articles, start=1):
            st.markdown(f"### {i}. [{art.get('title')}]({art.get('url')})")
            if art.get("urlToImage"):
                st.image(art["urlToImage"], use_column_width=True)
            st.caption(f"{art.get('source',{}).get('name','')} | {art.get('publishedAt','')[:19].replace('T',' ')}")
            st.write(art.get("description", ""))
            st.write("---")

# ==============================
# Sentiment
# ==============================
elif page == "💬 Sentiment":
    st.header("💬 Business News Sentiment")
    if st.button("Analyze"):
        articles = fetch_news("business", 8)
        if not articles:
            st.info("No headlines found.")
        else:
            for a in articles:
                title = a.get("title", "")
                sentiment = sentiment_label(title)
                st.markdown(f"- {sentiment}: {title}")

# ==============================
# About
# ==============================
else:
    st.header("ℹ️ About")
    st.markdown("""
    ### Indian Market Dashboard  
    **Features:**  
    - Live NIFTY / SENSEX performance with charts  
    - Stock Search with growth %  
    - Top Gainers & Losers  
    - Latest Indian Business News  
    - Sentiment Analysis (AI-based)  
    - Professional blue-dark theme  

    **Notes:**  
    - Some NSE APIs may block direct access.  
    - Use `.NS` or `.BO` suffix for yfinance (e.g., RELIANCE.NS).  
    - NewsAPI may have daily request limits for free keys.
    """)
