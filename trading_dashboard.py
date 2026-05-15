"""
╔══════════════════════════════════════════════════════════════╗
║   Advanced Confluence Trading Dashboard                      ║
║   Signals for Nifty, BankNifty, Gold, Crude Oil             ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Confluence Trader Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS — Dark terminal-trading aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700;900&display=swap');

  /* ── Root variables ── */
  :root {
    --bg-deep:    #080c14;
    --bg-panel:   #0d1421;
    --bg-card:    #111927;
    --border:     #1e3a5f;
    --accent:     #00d4ff;
    --green:      #00ff88;
    --red:        #ff3366;
    --yellow:     #ffd700;
    --text-main:  #c8daf0;
    --text-dim:   #5a7a9a;
    --font-mono:  'Share Tech Mono', monospace;
    --font-main:  'Exo 2', sans-serif;
  }

  /* ── Global ── */
  html, body, [class*="css"] {
    font-family: var(--font-main);
    background-color: var(--bg-deep) !important;
    color: var(--text-main) !important;
  }
  .stApp { background-color: var(--bg-deep) !important; }
  .block-container { padding: 1.5rem 2rem !important; max-width: 1600px; }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-right: 1px solid var(--border);
  }
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stRadio label,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span {
    color: var(--text-main) !important;
    font-family: var(--font-main) !important;
  }
  section[data-testid="stSidebar"] div[data-baseweb="select"] div {
    background-color: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text-main) !important;
  }
  .stRadio div { gap: 0.4rem; }
  .stRadio label span { color: var(--text-main) !important; }

  /* ── Headers ── */
  h1, h2, h3 { font-family: var(--font-main) !important; }
  .dashboard-title {
    font-family: var(--font-main);
    font-weight: 900;
    font-size: 2rem;
    letter-spacing: 0.05em;
    background: linear-gradient(90deg, var(--accent), #7b5cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
  }
  .subtitle {
    font-family: var(--font-mono);
    color: var(--text-dim);
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    margin-top: 0.2rem;
    text-transform: uppercase;
  }

  /* ── Signal Box ── */
  .signal-box {
    border-radius: 12px;
    padding: 1.6rem 2rem;
    text-align: center;
    border: 1px solid;
    position: relative;
    overflow: hidden;
  }
  .signal-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    opacity: 0.06;
    background: radial-gradient(circle at 50% -20%, white, transparent 70%);
  }
  .signal-box.buy  { background: rgba(0,255,136,0.08); border-color: var(--green); }
  .signal-box.sell { background: rgba(255,51,102,0.08); border-color: var(--red); }
  .signal-box.wait { background: rgba(255,215,0,0.06);  border-color: var(--yellow); }

  .signal-label {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    opacity: 0.7;
    margin-bottom: 0.3rem;
  }
  .signal-value {
    font-family: var(--font-main);
    font-weight: 900;
    font-size: 2.4rem;
    letter-spacing: 0.04em;
    line-height: 1;
  }
  .signal-value.buy  { color: var(--green); text-shadow: 0 0 20px rgba(0,255,136,0.4); }
  .signal-value.sell { color: var(--red);   text-shadow: 0 0 20px rgba(255,51,102,0.4); }
  .signal-value.wait { color: var(--yellow);text-shadow: 0 0 20px rgba(255,215,0,0.4); }
  .signal-sub {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    opacity: 0.55;
    margin-top: 0.5rem;
  }

  /* ── Metric Cards ── */
  .metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.5rem;
  }
  .metric-card .m-label {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    letter-spacing: 0.15em;
    color: var(--text-dim);
    text-transform: uppercase;
  }
  .metric-card .m-value {
    font-family: var(--font-main);
    font-weight: 700;
    font-size: 1.25rem;
    margin-top: 0.15rem;
  }

  /* ── Condition Badges ── */
  .cond-row { display: flex; flex-direction: column; gap: 0.4rem; margin-top: 0.5rem; }
  .cond-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.4rem 0.7rem;
    font-family: var(--font-mono);
    font-size: 0.72rem;
  }
  .cond-badge .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .cond-badge .dot.ok  { background: var(--green); box-shadow: 0 0 6px var(--green); }
  .cond-badge .dot.bad { background: var(--red);   box-shadow: 0 0 6px var(--red); }
  .cond-badge .dot.na  { background: var(--text-dim); }

  /* ── Table ── */
  .stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px; }
  .stDataFrame thead th {
    background: var(--bg-panel) !important;
    color: var(--accent) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }
  .stDataFrame tbody tr { background: var(--bg-card) !important; }
  .stDataFrame tbody td { font-family: var(--font-mono) !important; font-size: 0.8rem !important; }

  /* ── Divider ── */
  hr { border-color: var(--border) !important; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: var(--bg-deep); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  /* ── Refresh Button ── */
  div.stButton > button {
    background: linear-gradient(135deg, #0a2a4a, #0d3b6e);
    color: var(--accent);
    border: 1px solid var(--accent);
    border-radius: 8px;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    letter-spacing: 0.1em;
    padding: 0.5rem 1.2rem;
    width: 100%;
    transition: all 0.2s;
  }
  div.stButton > button:hover {
    background: linear-gradient(135deg, #0d3b6e, #0a2a4a);
    box-shadow: 0 0 12px rgba(0,212,255,0.3);
  }

  /* ── Section header ── */
  .section-hdr {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4rem;
    margin-bottom: 0.8rem;
    margin-top: 1rem;
  }

  /* ── Live badge ── */
  .live-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(0,255,136,0.1);
    border: 1px solid var(--green);
    border-radius: 4px;
    padding: 2px 8px;
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--green);
    letter-spacing: 0.1em;
  }
  .live-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--green);
    animation: blink 1.2s infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

  /* override streamlit metric */
  [data-testid="stMetric"] { background: transparent !important; }
  [data-testid="stMetricLabel"] { color: var(--text-dim) !important; font-family: var(--font-mono) !important; font-size: 0.7rem !important; }
  [data-testid="stMetricValue"] { color: var(--text-main) !important; font-family: var(--font-main) !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════

ASSETS = {
    "🇮🇳  NIFTY 50":     "^NSEI",
    "🏦  BANK NIFTY":    "^NSEBANK",
    "🥇  GOLD":          "GC=F",
    "🛢️  CRUDE OIL":    "CL=F",
    "💹  SENSEX":        "^BSESN",
    "💎  SILVER":        "SI=F",
}

TIMEFRAMES = {
    "5m":    ("5m",  "2d"),
    "15m":   ("15m", "5d"),
    "1h":    ("1h",  "60d"),
    "Daily": ("1d",  "365d"),
}

COLORS = {
    "bg":       "#080c14",
    "panel":    "#0d1421",
    "card":     "#111927",
    "border":   "#1e3a5f",
    "accent":   "#00d4ff",
    "green":    "#00ff88",
    "red":      "#ff3366",
    "yellow":   "#ffd700",
    "ema":      "#7b5cff",
    "bb_upper": "#ff6b35",
    "bb_lower": "#00d4ff",
    "bb_mid":   "#888888",
    "vol_avg":  "#7b5cff",
}


# ═══════════════════════════════════════════════════════════
#  MODULE 1 — DATA FETCHING
# ═══════════════════════════════════════════════════════════

@st.cache_data(ttl=60, show_spinner=False)
def fetch_data(ticker: str, interval: str, period: str) -> pd.DataFrame | None:
    """Download OHLCV data via yfinance. Returns None on failure."""
    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
        )
        if df is None or df.empty:
            return None
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna(subset=["Close", "Volume"])
        df.index = pd.to_datetime(df.index)
        df = df.rename(columns=str.capitalize)
        # Ensure required columns
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col not in df.columns:
                return None
        return df
    except Exception as e:
        st.error(f"Data fetch error: {e}")
        return None


# ═══════════════════════════════════════════════════════════
#  MODULE 2 — INDICATOR ENGINE
# ═══════════════════════════════════════════════════════════

def compute_ema(df: pd.DataFrame, period: int = 50) -> pd.Series:
    return ta.ema(df["Close"], length=period)


def compute_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    return ta.rsi(df["Close"], length=period)


def compute_bollinger_bands(df: pd.DataFrame, period: int = 20, std: float = 2.0):
    bb = ta.bbands(df["Close"], length=period, std=std)
    if bb is None:
        return None, None, None
    upper = bb[f"BBU_{period}_{std}"]
    mid   = bb[f"BBM_{period}_{std}"]
    lower = bb[f"BBL_{period}_{std}"]
    return upper, mid, lower


def compute_volume_avg(df: pd.DataFrame, period: int = 20) -> pd.Series:
    return df["Volume"].rolling(window=period).mean()


def compute_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0):
    """
    SuperTrend implementation using pandas_ta.
    Returns (supertrend_series, direction_series).
    Direction: 1 = Bullish, -1 = Bearish.
    """
    try:
        st_df = ta.supertrend(
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            length=period,
            multiplier=multiplier,
        )
        if st_df is None or st_df.empty:
            return None, None

        # Column name lookup (pandas_ta naming varies)
        col_st  = [c for c in st_df.columns if c.startswith("SUPERT_") and "d" not in c.lower() and "s" not in c.lower()]
        col_dir = [c for c in st_df.columns if "SUPERTd" in c]

        if not col_st or not col_dir:
            # fallback: take first two numeric columns
            num_cols = [c for c in st_df.columns]
            if len(num_cols) >= 4:
                col_st  = [num_cols[0]]
                col_dir = [num_cols[1]]
            else:
                return None, None

        st_vals  = st_df[col_st[0]]
        dir_vals = st_df[col_dir[0]]
        return st_vals, dir_vals
    except Exception:
        return None, None


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    return ta.atr(df["High"], df["Low"], df["Close"], length=period)


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute and attach all indicators to DataFrame."""
    df = df.copy()

    df["EMA50"]      = compute_ema(df, 50)
    df["RSI14"]      = compute_rsi(df, 14)
    df["VolAvg20"]   = compute_volume_avg(df, 20)
    df["ATR14"]      = compute_atr(df, 14)

    bb_u, bb_m, bb_l = compute_bollinger_bands(df)
    df["BB_Upper"]   = bb_u
    df["BB_Mid"]     = bb_m
    df["BB_Lower"]   = bb_l

    st_vals, st_dir  = compute_supertrend(df, period=10, multiplier=3.0)
    df["SuperTrend"] = st_vals
    df["ST_Dir"]     = st_dir

    return df


