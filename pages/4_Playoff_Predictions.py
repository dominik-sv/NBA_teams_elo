import streamlit as st
import pandas as pd
import json
import plotly.express as px
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_data_dir():
    for name in ("Data", "data"):
        path = os.path.join(BASE_DIR, "..", name)
        if os.path.exists(path):
            return path
    return os.path.join(BASE_DIR, "..", "Data")

DATA = get_data_dir()
RESULTS_CSV = os.path.join(DATA, "playoff_results", "results.csv")
TEAM_STATS = os.path.join(DATA, "team_stats", "team_stats.json")
MATCH_DATA_CSV = os.path.join(DATA, "match_data.csv")

st.title("Playoff Predictions")

missing = []
if not os.path.exists(RESULTS_CSV): missing.append("Data/playoff_results/results.csv")
if not os.path.exists(TEAM_STATS):  missing.append("Data/team_stats/team_stats.json")
if not os.path.exists(MATCH_DATA_CSV): missing.append("Data/match_data.csv")

if missing:
    st.warning("Missing:\n- " + "\n- ".join(missing) + "\n\nRun `python evaluate_models.py` and `python calculate_elo.py`.")
    st.stop()

# Load data
results_df = pd.read_csv(RESULTS_CSV)
match_df = pd.read_csv(MATCH_DATA_CSV)
with open(TEAM_STATS) as f:
    team_stats = json.load(f)

if "date" in match_df.columns:
    match_df["date"] = pd.to_datetime(match_df["date"], errors="coerce")

# User Interface: League, Season, Model
leagues = sorted(set(results_df.get("league", pd.Series([])).dropna().unique().tolist()) |
                 set(team_stats.keys()))
league = st.selectbox("League", leagues)

# Seasons intersection (from results + team_stats for this league)
seasons_from_results = set(results_df[results_df.get("league") == league]["season"].unique().tolist())
seasons_from_stats = set(map(int, team_stats.get(league, {}).keys()))
seasons = sorted(list(seasons_from_results & seasons_from_stats), reverse=True)
if not seasons:
    st.warning("No overlapping seasons for this league. Try another league or regenerate data.")
    st.stop()
season = st.selectbox("Season", seasons)

models = [
    "elo_basic", "elo_margin", "elo_home_adv", "elo_updK_end", "elo_updK_start", "elo_transfer_elo"
]
model = st.selectbox("Prediction Model", models)

# Predict each matchup for selected league+season
df = results_df[(results_df["season"] == season) & (results_df["league"] == league)].copy()
predictions = []
for _, row in df.iterrows():
    t1, t2 = row["team1"], row["team2"]
    stats_season = team_stats.get(league, {}).get(str(season), {})
    if t1 not in stats_season or t2 not in stats_season:
        continue
    t1_elo = stats_season[t1][model]
    t2_elo = stats_season[t2][model]
    pred = t1 if t1_elo > t2_elo else t2
    predictions.append({
        "Matchup": f"{t1} vs {t2}",
        "Predicted Winner": pred,
        "Actual Winner": row["winner"],
        "Correct": "✅" if pred == row["winner"] else "❌"
    })

if predictions:
    pred_df = pd.DataFrame(predictions)
    st.subheader("Series-by-Series Prediction")
    st.dataframe(pred_df, use_container_width=True)

    summary = pred_df["Correct"].value_counts().rename({"✅": "Correct", "❌": "Incorrect"})
    fig = px.pie(names=summary.index, values=summary.values, title="Prediction Accuracy")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No series predictions available for this selection.")

# Actual & Predicted Champion for the season
playoff_games = match_df[(match_df.get("league") == league) & (match_df["season"] == season) & (match_df["postseason"] == True)]
if not playoff_games.empty and "date" in playoff_games.columns:
    latest_date = playoff_games["date"].max()
    final_game = playoff_games[playoff_games["date"] == latest_date].iloc[0]
    final_t1, final_t2 = final_game["home_name"], final_game["visitor_name"]
    actual_champion = final_t1 if bool(final_game.get("home_win")) else final_t2

    stats_season = team_stats.get(league, {}).get(str(season), {})
    if final_t1 in stats_season and final_t2 in stats_season:
        t1_elo = stats_season[final_t1][model]
        t2_elo = stats_season[final_t2][model]
        predicted_champion = final_t1 if t1_elo > t2_elo else final_t2

        st.subheader("Championship Prediction")
        st.markdown(f"**Predicted Champion:** {predicted_champion}")
        st.markdown(f"**Actual Champion:** {actual_champion}")
else:
    st.info("Finals not found in match data for this league/season.")

# Matchup simulator
st.subheader("Simulate Your Own Matchup")
stats_season = team_stats.get(league, {}).get(str(season), {})
teams = sorted(stats_season.keys())
if len(teams) < 2:
    st.info("Not enough teams found for this season in team stats.")
else:
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Team A", teams)
    with col2:
        team2 = st.selectbox("Team B", teams, index=1)
    t1_elo = stats_season[team1][model]
    t2_elo = stats_season[team2][model]
    prob = 1 / (1 + 10 ** ((t2_elo - t1_elo) / 400))
    st.markdown(f"**{team1}** has a **{prob * 100:.1f}%** chance to beat **{team2}** (single game, neutral).")
