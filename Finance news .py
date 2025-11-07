import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from textblob import TextBlob

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="📊 Indian Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================
# CUSTOM PROFESSIONAL THEME (Blue-Green + Dark Sidebar)
# ==============================
st.markdown("""
    <style>
