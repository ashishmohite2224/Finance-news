import streamlit as st
import requests
import os
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
# Load API Key (Flexible Handling)
# -------------------------------
API_KEY = None

# 1️⃣ Try to get from Streamlit Secrets
if "NEWS_API_KEY" in st.secrets:
    API_KEY = st.secrets["NEWS_API_KEY"]

# 2️⃣ Try from Environment Variable
elif os.getenv("NEWS_API_KEY"):
    API_KEY = os.getenv("NEWS_API_KEY")

# 3️⃣ Ask user to input manually
else:
    API_KEY = st.text_input(
        "🔑 Enter your NewsAPI Key",
        type="password",
        help="Get a free API key from https://newsapi.org"
    )

if not API_KEY:
    st.warning("⚠️ Please provide a valid API key to continue.")
    st.stop()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filters")

country = st.sidebar.selectbox("🌍 Country", ["us", "gb", "in", "ca", "au"], index=0)

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
def fetch_news(category, country, keyword, source, num_articles, from_date, to_date, API_KEY):
    # Choose endpoint dynamically
    endpoint = "top-headlines" if not (keyword or from_date or to_date) else "everything"
    base_url = f"https://newsapi.org/v2/{endpoint}"

    params = {
        "apiKey": API_KEY,
        "pageSize": num_articles,
        "sortBy": "publishedAt"
    }

    # Add either country/category or source (not both)
    if source:
        params["sources"] = source
    elif endpoint == "top-headlines":
        params["country"] = country
        params["category"] = category

    if keyword:
        params["q"] = keyword

    if endpoint == "everything":
        params["from"] = from_date
        params["to"] = to_date

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news: {e}")
        return []

# -------------------------------
# Display News
# -------------------------------
if st.button("Get Financial News"):
    st.info(f"Fetching {category.title()} news for {country.upper()}...")

    articles = fetch_news(category, country, keyword, source, num_articles, from_date, to_date, API_KEY)

    if not articles:
        st.warning("No articles found. Try different filters.")
    else:
        for idx, article in enumerate(articles, start=1):
            st.markdown(f"### {idx}. [{article.get('title', 'No Title')}]({article.get('url', '#')})")

            img_url = article.get("urlToImage")
            if img_url:
                st.image(img_url, use_container_width=True)
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
        articles = fetch_news("business", country, kw, None, 3, from_date, to_date, API_KEY)

        for article in articles:
            st.markdown(f"#### [{article.get('title', 'No Title')}]({article.get('url', '#')})")
            st.write(article.get("description", "No description available."))
            st.caption(
                f"Source: {article.get('source', {}).get('name', 'Unknown')} | "
                f"Published: {article.get('publishedAt', 'N/A')}"
            )
            st.write("---")