# ═══════════════════════════════════════════════════════════
#  MODULE 3 — CONFLUENCE SIGNAL ENGINE
# ═══════════════════════════════════════════════════════════

def evaluate_conditions(row: pd.Series) -> dict:
    """
    Evaluate each of the 5 confluence conditions for a single candle row.
    Returns dict with keys: trend, momentum, volatility, volume, supertrend
    Each value: +1 (bullish), -1 (bearish), 0 (neutral/NaN)
    """
    results = {}

    # 1. Trend: Price vs EMA50
    if pd.notna(row.get("EMA50")) and pd.notna(row.get("Close")):
        results["trend"] = 1 if row["Close"] > row["EMA50"] else -1
    else:
        results["trend"] = 0

    # 2. Momentum: RSI14
    if pd.notna(row.get("RSI14")):
        if row["RSI14"] > 55:
            results["momentum"] = 1
        elif row["RSI14"] < 45:
            results["momentum"] = -1
        else:
            results["momentum"] = 0
    else:
        results["momentum"] = 0

    # 3. Volatility: Close vs BB_Mid
    if pd.notna(row.get("BB_Mid")) and pd.notna(row.get("Close")):
        results["volatility"] = 1 if row["Close"] >= row["BB_Mid"] else -1
    else:
        results["volatility"] = 0

    # 4. Volume: Current > 20-period average
    if pd.notna(row.get("Volume")) and pd.notna(row.get("VolAvg20")) and row["VolAvg20"] > 0:
        results["volume"] = 1 if row["Volume"] > row["VolAvg20"] else 0
    else:
        results["volume"] = 0

    # 5. SuperTrend direction
    if pd.notna(row.get("ST_Dir")):
        val = int(row["ST_Dir"])
        results["supertrend"] = 1 if val == 1 else (-1 if val == -1 else 0)
    else:
        results["supertrend"] = 0

    return results


