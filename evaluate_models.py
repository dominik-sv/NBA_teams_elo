import pandas as pd
import os
import json
from collections import Counter, defaultdict
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


# Constants
NET_RATING_MULTIPLIER = 0.2

# Import
print("Importing data...")
data_directory = "data"
elo_directory = "elo_history"
comb_directory = os.path.join(data_directory, elo_directory)
os.makedirs(comb_directory, exist_ok=True)

VARIANTS_LIST = ["basic", "margin", "home_adv", "updK_end", "updK_start", "transfer_elo"]
elo_df = {
    name: pd.read_csv(os.path.join(comb_directory, f"elo_df_{name}.csv"))
    for name in VARIANTS_LIST
}

stats_directory = "team_stats"
comb_directory2 = os.path.join(data_directory, stats_directory)
os.makedirs(comb_directory2, exist_ok=True)

with open(os.path.join(comb_directory2, "team_stats.json"), "r") as f:
    team_stats = json.load(f)

url = "https://raw.githubusercontent.com/dominik-sv/NBA_teams_elo/main/Data/match_data.csv"
matches_df = pd.read_csv(url)

# Create dataframe of postseason results
results_list = []
postseason_df = matches_df[matches_df["postseason"] == True]

for league in sorted(postseason_df["league"].unique()):
    league_df = postseason_df[postseason_df["league"] == league]

    for season in sorted(league_df["season"].unique()):
        df = league_df[league_df["season"] == season].copy()

        df["matchup"] = df.apply(
            lambda row: tuple(sorted([row["home_name"], row["visitor_name"]])), axis=1
        )
        df["winner"] = df.apply(
            lambda row: row["home_name"] if row["home_win"] else row["visitor_name"],
            axis=1,
        )

        matchups = df.groupby("matchup")

        # Process matchups
        for matchup, group in matchups:
            win_counts = Counter(group["winner"])
            series_winner = win_counts.most_common(1)[0][0]
            team1, team2 = matchup
            team1_wins = win_counts.get(team1, 0)
            team2_wins = win_counts.get(team2, 0)
            game_score = f"{team1_wins}:{team2_wins}"

            results_list.append(
                {
                    "league": league,
                    "season": season,
                    "team1": team1,
                    "team2": team2,
                    "winner": series_winner,
                    "game_score": game_score,
                }
            )

series_results_df = pd.DataFrame(results_list)

MODELS_LIST = [f"elo_{v}" for v in VARIANTS_LIST] + ["win_rate", "net_rating"]

model_evaluations = defaultdict(lambda: {"tae": 0, "tse": 0, "bin": 0, "total_series": 0})


# Evaluation functions
def evaluate_model(expected_outcome, result):
    diff = result - expected_outcome
    exp_outcome_bin = 1 if expected_outcome >= 0.5 else 0
    bin_outcome_correct = 1 if exp_outcome_bin == result else 0
    return diff, bin_outcome_correct


def add_model_evaluation_metrics(model_name, diff, bin_outcome_correct):
    model_evaluations[model_name]["tae"] += abs(diff)
    model_evaluations[model_name]["tse"] += diff**2
    model_evaluations[model_name]["bin"] += bin_outcome_correct
    model_evaluations[model_name]["total_series"] += 1


for series in results_list:
    # Get team stats
    league = series["league"]
    season = str(series["season"])
    team1 = series["team1"]
    team2 = series["team2"]
    t1_stats = team_stats[league][season][team1]
    t2_stats = team_stats[league][season][team2]

    result = 1 if series["winner"] == team1 else 0

    # Elo models
    for v in VARIANTS_LIST:
        model_name = f"elo_{v}"
        expected_outcome = 1 / (1 + 10 ** ((t2_stats[model_name] - t1_stats[model_name]) / 400))
        diff, bin_outcome_correct = evaluate_model(expected_outcome, result)
        add_model_evaluation_metrics(model_name, diff, bin_outcome_correct)

    # Win rate model
    t1_win_rate = max(0.001, min(0.999, t1_stats["wins"] / t1_stats["games_played"]))
    t2_win_rate = max(0.001, min(0.999, t2_stats["wins"] / t2_stats["games_played"]))
    logit_diff = np.log(t1_win_rate / (1 - t1_win_rate)) - np.log(
        t2_win_rate / (1 - t2_win_rate)
    )
    expected_outcome = 1 / (1 + np.exp(-logit_diff))
    diff, bin_outcome_correct = evaluate_model(expected_outcome, result)
    add_model_evaluation_metrics("win_rate", diff, bin_outcome_correct)

    # Net rating model
    net_diff = (
        t1_stats["net_rating"] / t1_stats["games_played"]
        - t2_stats["net_rating"] / t2_stats["games_played"]
    )
    expected_outcome = 1 / (1 + np.exp(-net_diff / NET_RATING_MULTIPLIER))
    diff, bin_outcome_correct = evaluate_model(expected_outcome, result)
    add_model_evaluation_metrics("net_rating", diff, bin_outcome_correct)

# Calculate output metrics
for key, value in model_evaluations.items():
    model = model_evaluations[key]
    model["mae"] = model["tae"] / model["total_series"]
    model["rmse"] = (model["tse"] / model["total_series"]) ** 0.5
    model["bin_error"] = 1 - model["bin"] / model["total_series"]

# Plot results
results_df = pd.DataFrame(model_evaluations).T
results_df = results_df[["mae", "rmse", "bin_error"]]

metrics = {
    "mae": "Mean Absolute Error (MAE)",
    "rmse": "Root Mean Squared Error (RMSE)",
    "bin_error": "Binary Error Rate"
}

plt.figure(figsize=(10, 6))
ax = plt.gca()
ax.yaxis.set_minor_locator(MultipleLocator(0.05))
ax.yaxis.set_major_locator(MultipleLocator(0.05))
ax.set_axisbelow(True)
results_df[["mae", "rmse", "bin_error"]].plot(kind='bar', ax=plt.gca(), rot=45)
plt.ylim(0, 0.6)

plt.grid(axis = 'y', which='both')

plt.title("Model Evaluation Across All Metrics")
plt.xlabel("Model")
plt.ylabel("Score")

plt.legend(title="Metric")
plt.tight_layout()
plt.show()

model_directory = "model_stats"
comb_directory3 = os.path.join(data_directory, model_directory)
os.makedirs(comb_directory3, exist_ok=True)

with open(os.path.join(comb_directory3, "model_stats.json"), "w") as f:
    json.dump(model_evaluations, f, indent=4)

playoff_directory = "playoff_results"
comb_directory4 = os.path.join(data_directory, playoff_directory)
os.makedirs(comb_directory4, exist_ok=True)
pd.DataFrame(results_list).to_csv(os.path.join(comb_directory4, "results.csv"), index=False)