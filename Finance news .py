import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from textblob import TextBlob
from datetime import datetime

# ------------------------------------------
# 🎯 Streamlit App Setup
# ------------------------------------------
st.set_page_config(
    page_title="Indian Market Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📊 Indian Stock Market Dashboard")
st.caption("Live Market Updates • Indian Stocks • Financial News • Sentiment Insights")

# ------------------------------------------
# 🔑 API Keys
# ------------------------------------------
API_KEY = "a9b91dc9740c491ab00c7b79d40486e4"

# ------------------------------------------
# 📂 Sidebar Menu
# ------------------------------------------
menu = st.sidebar.radio(
    "📁 Select Section",
    [
        "Market Overview",
        "Top Gainers & Losers",
        "Stock Price Tracker",
        "Market News",
        "Sentiment Analysis",
        "About"
    ]
)

# ------------------------------------------
# 🧩 Helper Functions
# ------------------------------------------

def fetch_news(category="business", num_articles=10):
    """Fetch latest financial news for India."""
    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={API_KEY}&pageSize={num_articles}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json().get("articles", [])
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

def get_stock_data(symbol, period="5d"):
    """Fetch stock data from Yahoo Finance."""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    except Exception as e:
        st.error(f"Error fetching stock data for {symbol}: {e}")
        return pd.DataFrame()

def get_sentiment(text):
    """Get sentiment from a news headline."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "🟢 Positive"
    elif polarity < 0:
        return "🔴 Negative"
    else:
        return "⚪ Neutral"

# ------------------------------------------
# 1️⃣ Market Overview
# ------------------------------------------
if menu == "Market Overview":
    st.header("📈 Market Overview: NIFTY 50 & SENSEX")

    indices = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN"
    }

    cols = st.columns(2)
    for i, (name, symbol) in enumerate(indices.items()):
        with cols[i]:
            data = get_stock_data(symbol)
            if not data.empty:
                last_close = data["Close"].iloc[-1]
                prev_close = data["Close"].iloc[-2]
                change = ((last_close - prev_close) / prev_close) * 100
                st.metric(label=name, value=f"₹{last_close:,.2f}", delta=f"{change:.2f}%")
                st.line_chart(data["Close"], height=200)
            else:
                st.warning(f"No data found for {name}")

# ------------------------------------------
# 2️⃣ Top Gainers & Losers (NSE Stocks)
# ------------------------------------------
elif menu == "Top Gainers & Losers":
    st.header("📊 Market Movers: Top Gainers & Losers")

    stocks = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ITC.NS", 
        "SBIN.NS", "ICICIBANK.NS", "LT.NS", "AXISBANK.NS", "BHARTIARTL.NS"
    ]

    data_list = []
    for symbol in stocks:
        data = get_stock_data(symbol, "2d")
        if len(data) >= 2:
            change = ((data["Close"].iloc[-1] - data["Close"].iloc[-2]) / data["Close"].iloc[-2]) * 100
            data_list.append({
                "Stock": symbol.replace(".NS", ""),
                "Last Price (₹)": round(data["Close"].iloc[-1], 2),
                "Change (%)": round(change, 2)
            })

    df = pd.DataFrame(data_list)
    if not df.empty:
        df_gainers = df.sort_values(by="Change (%)", ascending=False).head(5)
        df_losers = df.sort_values(by="Change (%)", ascending=True).head(5)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🏆 Top Gainers")
            st.dataframe(df_gainers, use_container_width=True)

        with col2:
            st.subheader("📉 Top Losers")
            st.dataframe(df_losers, use_container_width=True)
    else:
        st.warning("No stock data available right now.")

# ------------------------------------------
# 3️⃣ Stock Price Tracker
# ------------------------------------------
elif menu == "Stock Price Tracker":
    st.header("💹 Stock Price Tracker")
    st.write("Enter NSE stock symbol (e.g., RELIANCE.NS, TCS.NS, HDFCBANK.NS)")

    symbol = st.text_input("Enter Stock Symbol", "RELIANCE.NS")

    if st.button("Get Stock Data"):
        data = get_stock_data(symbol, "1mo")
        if not data.empty:
            st.subheader(f"Stock Performance: {symbol}")
            st.line_chart(data["Close"])
            st.metric("Last Close", f"₹{data['Close'].iloc[-1]:,.2f}")
            st.write(f"**High:** ₹{data['High'].iloc[-1]:,.2f} | **Low:** ₹{data['Low'].iloc[-1]:,.2f}")
            st.write(f"**Volume:** {data['Volume'].iloc[-1]:,}")
        else:
            st.warning("No stock data found. Try another symbol.")

# ------------------------------------------
# 4️⃣ Market News
# ------------------------------------------
elif menu == "Market News":
    st.header("📰 Latest Indian Financial & Market News")
    num_articles = st.sidebar.slider("🗞️ Number of Articles", 3, 15, 6)
    category = st.sidebar.selectbox("📂 Category", ["business", "general", "technology"], index=0)

    if st.button("Show Latest News"):
        articles = fetch_news(category, num_articles)
        if not articles:
            st.warning("No articles found.")
        else:
            for idx, article in enumerate(articles, start=1):
                st.markdown(f"### {idx}. [{article.get('title', 'No Title')}]({article.get('url', '#')})")
                if article.get("urlToImage"):
                    st.image(article["urlToImage"], use_container_width=True)
                st.caption(f"Source: {article.get('source', {}).get('name', 'Unknown')} | Published: {article.get('publishedAt', 'N/A')}")
                st.write(article.get("description", ""))
                st.write("---")

# ------------------------------------------
# 5️⃣ Sentiment Analysis
# ------------------------------------------
elif menu == "Sentiment Analysis":
    st.header("💬 News Sentiment: Indian Market Headlines")

    if st.button("Analyze Latest Business Headlines"):
        articles = fetch_news("business", 5)
        if not articles:
            st.warning("No headlines found.")
        else:
            for art in articles:
                title = art.get("title", "No Title")
                sentiment = get_sentiment(title)
                st.markdown(f"#### [{title}]({art.get('url', '#')})")
                st.write(f"Sentiment: {sentiment}")
                st.write("---")

# ------------------------------------------
# 6️⃣ About
# ------------------------------------------
elif menu == "About":
    st.header("ℹ️ About This Dashboard")
    st.markdown("""
    **📘 Indian Market Dashboard**  
    Built using Python & Streamlit to give real-time Indian stock market insights.

    **Features:**
    - NIFTY & SENSEX Overview 📈  
    - Top Gainers / Losers 📊  
    - Stock Price Tracker 💹  
    - Market News 📰  
    - Sentiment Analysis 💬  

    **Tech Used:** Streamlit • Yahoo Finance • NewsAPI • TextBlob • Pandas  
    """)

    st.success("💡 Developed by: Your Name (Finance Student @ BSE Institute)")
