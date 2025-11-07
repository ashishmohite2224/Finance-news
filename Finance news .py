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
# Load API Key
# -------------------------------
API_KEY = st.secrets.get("NEWS_API_KEY", None)

if not API_KEY:
    st.error("⚠️ Missing API key! Please add your NEWS_API_KEY in Streamlit Secrets.")
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

source = st.sidebar.text_input("News Source (optional, e.g., bloomberg, cnbc)")

num_articles = st.sidebar.slider("📰 Number of Articles", 1, 20, 5)

to_date = st.sidebar.date_input("To Date", datetime.today())
from_date = st.sidebar.date_input("From Date", datetime.today() - timedelta(days=7))

# -------------------------------
# Function to Fetch News
# -------------------------------
@st.cache_data(ttl=600)
def fetch_news(category, country, keyword, source, num_articles, from_date, to_date):
    # Choose endpoint
    endpoint = "top-headlines" if not (keyword or from_date or to_date) else "everything"
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
        params["categ]()
