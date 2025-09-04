import streamlit as st
import pandas as pd
import json
import plotly.express as px
import os

# Dynamic path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE_DIR, "..", "Data")
RESULTS_CSV = os.path.join(DATA, "playoff_results", "results.csv")
TEAM_STATS = os.path.join(DATA, "team_stats", "team_stats.json")
MATCH_DATA_CSV = os.path.join(DATA, "match_data.csv")

match_df = pd.read_csv(MATCH_DATA_CSV)
match_df["date"] = pd.to_datetime(match_df["date"])

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE_DIR, "..", "Data")
RESULTS_CSV = os.path.join(DATA, "playoff_results", "results.csv")
TEAM_STATS = os.path.join(DATA, "team_stats", "team_stats.json")

# Load data
results_df = pd.read_csv(RESULTS_CSV)
with open(TEAM_STATS) as f:
    team_stats = json.load(f)

# UI
st.title("Playoff Predictions")
season = st.selectbox("Season (2000–2023)", list(range(2000, 2024))[::-1])
model = st.selectbox("Prediction Model", [
    "elo_basic", "elo_margin", "elo_home_adv", "elo_updK_end", "elo_updK_start", "elo_transfer_elo"
])

df = results_df[results_df["season"] == season]

# Predict each matchup
predictions = []
for _, row in df.iterrows():
    t1, t2 = row["team1"], row["team2"]
    league = row["league"]
    t1_elo = team_stats[league][str(season)][t1][model]
    t2_elo = team_stats[league][str(season)][t2][model]
    pred = t1 if t1_elo > t2_elo else t2
    predictions.append({
        "Matchup": f"{t1} vs {t2}",
        "Predicted Winner": pred,
        "Actual Winner": row["winner"],
        "Correct": "✅" if pred == row["winner"] else "❌"
    })

pred_df = pd.DataFrame(predictions)
st.subheader("Series-by-Series Prediction")
st.dataframe(pred_df)

# Accuracy pie
summary = pred_df["Correct"].value_counts().rename({"✅": "Correct", "❌": "Incorrect"})
fig = px.pie(names=summary.index, values=summary.values, title="Prediction Accuracy")
st.plotly_chart(fig)

# Get actual Finals matchup from latest playoff game
playoff_games = match_df[(match_df["season"] == season) & (match_df["postseason"] == True)]
latest_date = playoff_games["date"].max()
final_game = playoff_games[playoff_games["date"] == latest_date].iloc[0]
final_t1, final_t2 = final_game["home_name"], final_game["visitor_name"]
actual_champion = final_t1 if final_game["home_win"] else final_t2

# Predict winner using Elo
t1_elo = team_stats[final_game["league"]][str(season)][final_t1][model]
t2_elo = team_stats[final_game["league"]][str(season)][final_t2][model]
predicted_champion = final_t1 if t1_elo > t2_elo else final_t2

# Display results
st.subheader("Championship Prediction")
st.markdown(f"**Predicted Champion:** {predicted_champion}")
st.markdown(f"**Actual Champion:** {actual_champion}")



# Matchup simulator
st.subheader("Simulate Your Own Matchup")
teams = sorted(team_stats[league][str(season)].keys())
team1 = st.selectbox("Team A", teams)
team2 = st.selectbox("Team B", teams, index=1)

t1_elo = team_stats[league][str(season)][team1][model]
t2_elo = team_stats[league][str(season)][team2][model]
prob = 1 / (1 + 10 ** ((t2_elo - t1_elo) / 400))

st.markdown(f"**{team1}** has a **{prob * 100:.1f}%** chance to beat **{team2}**.")
