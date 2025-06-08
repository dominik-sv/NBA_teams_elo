import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.cm as cm
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio

pio.renderers.default = "browser"

# Data load
url = "https://raw.githubusercontent.com/dominik-sv/NBA_teams_elo/main/Data/match_data.csv"
df = pd.read_csv(url)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# Constants
INITIAL_ELO = 1000
K = 40
SEASON = 2023
MODEL = "increasing_K"  # Options: "basic", "margin", "home_adv", "increasing_K", "decreasing_K"
K_CHANGE = 15


# Functions
def adjust_expected_outcome_home_advantage(expected_outcome, home_advantage, weight):
    return (1 - weight) * expected_outcome + weight * home_advantage

def calculate_expected_outcome(elo_away, elo_home, home_advantage = False):
    if home_advantage:
        elo_home += home_advantage
    return 1 / (1 + 10 ** ((elo_away - elo_home) / 400))

def calculate_elo_update(K, outcome_home, exp_home, mov_mult = False):
    outcome = outcome_home - exp_home
    if mov_mult:
        return K * outcome * mov_mult
    else:
        return K * outcome

def add_elo_to_history(base_match_data, elo_after_home, elo_after_away):
    match_data = base_match_data.copy()
    match_data.update({
        "home_elo_after": elo_after_home,
        "away_elo_after": elo_after_away,
    })
    return match_data

def calculate_season_progress(starting_date, ending_date, current_date):
    return (current_date - starting_date) / (ending_date - starting_date)



# Elaborate elo calculation
elo_carried = defaultdict(lambda: INITIAL_ELO)

history_basic, history_margin, history_home_adv, history_updK_end, history_updK_start = [], [], [], [], []

for season in sorted(df["season"].unique()):
    elo_basic = defaultdict(lambda: INITIAL_ELO)
    elo_margin = defaultdict(lambda: INITIAL_ELO)
    elo_home_adv = defaultdict(lambda: INITIAL_ELO)
    elo_updK_end = defaultdict(lambda: INITIAL_ELO)
    elo_updK_start = defaultdict(lambda: INITIAL_ELO)
    
    season_games = df[df["season"] == season]
    home_team_advantage = season_games["home_win"].mean()
    home_team_elo_shift = np.log(home_team_advantage / (1 - home_team_advantage)) / np.log(10) * 400

    # Initialize elo for teams in the season
    teams_in_season = pd.unique(season_games[["home_name", "visitor_name"]].values.ravel())
    first_game_date = season_games["date"].min() - pd.Timedelta(days=1)

    for team in teams_in_season:
        base_match_data = {
            "date": first_game_date,
            "season": season,
            "postseason": False,
            "home_team": team,
            "away_team": team,
            "home_win": None,
        }

        history_basic.append(add_elo_to_history(base_match_data, INITIAL_ELO, INITIAL_ELO))
        history_margin.append(add_elo_to_history(base_match_data, INITIAL_ELO, INITIAL_ELO))
        history_home_adv.append(add_elo_to_history(base_match_data, INITIAL_ELO, INITIAL_ELO))
        history_updK_end.append(add_elo_to_history(base_match_data, INITIAL_ELO, INITIAL_ELO))
        history_updK_start.append(add_elo_to_history(base_match_data, INITIAL_ELO, INITIAL_ELO))

    # Dates
    starting_date = season_games["date"].min()
    ending_date = season_games["date"].max()

    # Iterate through games in the season
    for _, row in season_games.iterrows():
        home, away = row["home_name"], row["visitor_name"]
        home_pts, away_pts = row["home_pts"], row["visitor_pts"]
        home_win = row["home_win"]
        margin = row["margin_of_victory"]

        # Original elo
        elo_home_b, elo_away_b = elo_basic[home], elo_basic[away]
        elo_home_m, elo_away_m = elo_margin[home], elo_margin[away]
        elo_home_h, elo_away_h = elo_home_adv[home], elo_home_adv[away]
        elo_home_Ke, elo_away_Ke = elo_updK_end[home], elo_updK_end[away]
        elo_home_Ks, elo_away_Ks = elo_updK_start[home], elo_updK_start[away]

        # Expected outcomes
        exp_home_b = calculate_expected_outcome(elo_away_b, elo_home_b)
        exp_home_m = calculate_expected_outcome(elo_away_m, elo_home_m)
        exp_home_h = calculate_expected_outcome(elo_away_h, elo_home_h, home_advantage=home_team_elo_shift)
        exp_home_Ke = calculate_expected_outcome(elo_away_Ke, elo_home_Ke, home_advantage=home_team_elo_shift)
        exp_home_Ks = calculate_expected_outcome(elo_away_Ks, elo_home_Ks, home_advantage=home_team_elo_shift)

        outcome_home = 1 if home_win else 0

        # Regular elo update
        delta_b = calculate_elo_update(K, outcome_home, exp_home_b)
        elo_basic[home] += delta_b
        elo_basic[away] -= delta_b

        # Margin of victory (MOV) elo update
        elo_diff_m = elo_home_m - elo_away_m
        mov_mult = np.log(max(margin, 1) + 1) * (2.2 / (0.001 * abs(elo_diff_m) + 2.2))
        delta_m = calculate_elo_update(K, outcome_home, exp_home_m, mov_mult=mov_mult)
        elo_margin[home] += delta_m
        elo_margin[away] -= delta_m

        # Home team advantage elo update
        delta_h = calculate_elo_update(K, outcome_home, exp_home_h, mov_mult=mov_mult)
        elo_home_adv[home] += delta_h
        elo_home_adv[away] -= delta_h

        # Updating K throughout season (larger at end, larger at start)
        season_progress = calculate_season_progress(starting_date, ending_date, row["date"])

        K_weighted_end = K + K_CHANGE * (2 * season_progress - 1)
        delta_updK_end = calculate_elo_update(K_weighted_end, outcome_home, exp_home_Ke, mov_mult=mov_mult)
        elo_updK_end[home] += delta_updK_end
        elo_updK_end[away] -= delta_updK_end

        K_weighted_start = K - K_CHANGE * (2 * season_progress - 1)
        delta_updK_start = calculate_elo_update(K_weighted_start, outcome_home, exp_home_Ks, mov_mult=mov_mult)
        elo_updK_start[home] += delta_updK_start
        elo_updK_start[away] -= delta_updK_start

        # Track
        base_match_data = {
            "date": row["date"],
            "season": season,
            "postseason": row["postseason"],
            "home_team": home,
            "away_team": away,
            "home_win": home_win,
        }

        match_data_basic = add_elo_to_history(base_match_data, elo_basic[home], elo_basic[away])
        match_data_margin = add_elo_to_history(base_match_data, elo_margin[home], elo_margin[away])
        match_data_home_adv = add_elo_to_history(base_match_data, elo_home_adv[home], elo_home_adv[away])
        match_data_updK_end = add_elo_to_history(base_match_data, elo_updK_end[home], elo_updK_end[away])
        match_data_updK_start = add_elo_to_history(base_match_data, elo_updK_start[home], elo_updK_start[away])

        history_basic.append(match_data_basic)
        history_margin.append(match_data_margin)
        history_home_adv.append(match_data_home_adv)
        history_updK_end.append(match_data_updK_end)
        history_updK_start.append(match_data_updK_start)


