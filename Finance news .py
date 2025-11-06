import streamlit as st
import requests
from datetime import datetime
from textblob import TextBlob  # For simple sentiment analysis

# -------------------------------
# Streamlit App Configuration
# -------------------------------
st.set_page_config(
    page_title="Financial News App",
    page_icon="💹",
    layout="wide"
)

st.title("💹 Financial News & IPO Tracker")
st.write("Get the latest financial news, stock updates, IPO information, and more!")

# -------------------------------
# Load API Key from Streamlit Secrets
# -------------------------------
# Add to Streamlit Secrets: NEWS_API_KEY="your_real_newsapi_key"
API_KEY = st.secrets.get("NEWS_API_KEY")

if not API_KEY:
    st.error("⚠️ Missing API key! Add your NEWS_API_KEY in Streamlit Secrets.")
    st.stop()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filters")

country = st.sidebar.selectbox(
    "🌍 Country",
    ["us", "gb", "in", "ca", "au"],
    index=0
)

category = st.sidebar.selectbox(
    "🗂️ Category",
    ["business", "general", "technology", "entertainment", "health", "science", "sports"],
    index=0
)

keyword = st.sidebar.text_input("🔍 Search Keyword (e.g., stock, IPO, crypto)")

source = st.sidebar.text_input("News Source (optional, e.g., cnn, bloomberg)")

num_articles = st.sidebar.slider("📰 Number of Articles", 1, 20, 5)

from_date = st.sidebar.date_input("From Date", datetime.today())
to_date = st.sidebar.date_input("To Date", datetime.today())

sentiment_analysis = st.sidebar.checkbox("🔎 Show Sentiment Analysis", value=True)

# -------------------------------
# Function to fetch news
# -------------------------------
def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&pageSize={num_articles}&apiKey={API_KEY}"

    if keyword:
        url += f"&q={keyword}"
    if source:
        url += f"&sources={source}"
    if from_date:
        url += f"&from={from_date}"
    if to_date:
        url += f"&to={to_date}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news: {e}")
        return []

# -------------------------------
# Button to fetch news
# -------------------------------
if st.button("Get Financial News"):
    st.info(f"Fetching {category.title()} news for {country.upper()}...")

    articles = fetch_news()

    if not articles:
        st.warning("No articles found. Try different filters.")
    else:
        for idx, article in enumerate(articles, start=1):
            st.markdown(f"### {idx}. [{article['title']}]({article['url']})")

            if article.get("urlToImage"):
                st.image(article["urlToImage"], use_container_width=True)

            with st.expander("Read More"):
                st.write(article.get("description", "No description available"))
                st.write(article.get("content", "No additional content"))

            if sentiment_analysis:
                text = article.get("title", "")
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                if polarity > 0:
                    sentiment = "Positive 🙂"
                elif polarity < 0:
                    sentiment = "Negative 🙁"
                else:
                    sentiment = "Neutral 😐"
                st.caption(f"Sentiment: {sentiment}")

            st.caption(f"Source: {article.get('source', {}).get('name', 'Unknown')} | Published: {article.get('publishedAt', 'N/A')}")
            st.write("---")
