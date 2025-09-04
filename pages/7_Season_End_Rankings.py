import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------- Paths (consistent with your other pages) ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE_DIR, "..", "Data")
ELO_DIR = os.path.join(DATA, "elo_history")
MATCH_DATA_CSV = os.path.join(DATA, "match_data.csv")

st.title("Season-End Elo Rankings")

# ---------------- Guards ----------------
missing = []
if not os.path.exists(MATCH_DATA_CSV):
    missing.append("Data/match_data.csv")
if not os.path.exists(ELO_DIR):
    missing.append("Data/elo_history/")

if missing:
    st.warning(
        "Missing required data files:\n\n- " + "\n- ".join(missing) +
        "\n\nRun `python calculate_elo.py` (and `python evaluate_models.py`) to generate them."
    )
    st.stop()

# ---------------- Load match data ----------------
matches = pd.read_csv(MATCH_DATA_CSV)
if "date" in matches.columns:
    matches["date"] = pd.to_datetime(matches["date"], errors="coerce")

leagues = sorted(matches["league"].dropna().unique().tolist())
league = st.selectbox("League", leagues)

seasons = sorted(matches[matches["league"] == league]["season"].dropna().unique().tolist(), reverse=True)
season = st.selectbox("Season", seasons)

models = ["basic", "margin", "home_adv", "updK_end", "updK_start", "transfer_elo"]
model = st.selectbox("Elo Model", models, index=models.index("transfer_elo") if "transfer_elo" in models else 0)

stage = st.radio("Stage", ["Regular season end", "Postseason end"], index=1)
top_n = st.slider("Show top N teams", 5, 30, 10)

# ---------------- Load Elo history for selected model ----------------
elo_csv = os.path.join(ELO_DIR, f"elo_df_{model}.csv")
if not os.path.exists(elo_csv):
    st.warning(f"Elo file not found: {elo_csv}\n\nRun `python calculate_elo.py` to generate it.")
    st.stop()

elo_df = pd.read_csv(elo_csv)
elo_df["date"] = pd.to_datetime(elo_df["date"], errors="coerce")

# Filter season + stage
if stage == "Regular season end":
    sdf = elo_df[(elo_df["season"] == season) & (elo_df["postseason"] == False)].copy()
else:
    sdf = elo_df[(elo_df["season"] == season) & (elo_df["postseason"] == True)].copy()

if sdf.empty:
    st.warning("No Elo data for this season/stage. Try the other stage or re-generate elo files.")
    st.stop()

# Build per-team latest Elo at the stage
# We gather the latest row per team considering both home_elo_after and away_elo_after.
home_latest = (
    sdf[["date", "home_team", "home_elo_after"]]
    .rename(columns={"home_team": "team", "home_elo_after": "elo"})
)
away_latest = (
    sdf[["date", "away_team", "away_elo_after"]]
    .rename(columns={"away_team": "team", "away_elo_after": "elo"})
)
both = pd.concat([home_latest, away_latest], ignore_index=True).dropna(subset=["elo", "date"])

# keep the last Elo per team (by date)
both = both.sort_values(["team", "date"])
last_elos = both.groupby("team").tail(1).reset_index(drop=True)
last_elos = last_elos.sort_values("elo", ascending=False)

# ---------------- Actual champion (from last playoff game) ----------------
def actual_champion_for_season(league_name: str, season_val: int) -> str | None:
    df = matches[(matches["league"] == league_name) & (matches["season"] == season_val) & (matches["postseason"] == True)]
    if df.empty or "date" not in df.columns:
        return None
    last_date = df["date"].max()
    finals = df[df["date"] == last_date]
    if finals.empty:
        return None
    row = finals.iloc[0]
    return row["home_name"] if row.get("home_win", False) else row["visitor_name"]

champion = actual_champion_for_season(league, season)

# Strongest non-champion
strongest_non_champ = None
if not last_elos.empty:
    if champion in set(last_elos["team"]):
        non_champs = last_elos[last_elos["team"] != champion]
        if not non_champs.empty:
            strongest_non_champ = non_champs.iloc[0]["team"]
    else:
        strongest_non_champ = last_elos.iloc[0]["team"]

# ---------------- Display ----------------
colA, colB = st.columns(2)
with colA:
    st.subheader("Highlights")
    if champion:
        st.markdown(f"**Actual Champion:** {champion}")
    else:
        st.markdown("**Actual Champion:** *(unknown in data)*")
    st.markdown(f"**Highest Elo (stage end):** {last_elos.iloc[0]['team']} — {last_elos.iloc[0]['elo']:.1f}")
    if strongest_non_champ:
        st.markdown(f"**Strongest team who didn’t win:** {strongest_non_champ}")

with colB:
    st.subheader(f"Top {top_n} Elo — {stage}")
    chart_df = last_elos.head(top_n).copy()
    # tag champion & strongest non-champ for color/labels
    def tag(team):
        if champion and team == champion:
            return "Champion"
        if strongest_non_champ and team == strongest_non_champ:
            return "Strongest non-champion"
        return "Other"
    chart_df["Tag"] = chart_df["team"].apply(tag)
    fig = px.bar(chart_df, x="team", y="elo", color="Tag", title=f"{season} {model} — {stage}")
    fig.update_layout(xaxis_title="Team", yaxis_title="Elo", showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Full Rankings")
st.dataframe(
    last_elos.reset_index(drop=True).rename(columns={"team": "Team", "elo": "Elo", "date": "Last Game Date"}),
    use_container_width=True
)

st.caption(
    "Elo is taken from the last game each team played within the selected stage (regular vs postseason). "
    "Champion is determined as the winner of the final playoff game in the season."
)
