import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_data_dir():
    for name in ("Data", "data"):
        path = os.path.join(BASE_DIR, "..", name)
        if os.path.exists(path):
            return path
    return os.path.join(BASE_DIR, "..", "Data")

DATA = get_data_dir()
ELO_DIR = os.path.join(DATA, "elo_history")
CONST_PATH = os.path.join(ELO_DIR, "elo_constants.json")

st.title("Elo vs Win Percentage")

if not os.path.exists(ELO_DIR):
    st.warning("Elo data not found. Run `python calculate_elo.py`.")
    st.stop()

constants = {}
if os.path.exists(CONST_PATH):
    with open(CONST_PATH, "r") as f:
        constants = json.load(f)

models = ["basic", "margin", "home_adv", "updK_end", "updK_start", "transfer_elo"]
model = st.selectbox("Model", models)

csv_path = os.path.join(ELO_DIR, f"elo_df_{model}.csv")
if not os.path.exists(csv_path):
    st.warning(f"Missing {csv_path}. Run `python calculate_elo.py`.")
    st.stop()

df = pd.read_csv(csv_path)
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

if "season" not in df.columns:
    st.error("Elo CSV missing 'season' column.")
    st.stop()

# ---- Dynamic seasons ----
seasons = sorted(df["season"].dropna().unique().tolist(), reverse=True)
season = st.selectbox("Season", seasons)

# Regular season only
df = df[(df["season"] == season) & (df["postseason"] == False)]

# Build win% and last Elo per team
team_stats = {}
for _, row in df.iterrows():
    h, a = row["home_team"], row["away_team"]
    team_stats.setdefault(h, {"wins": 0, "games": 0})
    team_stats.setdefault(a, {"wins": 0, "games": 0})
    team_stats[h]["games"] += 1
    team_stats[a]["games"] += 1
    if pd.notna(row.get("home_win")):
        team_stats[h]["wins"] += int(bool(row["home_win"]))
        team_stats[a]["wins"] += int(not bool(row["home_win"]))

data = []
for team in team_stats:
    recent = df[(df["home_team"] == team) | (df["away_team"] == team)].copy()
    if not recent.empty:
        # take Elo from the last game (home/away)
        recent = recent.sort_values("date")
        last_row = recent.iloc[-1]
        last_elo = max(last_row.get("home_elo_after", float("nan")), last_row.get("away_elo_after", float("nan")))
        win_pct = team_stats[team]["wins"] / max(1, team_stats[team]["games"])
        data.append({"Team": team, "Elo": last_elo, "Win %": win_pct})

plot_df = pd.DataFrame(data)
if plot_df.empty:
    st.info("No data to plot for this selection.")
else:
    fig = px.scatter(plot_df, x="Elo", y="Win %", text="Team", color="Team", title=f"Elo vs Win % – {season} ({model})")
    fig.update_traces(textposition="top center")
    if "INITIAL_ELO" in constants:
        fig.add_vline(x=constants["INITIAL_ELO"], line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)
