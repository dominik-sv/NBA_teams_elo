import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import json

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_data_dir():
    # tolerate Data/ vs data/
    for name in ("Data", "data"):
        path = os.path.join(BASE_DIR, "..", name)
        if os.path.exists(path):
            return path
    return os.path.join(BASE_DIR, "..", "Data")

DATA = get_data_dir()
ELO_DIR = os.path.join(DATA, "elo_history")
CONST_PATH = os.path.join(ELO_DIR, "elo_constants.json")

st.title("Elo Progression")

if not os.path.exists(ELO_DIR):
    st.warning("Elo data not found. Run `python calculate_elo.py` to generate files in Data/elo_history/.")
    st.stop()

# Load constants (optional)
constants = {}
if os.path.exists(CONST_PATH):
    with open(CONST_PATH, "r") as f:
        constants = json.load(f)

models = ["basic", "margin", "home_adv", "updK_end", "updK_start", "transfer_elo"]
model = st.selectbox("Elo Model", models)

csv_path = os.path.join(ELO_DIR, f"elo_df_{model}.csv")
if not os.path.exists(csv_path):
    st.warning(f"Missing {csv_path}. Run `python calculate_elo.py`.")
    st.stop()

df = pd.read_csv(csv_path)
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

# ---- Seasons from data (dynamic) ----
if "season" not in df.columns:
    st.error("Elo CSV missing 'season' column.")
    st.stop()

seasons = sorted(df["season"].dropna().unique().tolist(), reverse=True)
season = st.selectbox("Season", seasons)

# Regular season rows only for progression
season_df = df[(df["season"] == season) & (df["postseason"] == False)]

# Teams from data
teams = sorted(pd.unique(season_df[["home_team", "away_team"]].values.ravel()))
if not teams:
    st.warning("No teams found for this season.")
    st.stop()
team = st.selectbox("Team", teams)

def get_team_data(name: str) -> pd.DataFrame:
    h = season_df[season_df["home_team"] == name][["date", "home_elo_after"]].rename(columns={"home_elo_after": "elo"})
    a = season_df[season_df["away_team"] == name][["date", "away_elo_after"]].rename(columns={"away_elo_after": "elo"})
    out = pd.concat([h, a]).dropna().sort_values("date")
    return out

team_data = get_team_data(team)
if team_data.empty:
    st.info("No Elo entries for this team/season.")
else:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=team_data["date"], y=team_data["elo"], mode="lines+markers", name=team))
    fig.update_layout(title=f"{team} Elo – {season} ({model})", xaxis_title="Date", yaxis_title="Elo", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
