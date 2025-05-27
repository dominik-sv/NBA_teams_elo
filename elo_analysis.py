import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.cm as cm
import plotly.graph_objs as go
import plotly.express as px

# Data load
url = 'https://raw.githubusercontent.com/dominik-sv/NBA_teams_elo/main/Data/match_data.csv'
df = pd.read_csv(url)

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

# Constants
INITIAL_ELO = 1500
K = 20

# Elaborate elo calculation
elo_basic = defaultdict(lambda: INITIAL_ELO)
elo_margin = defaultdict(lambda: INITIAL_ELO)
history_basic, history_margin = [], []

for season in sorted(df['season'].unique()):
    elo_basic = defaultdict(lambda: INITIAL_ELO)
    elo_margin = defaultdict(lambda: INITIAL_ELO)
    season_games = df[df['season'] == season]

    for _, row in season_games.iterrows():
        home, away = row['home_name'], row['visitor_name']
        home_pts, away_pts = row['home_pts'], row['visitor_pts']
        home_win = row['home_win']
        margin = abs(home_pts - away_pts)

        # Original elo
        elo_home_b, elo_away_b = elo_basic[home], elo_basic[away]
        elo_home_m, elo_away_m = elo_margin[home], elo_margin[away]

        # Expected outcomes
        exp_home_b = 1 / (1 + 10**((elo_away_b - elo_home_b) / 400))
        exp_home_m = 1 / (1 + 10**((elo_away_m - elo_home_m) / 400))
        score_home = 1 if home_win else 0

        # Regular elo update
        delta_b = K * (score_home - exp_home_b)
        elo_basic[home] += delta_b
        elo_basic[away] -= delta_b

        # Margin of victory (MOV) elo update
        elo_diff_m = elo_home_m - elo_away_m
        mov_mult = np.log(margin + 1) * (2.2 / (0.001 * abs(elo_diff_m) + 2.2))
        delta_m = K * (score_home - exp_home_m) * mov_mult
        elo_margin[home] += delta_m
        elo_margin[away] -= delta_m

        # Track
        history_basic.append({
            'date': row['date'], 'season': season, 'postseason': row['postseason'],
            'home_team': home, 'away_team': away,
            'home_elo_before': elo_home_b, 'away_elo_before': elo_away_b,
            'home_elo_after': elo_basic[home], 'away_elo_after': elo_basic[away],
            'home_win': home_win
        })

        history_margin.append({
            'date': row['date'], 'season': season, 'postseason': row['postseason'],
            'home_team': home, 'away_team': away,
            'home_elo_before': elo_home_m, 'away_elo_before': elo_away_m,
            'home_elo_after': elo_margin[home], 'away_elo_after': elo_margin[away],
            'home_win': home_win
        })

elo_df_basic = pd.DataFrame(history_basic)
elo_df_margin = pd.DataFrame(history_margin)

# MOV multiplier curve
margin_range = np.arange(1, 60)
elo_diff_example = 100
mov_multipliers = np.log(margin_range + 1) * (2.2 / (0.001 * abs(elo_diff_example) + 2.2))

plt.figure(figsize=(10, 5))
plt.plot(margin_range, mov_multipliers, color='purple')
plt.title("MOV multiplier vs margin of victory (elo diff = 100)")
plt.xlabel("margin of victory")
plt.ylabel("MOV multiplier")
plt.grid(True)
plt.tight_layout()
plt.show()

# Elo progress for 3 teams 
recent_season = elo_df_basic['season'].max()
recent_regular = elo_df_basic[(elo_df_basic['season'] == recent_season) & (elo_df_basic['postseason'] == False)]
last_date = recent_regular['date'].max()

final_elos = {}
for _, row in recent_regular[recent_regular['date'] == last_date].iterrows():
    final_elos[row['home_team']] = row['home_elo_after']
    final_elos[row['away_team']] = row['away_elo_after']

top_3_teams = sorted(final_elos.items(), key=lambda x: x[1], reverse=True)[:3]
top_3_names = [team for team, _ in top_3_teams]

plt.figure(figsize=(14, 6))
for team in top_3_names:
    team_data = pd.concat([
        recent_regular[recent_regular['home_team'] == team][['date', 'home_elo_after']].rename(columns={'home_elo_after': 'elo'}),
        recent_regular[recent_regular['away_team'] == team][['date', 'away_elo_after']].rename(columns={'away_elo_after': 'elo'})
    ])
    team_data = team_data.sort_values('date')
    plt.plot(team_data['date'], team_data['elo'], label=team)

plt.title(f"elo progression for 3 teams – {recent_season}")
plt.xlabel("date")
plt.ylabel("elo rating")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Interactive elo progress (all teams), plotly
teams = sorted(pd.unique(recent_regular[['home_team', 'away_team']].values.ravel()))
fig = go.Figure()

for team in teams:
    team_data = pd.concat([
        recent_regular[recent_regular['home_team'] == team][['date', 'home_elo_after']].rename(columns={'home_elo_after': 'elo'}),
        recent_regular[recent_regular['away_team'] == team][['date', 'away_elo_after']].rename(columns={'away_elo_after': 'elo'})
    ])
    team_data = team_data.sort_values('date')
    fig.add_trace(go.Scatter(
        x=team_data['date'],
        y=team_data['elo'],
        mode='lines',
        name=team
    ))

fig.update_layout(
    title=f"interactive elo progress – {recent_season} (basic elo)",
    xaxis_title="date",
    yaxis_title="elo rating",
    template="plotly_white",
    legend=dict(font=dict(size=10), orientation='v')
)
fig.show()

# Elo compared to win %, plotly
from collections import defaultdict
team_stats = defaultdict(lambda: {'wins': 0, 'games': 0, 'elo': None})

for _, row in recent_regular.iterrows():
    home = row['home_team']
    away = row['away_team']
    win = row['home_win']

    team_stats[home]['games'] += 1
    team_stats[away]['games'] += 1
    if win:
        team_stats[home]['wins'] += 1
    else:
        team_stats[away]['wins'] += 1

# Track for each team's elo in the season
for team in pd.unique(recent_regular[['home_team', 'away_team']].values.ravel()):
    team_games = pd.concat([
        recent_regular[recent_regular['home_team'] == team][['date', 'home_elo_after']].rename(columns={'home_elo_after': 'elo'}),
        recent_regular[recent_regular['away_team'] == team][['date', 'away_elo_after']].rename(columns={'away_elo_after': 'elo'})
    ])
    team_games = team_games.sort_values('date')
    if not team_games.empty:
        team_stats[team]['elo'] = team_games.iloc[-1]['elo']

team_data = pd.DataFrame([
    {'team': team, 'win_pct': stats['wins'] / stats['games'], 'elo': stats['elo']}
    for team, stats in team_stats.items()
    if stats['elo'] is not None
])

fig2 = px.scatter(
    team_data,
    x='elo',
    y='win_pct',
    text='team',
    color='team',
    title=f"elo vs win percentage – {recent_season} regular season",
    labels={'elo': 'final elo rating', 'win_pct': 'win percentage'}
)
fig2.update_traces(textposition='top center')
fig2.update_layout(template='plotly_white', showlegend=False)
fig2.show()