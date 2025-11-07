import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime
from textblob import TextBlob

# ======================================
# Streamlit Configuration & Styling
# ======================================
st.set_page_config(
    page_title="📊 Indian Market Dashboard",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>
    body { background-color: #0e1117; color: #f1f1f1; }
    [data-testid="stSidebar"] { background-color: #1b1f2a; }
    h1, h2, h3, h4 { color: #00bfff; }
    .stMetric label { color: #f5f5f5 !important; }
    .stButton>button {
        background-color: #00bfff !important;
        color: black !important;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Indian Stock Market Dashboard")
st.caption("Live NSE & BSE Data • Growth % • Business News • Sentiment")

# ======================================
# News API Key
# ======================================
API_KEY = "a9b91dc9740c491ab00c7b79d40486e4"

# ======================================
# Helper Functions
# ======================================
@st.cache_data(ttl=3600)
def fetch_nse_stocks():
    """Fetch all NSE listed stocks"""
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        data = res.json()["data"]
        df = pd.DataFrame(data)[["symbol", "lastPrice", "pChange"]]
        return df
    except Exception as e:
        st.error(f"Error loading NSE list: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_bse_stocks():
    """Fetch BSE SENSEX & 500 sample companies"""
    try:
        bse_url = "https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?flag=Equity"
        res = requests.get(bse_url)
        data = res.json().get("Table", [])
        df = pd.DataFrame(data)
        return df[["Security_Name", "Scrip_Code"]] if not df.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

def get_stock_data(symbol, period="1mo"):
    """Fetch stock history from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    except:
        return pd.DataFrame()

def fetch_news(category="business", num_articles=8):
    """Fetch business news for India"""
    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={API_KEY}&pageSize={num_articles}"
    res = requests.get(url)
    return res.json().get("articles", [])

def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0: return "🟢 Positive"
    elif polarity < 0: return "🔴 Negative"
    else: return "⚪ Neutral"

# ======================================
# Sidebar Navigation
# ======================================
menu = st.sidebar.radio(
    "📁 Navigate",
    ["Market Overview", "Stock Search", "Market Movers", "Business News", "Sentiment Analysis", "About"]
)

# ======================================
# 1️⃣ Market Overview
# ======================================
if menu == "Market Overview":
    st.header("📊 NIFTY & SENSEX Overview")
    indices = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN"}
    cols = st.columns(2)
    for i, (name, symbol) in enumerate(indices.items()):
        with cols[i]:
            data = get_stock_data(symbol, "1mo")
            if not data.empty:
                start_price, end_price = data["Close"].iloc[0], data["Close"].iloc[-1]
                growth = ((end_price - start_price) / start_price) * 100
                st.metric(label=name, value=f"₹{end_price:,.2f}", delta=f"{growth:.2f}%")
                st.line_chart(data["Close"], height=200)
            else:
                st.warning(f"No data for {name}")

# ======================================
# 2️⃣ Stock Search (All NSE + BSE)
# ======================================
elif menu == "Stock Search":
    st.header("🔍 Search Stocks (NSE + BSE)")

    nse_df = fetch_nse_stocks()
    bse_df = fetch_bse_stocks()

    all_symbols = []
    if not nse_df.empty:
        all_symbols.extend(nse_df["symbol"].tolist())
    if not bse_df.empty:
        all_symbols.extend(bse_df["Security_Name"].tolist())

    selected_stock = st.selectbox("Select a Stock", sorted(set(all_symbols)))
    time_frame = st.selectbox("Select Period", ["5d", "1mo", "3mo", "6mo", "1y"], index=1)

    if st.button("Show Stock Data"):
        ticker_symbol = selected_stock + ".NS" if selected_stock.isupper() else selected_stock
        data = get_stock_data(ticker_symbol, time_frame)
        if not data.empty:
            start_price = data["Close"].iloc[0]
            end_price = data["Close"].iloc[-1]
            growth = ((end_price - start_price) / start_price) * 100
            st.metric(label=f"{selected_stock} Growth", value=f"₹{end_price:,.2f}", delta=f"{growth:.2f}%")
            st.line_chart(data["Close"], height=300)
        else:
            st.warning("No data found for selected stock")

# ======================================
# 3️⃣ Market Movers
# ======================================
elif menu == "Market Movers":
    st.header("📈 Top Gainers & 📉 Losers (NSE)")

    df = fetch_nse_stocks()
    if not df.empty:
        gainers = df.sort_values(by="pChange", ascending=False).head(10)
        losers = df.sort_values(by="pChange", ascending=True).head(10)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🏆 Top Gainers")
            st.dataframe(gainers, use_container_width=True)
        with col2:
            st.subheader("📉 Top Losers")
            st.dataframe(losers, use_container_width=True)
    else:
        st.warning("Could not load NSE data")

# ======================================
# 4️⃣ Business News
# ======================================
elif menu == "Business News":
    st.header("📰 Latest Business News (India)")
    articles = fetch_news("business", 8)
    for idx, art in enumerate(articles, start=1):
        st.markdown(f"### {idx}. [{art.get('title','No Title')}]({art.get('url','#')})")
        if art.get("urlToImage"): st.image(art["urlToImage"], use_container_width=True)
        st.caption(f"🗞️ {art.get('source', {}).get('name', 'Unknown')} | 🕒 {art.get('publishedAt', 'N/A')}")
        st.write(art.get("description", ""))
        st.write("---")

# ======================================
# 5️⃣ Sentiment Analysis
# ======================================
elif menu == "Sentiment Analysis":
    st.header("💬 Sentiment of Latest Business Headlines")
    if st.button("Analyze"):
        articles = fetch_news("business", 5)
        for art in articles:
            title = art.get("title", "")
            sentiment = get_sentiment(title)
            st.markdown(f"#### [{title}]({art.get('url', '#')})")
            st.write(f"Sentiment: {sentiment}")
            st.write("---")

# ======================================
# 6️⃣ About
# ======================================
else:
    st.header("ℹ️ About This Dashboard")
    st.markdown("""
    **Indian Market Dashboard**  
    Real-time stock data, market movers, and business news.  
    - Uses NSE/BSE APIs + Yahoo Finance  
    - Growth %, Graphs, Sentiment  
    - Modern UI for professionals  

    **Developer:** Finance Student @ BSE Institute  
    """)

    st.success("✅ Dashboard loaded successfully")
