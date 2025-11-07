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
# ✅ Your NewsAPI Key
# -------------------------------
API_KEY = "a9b91dc9740c491ab00c7b79d40486e4"  # ✅ Your working NewsAPI key

if not API_KEY or API_KEY.strip() == "":
    st.error("⚠️ Missing valid API key. Please check the API_KEY value.")
    st.stop()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filters")

country = st.sidebar
