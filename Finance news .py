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
        if not df.empty and "Security_Name" in df.columns and "Scrip_Code" in df.columns:
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
    cols = st.columns(2)

    indices = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN"}
    for i, (label, symbol) in enumerate(indices.items()):
        with cols[i]:
            st.markdown(f"#### {label}")
            df = get_stock_data(symbol, period="1mo")
            if not df.empty and "Close" in df.columns and len(df["Close"]) >= 2:
                start = df["Close"].iloc[0]
                end = df["Close"].iloc[-1]
                growth = ((end - start) / start) * 100
                st.metric(label="Value", value=f"₹{end:,.2f}", delta=f"{growth:.2f}%")
                st.line_chart(df["Close"], height=220)
            else:
                st.warning(f"No data available for {label}")

    st.markdown("---")
    st.subheader("NSE Snapshot (sample)")
    nse_df = fetch_nse_data()
    if not nse_df.empty:
        display_df = nse_df.copy()
        if "lastPrice" in display_df.columns:
            display_df["lastPrice"] = pd.to_numeric(display_df["lastPrice"], errors="coerce").round(2)
        if "pChange" in display_df.columns:
            display_df["pChange"] = pd.to_numeric(display_df["pChange"], errors="coerce").round(2)
        st.dataframe(display_df.head(30), use_container_width=True)
    else:
        st.info("NSE sample data not available right now (NSE site may block direct requests).")

# ==============================
# Page: Stock Search
# ==============================
elif page == "Stock Search":
    st.header("Stock Search (NSE & BSE)")

    nse_df = fetch_nse_data()
    bse_df = fetch_bse_data()

    stock_options = []
    if not nse_df.empty and "symbol" in nse_df.columns:
        stock_options += nse_df["symbol"].astype(str).tolist()
    if not bse_df.empty and "Security_Name" in bse_df.columns:
        stock_options += bse_df["Security_Name"].astype(str).tolist()

    if not stock_options:
        st.warning("Stock lists could not be loaded. You can still enter an NSE symbol manually (e.g., RELIANCE.NS).")
        manual_symbol = st.text_input("Enter NSE symbol manually", "RELIANCE.NS")
        symbol_to_show = manual_symbol.strip()
    else:
        symbol_choice = st.selectbox("Choose stock (or type manually)", sorted(set(stock_options)))
        manual_symbol = st.text_input("Or enter symbol manually (NSE format like RELIANCE.NS)", "")
        if manual_symbol.strip():
            symbol_to_show = manual_symbol.strip()
        else:
            # If the selected symbol looks like an NSE symbol (uppercase), append .NS for yfinance
            if symbol_choice.isupper():
                symbol_to_show = symbol_choice + ".NS"
            else:
                symbol_to_show = symbol_choice

    period = st.selectbox("Timeframe", ["5d", "1mo", "3mo", "6mo", "1y"], index=1)

    if st.button("Show"):
        df = get_stock_data(symbol_to_show, period=period)
        if not df.empty and "Close" in df.columns:
            start = df["Close"].iloc[0]
            end = df["Close"].iloc[-1]
            growth = ((end - start) / start) * 100
            st.metric(label=f"{symbol_to_show} (Close)", value=f"₹{end:,.2f}", delta=f"{growth:.2f}%")
            st.line_chart(df["Close"], height=300)
            st.write("Latest stats:")
            last_row = df.iloc[-1]
            st.write({
                "Open": f"₹{last_row['Open']:,.2f}",
                "High": f"₹{last_row['High']:,.2f}",
                "Low": f"₹{last_row['Low']:,.2f}",
                "Volume": f"{int(last_row['Volume']):,}"
            })
        else:
            st.error("Price data not available for this symbol. Try another symbol or manual input like RELIANCE.NS")

# ==============================
# Page: Top Movers
# ==============================
elif page == "Top Movers":
    st.header("Top Gainers & Losers (NSE sample)")
    nse_df = fetch_nse_data()
    if not nse_df.empty and "pChange" in nse_df.columns:
        df = nse_df.copy()
        df["pChange"] = pd.to_numeric(df["pChange"], errors="coerce")
        gainers = df.sort_values("pChange", ascending=False).head(10)
        losers = df.sort_values("pChange", ascending=True).head(10)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Top Gainers")
            st.dataframe(gainers.reset_index(drop=True), use_container_width=True)
        with c2:
            st.subheader("Top Losers")
            st.dataframe(losers.reset_index(drop=True), use_container_width=True)
    else:
        st.info("Top movers data not available right now. Try again later.")

# ==============================
# Page: Latest News
# ==============================
elif page == "Latest News":
    st.header("Latest Business & Market News (India)")
    num = st.slider("Number of articles", 3, 12, 6)
    if st.button("Load News"):
        articles = fetch_news("business", num)
        if not articles:
            st.info("No news available or NewsAPI limit reached.")
        else:
            for i, art in enumerate(articles, start=1):
                title = art.get("title", "No title")
                url = art.get("url", "#")
                img = art.get("urlToImage")
                source = art.get("source", {}).get("name", "Unknown")
                date = art.get("publishedAt", "")[:19].replace("T", " ")
                description = art.get("description", "")
                st.markdown(f"### {i}. [{title}]({url})")
                if img:
                    st.image(img, use_container_width=True)
                st.caption(f"{source} | {date}")
                st.write(description)
                st.write("---")

# ==============================
# Page: Sentiment
# ==============================
elif page == "Sentiment":
    st.header("Sentiment Analysis for Latest Headlines")
    if st.button("Analyze"):
        articles = fetch_news("business", 8)
        if not articles:
            st.info("No headlines available to analyze.")
        else:
            for art in articles:
                title = art.get("title", "")
                url = art.get("url", "#")
                label = analyze_sentiment(title)
                st.markdown(f"- [{title}]({url})  → **{label}**")

# ==============================
# Page: About
# ==============================
else:
    st.header("About")
    st.markdown(
        """
        **Indian Stock Market Dashboard**  
        - Dark professional UI with blue accent  
        - NSE & BSE sample lists (NSE: NIFTY 500 sample)  
        - Stock search with line chart and growth % by timeframe  
        - Top gainers & losers, latest news and headline sentiment  

        ⚠️ Notes:
        - NSE may block direct requests; if NSE endpoints fail, use manual symbol input (e.g. RELIANCE.NS) for prices.
        - NewsAPI may have rate limits; ensure your API key is active.
        """
    )
    st.success("Ready — run analysis and explore stocks!")
