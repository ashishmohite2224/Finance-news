# app.py
"""
Streamlit Finance Dashboard (dark theme)
- Robust imports: uses plotly if available, else mplfinance, else matplotlib fallback.
- Portfolio tracker (session), technicals (SMA/EMA/RSI), sentiment (TextBlob).
Save as app.py and run: streamlit run app.py
If you want advanced candlesticks install: pip install plotly mplfinance
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from textblob import TextBlob

# Try optional plotting libs
_HAS_PLOTLY = False
_HAS_MPLFINANCE = False
try:
    import plotly.graph_objects as go
    _HAS_PLOTLY = True
except Exception:
    try:
        import mplfinance as mpf
        _HAS_MPLFINANCE = True
    except Exception:
        import matplotlib.pyplot as plt

# ---------------------------
# Page config & CSS (dark)
# ---------------------------
st.set_page_config(page_title="Finance Dashboard — Dark", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    :root {
        --bg: #0b0f12;
        --card: #0f1720;
        --muted: #9aa6b2;
        --accent: #00b894;
        --accent-2: #3b82f6;
        --white: #e6eef6;
    }
    html, body, [class*="css"]  {
        background-color: var(--bg) !important;
        color: var(--white) !important;
    }
    .stApp {
        background-color: var(--bg) !important;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    .card {
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border: 1px solid rgba(255,255,255,0.03);
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 6px 18px rgba(2,6,23,0.6);
    }
    .section-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .small-muted {
        color: var(--muted);
        font-size: 13px;
    }
    .stButton>button {
        background-color: var(--accent) !important;
        color: black !important;
        font-weight: 600;
    }
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div>input {
        background-color: transparent !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        color: var(--white) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Utilities: TA functions
# ---------------------------
def fetch_data(ticker, period="6mo", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, threads=False)
        if data is None or data.empty:
            return None
        data = data.dropna()
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

def sma(series, period):
    return series.rolling(period).mean()

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=period, min_periods=period).mean()
    ma_down = down.rolling(window=period, min_periods=period).mean()
    rs = ma_up / ma_down
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ---------------------------
# Sidebar controls
# ---------------------------
st.sidebar.title("Controls")
st.sidebar.markdown("**Search stock** (Yahoo ticker like AAPL, MSFT, TCS.NS, INFY.NS)")

ticker = st.sidebar.text_input("Ticker", value="AAPL")
range_days = st.sidebar.selectbox("Chart range", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)
interval = st.sidebar.selectbox("Interval", options=["1d", "1wk", "1h"], index=0)
show_ma = st.sidebar.checkbox("Show Moving Averages (SMA/EMA)", value=True)
show_rsi = st.sidebar.checkbox("Show RSI", value=True)

# Portfolio controls in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Portfolio (local)")
with st.sidebar.form("add_trade"):
    p_ticker = st.text_input("Ticker to add", value="")
    p_shares = st.number_input("Shares", min_value=0.0, format="%.4f", value=0.0)
    p_price = st.number_input("Buy price (per share)", min_value=0.0, format="%.4f", value=0.0)
    submitted = st.form_submit_button("Add Position")
    if submitted:
        if p_ticker.strip() == "" or p_shares <= 0:
            st.sidebar.error("Enter ticker and shares > 0")
        else:
            if "portfolio" not in st.session_state:
                st.session_state.portfolio = []
            st.session_state.portfolio.append({
                "ticker": p_ticker.upper(),
                "shares": float(p_shares),
                "buy_price": float(p_price),
                "added_at": datetime.utcnow().isoformat()
            })
            st.sidebar.success(f"Added {p_shares} of {p_ticker.upper()}")

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

# ---------------------------
# Main layout
# ---------------------------
st.title("Finance Dashboard")
st.markdown("<div class='small-muted'>Dark professional dashboard • no news • portfolio, charts, indicators, sentiment</div>", unsafe_allow_html=True)
st.write("")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Price & Technicals</div>", unsafe_allow_html=True)

    data = fetch_data(ticker, period=range_days, interval=interval)
    if data is None:
        st.error("No data found for ticker. Please check the ticker symbol.")
    else:
        last_close = data["Close"].iloc[-1]
        prev_close = data["Close"].iloc[-2] if len(data) > 1 else last_close
        change = last_close - prev_close
        change_pct = (change / prev_close) * 100 if prev_close else 0.0

        st.markdown(f"**{ticker.upper()}** • Last close: **{last_close:.2f}**  •  Change: **{change:.2f} ({change_pct:.2f}%)**")
        st.markdown("<hr/>", unsafe_allow_html=True)

        # Indicators
        if show_ma:
            data["SMA20"] = sma(data["Close"], 20)
            data["SMA50"] = sma(data["Close"], 50)
            data["EMA20"] = ema(data["Close"], 20)
        if show_rsi:
            data["RSI14"] = rsi(data["Close"], 14)

        # Plot: prefer plotly candlestick if available
        if _HAS_PLOTLY:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name="Price",
                increasing_line_color="#00b894",
                decreasing_line_color="#ff7675",
                showlegend=False,
            ))
            if show_ma:
                if "SMA20" in data.columns:
                    fig.add_trace(go.Scatter(x=data.index, y=data["SMA20"], mode="lines", name="SMA20", line=dict(width=1.2, dash="dash")))
                if "SMA50" in data.columns:
                    fig.add_trace(go.Scatter(x=data.index, y=data["SMA50"], mode="lines", name="SMA50", line=dict(width=1.2)))
                if "EMA20" in data.columns:
                    fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], mode="lines", name="EMA20", line=dict(width=1.2, dash="dot")))
            fig.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=20, b=0), xaxis_rangeslider_visible=False, height=420)
            st.plotly_chart(fig, use_container_width=True)

        elif _HAS_MPLFINANCE:
            # mplfinance candlestick
            mpf_style = mpf.make_mpf_style(base_mpf_style='nightclouds', rc={'font.size':10})
            mpf.plot(data, type='candle', mav=(20,50), volume=False, style=mpf_style, figsize=(9,4), tight_layout=True, show_nontrading=False, block=False)
            # mplfinance displays directly in notebook; streamlit will show the matplotlib figure
            import matplotlib.pyplot as plt
            fig = plt.gcf()
            st.pyplot(fig)

        else:
            # Matplotlib fallback: line chart for Close + MAs
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 4), tight_layout=True)
            ax.plot(data.index, data["Close"], label="Close", linewidth=1.1)
            if show_ma:
                if "SMA20" in data.columns:
                    ax.plot(data.index, data["SMA20"], label="SMA20", linewidth=0.9, linestyle="--")
                if "SMA50" in data.columns:
                    ax.plot(data.index, data["SMA50"], label="SMA50", linewidth=0.9)
                if "EMA20" in data.columns:
                    ax.plot(data.index, data["EMA20"], label="EMA20", linewidth=0.9, linestyle=":")
            ax.set_title("Price (Close)")
            ax.grid(alpha=0.15)
            ax.legend(loc="upper left", fontsize="small")
            # dark theme adjustments for matplotlib
            ax.set_facecolor("#0f1720")
            fig.patch.set_facecolor("#0b0f12")
            for spine in ax.spines.values():
                spine.set_color("#2b3440")
            ax.tick_params(colors="#e6eef6")
            st.pyplot(fig)

        # RSI plot (matplotlib or plotly)
        if show_rsi and "RSI14" in data.columns:
            if _HAS_PLOTLY:
                rsi_fig = go.Figure()
                rsi_fig.add_trace(go.Scatter(x=data.index, y=data["RSI14"], name="RSI14"))
                rsi_fig.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=10, b=0), height=200, yaxis=dict(range=[0, 100]))
                rsi_fig.add_hline(y=70, line=dict(color="red", dash="dash"))
                rsi_fig.add_hline(y=30, line=dict(color="green", dash="dash"))
                st.plotly_chart(rsi_fig, use_container_width=True)
            else:
                import matplotlib.pyplot as plt
                fig2, ax2 = plt.subplots(figsize=(10, 2.5), tight_layout=True)
                ax2.plot(data.index, data["RSI14"], linewidth=1.0)
                ax2.axhline(70, color='r', linestyle='--', linewidth=0.8)
                ax2.axhline(30, color='g', linestyle='--', linewidth=0.8)
                ax2.set_ylim(0, 100)
                ax2.set_title("RSI (14)")
                ax2.set_facecolor("#0f1720")
                fig2.patch.set_facecolor("#0b0f12")
                ax2.tick_params(colors="#e6eef6")
                for spine in ax2.spines.values():
                    spine.set_color("#2b3440")
                st.pyplot(fig2)

    st.markdown("</div>", unsafe_allow_html=True)

    # Sentiment Analyzer
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Sentiment Analyzer</div>", unsafe_allow_html=True)
    txt = st.text_area("Paste text or type your trade thesis / news excerpt", height=120)
    if st.button("Analyze Sentiment"):
        if not txt.strip():
            st.warning("Enter some text to analyze.")
        else:
            blob = TextBlob(txt)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            st.metric("Polarity (-1 to 1)", f"{polarity:.3f}")
            st.metric("Subjectivity (0-1)", f"{subjectivity:.3f}")
            if polarity > 0.1:
                st.success("Overall Positive tone")
            elif polarity < -0.1:
                st.error("Overall Negative tone")
            else:
                st.info("Neutral / mixed tone")
            st.markdown("---")
            st.write("**Quick tips:** Polarity >0 = positive, <0 = negative. Subjectivity near 1 => opinionated; near 0 => factual.")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Portfolio Overview</div>", unsafe_allow_html=True)

    if len(st.session_state.portfolio) == 0:
        st.info("Your portfolio is empty. Use the sidebar form to add positions.")
    else:
        port_df = pd.DataFrame(st.session_state.portfolio)
        unique_tickers = port_df['ticker'].unique().tolist()
        prices = {}
        for t in unique_tickers:
            try:
                q = yf.Ticker(t)
                hist = q.history(period="1d")
                if not hist.empty:
                    prices[t] = hist['Close'].iloc[-1]
                else:
                    info = q.info
                    prices[t] = info.get("previousClose", np.nan)
            except Exception:
                prices[t] = np.nan

        port_df["current_price"] = port_df["ticker"].apply(lambda x: prices.get(x, np.nan))
        port_df["market_value"] = port_df["current_price"] * port_df["shares"]
        port_df["cost_basis"] = port_df["buy_price"] * port_df["shares"]
        port_df["pl_abs"] = port_df["market_value"] - port_df["cost_basis"]
        port_df["pl_pct"] = np.where(port_df["cost_basis"] != 0, (port_df["pl_abs"] / port_df["cost_basis"]) * 100, 0.0)

        total_mv = port_df["market_value"].sum()
        total_cost = port_df["cost_basis"].sum()
        total_pl = total_mv - total_cost
        total_pl_pct = (total_pl / total_cost) * 100 if total_cost != 0 else 0.0

        st.metric("Total Market Value", f"${total_mv:,.2f}")
        st.metric("Total P/L", f"${total_pl:,.2f} ({total_pl_pct:.2f}%)")

        st.dataframe(port_df[["ticker", "shares", "buy_price", "current_price", "market_value", "pl_abs", "pl_pct"]].sort_values(by="market_value", ascending=False).reset_index(drop=True))

        st.markdown("---")
        st.write("Manage positions")
        idx_to_remove = st.selectbox("Select position to remove", options=[""] + [f"{i} | {row['ticker']} | {row['shares']} sh" for i, row in port_df.reset_index().iterrows()])
        if st.button("Remove selected"):
            if idx_to_remove:
                idx = int(idx_to_remove.split("|")[0].strip())
                try:
                    del st.session_state.portfolio[idx]
                    st.success("Removed position.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error("Could not remove: " + str(e))

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Quick Lookup</div>", unsafe_allow_html=True)
    if data is not None:
        st.write(f"Last 5 rows for **{ticker.upper()}**")
        st.dataframe(data.tail(5)[["Open", "High", "Low", "Close", "Volume"]])
    else:
        st.write("No data to show.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
st.markdown(
    """
    <div class='card'>
    <div style='display:flex; justify-content:space-between; align-items:center;'>
      <div>
        <strong>Finance Dashboard</strong> &nbsp; • &nbsp; Dark professional theme<br/>
        <span class='small-muted'>Built with Streamlit • Data: yfinance</span>
      </div>
      <div style='text-align:right;'>
        <span class='small-muted'>Tip:</span> Use tickers like <code>AAPL</code>, <code>MSFT</code>, or Indian tickers like <code>TCS.NS</code> / <code>INFY.NS</code>.
      </div>
    </div>
    </div>
    """,
    unsafe_allow_html=True,
)
