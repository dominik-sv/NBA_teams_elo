import streamlit as st
import json
import os
import math
import plotly.express as px
import pandas as pd

# -------- Paths (match your other pages) --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE_DIR, "..", "Data")
TEAM_STATS = os.path.join(DATA, "team_stats", "team_stats.json")

# -------- Guard: friendly message if data missing --------
if not os.path.exists(TEAM_STATS):
    st.title("Series Simulator")
    st.warning("Team stats not found.\n\nPlease run `python calculate_elo.py` first (and `python evaluate_models.py` if needed) so `Data/team_stats/team_stats.json` exists.")
    st.stop()

# -------- Load data --------
with open(TEAM_STATS, "r") as f:
    team_stats = json.load(f)

st.title("Series Simulator (Elo-based)")

# UI controls
leagues = sorted(team_stats.keys())
league = st.selectbox("League", leagues)

seasons = sorted(map(int, team_stats[league].keys()), reverse=True)
season = st.selectbox("Season", seasons)

models = [
    "elo_basic", "elo_margin", "elo_home_adv",
    "elo_updK_end", "elo_updK_start", "elo_transfer_elo"
]
model = st.selectbox("Elo Model", models)

teams = sorted(team_stats[league][str(season)].keys())
col1, col2 = st.columns(2)
with col1:
    team_a = st.selectbox("Team A", teams)
with col2:
    # default to a different team than A if possible
    default_idx = 1 if len(teams) > 1 else 0
    team_b = st.selectbox("Team B", teams, index=default_idx)

series_len = st.selectbox("Series length", options=[3, 5, 7], index=2)  # default Bo7

# -------- Pull Elo and compute per-game probability --------
try:
    a_elo = team_stats[league][str(season)][team_a][model]
    b_elo = team_stats[league][str(season)][team_b][model]
except KeyError:
    st.error("Selected combination not found in team stats. Try a different season/model.")
    st.stop()

# Elo win probability for A vs B on neutral (no home shift applied here)
def elo_win_prob(elo_a, elo_b):
    return 1.0 / (1.0 + 10.0 ** ((elo_b - elo_a) / 400.0))

p_game = elo_win_prob(a_elo, b_elo)

# -------- Series probability (analytical DP) --------
# Probability Team A wins a best-of-N series given per-game win prob p.
# Works for N = 1, 3, 5, 7 ... (odd numbers). We also allow 3/5/7 explicitly.
def series_win_prob_best_of(p: float, best_of: int) -> float:
    need = best_of // 2 + 1
    # dp[wA][wB] = probability of reaching (wA, wB). Start at (0,0).
    dp = [[0.0 for _ in range(need)] for __ in range(need)]
    dp[0][0] = 1.0

    prob_a_series = 0.0
    for wA in range(need):
        for wB in range(need):
            cur = dp[wA][wB]
            if cur == 0.0:
                continue
            # If already terminal, count outcomes and continue
            if wA == need:
                prob_a_series += cur
                continue
            if wB == need:
                continue
            # Next game:
            if wA + 1 == need:
                prob_a_series += cur * p
            else:
                dp[wA + 1][wB] += cur * p

            if wB + 1 == need:
                # Team B would clinch; no addition to A's series prob
                pass
            else:
                dp[wA][wB + 1] += cur * (1.0 - p)
    return prob_a_series

p_series_a = series_win_prob_best_of(p_game, series_len)
p_series_b = 1.0 - p_series_a

# -------- Display --------
st.subheader("Per-game & Series Probabilities")
st.markdown(f"- **{team_a}** Elo: **{a_elo:.1f}**")
st.markdown(f"- **{team_b}** Elo: **{b_elo:.1f}**")
st.markdown(f"- Per-game win probability for **{team_a}**: **{p_game*100:.1f}%**")
st.markdown(f"- **Best-of-{series_len}** series win probability for **{team_a}**: **{p_series_a*100:.1f}%**")

# Simple bar chart
chart_df = pd.DataFrame({
    "Team": [team_a, team_b],
    "Series Win %": [p_series_a * 100, p_series_b * 100]
})
fig = px.bar(chart_df, x="Team", y="Series Win %", text="Series Win %", title=f"Series Win Probability (Bo{series_len})")
fig.update_traces(texttemplate="%{y:.1f}%")
st.plotly_chart(fig, use_container_width=True)

st.caption("Note: Neutral per-game probability from Elo (no explicit home-court adjustment at series level).")
