import streamlit as st
import os
import json
import pandas as pd

st.set_page_config(page_title="NBA Elo Dashboard", layout="wide")

# ---------- Paths & helpers ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_data_dir():
    for name in ("Data", "data"):
        p = os.path.join(BASE_DIR, name)
        if os.path.exists(p):
            return p
    return os.path.join(BASE_DIR, "Data")

DATA = get_data_dir()
ELO_DIR = os.path.join(DATA, "elo_history")
TEAM_STATS = os.path.join(DATA, "team_stats", "team_stats.json")
MODEL_STATS = os.path.join(DATA, "model_stats", "model_stats.json")
PLAYOFF_RESULTS = os.path.join(DATA, "playoff_results", "results.csv")
MATCH_DATA = os.path.join(DATA, "match_data.csv")

def exists(path):
    return os.path.exists(path)

def seasons_from_match_data():
    if not exists(MATCH_DATA):
        return []
    try:
        df = pd.read_csv(MATCH_DATA)
        return sorted(pd.Series(df.get("season", [])).dropna().unique().tolist())
    except Exception:
        return []

def status_badge(ok: bool) -> str:
    return "✅" if ok else "❌"

# ---------- Header ----------
st.title("NBA Elo Ratings Dashboard")
st.caption("Explore Elo models, visualizations, and playoff predictions across seasons.")

# ---------- Top info / quick start ----------
with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("What you can find here")
        st.markdown("""
- **Elo Progression** — Track a team’s Elo through a season.
- **Elo vs. Win %** — See how Elo correlates with regular-season performance.
- **Model Leaderboard** — Compare models on MAE, RMSE, and binary error.
- **Playoff Predictions** — Series-by-series picks and season champion pick.
- **Series Simulator** — Best-of-3/5/7 series win probabilities (analytical).
- **Champion Leaderboard** — How often each model picked the right champion.
- **Season-End Rankings** — Final Elo table and the strongest non-champion.
- **Model Radar** — Normalized performance view across errors.
        """)