elo_df_basic = pd.DataFrame(history_basic)
elo_df_margin = pd.DataFrame(history_margin)
elo_df_home_adv = pd.DataFrame(history_home_adv)
elo_df_updK_end = pd.DataFrame(history_updK_end)
elo_df_updK_start = pd.DataFrame(history_updK_start)

# # MOV multiplier curve
# margin_range = np.arange(1, 60)
# elo_diff_example = 100
# mov_multipliers = np.log(margin_range + 1) * (
#     2.2 / (0.001 * abs(elo_diff_example) + 2.2)
# )

# plt.figure(figsize=(10, 5))
# plt.plot(margin_range, mov_multipliers, color="purple")
# plt.title("MOV multiplier vs margin of victory (elo diff = 100)")
# plt.xlabel("margin of victory")
# plt.ylabel("MOV multiplier")
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# Elo progress for 3 teams
# recent_season = elo_df_basic["season"].max()
# recent_regular = elo_df_basic[
#     (elo_df_basic["season"] == recent_season) & (elo_df_basic["postseason"] == False)
# ]
# last_date = recent_regular["date"].max()

# final_elos = {}
# for _, row in recent_regular[recent_regular["date"] == last_date].iterrows():
#     final_elos[row["home_team"]] = row["home_elo_after"]
#     final_elos[row["away_team"]] = row["away_elo_after"]

# top_3_teams = sorted(final_elos.items(), key=lambda x: x[1], reverse=True)[:3]
# top_3_names = [team for team, _ in top_3_teams]

# plt.figure(figsize=(14, 6))
# for team in top_3_names:
#     team_data = pd.concat(
#         [
#             recent_regular[recent_regular["home_team"] == team][
#                 ["date", "home_elo_after"]
#             ].rename(columns={"home_elo_after": "elo"}),
#             recent_regular[recent_regular["away_team"] == team][
#                 ["date", "away_elo_after"]
#             ].rename(columns={"away_elo_after": "elo"}),
#         ]
#     )
#     team_data = team_data.sort_values("date")
#     plt.plot(team_data["date"], team_data["elo"], label=team)

# plt.title(f"elo progression for 3 teams – {recent_season}")
# plt.xlabel("date")
# plt.ylabel("elo rating")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# Choose model and season
if MODEL == "basic":
    elo_df = elo_df_basic
elif MODEL == "margin":
    elo_df = elo_df_margin
elif MODEL == "home_adv":
    elo_df = elo_df_home_adv
elif MODEL == "increasing_K":
    elo_df = elo_df_updK_end
elif MODEL == "decreasing_K":
    elo_df = elo_df_updK_start

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