def get_confluence_signal(conditions: dict) -> tuple[str, int, int]:
    """
    Derive final signal from 5 conditions.
    Returns (signal_label, bull_count, bear_count)
    """
    bull = sum(1 for v in conditions.values() if v == 1)
    bear = sum(1 for v in conditions.values() if v == -1)

    if bull >= 3 and bull > bear:
        return "STRONG BUY", bull, bear
    elif bear >= 3 and bear > bull:
        return "STRONG SELL", bull, bear
    else:
        return "WAIT", bull, bear


def generate_signals_history(df: pd.DataFrame) -> pd.DataFrame:
    """
    Walk the DataFrame and record every row's signal.
    Returns DataFrame with signal columns added.
    """
    signals = []
    for i, (idx, row) in enumerate(df.iterrows()):
        conds  = evaluate_conditions(row)
        signal, bull, bear = get_confluence_signal(conds)
        signals.append({
            "datetime":  idx,
            "signal":    signal,
            "bull_cnt":  bull,
            "bear_cnt":  bear,
            "close":     row["Close"],
            "atr":       row.get("ATR14", np.nan),
        })
    sig_df = pd.DataFrame(signals).set_index("datetime")
    return df.join(sig_df[["signal", "bull_cnt", "bear_cnt"]])


# ═══════════════════════════════════════════════════════════
#  MODULE 4 — SIGNAL TABLE BUILDER
# ═══════════════════════════════════════════════════════════

