import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import json

# Resolve paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE_DIR, "..", "Data")
ELO_DIR = os.path.join(DATA, "elo_history")

# Load constants
with open(os.path.join(ELO_DIR, "elo_constants.json")) as f:
    constants = json.load(f)

st.title("Elo Progression")

models = ["basic", "margin", "home_adv", "updK_end", "updK_start", "transfer_elo"]
seasons = list(range(2000, 2026))[::-1]

season = st.selectbox("Season", seasons)
model = st.selectbox("Elo Model", models)

# Load Elo CSV
df = pd.read_csv(os.path.join(ELO_DIR, f"elo_df_{model}.csv"))
df["date"] = pd.to_datetime(df["date"])
season_df = df[(df["season"] == season) & (~df["postseason"])]

teams = sorted(pd.unique(season_df[["home_team", "away_team"]].values.ravel()))
team = st.selectbox("Team", teams)

def get_team_data(name):
    h = season_df[season_df["home_team"] == name][["date", "home_elo_after"]].rename(columns={"home_elo_after": "elo"})
    a = season_df[season_df["away_team"] == name][["date", "away_elo_after"]].rename(columns={"away_elo_after": "elo"})
    return pd.concat([h, a]).sort_values("date")

team_data = get_team_data(team)

fig = go.Figure()
fig.add_trace(go.Scatter(x=team_data["date"], y=team_data["elo"], mode="lines+markers", name=team))
fig.update_layout(title=f"{team} Elo – {season}", xaxis_title="Date", yaxis_title="Elo Rating", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)