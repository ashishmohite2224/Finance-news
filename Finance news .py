import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from textblob import TextBlob

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
# CUSTOM GREEN-BLUE THEME
# ==============================
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #013A63 0%, #026C7C 50%, #019267 100%);
            color: #EAF6F4;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #012C3D 0%, #013A63 100%);
            color: #EAF6F4;
        }
        h1, h2, h3, h4 {
            color: #2EF2B6;
            font-weight: 700;
        }
        .stButton>button {
            background-color: #00DFA2 !important;
            color: #012B39 !important;
            border-radius: 8px;
            font-weight: 700;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #38E4B7 !important;
            transform: scale(1.05);
        }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }
        [data-testid="stMetricValue"] { color: #00DFA2; font-weight: 700; }
        [data-testid="stMetricLabel"] { color: #EAF6F4; }
    </style>
""", unsafe_allow_html=True)

# ==============================
# API KEY
# ==============================
NEWS_API_KEY = "pub_0c5f15ab4f13424cbbad70c0c7fe1207"

# ==============================
# FUNCTIONS
# ==============================
@st.cache_data(ttl=1800)
def fetch_nse_data():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        df = pd.DataFrame(res.json().get("data", []))
        if "symbol" in df.columns:
            return df[["symbol", "lastPrice", "pChange"]]
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def fetch_market_news(num_articles=8):
    """Fetch latest Indian market-related news."""
    try:
        url = f"https://newsdata.io/api/1/news?country=in&category=business,markets&language=en&apikey={NEWS_API_KEY}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        return data.get("results", [])[:num_articles]
    except Exception as e:
        print("Error fetching news:", e)
        return []

def get_stock_data(symbol, period="1mo"):
    try:
        df = yf.Ticker(symbol).history(period=period)
        return df
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
        "ℹ️ About",
    ),
)

# ==============================
# 🏠 DASHBOARD
# ==============================
if page == "🏠 Dashboard":
    st.header("📊 Indian Market Overview")

    col1, col2, col3 = st.columns([1.2, 1.2, 1.6])

    nifty = get_stock_data("^NSEI", "1mo")
    sensex = get_stock_data("^BSESN", "1mo")

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📈 NIFTY 50")
        if not nifty.empty:
            start, end = nifty["Close"].iloc[0], nifty["Close"].iloc[-1]
            growth = ((end - start) / start) * 100
            st.metric("Value", f"₹{end:,.2f}", delta=f"{growth:.2f}%")
            st.line_chart(nifty["Close"], height=160)
        else:
            st.warning("NIFTY data unavailable.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📉 SENSEX")
        if not sensex.empty:
            start, end = sensex["Close"].iloc[0], sensex["Close"].iloc[-1]
            growth = ((end - start) / start) * 100
            st.metric("Value", f"₹{end:,.2f}", delta=f"{growth:.2f}%")
            st.line_chart(sensex["Close"], height=160)
        else:
            st.warning("SENSEX data unavailable.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📰 Latest Market News")
        news = fetch_market_news(5)
        if news:
            for n in news:
                st.markdown(f"- **[{n.get('title','No title')}]({n.get('link','#')})**")
        else:
            st.info("No market news available. Try again later.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📄 NSE Sample Data")
    df = fetch_nse_data()
    if not df.empty:
        df["pChange"] = pd.to_numeric(df["pChange"], errors="coerce").round(2)
        st.dataframe(df.head(25), use_container_width=True)
    else:
        st.info("NSE data currently unavailable.")

# ==============================
# 🔎 STOCK SEARCH
# ==============================
elif page == "🔎 Stock Search":
    st.header("🔎 Stock Search")
    symbol = st.text_input("Enter NSE Symbol (e.g., RELIANCE.NS, TCS.NS)", "RELIANCE.NS")
    period = st.selectbox("Select Timeframe", ["5d", "1mo", "3mo", "6mo", "1y"], index=1)
    if st.button("Show Data"):
        data = get_stock_data(symbol, period)
        if data.empty:
            st.error("Stock data not found.")
        else:
            start, end = data["Close"].iloc[0], data["Close"].iloc[-1]
            growth = ((end - start) / start) * 100
            st.metric("Growth", f"{growth:.2f}%")
            st.line_chart(data["Close"], height=350)
            st.dataframe(data.tail(), use_container_width=True)

# ==============================
# 🚀 TOP MOVERS
# ==============================
elif page == "🚀 Top Movers":
    st.header("🚀 Top Gainers & Losers (NSE)")
    df = fetch_nse_data()
    if df.empty:
        st.info("NSE data unavailable.")
    else:
        df["pChange"] = pd.to_numeric(df["pChange"], errors="coerce")
        gainers = df.sort_values("pChange", ascending=False).head(10)
        losers = df.sort_values("pChange", ascending=True).head(10)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🏆 Top Gainers")
            st.dataframe(gainers, use_container_width=True)
        with c2:
            st.subheader("📉 Top Losers")
            st.dataframe(losers, use_container_width=True)

# ==============================
# 📰 LATEST NEWS
# ==============================
elif page == "📰 Latest News":
    st.header("📰 Latest Market & Business News (India)")
    num = st.slider("Number of Articles", 3, 12, 6)
    if st.button("Load News"):
        articles = fetch_market_news(num)
        if not articles:
            st.warning("No news available. Try again later.")
        for i, art in enumerate(articles, start=1):
            st.markdown(f"### {i}. [{art.get('title')}]({art.get('link')})")
            if art.get("image_url"):
                st.image(art["image_url"], use_column_width=True)
            st.caption(f"{art.get('source_id','')} | {art.get('pubDate','')}")
            st.write(art.get("description", ""))
            st.write("---")

# ==============================
# 💬 SENTIMENT
# ==============================
elif page == "💬 Sentiment":
    st.header("💬 Market News Sentiment")
    if st.button("Analyze"):
        articles = fetch_market_news(8)
        if not articles:
            st.info("No news found.")
        else:
            for a in articles:
                title = a.get("title", "")
                sentiment = sentiment_label(title)
                st.markdown(f"- {sentiment}: {title}")

# ==============================
# ℹ️ ABOUT
# ==============================
else:
    st.header("ℹ️ About")
    st.markdown("""
    ### Indian Market Dashboard  
    **Features:**  
    - Live NIFTY / SENSEX charts  
    - Stock search with % growth  
    - Top Gainers & Losers  
    - Market-related business news  
    - Sentiment Analysis  
    - Blue-Green professional theme  
    """)
