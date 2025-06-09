import pandas as pd
import numpy as np
from collections import defaultdict
import os
import json
from tqdm import tqdm
from dataclasses import dataclass, field
from typing import Callable, Dict

# Data load
print("Importing data...")
url = "https://raw.githubusercontent.com/dominik-sv/NBA_teams_elo/main/Data/match_data.csv"
df = pd.read_csv(url)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# Constants
INITIAL_ELO = 1000
K = 40
K_CHANGE = 15

@dataclass
class EloVariant:
    name: str
    k_func: Callable[[float], float]
    expect_func: Callable[[float, float, float], float]
    use_mov_mult: bool
    use_home_shift: bool
    ratings: Dict[str, float] = field(default_factory=lambda: defaultdict(lambda: INITIAL_ELO))

    def expected(self, elo_h, elo_a, shift):
        return self.expect_func(elo_h, elo_a, shift if self.use_home_shift else 0)
    
    def k(self, progress):
        return self.k_func(progress)
    
    def apply_game(self, home: str, away: str, outcome_home: int, progress: float, mov_mult: float, shift: float):
        elo_h, elo_a = self.ratings[home], self.ratings[away]
        p_home = self.expected(elo_h, elo_a, shift)
        outcome_diff = outcome_home - p_home
        mult = mov_mult if self.use_mov_mult else 1
        delta = self.k(progress) * outcome_diff * mult

        self.ratings[home] += delta
        self.ratings[away] -= delta
        return self.ratings[home], self.ratings[away]

VARIANTS = [
    EloVariant(
        name="basic",
        k_func=lambda prog: K,
        expect_func=lambda eh, ea, _: 1 / (1 + 10 ** ((ea - eh) / 400)),
        use_mov_mult=False,
        use_home_shift=False,
    ),
    EloVariant(
        name="margin",
        k_func=lambda prog: K,
        expect_func=lambda eh, ea, _: 1 / (1 + 10 ** ((ea - eh) / 400)),
        use_mov_mult=True,
        use_home_shift=False,
    ),
    EloVariant(
        name="home_adv",
        k_func=lambda prog: K,
        expect_func=lambda eh, ea, shift: 1 / (1 + 10 ** (((ea) - (eh + shift)) / 400)),
        use_mov_mult=True,
        use_home_shift=True,
    ),
    EloVariant(
        name="updK_end",
        k_func=lambda prog: K + K_CHANGE * (2 * prog - 1),
        expect_func=lambda eh, ea, shift: 1 / (1 + 10 ** (((ea) - (eh + shift)) / 400)),
        use_mov_mult=True,
        use_home_shift=True,
    ),
    EloVariant(
        name="updK_start",
        k_func=lambda prog: K - K_CHANGE * (2 * prog - 1),
        expect_func=lambda eh, ea, shift: 1 / (1 + 10 ** (((ea) - (eh + shift)) / 400)),
        use_mov_mult=True,
        use_home_shift=True,
    ),
]

# Functions
def add_elo_to_history(base_match_data, elo_after_home, elo_after_away):
    match_data = base_match_data.copy()
    match_data.update(
        {
            "home_elo_after": elo_after_home,
            "away_elo_after": elo_after_away,
        }
    )
    return match_data

# Initialize dictionaries
history = {v.name: [] for v in VARIANTS}
team_stats_all_seasons = defaultdict(dict)

