import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from textblob import TextBlob

# ==============================
# 🎨 Streamlit Page Configuration
# ==============================
st.set_page_config(
    page_title="📊 Indian Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
)

# ==============================
# 🌈 Custom CSS Theme (Dark + Blue)
# ==============================
st.markdown("""
    <style>
        body {
            background-color: #0b132b;
            color: #e0e0e0;
        }
        [data-testid="stAppViewContainer"] {
            background-color: #0b132b;
        }
        [data-testid="stSidebar"] {
            background-color: #1c2541;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #00bfff;
        }
        .stButton>button {
            background-color: #00bfff !important;
            color: black !important;
            border-radius: 10px;
            font-weight: bold;
        }
        .stMetric label, .stDataFrame, .stMarkdown {
            color: #e0e0e0 !important;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================
# 🧭 Title
# ==============================
st.title("📈 Indian Stock Market Dashboard")
st.caption("Real-time NSE & BSE Stocks • Growth % • Business News • Sentiment Analysis")

# ==============================
# 🔑 API Keys
# ==============================
API_KEY = "a9b91dc9740c491ab00c7b79d40486e4"

# ==============================
# 📦 Helper Functions
# ==============================
@st.cache_data(ttl=3600)
def fetch_nse_stocks():
    """Fetch NSE listed stocks (NIFTY 500 sample)"""
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        data = res.json()["data"]
        df = pd.DataFrame(data)[["symbol", "lastPrice", "pChange"]]
        return df
    except Exception as e:
        st.error(f"Error fetching NSE data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_bse_stocks():
    """Fetch sample of BSE listed stocks"""
    try:
        url = "https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?flag=Equity"
        res = requests.get(url)
        data = res.json().get("Table", [])
        df = pd.DataFrame(data)
        return df[["Security_Name", "Scrip_Code"]] if not df.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

def get_stock_data(symbol, period="1mo"):
    """Fetch stock price data"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    except:
        return pd.DataFrame()

def fetch_news(category="business", num_articles=10):
    """Fetch latest business or market news for India"""
    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={API_KEY}&pageSize={num_articles}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json().get("articles", [])
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

def get_sentiment(text):
    """Analyze text sentiment"""
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0: return "🟢 Positive"
    elif polarity < 0: return "🔴 Negative"
    else: return "⚪ Neutral"

# ==============================
# 📑 Sidebar Navigation
# ==============================
menu = st.sidebar.radio(
    "📁 Navigate",
    ["Market Overview", "Stock Search", "Market Movers", "Latest News", "Sentiment Analysis", "About"]
)

# ==============================
# 1️⃣ Market Overview
# ==============================
if menu == "Market Overview":
    st.header("📊 NIFTY & SENSEX Overview")

    indices = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN"}
    cols = st.columns(2)

    for i, (name, symbol) in enumerate(indices.items()):
        with cols[i]:
            data = get_stock_data(symbol, "1mo")
            if not data.empty:
                start_price = data["Close"].iloc[0]
                end_price = data["Close"].iloc[-1]
                growth = ((end_price - start_price) / start_price) * 100
                st.metric(label=name, value=f"₹{end_price:,.2f}", delta=f"{growth:.2f}%")
                st.line_chart(data["Close"], height=220)
            else:
                st.warning(f"No data for {name}")

# ==============================
# 2️⃣ Stock Search
# ==============================
elif menu == "Stock Search":
    st.header("🔍 Search NSE & BSE Stocks")

    nse_df = fetch_nse_stocks()
    bse_df = fetch_bse_stocks()

    all_stocks = []
    if not nse_df.empty:
        all_stocks.extend(nse_df["symbol"].tolist())
    if not bse_df.empty:
        all_stocks.extend(bse_df["Security_Name"].tolist())

    selected_stock = st.selectbox("Select Stock", sorted(set(all_stocks)))
    period = st.selectbox("Select Time Period", ["5d", "1mo", "3mo", "6mo", "1y"], index=1)

    if st.button("Show Stock Data"):
        ticker = selected_stock + ".NS" if selected_stock.isupper() else selected_stock
        data = get_stock_data(ticker, period)
        if not data.empty:
            start_price = data["Close"].iloc[0]
            end_price = data["Close"].iloc[-1]
            growth = ((end_price - start_price) / start_price) * 100
            st.metric(label=f"{selected_stock} Growth", value=f"₹{end_price:,.2f}", delta=f"{growth:.2f}%")
            st.line_chart(data["Close"], height=300)
        else:
            st.warning("No data found for this stock.")

# ==============================
# 3️⃣ Market Movers
# ==============================
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
        st.warning("Unable to load NSE market data")

# ==============================
# 4️⃣ Latest News (Business + Market)
# ==============================
elif menu == "Latest News":
    st.header("📰 Latest Business & Market News (India)")

    news_articles = fetch_news("business", 8)
    if not news_articles:
        st.warning("No latest news found.")
    else:
        for idx, article in enumerate(news_articles, start=1):
            st.markdown(f"### {idx}. [{article.get('title','No Title')}]({article.get('url','#')})")
            if article.get("urlToImage"):
                st.image(article["urlToImage"], use_container_width=True)
            st.caption(f"🗞️ {article.get('source', {}).get('name', 'Unknown')} | 🕒 {article.get('publishedAt', 'N/A')}")
            st.write(article.get("description", ""))
            st.write("---")

# ==============================
# 5️⃣ Sentiment Analysis
# ==============================
elif menu == "Sentiment Analysis":
    st.header("💬 Sentiment of Business Headlines")

    if st.button("Analyze"):
        articles = fetch_news("business", 5)
        for art in articles:
            title = art.get("title", "")
            sentiment = get_sentiment(title)
            st.markdown(f"#### [{title}]({art.get('url', '#')})")
            st.write(f"Sentiment: {sentiment}")
            st.write("---")

# ==============================
# 6️⃣ About
# ==============================
else:
    st.header("ℹ️ About This Dashboard")
    st.markdown("""
    **Indian Market Dashboard**  
    Real-time NSE & BSE stock data with performance graphs, gainers/losers, and business news.

    **Features:**
    - Dark Blue Professional Theme  
    - Line Graphs + Growth %  
    - Top Gainers/Losers  
    - Live Business News  
    - Sentiment Analysis  

    💡 **Developer:** Finance Student @ BSE Institute
    """)
    st.success("✅ Ready for professional use!")
