import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# Dynamic path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE_DIR, "..", "Data")
ELO_DIR = os.path.join(DATA, "elo_history")

# Load constants
with open(os.path.join(ELO_DIR, "elo_constants.json")) as f:
    constants = json.load(f)

# UI selections
st.title("Elo vs Win Percentage")
models = ["basic", "margin", "home_adv", "updK_end", "updK_start", "transfer_elo"]
season = st.selectbox("Season", list(range(2000, 2026))[::-1])
model = st.selectbox("Model", models)

# Load Elo data
df = pd.read_csv(os.path.join(ELO_DIR, f"elo_df_{model}.csv"))
df["date"] = pd.to_datetime(df["date"])
df = df[(df["season"] == season) & (~df["postseason"])]

# Build win % and Elo per team
team_stats = {}
for _, row in df.iterrows():
    h, a = row["home_team"], row["away_team"]
    team_stats.setdefault(h, {"wins": 0, "games": 0})
    team_stats.setdefault(a, {"wins": 0, "games": 0})
    team_stats[h]["games"] += 1
    team_stats[a]["games"] += 1
    if pd.notna(row["home_win"]):
        team_stats[h]["wins"] += int(row["home_win"])
        team_stats[a]["wins"] += int(not row["home_win"])

# Build final DataFrame
data = []
for team in team_stats:
    recent = df[(df["home_team"] == team) | (df["away_team"] == team)]
    if not recent.empty:
        last_elo = recent[["home_elo_after", "away_elo_after"]].max(axis=1).iloc[-1]
        win_pct = team_stats[team]["wins"] / team_stats[team]["games"]
        data.append({"Team": team, "Elo": last_elo, "Win %": win_pct})

# Scatter plot
plot_df = pd.DataFrame(data)
fig = px.scatter(plot_df, x="Elo", y="Win %", text="Team", color="Team")
fig.update_traces(textposition="top center")
fig.add_vline(x=constants["INITIAL_ELO"], line_dash="dash", line_color="gray")
fig.update_layout(title=f"Elo vs Win % – {season}", template="plotly_white")

st.plotly_chart(fig, use_container_width=True)
