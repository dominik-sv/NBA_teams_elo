import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------- Paths (consistent with your other pages) ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE_DIR, "..", "Data")

MATCH_DATA_CSV = os.path.join(DATA, "match_data.csv")
TEAM_STATS_JSON = os.path.join(DATA, "team_stats", "team_stats.json")

# ---------------- Guards for missing data ----------------
st.title("Champion Leaderboard (Historical Correctness)")

missing = []
if not os.path.exists(MATCH_DATA_CSV):
    missing.append("Data/match_data.csv")
if not os.path.exists(TEAM_STATS_JSON):
    missing.append("Data/team_stats/team_stats.json")

if missing:
    st.warning(
        "Missing required data files:\n\n- " + "\n- ".join(missing) +
        "\n\nRun `python calculate_elo.py` (and `python evaluate_models.py`) to generate them."
    )
    st.stop()

# ---------------- Load data ----------------
matches = pd.read_csv(MATCH_DATA_CSV)
matches["date"] = pd.to_datetime(matches["date"])

with open(TEAM_STATS_JSON, "r") as f:
    team_stats = json.load(f)

# Sanity filters
matches = matches[(matches["postseason"] == True) & matches["date"].notna()]

# ---------------- UI ----------------
leagues = sorted(matches["league"].dropna().unique().tolist())
league = st.selectbox("League", leagues)

# available seasons from both datasets
seasons_matches = set(matches[matches["league"] == league]["season"].unique().tolist())
seasons_stats = set(map(int, team_stats.get(league, {}).keys()))
seasons_all = sorted(list(seasons_matches & seasons_stats), reverse=True)

if not seasons_all:
    st.warning("No overlapping seasons between match data and team stats for this league.")
    st.stop()

start, end = st.select_slider(
    "Season range",
    options=seasons_all[::-1],  # ascending for nicer slider feel
    value=(min(seasons_all), max(seasons_all))
)

models = [
    "elo_basic", "elo_margin", "elo_home_adv",
    "elo_updK_end", "elo_updK_start", "elo_transfer_elo"
]
selected_models = st.multiselect(
    "Models to evaluate",
    options=models,
    default=models
)

if not selected_models:
    st.info("Select at least one model to evaluate.")
    st.stop()

# ---------------- Helper: actual champion by season ----------------
def actual_champion_for_season(league_name: str, season: int) -> str | None:
    df = matches[(matches["league"] == league_name) & (matches["season"] == season)]
    if df.empty:
        return None
    last_date = df["date"].max()
    finals = df[df["date"] == last_date]
    if finals.empty:
        return None
    row = finals.iloc[0]
    # winner of the last playoff game
    return row["home_name"] if row["home_win"] else row["visitor_name"]

# ---------------- Helper: finalist teams for last game ----------------
def finals_teams_for_season(league_name: str, season: int) -> tuple[str | None, str | None]:
    df = matches[(matches["league"] == league_name) & (matches["season"] == season)]
    if df.empty:
        return None, None
    last_date = df["date"].max()
    finals = df[df["date"] == last_date]
    if finals.empty:
        return None, None
    row = finals.iloc[0]
    return row["home_name"], row["visitor_name"]

# ---------------- Compute correctness per season & model ----------------
records = []
for season in range(start, end + 1):
    actual = actual_champion_for_season(league, season)
    t1, t2 = finals_teams_for_season(league, season)

    # Need the two finalists to score per model; otherwise skip
    if actual is None or t1 is None or t2 is None:
        continue

    stats_season = team_stats.get(league, {}).get(str(season), {})
    if t1 not in stats_season or t2 not in stats_season:
        # team not present in team_stats for that season
        continue

    row = {"league": league, "season": season, "actual": actual, "finalist_A": t1, "finalist_B": t2}
    for m in selected_models:
        try:
            t1_elo = stats_season[t1][m]
            t2_elo = stats_season[t2][m]
        except KeyError:
            # model key missing for a team
            continue
        predicted = t1 if t1_elo > t2_elo else t2
        row[m + "_pred"] = predicted
        row[m + "_correct"] = int(predicted == actual)
    records.append(row)

if not records:
    st.warning("No seasons available for evaluation in the selected range.")
    st.stop()

df = pd.DataFrame(records).sort_values("season", ascending=False)

# ---------------- Accuracy summary ----------------
summary_rows = []
for m in selected_models:
    correct_col = m + "_correct"
    if correct_col in df.columns:
        total = df[correct_col].count()
        if total > 0:
            acc = df[correct_col].mean()
            summary_rows.append({"Model": m, "Seasons": total, "Accuracy": acc})
summary = pd.DataFrame(summary_rows).sort_values("Accuracy", ascending=False)

st.subheader("Model Accuracy (Champion Correctness)")
if not summary.empty:
    fig = px.bar(summary, x="Model", y="Accuracy", text="Accuracy", title="Champion Prediction Accuracy by Model")
    fig.update_traces(texttemplate="%{y:.1%}")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        summary.style.format({"Accuracy": "{:.1%}"})
    )
else:
    st.info("No accuracy to display for the selected models.")

# ---------------- Season-by-season table ----------------
st.subheader("Season-by-Season Results")
show_cols = ["season", "actual", "finalist_A", "finalist_B"] + \
    [m + "_pred" for m in selected_models if m + "_pred" in df.columns] + \
    [m + "_correct" for m in selected_models if m + "_correct" in df.columns]

pretty = df[show_cols].rename(columns={
    "season": "Season",
    "actual": "Actual Champion",
    "finalist_A": "Finalist A",
    "finalist_B": "Finalist B",
    **{m + "_pred": f"{m} → Predicted" for m in selected_models if m + "_pred" in df.columns},
    **{m + "_correct": f"{m} → Correct?" for m in selected_models if m + "_correct" in df.columns},
})
st.dataframe(pretty, use_container_width=True)

st.caption(
    "Champion is taken as the winner of the last playoff game in each season. "
    "Predicted champion per model is the finalist with the higher end-of-season Elo."
)
