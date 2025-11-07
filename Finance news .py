import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from textblob import TextBlob
from datetime import datetime

# ==============================
# 🌍 Page Setup
# ==============================
st.set_page_config(
    page_title="📊 Indian Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# ==============================
# 🎨 Custom Dark Blue Professional Theme
# ==============================
st.markdown("""
<style>
    body {
        background-color: #0a0f24;
        color: #f5f5f5;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #0b132b, #1c2541);
        color: white;
    }
    [data-testid="stSidebar"] {
        background-color: #0b132b;
        border-right: 1px solid #1c2541;
    }
    h1, h2, h3 {
        color: #00bfff;
        font-weight: 700;
    }
    .stMetric label, .stDataFrame {
        color: #f5f5f5 !important;
    }
    .stButton>button {
        background-color: #00bfff;
        color: black;
        border-radius: 8px;
        font-weight: bold;
    }
    .card {
        background-color: #1c2541;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 0 10px rgba(0,191,255,0.2);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔑 API Key for News
# ==============================
API_KEY = "a9b91dc9740c491ab00c7b79d40486e4"

# ==============================
# 🔧 Helper Functions
# ==============================
@st.cache_data(t_