def build_signal_table(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Extract last N actionable signals (BUY or SELL) with SL and Target.
    SL  = ATR-based (entry ± 1.5 × ATR)
    TGT = 1:2 risk-reward
    """
    active = df[df["signal"].isin(["STRONG BUY", "STRONG SELL"])].tail(n).copy()
    rows   = []
    for ts, row in active.iterrows():
        entry  = round(float(row["Close"]), 2)
        atr    = row.get("ATR14", np.nan)
        sl_gap = round(float(atr) * 1.5, 2) if pd.notna(atr) else None
        if row["signal"] == "STRONG BUY":
            sl  = round(entry - sl_gap, 2) if sl_gap else "—"
            tgt = round(entry + sl_gap * 2, 2) if sl_gap else "—"
            rr  = "1:2"
        else:
            sl  = round(entry + sl_gap, 2) if sl_gap else "—"
            tgt = round(entry - sl_gap * 2, 2) if sl_gap else "—"
            rr  = "1:2"

        rows.append({
            "Time":     ts.strftime("%d %b %H:%M") if hasattr(ts, 'strftime') else str(ts),
            "Signal":   row["signal"],
            "Entry":    entry,
            "Stop Loss":sl,
            "Target":   tgt,
            "R:R":      rr,
            "Strength": f"▲{int(row['bull_cnt'])} ▼{int(row['bear_cnt'])}",
        })
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════
#  MODULE 5 — CHART BUILDER
# ═══════════════════════════════════════════════════════════

def build_chart(df: pd.DataFrame, asset_name: str) -> go.Figure:
    """Build a multi-panel Plotly chart: Candlestick + Volume + RSI."""
    tail = df.tail(120)  # show last 120 candles for performance

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.60, 0.20, 0.20],
        vertical_spacing=0.02,
        subplot_titles=("", "", ""),
    )

    # ── Candlestick ──────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=tail.index,
        open=tail["Open"], high=tail["High"],
        low=tail["Low"],   close=tail["Close"],
        name="Price",
        increasing_fillcolor=COLORS["green"],
        decreasing_fillcolor=COLORS["red"],
        increasing_line_color=COLORS["green"],
        decreasing_line_color=COLORS["red"],
        line_width=1,
    ), row=1, col=1)

    # ── EMA 50 ───────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=tail.index, y=tail["EMA50"],
        name="EMA 50", mode="lines",
        line=dict(color=COLORS["ema"], width=1.5, dash="dot"),
    ), row=1, col=1)

    # ── Bollinger Bands ───────────────────────────────
    fig.add_trace(go.Scatter(
        x=tail.index, y=tail["BB_Upper"],
        name="BB Upper", mode="lines",
        line=dict(color=COLORS["bb_upper"], width=1, dash="dash"),
        opacity=0.7,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=tail.index, y=tail["BB_Mid"],
        name="BB Mid", mode="lines",
        line=dict(color=COLORS["bb_mid"], width=1),
        opacity=0.5,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=tail.index, y=tail["BB_Lower"],
        name="BB Lower", mode="lines",
        line=dict(color=COLORS["bb_lower"], width=1, dash="dash"),
        opacity=0.7,
        fill="tonexty",
        fillcolor="rgba(0,212,255,0.03)",
    ), row=1, col=1)

    # ── SuperTrend ─────────────────────────────────────
    if "SuperTrend" in tail.columns and tail["SuperTrend"].notna().any():
        bull_st = tail[tail["ST_Dir"] == 1]
        bear_st = tail[tail["ST_Dir"] == -1]
        if not bull_st.empty:
            fig.add_trace(go.Scatter(
                x=bull_st.index, y=bull_st["SuperTrend"],
                name="ST Bull", mode="lines",
                line=dict(color=COLORS["green"], width=2),
                opacity=0.6,
            ), row=1, col=1)
        if not bear_st.empty:
            fig.add_trace(go.Scatter(
                x=bear_st.index, y=bear_st["SuperTrend"],
                name="ST Bear", mode="lines",
                line=dict(color=COLORS["red"], width=2),
                opacity=0.6,
            ), row=1, col=1)

    # ── Buy / Sell Markers ─────────────────────────────
    if "signal" in tail.columns:
        buys  = tail[tail["signal"] == "STRONG BUY"]
        sells = tail[tail["signal"] == "STRONG SELL"]

        if not buys.empty:
            fig.add_trace(go.Scatter(
                x=buys.index, y=buys["Low"] * 0.998,
                mode="markers+text",
                marker=dict(symbol="triangle-up", size=14, color=COLORS["green"],
                            line=dict(color="white", width=0.5)),
                text=["B"] * len(buys), textposition="bottom center",
                textfont=dict(color=COLORS["green"], size=8),
                name="Buy Signal",
            ), row=1, col=1)

        if not sells.empty:
            fig.add_trace(go.Scatter(
                x=sells.index, y=sells["High"] * 1.002,
                mode="markers+text",
                marker=dict(symbol="triangle-down", size=14, color=COLORS["red"],
                            line=dict(color="white", width=0.5)),
                text=["S"] * len(sells), textposition="top center",
                textfont=dict(color=COLORS["red"], size=8),
                name="Sell Signal",
            ), row=1, col=1)

    # ── Volume Bars ────────────────────────────────────
    colors_vol = [
        COLORS["green"] if c >= o else COLORS["red"]
        for c, o in zip(tail["Close"], tail["Open"])
    ]
    fig.add_trace(go.Bar(
        x=tail.index, y=tail["Volume"],
        name="Volume",
        marker_color=colors_vol,
        opacity=0.7,
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=tail.index, y=tail["VolAvg20"],
        name="Vol MA20", mode="lines",
        line=dict(color=COLORS["vol_avg"], width=1.5, dash="dot"),
    ), row=2, col=1)

    # ── RSI ────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=tail.index, y=tail["RSI14"],
        name="RSI 14", mode="lines",
        line=dict(color=COLORS["accent"], width=1.5),
    ), row=3, col=1)
    for level, color in [(70, COLORS["red"]), (50, COLORS["bb_mid"]), (30, COLORS["green"])]:
        fig.add_hline(y=level, line_dash="dot", line_color=color,
                      line_width=1, opacity=0.5, row=3, col=1)

    # ── Layout ─────────────────────────────────────────
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["panel"],
        font=dict(family="Share Tech Mono", size=11, color="#c8daf0"),
        xaxis_rangeslider_visible=False,
        margin=dict(l=60, r=20, t=30, b=20),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01,
            xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)", font=dict(size=10),
        ),
        height=680,
        hovermode="x unified",
    )
    for ax in ["xaxis", "xaxis2", "xaxis3"]:
        fig.update_layout({ax: {"gridcolor": COLORS["border"], "showgrid": True}})
    for ax in ["yaxis", "yaxis2", "yaxis3"]:
        fig.update_layout({ax: {"gridcolor": COLORS["border"], "showgrid": True}})

    return fig


# ═══════════════════════════════════════════════════════════
#  MODULE 6 — UI HELPERS
# ═══════════════════════════════════════════════════════════

def signal_html(signal: str, bull: int, bear: int, price: float, ts) -> str:
    cls = {"STRONG BUY": "buy", "STRONG SELL": "sell", "WAIT": "wait"}.get(signal, "wait")
    icon = {"STRONG BUY": "▲", "STRONG SELL": "▼", "WAIT": "◆"}.get(signal, "◆")
    return f"""
    <div class="signal-box {cls}">
      <div class="signal-label">Confluence Signal</div>
      <div class="signal-value {cls}">{icon} {signal}</div>
      <div class="signal-sub">
        ▲ {bull} Bullish &nbsp;|&nbsp; ▼ {bear} Bearish &nbsp;|&nbsp;
        Price: {price:,.2f} &nbsp;|&nbsp;
        {ts.strftime('%H:%M  %d %b') if hasattr(ts,'strftime') else ts}
      </div>
    </div>
    """


def condition_badges_html(conditions: dict, signal: str) -> str:
    label_map = {
        "trend":      "Trend  (Price vs EMA50)",
        "momentum":   "Momentum  (RSI 14)",
        "volatility": "Volatility  (BB Mid-line)",
        "volume":     "Volume  (vs 20-period avg)",
        "supertrend": "SuperTrend  (10, 3)",
    }
    val_map = {
        1:  ("ok",  "✔ BULLISH"),
        -1: ("bad", "✘ BEARISH"),
        0:  ("na",  "– NEUTRAL"),
    }
    html = '<div class="cond-row">'
    for key, val in conditions.items():
        dot_cls, txt = val_map.get(val, ("na", "—"))
        html += (
            f'<div class="cond-badge">'
            f'<span class="dot {dot_cls}"></span>'
            f'<span style="color:#7a9abb;min-width:200px">{label_map[key]}</span>'
            f'<span style="color:{"#00ff88" if val==1 else ("#ff3366" if val==-1 else "#5a7a9a")}">{txt}</span>'
            f'</div>'
        )
    html += "</div>"
    return html


def metric_card(label: str, value: str, delta: str = "", color: str = "#c8daf0") -> str:
    delta_html = f'<div style="font-size:0.68rem;color:#5a7a9a;margin-top:3px">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card">
      <div class="m-label">{label}</div>
      <div class="m-value" style="color:{color}">{value}</div>
      {delta_html}
    </div>
    """


def style_signal_table(df: pd.DataFrame):
    """Apply color styling to signal table."""
    def row_color(val):
        if val == "STRONG BUY":
            return "background-color: rgba(0,255,136,0.1); color: #00ff88;"
        elif val == "STRONG SELL":
            return "background-color: rgba(255,51,102,0.1); color: #ff3366;"
        return ""

    return df.style.applymap(
        row_color, subset=["Signal"]
    ).set_properties(**{
        "background-color": "#111927",
        "color": "#c8daf0",
        "font-family": "'Share Tech Mono', monospace",
        "font-size": "0.78rem",
        "border": "1px solid #1e3a5f",
    }).set_table_styles([{
        "selector": "th",
        "props": [
            ("background-color", "#0d1421"),
            ("color", "#00d4ff"),
            ("font-family", "'Share Tech Mono', monospace"),
            ("font-size", "0.70rem"),
            ("letter-spacing", "0.08em"),
        ]
    }])


# ═══════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════

def main():

    # ── SIDEBAR ─────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0 0.5rem">
          <div style="font-family:'Exo 2',sans-serif;font-weight:900;font-size:1.3rem;
                      background:linear-gradient(90deg,#00d4ff,#7b5cff);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent">
            CONFLUENCE TRADER
          </div>
          <div style="font-family:'Share Tech Mono',monospace;font-size:0.62rem;
                      color:#5a7a9a;letter-spacing:0.15em;margin-top:4px">
            PRO SIGNAL ENGINE v2.0
          </div>
        </div>
        <hr style="margin:0.5rem 0">
        """, unsafe_allow_html=True)

        asset_name = st.selectbox(
            "Select Asset",
            list(ASSETS.keys()),
            index=0,
        )

        st.markdown("**Timeframe**")
        timeframe = st.radio(
            "Timeframe",
            list(TIMEFRAMES.keys()),
            index=1,
            horizontal=True,
            label_visibility="collapsed",
        )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button("⟳  Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.62rem;
                    color:#5a7a9a;line-height:1.8;padding:0.3rem 0">
          <b style="color:#00d4ff">Signal Logic:</b><br>
          ≥ 3 of 5 conditions must agree<br><br>
          <b style="color:#00d4ff">Conditions:</b><br>
          1. Price vs EMA 50<br>
          2. RSI(14) threshold<br>
          3. Bollinger Band Mid<br>
          4. Volume vs 20-MA<br>
          5. SuperTrend (10,3)<br><br>
          <b style="color:#00d4ff">Risk Model:</b><br>
          SL  → 1.5 × ATR(14)<br>
          TGT → 1:2 Risk:Reward
        </div>
        """, unsafe_allow_html=True)

    # ── HEADER ──────────────────────────────────────────
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown('<div class="dashboard-title">CONFLUENCE TRADER PRO</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="subtitle">Advanced Multi-Indicator Signal Engine · NSE / MCX</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div style="text-align:right;padding-top:0.8rem">'
            f'<span class="live-badge"><span class="live-dot"></span>LIVE</span>'
            f'<br><span style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
            f'color:#5a7a9a">{datetime.now().strftime("%d %b %Y  %H:%M:%S")}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── DATA FETCH ───────────────────────────────────────
    ticker   = ASSETS[asset_name]
    interval, period = TIMEFRAMES[timeframe]

    with st.spinner(f"Fetching {asset_name} [{timeframe}] …"):
        raw_df = fetch_data(ticker, interval, period)

    if raw_df is None or raw_df.empty:
        st.error(
            f"⚠️  Could not fetch data for **{asset_name}** (`{ticker}`).\n\n"
            "Possible reasons: market is closed, ticker unavailable on Yahoo Finance, "
            "or network issue. Try a different asset or timeframe."
        )
        st.stop()

    # ── COMPUTE INDICATORS ───────────────────────────────
    df = add_all_indicators(raw_df)
    df = generate_signals_history(df)

    # Latest row
    latest = df.iloc[-1]
    conds  = evaluate_conditions(latest)
    signal, bull, bear = get_confluence_signal(conds)
    ts     = df.index[-1]
    price  = float(latest["Close"])
    atr    = float(latest["ATR14"]) if pd.notna(latest.get("ATR14")) else None

    # Price change
    prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else price
    pct_chg    = ((price - prev_close) / prev_close * 100) if prev_close else 0

    # ── SIGNAL BOX + METRICS ─────────────────────────────
    sig_col, metrics_col = st.columns([2, 1])

    with sig_col:
        st.markdown(signal_html(signal, bull, bear, price, ts), unsafe_allow_html=True)

    with metrics_col:
        st.markdown(
            metric_card("LTP / Close", f"₹{price:,.2f}" if "NSEI" in ticker or "NSEBANK" in ticker or "BSE" in ticker else f"{price:,.2f}",
                        f"{'+' if pct_chg>=0 else ''}{pct_chg:.2f}%  vs prev candle",
                        COLORS["green"] if pct_chg >= 0 else COLORS["red"]),
            unsafe_allow_html=True,
        )
        sl_val  = round(price - 1.5 * atr, 2) if atr and signal == "STRONG BUY"  else \
                  round(price + 1.5 * atr, 2) if atr and signal == "STRONG SELL" else None
        tgt_val = round(price + 3.0 * atr, 2) if atr and signal == "STRONG BUY"  else \
                  round(price - 3.0 * atr, 2) if atr and signal == "STRONG SELL" else None

        col_sl, col_tgt = st.columns(2)
        with col_sl:
            st.markdown(metric_card("Stop Loss", f"{sl_val:,.2f}" if sl_val else "—",
                                    "1.5 × ATR", COLORS["red"]), unsafe_allow_html=True)
        with col_tgt:
            st.markdown(metric_card("Target", f"{tgt_val:,.2f}" if tgt_val else "—",
                                    "3.0 × ATR  (1:2)", COLORS["green"]), unsafe_allow_html=True)

    # ── CONDITION CHECKLIST ──────────────────────────────
    st.markdown('<div class="section-hdr">// Condition Scorecard</div>', unsafe_allow_html=True)
    cond_col1, cond_col2 = st.columns([1, 1])

    cond_items = list(conds.items())
    with cond_col1:
        st.markdown(condition_badges_html(dict(cond_items[:3]), signal), unsafe_allow_html=True)
    with cond_col2:
        st.markdown(condition_badges_html(dict(cond_items[3:]), signal), unsafe_allow_html=True)

    # Quick stats row
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    ema_val  = f"{latest['EMA50']:.2f}"  if pd.notna(latest.get('EMA50'))  else "—"
    rsi_val  = f"{latest['RSI14']:.1f}"  if pd.notna(latest.get('RSI14'))  else "—"
    atr_str  = f"{atr:.2f}"             if atr                              else "—"
    vol_ratio = (float(latest["Volume"]) / float(latest["VolAvg20"])) \
                if pd.notna(latest.get("VolAvg20")) and float(latest.get("VolAvg20", 0)) > 0 else None
    vol_str  = f"{vol_ratio:.2f}x"      if vol_ratio else "—"
    st_dir   = "BULL" if conds["supertrend"] == 1 else ("BEAR" if conds["supertrend"] == -1 else "—")
    st_color = COLORS["green"] if conds["supertrend"] == 1 else (COLORS["red"] if conds["supertrend"] == -1 else COLORS["text_dim"] if "text_dim" in COLORS else "#5a7a9a")

    with sc1: st.markdown(metric_card("EMA 50", ema_val, "trend anchor"), unsafe_allow_html=True)
    with sc2: st.markdown(metric_card("RSI 14", rsi_val,
                                       "overbought >70" if float(rsi_val) > 70 else ("oversold <30" if float(rsi_val) < 30 else "neutral zone") if rsi_val != "—" else "",
                                       COLORS["red"] if rsi_val != "—" and float(rsi_val) > 70 else
                                       COLORS["green"] if rsi_val != "—" and float(rsi_val) < 30 else "#c8daf0"),
                          unsafe_allow_html=True)
    with sc3: st.markdown(metric_card("ATR 14", atr_str, "volatility measure"), unsafe_allow_html=True)
    with sc4: st.markdown(metric_card("Vol Ratio", vol_str,
                                       "above avg" if vol_ratio and vol_ratio > 1 else "below avg",
                                       COLORS["green"] if vol_ratio and vol_ratio > 1 else COLORS["red"]),
                          unsafe_allow_html=True)
    with sc5: st.markdown(metric_card("SuperTrend", st_dir, "10-period / 3.0×", st_color),
                          unsafe_allow_html=True)

    # ── CHART ─────────────────────────────────────────────
    st.markdown('<div class="section-hdr">// Price Chart with Indicators</div>', unsafe_allow_html=True)
    fig = build_chart(df, asset_name)
    st.plotly_chart(fig, use_container_width=True, config={
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {"format": "png", "filename": f"{asset_name}_{timeframe}"},
    })

    # ── SIGNAL HISTORY TABLE ──────────────────────────────
    st.markdown('<div class="section-hdr">// Last 10 Confluence Signals</div>', unsafe_allow_html=True)
    sig_table = build_signal_table(df, n=10)

    if sig_table.empty:
        st.info("No actionable (BUY/SELL) confluence signals found in the loaded data window. "
                "Try a larger timeframe such as 1h or Daily.")
    else:
        # Count signals
        buy_cnt  = (sig_table["Signal"] == "STRONG BUY").sum()
        sell_cnt = (sig_table["Signal"] == "STRONG SELL").sum()
        t1, t2, t3 = st.columns(3)
        with t1: st.markdown(metric_card("Total Signals", str(len(sig_table)), "in visible window"), unsafe_allow_html=True)
        with t2: st.markdown(metric_card("BUY Signals",  str(buy_cnt),  "", COLORS["green"]),  unsafe_allow_html=True)
        with t3: st.markdown(metric_card("SELL Signals", str(sell_cnt), "", COLORS["red"]),   unsafe_allow_html=True)

        st.dataframe(
            style_signal_table(sig_table),
            use_container_width=True,
            hide_index=True,
        )

    # ── RAW DATA EXPANDER ──────────────────────────────────
    with st.expander("🔍  Raw Data (last 30 candles)", expanded=False):
        show_cols = ["Open", "High", "Low", "Close", "Volume",
                     "EMA50", "RSI14", "BB_Upper", "BB_Mid", "BB_Lower",
                     "SuperTrend", "ATR14", "signal"]
        disp_cols = [c for c in show_cols if c in df.columns]
        st.dataframe(
            df[disp_cols].tail(30).style.format({
                c: "{:.2f}" for c in disp_cols if c not in ["signal"]
            }).set_properties(**{
                "background-color": "#111927",
                "color": "#c8daf0",
                "font-family": "'Share Tech Mono', monospace",
                "font-size": "0.73rem",
            }),
            use_container_width=True,
        )

    # ── FOOTER ────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;font-family:'Share Tech Mono',monospace;
                font-size:0.62rem;color:#2a4a6a;padding:1rem 0;
                border-top:1px solid #1e3a5f;margin-top:1rem">
      ⚠ FOR EDUCATIONAL &amp; RESEARCH PURPOSES ONLY · NOT FINANCIAL ADVICE ·
      ALL TRADING INVOLVES RISK · DATA VIA YAHOO FINANCE
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
