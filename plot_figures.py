import pandas as pd
import numpy as np
from collections import defaultdict
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio
import os
import json

pio.renderers.default = "browser"

# Import
data_directory = "data"
elo_directory = "elo_history"
comb_directory = os.path.join(data_directory, elo_directory)
os.makedirs(comb_directory, exist_ok=True)

with open(os.path.join(comb_directory, "elo_constants.json"), "r") as f:
    elo_constants = json.load(f)

# Constants
INITIAL_ELO = elo_constants["INITIAL_ELO"]
K = elo_constants["K"]
K_CHANGE = elo_constants["K_CHANGE"]
SEASON = 2025
MODEL = "transfer_elo"  # Options: "basic", "margin", "home_adv", "updK_end", "updK_start", "transfer_elo"

# Extract data
elo_df = pd.read_csv(os.path.join(data_directory, elo_directory, f"elo_df_{MODEL}.csv"))
regular_season = elo_df[
    (elo_df["season"] == SEASON) & (elo_df["postseason"] == False)
]

last_date = regular_season["date"].max()

teams = sorted(pd.unique(regular_season[["home_team", "away_team"]].values.ravel()))

def get_team_data(team, reg_season):
    team_data = pd.concat(
        [
            reg_season[reg_season["home_team"] == team][
                ["date", "home_elo_after"]
            ].rename(columns={"home_elo_after": "elo"}),
            reg_season[reg_season["away_team"] == team][
                ["date", "away_elo_after"]
            ].rename(columns={"away_elo_after": "elo"}),
        ]
    )
    team_data = team_data.sort_values("date")
    return team_data


# PLOT
## Interactive elo progress (all teams), plotly
fig = go.Figure()
for team in teams:
    team_data = get_team_data(team, regular_season)
    fig.add_trace(
        go.Scatter(x=team_data["date"], y=team_data["elo"], mode="lines", name=team)
    )

fig.update_layout(
    title=f"interactive elo progress – {SEASON} ({MODEL} model)",
    xaxis_title="date",
    yaxis_title="elo rating",
    template="plotly_white",
    legend=dict(font=dict(size=10), orientation="v"),
)
fig.show()


## Elo compared to win %, plotly
team_stats = defaultdict(lambda: {"wins": 0, "games": 0, "elo": None})

for _, row in regular_season.iterrows():
    home = row["home_team"]
    away = row["away_team"]
    win = row["home_win"]

    team_stats[home]["games"] += 1
    team_stats[away]["games"] += 1
    if win:
        team_stats[home]["wins"] += 1
    else:
        team_stats[away]["wins"] += 1

for team in pd.unique(regular_season[["home_team", "away_team"]].values.ravel()):
    team_data = get_team_data(team, regular_season)
    if not team_data.empty:
        team_stats[team]["elo"] = team_data.iloc[-1]["elo"]

team_data = pd.DataFrame(
    [
        {"team": team, "win_pct": stats["wins"] / stats["games"], "elo": stats["elo"]}
        for team, stats in team_stats.items()
        if stats["elo"] is not None
    ]
)

fig2 = px.scatter(
    team_data,
    x="elo",
    y="win_pct",
    text="team",
    color="team",
    title=f"elo vs win percentage – {SEASON} regular season",
    labels={"elo": "final elo rating", "win_pct": "win percentage"},
)

### Update ranges
fig2.update_yaxes(range=[0, 1])
x_vals = team_data["elo"]
x_min = x_vals.min()
x_max = x_vals.max()
x_margin = max(INITIAL_ELO - x_min - 100, x_max - INITIAL_ELO + 100)
fig2.update_xaxes(range=[INITIAL_ELO - x_margin, INITIAL_ELO + x_margin])

### Add vline
fig2.add_vline(x=INITIAL_ELO, line_width=2, line_dash="dash", line_color="gray")

coeffs = np.polyfit(team_data["elo"], team_data["win_pct"], deg=1)
x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
y_line = coeffs[0] * x_line + coeffs[1]
fig2.add_trace(
    go.Scatter(
        x=x_line, y=y_line, mode="lines", name="Linear fit", line=dict(dash="dot")
    )
)

fig2.update_traces(textposition="top center")
fig2.update_layout(template="plotly_white", showlegend=False)
fig2.show()