import streamlit as st
import requests
from datetime import datetime, timedelta

# -------------------------------
# Streamlit App Configuration
# -------------------------------
st.set_page_config(
    page_title="Financial News Dashboard",
    page_icon="💹",
    layout="wide"
)

st.title("💹 Financial News & IPO Dashboard")
st.write("Get the latest financial news, stock updates, IPO info, and more!")

# -------------------------------
# ✅ Use Your API Key Here
# -------------------------------
# 🔑 Replace below with your actual NewsAPI key
API_KEY = "123abc456def789ghi"  # <-- PUT YOUR REAL KEY HERE

if not API_KEY or API_KEY == "your_real_newsapi_key_here":
    st.error("⚠️ Missing valid API key. Please update the API_KEY variable in the code.")
    st.stop()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filters")

country = st.sidebar.selectbox("🌍 Country", ["us", "gb", "in", "ca", "au"], index=2)
category = st.sidebar.selectbox(
    "🗂️ Category",
    ["business", "general", "technology", "entertainment", "health", "science", "sports"],
    index=0
)
keyword = st.sidebar.text_input("🔍 Keyword (optional, e.g., stock, IPO, crypto)")
source = st.sidebar.text_input("📰 News Source (optional, e.g., bloomberg, cnbc)")
num_articles = st.sidebar.slider("📰 Number of Articles", 1, 20, 5)
to_date = st.sidebar.date_input("To Date", datetime.today())
from_date = st.sidebar.date_input("From Date", datetime.today() - timedelta(days=7))

# -------------------------------
# Function to Fetch News
# -------------------------------
@st.cache_data(ttl=600)
def fetch_news(category, country, keyword, source, num_articles, from_date, to_date):
    endpoint = "top-headlines" if not keyword else "everything"
    base_url = f"https://newsapi.org/v2/{endpoint}"

    params = {
        "apiKey": API_KEY,
        "pageSize": num_articles,
        "sortBy": "publishedAt"
    }

    if source:
        params["sources"] = source
    elif endpoint == "top-headlines":
        params["country"] = country
        params["category"] = category

    if keyword:
        params["q"] = keyword
        params["from"] = from_date
        params["to"] = to_date

    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 401:
            st.error("❌ Unauthorized: Invalid API key. Please check your API key.")
            return []
        response.raise_for_status()
        return response.json().get("articles", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news: {e}")
        return []

# -------------------------------
# Display News
# -------------------------------
if st.button("Get Financial News"):
    st.info(f"Fetching {category.title()} news for {country.upper()}...")
    articles = fetch_news(category, country, keyword, source, num_articles, from_date, to_date)

    if not articles:
        st.warning("No articles found. Try different filters.")
    else:
        for idx, article in enumerate(articles, start=1):
            st.markdown(f"### {idx}. [{article.get('title', 'No Title')}]({article.get('url', '#')})")

            if article.get("urlToImage"):
                st.image(article["urlToImage"], use_container_width=True)
            else:
                st.image("https://via.placeholder.com/800x400?text=No+Image", use_container_width=True)

            with st.expander("Read More"):
                st.write(article.get("description", "No description available."))
                st.write(article.get("content", "No additional content."))

            st.caption(
                f"Source: {article.get('source', {}).get('name', 'Unknown')} | "
                f"Published: {article.get('publishedAt', 'N/A')}"
            )
            st.write("---")

# -------------------------------
# Optional: Show Top Stock & IPO News
# -------------------------------
st.sidebar.header("Stocks & IPOs")
show_stocks = st.sidebar.checkbox("Show Top Stock & IPO News")

if show_stocks:
    st.subheader("📈 Top Stock & IPO News")
    stock_keywords = ["stock", "IPO", "market", "finance"]

    for kw in stock_keywords:
        st.write(f"### 🔎 {kw.title()} News")
        articles = fetch_news("business", country, kw, None, 3, from_date, to_date)

        for article in articles:
            st.markdown(f"#### [{article.get('title', 'No Title')}]({article.get('url', '#')})")
            st.write(article.get("description", "No description available."))
            st.caption(
                f"Source: {article.get('source', {}).get('name', 'Unknown')} | "
                f"Published: {article.get('publishedAt', 'N/A')}"
            )
            st.write("---")
