import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from textblob import TextBlob
from datetime import datetime

# ------------------------------------------
# 🎯 Streamlit App Configuration
# ------------------------------------------
st.set_page_config(page_title="Indian Financial Market Dashboard", page_icon="🇮🇳", layout="wide")

st.title("🇮🇳 Indian Financial Market Dashboard")
st.caption("Real-time Financial Insights • Stock Data • FII/DII Flow • Market Sentiment")

# ------------------------------------------
# 🔐 API Key for NewsAPI
# ------------------------------------------
API_KEY = "a9b91dc9740c491ab00c7b79d40486e4"

# ------------------------------------------
# 🧭 Sidebar Navigation
# ------------------------------------------
menu = st.sidebar.radio(
    "📂 Select Section",
    [
        "Market Overview",
        "Indian Financial News",
        "Stock Price Tracker",
        "Market Movers",
        "FII/DII Data",
        "News Sentiment",
        "About App"
    ]
)

# ------------------------------------------
# 🧮 Helper Functions
# ------------------------------------------

def fetch_news(category="business", num_articles=10):
    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={API_KEY}&pageSize={num_articles}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json().get("articles", [])
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="5d")
        return data
    except Exception as e:
        st.error(f"Error fetching stock data for {symbol}: {e}")
        return pd.DataFrame()

def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "🟢 Positive"
    elif polarity < 0:
        return "🔴 Negative"
    else:
        return "⚪ Neutral"

# ------------------------------------------
# 🟢 1. Market Overview (Nifty + Sensex)
# ------------------------------------------
if menu == "Market Overview":
    st.header("📊 Market Overview: NIFTY 50 & SENSEX")

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
                st.line_chart(data["Close"])
            else:
                st.warning(f"No data found for {name}")

# ------------------------------------------
# 📰 2. Indian Financial News
# ------------------------------------------
elif menu == "Indian Financial News":
    st.header("📰 Latest Indian Financial & Stock Market News")
    num_articles = st.sidebar.slider("📰 Number of Articles", 3, 15, 6)
    category = st.sidebar.selectbox("📂 Category", ["business", "technology", "general"], index=0)

    if st.button("Get Latest News"):
        articles = fetch_news(category, num_articles)
        if not articles:
            st.warning("No articles found.")
        else:
            for idx, article in enumerate(articles, start=1):
                st.markdown(f"### {idx}. [{article.get('title', 'No Title')}]({article.get('url', '#')})")
                if article.get("urlToImage"):
                    st.image(article["urlToImage"], use_container_width=True)
                st.caption(f"Source: {article.get('source', {}).get('name', 'Unknown')} | Published: {article.get('publishedAt', 'N/A')}")
                st.write("---")

# ------------------------------------------
# 💹 3. Stock Price Tracker
# ------------------------------------------
elif menu == "Stock Price Tracker":
    st.header("💹 Indian Stock Price Tracker")
    st.write("Enter NSE stock symbol (e.g., RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS)")
    symbol = st.text_input("Enter Stock Symbol", "RELIANCE.NS")

    if st.button("Get Stock Data"):
        data = get_stock_data(symbol)
        if not data.empty:
            st.subheader(f"📈 Stock Performance: {symbol}")
            st.line_chart(data["Close"])
            st.metric("Last Close Price", f"₹{data['Close'].iloc[-1]:,.2f}")
            st.write(f"**High:** ₹{data['High'].iloc[-1]:,.2f} | **Low:** ₹{data['Low'].iloc[-1]:,.2f}")
            st.write(f"**Volume:** {data['Volume'].iloc[-1]:,}")
        else:
            st.warning("No data found. Try another symbol.")

# ------------------------------------------
# 📈 4. Market Movers (Top Gainers / Losers)
# ------------------------------------------
elif menu == "Market Movers":
    st.header("📈 Market Movers: Top Gainers / Losers (Sample NSE Stocks)")

    stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ITC.NS", "SBIN.NS", "ICICIBANK.NS"]
    data_list = []

    for symbol in stocks:
        data = get_stock_data(symbol)
        if len(data) >= 2:
            change = ((data["Close"].iloc[-1] - data["Close"].iloc[-2]) / data["Close"].iloc[-2]) * 100
            data_list.append({
                "Stock": symbol,
                "Last Price (₹)": round(data["Close"].iloc[-1], 2),
                "Change (%)": round(change, 2)
            })

    df = pd.DataFrame(data_list)
    df_gainers = df.sort_values(by="Change (%)", ascending=False)
    df_losers = df.sort_values(by="Change (%)", ascending=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Gainers")
        st.dataframe(df_gainers.head(5), use_container_width=True)

    with col2:
        st.subheader("Top Losers")
        st.dataframe(df_losers.head(5), use_container_width=True)

# ------------------------------------------
# 💰 5. FII/DII Data (Mock API)
# ------------------------------------------
elif menu == "FII/DII Data":
    st.header("💰 FII/DII Investment Data")

    try:
        # Using mock data (since NSE official API is restricted)
        fii_data = {
            "Date": ["2025-11-06", "2025-11-05", "2025-11-04"],
            "FII (₹ Cr)": [1450.25, -980.60, 1220.35],
            "DII (₹ Cr)": [-520.45, 880.15, -300.25]
        }
        df_fii = pd.DataFrame(fii_data)
        st.dataframe(df_fii, use_container_width=True)

        st.bar_chart(df_fii.set_index("Date")[["FII (₹ Cr)", "DII (₹ Cr)"]])
        st.info("📝 Note: FII/DII data shown is a demo representation for app design.")
    except Exception as e:
        st.error(f"Error fetching FII/DII data: {e}")

# ------------------------------------------
# 💬 6. News Sentiment
# ------------------------------------------
elif menu == "News Sentiment":
    st.header("💬 Sentiment Analysis of Indian Financial Headlines")

    if st.button("Analyze Latest Headlines"):
        articles = fetch_news("business", 5)
        if not articles:
            st.warning("No news found.")
        else:
            for art in articles:
                title = art.get("title", "No Title")
                sentiment = get_sentiment(title)
                st.markdown(f"### [{title}]({art.get('url', '#')})")
                st.write(f"Sentiment: {sentiment}")
                st.write("---")

# ------------------------------------------
# ℹ️ 7. About App
# ------------------------------------------
elif menu == "About App":
    st.header("📘 About This App")
    st.markdown("""
    This dashboard is built to help **Indian investors, traders, and students** analyze market trends easily.

    **Features:**
    - Live Indian financial news 📰  
    - Real-time stock tracker 💹  
    - Nifty & Sensex overview 📊  
    - FII/DII inflow-outflow data 💰  
    - Sentiment analysis of news 💬  

    **Tech Used:** Streamlit, Yahoo Finance API, NewsAPI, TextBlob, Pandas
    """)

    st.success("💡 Developed by: Your Name (Finance Student @ BSE Institute)")