# Process seasons
for season in tqdm(sorted(df["season"].unique()), desc="Processing seasons"):
    season_games = df[(df["season"] == season) & (df["postseason"] == False)]

    # Initialize elo rating dictionary
    for v in VARIANTS:
        v.ratings = defaultdict(lambda: INITIAL_ELO)

    # Calculate home court advantage
    home_team_advantage = season_games["home_win"].mean()
    home_team_elo_shift = (
        np.log(home_team_advantage / (1 - home_team_advantage)) / np.log(10) * 400
    )

    # Initialize statistics dictionary
    team_stats = defaultdict(lambda: {
        **{f"elo_{v.name}": None for v in VARIANTS},
        "wins": 0,
        "games_played": 0,
        "net_rating": 0,
    })

    # Get teams that played in season
    teams_in_season = pd.unique(
        season_games[["home_name", "visitor_name"]].values.ravel()
    )

    # Begin rating history with dummy row
    first_game_date = season_games["date"].min() - pd.Timedelta(days=1)
    for team in teams_in_season:
        dummy_row = {
            "date": first_game_date,
            "season": season,
            "postseason": False,
            "home_team": team,
            "away_team": team,
            "home_win": None,
        }
        for v in VARIANTS:
            history[v.name].append(
                add_elo_to_history(dummy_row, INITIAL_ELO, INITIAL_ELO)
            )

    # Get dates
    starting_date = season_games["date"].min()
    ending_date = season_games["date"].max()

    # Iterate through games in the season
    for _, row in season_games.iterrows():

        # Get match data
        home, away = row["home_name"], row["visitor_name"]
        home_pts, away_pts = row["home_pts"], row["visitor_pts"]
        home_win = row["home_win"]
        margin = row["margin_of_victory"]

        # Calculate needed variables
        season_progress = (row["date"] - starting_date) / (ending_date - starting_date)
        elo_diff = VARIANTS[0].ratings[home] - VARIANTS[0].ratings[away]
        mov_mult = np.log(max(margin, 1) + 1) * (2.2 / (0.001 * abs(elo_diff) + 2.2))
        outcome_home = 1 if home_win else 0

        # Evaluate and append models
        for v in VARIANTS:
            elo_h_after, elo_a_after = v.apply_game(
                home, away,
                outcome_home=outcome_home,
                progress=season_progress,
                mov_mult=mov_mult,
                shift=home_team_elo_shift,
            )

            history[v.name].append(
                add_elo_to_history(
                    {
                        "date": row["date"],
                        "season": season,
                        "postseason": row["postseason"],
                        "home_team": home,
                        "away_team": away,
                        "home_win": home_win,
                    },
                    elo_h_after,
                    elo_a_after,
                )
            )

        # Track statistics
        for v in VARIANTS:
            team_stats[home][f"elo_{v.name}"] = v.ratings[home]
            team_stats[away][f"elo_{v.name}"] = v.ratings[away]

        team_stats[home]["wins"] += outcome_home
        team_stats[away]["wins"] += 1 - outcome_home
        team_stats[home]["games_played"] += 1
        team_stats[away]["games_played"] += 1

        if outcome_home:
            team_stats[home]["net_rating"] += margin
            team_stats[away]["net_rating"] -= margin
        else:
            team_stats[home]["net_rating"] -= margin
            team_stats[away]["net_rating"] += margin

    team_stats_all_seasons[int(season)] = team_stats

# Prepare constants for export
elo_constants = {
    "INITIAL_ELO": INITIAL_ELO,
    "K": K,
    "K_CHANGE": K_CHANGE,
}

# Export CSV files
print("Exporting data...")

data_directory = "data"
elo_directory = "elo_history"
comb_directory = os.path.join(data_directory, elo_directory)
os.makedirs(comb_directory, exist_ok=True)

for v in VARIANTS:
    pd.DataFrame(history[v.name]).to_csv(
        os.path.join(comb_directory, f"elo_df_{v.name}.csv"),
        index=False,
    )

# Export json files
with open(os.path.join(comb_directory, "elo_constants.json"), "w") as f:
    json.dump(elo_constants, f)


team_stats_directory = "team_stats"
comb_directory2 = os.path.join(data_directory, team_stats_directory)
os.makedirs(comb_directory2, exist_ok=True)

with open(os.path.join(comb_directory2, "team_stats.json"), "w") as f:
    json.dump(team_stats_all_seasons, f)
    # json.dump({season: dict(stats) for season, stats in team_stats_all_seasons.items()}, f)

print("Elo calculated and data exported successfully.")

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

# Model evaluation
## For all seasons
