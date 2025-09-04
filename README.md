# NBA Teams Elo

This repository implements Elo rating systems for NBA teams.  
It includes data scraping, Elo calculation, multiple Elo model variations, model evaluation, and a multipage **Streamlit dashboard** for interactive exploration.

---

## Features
- **Elo rating calculation** with multiple variants:
  - `basic`
  - `margin`
  - `home_adv`
  - `updK_end`
  - `updK_start`
  - `transfer_elo`
- **Evaluation of predictive accuracy** (MAE, RMSE, binary error).
- **Champion prediction and playoff analysis.**
- **Interactive visualizations** in a multipage Streamlit dashboard.

---

## Repository Structure

# NBA_teams_elo

* [Data/](./NBA_teams_elo/Data)
  * [elo_history/](./NBA_teams_elo/Data/elo_history)
    * [elo_constants.json](./NBA_teams_elo/Data/elo_history/elo_constants.json)
    * [elo_df_basic.csv](./NBA_teams_elo/Data/elo_history/elo_df_basic.csv)
    * [elo_df_home_adv.csv](./NBA_teams_elo/Data/elo_history/elo_df_home_adv.csv)
    * [elo_df_margin.csv](./NBA_teams_elo/Data/elo_history/elo_df_margin.csv)
    * [elo_df_transfer_elo.csv](./NBA_teams_elo/Data/elo_history/elo_df_transfer_elo.csv)
    * [elo_df_updK_end.csv](./NBA_teams_elo/Data/elo_history/elo_df_updK_end.csv)
    * [elo_df_updK_start.csv](./NBA_teams_elo/Data/elo_history/elo_df_updK_start.csv)
  * [model_stats/](./NBA_teams_elo/Data/model_stats)
    * [model_stats.json](./NBA_teams_elo/Data/model_stats/model_stats.json)
  * [playoff_results/](./NBA_teams_elo/Data/playoff_results)
    * [results.csv](./NBA_teams_elo/Data/playoff_results/results.csv)
  * [team_stats/](./NBA_teams_elo/Data/team_stats)
    * [team_stats.json](./NBA_teams_elo/Data/team_stats/team_stats.json)
  * [match_data.csv](./NBA_teams_elo/Data/match_data.csv)
* [pages/](./NBA_teams_elo/pages)
  * [1_Elo_Progression.py](./NBA_teams_elo/pages/1_Elo_Progression.py)
  * [2_Elo_vs_Win.py](./NBA_teams_elo/pages/2_Elo_vs_Win.py)
  * [3_Model_Leaderboard.py](./NBA_teams_elo/pages/3_Model_Leaderboard.py)
  * [4_Playoff_Predictions.py](./NBA_teams_elo/pages/4_Playoff_Predictions.py)
  * [5_Series_Simulator.py](./NBA_teams_elo/pages/5_Series_Simulator.py)
  * [6_Champion_Leaderboard.py](./NBA_teams_elo/pages/6_Champion_Leaderboard.py)
  * [7_Season_End_Rankings.py](./NBA_teams_elo/pages/7_Season_End_Rankings.py)
  * [8_Model_Radar.py](./NBA_teams_elo/pages/8_Model_Radar.py)
* [venv/](./NBA_teams_elo/venv)
  * [Include/](./NBA_teams_elo/venv/Include)
  * [Lib/](./NBA_teams_elo/venv/Lib)
    * [site-packages/](./NBA_teams_elo/venv/Lib/site-packages)
      * [pip/](./NBA_teams_elo/venv/Lib/site-packages/pip)
        * [_internal/](./NBA_teams_elo/venv/Lib/site-packages/pip/_internal)
        * [_vendor/](./NBA_teams_elo/venv/Lib/site-packages/pip/_vendor)
        * [__pycache__/](./NBA_teams_elo/venv/Lib/site-packages/pip/__pycache__)
        * [py.typed](./NBA_teams_elo/venv/Lib/site-packages/pip/py.typed)
        * [__init__.py](./NBA_teams_elo/venv/Lib/site-packages/pip/__init__.py)
        * [__main__.py](./NBA_teams_elo/venv/Lib/site-packages/pip/__main__.py)
        * [__pip-runner__.py](./NBA_teams_elo/venv/Lib/site-packages/pip/__pip-runner__.py)
      * [pip-24.0.dist-info/](./NBA_teams_elo/venv/Lib/site-packages/pip-24.0.dist-info)
        * [AUTHORS.txt](./NBA_teams_elo/venv/Lib/site-packages/pip-24.0.dist-info/AUTHORS.txt)
        * [entry_points.txt](./NBA_teams_elo/venv/Lib/site-packages/pip-24.0.dist-info/entry_points.txt)
        * [INSTALLER](./NBA_teams_elo/venv/Lib/site-packages/pip-24.0.dist-info/INSTALLER)
        * [LICENSE.txt](./NBA_teams_elo/venv/Lib/site-packages/pip-24.0.dist-info/LICENSE.txt)
        * [METADATA](./NBA_teams_elo/venv/Lib/site-packages/pip-24.0.dist-info/METADATA)
        * [RECORD](./NBA_teams_elo/venv/Lib/site-packages/pip-24.0.dist-info/RECORD)
        * [REQUESTED](./NBA_teams_elo/venv/Lib/site-packages/pip-24.0.dist-info/REQUESTED)
        * [top_level.txt](./NBA_teams_elo/venv/Lib/site-packages/pip-24.0.dist-info/top_level.txt)
        * [WHEEL](./NBA_teams_elo/venv/Lib/site-packages/pip-24.0.dist-info/WHEEL)
  * [Scripts/](./NBA_teams_elo/venv/Scripts)
    * [activate](./NBA_teams_elo/venv/Scripts/activate)
    * [activate.bat](./NBA_teams_elo/venv/Scripts/activate.bat)
    * [Activate.ps1](./NBA_teams_elo/venv/Scripts/Activate.ps1)
    * [deactivate.bat](./NBA_teams_elo/venv/Scripts/deactivate.bat)
    * [pip.exe](./NBA_teams_elo/venv/Scripts/pip.exe)
    * [pip3.12.exe](./NBA_teams_elo/venv/Scripts/pip3.12.exe)
    * [pip3.exe](./NBA_teams_elo/venv/Scripts/pip3.exe)
    * [python.exe](./NBA_teams_elo/venv/Scripts/python.exe)
    * [pythonw.exe](./NBA_teams_elo/venv/Scripts/pythonw.exe)
  * [pyvenv.cfg](./NBA_teams_elo/venv/pyvenv.cfg)
* [.gitignore](./NBA_teams_elo/.gitignore)
* [calculate_elo.py](./NBA_teams_elo/calculate_elo.py)
* [combine_scraped_data.ipynb](./NBA_teams_elo/combine_scraped_data.ipynb)
* [dashboard.py](./NBA_teams_elo/dashboard.py)
* [evaluate_models.py](./NBA_teams_elo/evaluate_models.py)
* [plot_figures.py](./NBA_teams_elo/plot_figures.py)
* [README.md](./NBA_teams_elo/README.md)
* [requirements.txt](./NBA_teams_elo/requirements.txt)
* [scrape_data.ipynb](./NBA_teams_elo/scrape_data.ipynb)

---

## File Reference (What each file does)

### Root scripts
- **`calculate_elo.py`**  
  Core Elo engine. Reads the game dataset, computes Elo ratings game-by-game for multiple model variants, and exports results for the dashboard.  
  **Outputs:**  
  - `Data/elo_history/elo_df_{model}.csv`  
  - `Data/elo_history/elo_constants.json`  
  - `Data/team_stats/team_stats.json`  

- **`evaluate_models.py`**  
  Evaluates predictive power of Elo models vs baselines (win% and net rating) on playoff series.  
  **Outputs:**  
  - `Data/model_stats/model_stats.json`  
  - `Data/playoff_results/results.csv`  

- **`plot_figures.py`**  
  Quick local visualization of Elo progression and Elo vs. win percentage (outside of Streamlit).  

- **`dashboard.py`**  
  Entry point for the Streamlit dashboard. Provides landing page with app overview, data status, and links to all pages.  

- **`elo_analysis.py`**  
  (Optional) Playground script for ad-hoc analysis outside of the dashboard. Reads from `Data/` and can generate custom plots/tables.  

- **`requirements.txt`**  
  Python dependencies (Streamlit, Pandas, NumPy, Plotly, Matplotlib, etc.).  

- **`notes.md`**  
  Developer notes and to-do items (e.g., how to classify Play-In games).  

### Data prep notebooks
- **`scrape_data.ipynb`**  
  Scrapes NBA data from web sources (e.g., Basketball Reference). Produces raw CSV dumps.  

- **`combine_scraped_data.ipynb`**  
  Cleans and merges scraped raw data into a single canonical file: `Data/match_data.csv`.  

### Data folder (`Data/`)
- **`match_data.csv`** – Unified dataset of NBA games (date, teams, scores, season, league, postseason flag).  
- **`elo_history/`** – Elo rating histories (one CSV per model) + constants JSON.  
- **`team_stats/`** – Season-end team-level stats (wins, Elo ratings per model, net rating).  
- **`model_stats/`** – Aggregated model evaluation results.  
- **`playoff_results/`** – Actual playoff outcomes (CSV).  
- **`custom/`** – Non-destructive adjusted files (e.g., Play-In adjusted `match_data_playin_adjusted.csv`).  

### Dashboard pages (`pages/`)
1. **`1_Elo_Progression.py`** – Select season & team; view Elo progression.  
2. **`2_Elo_vs_Win.py`** – Scatter of final Elo vs win percentage.  
3. **`3_Model_Leaderboard.py`** – Compare models with error metrics (MAE, RMSE, binary error).  
4. **`4_Playoff_Predictions.py`** – Playoff predictions, accuracy, champion pick, matchup simulator.  
5. **`5_Series_Simulator.py`** – Best-of-3/5/7 series probabilities (analytical).  
6. **`6_Champion_Leaderboard.py`** – Historical correctness of models in picking champions.  
7. **`7_Season_End_Rankings.py`** – End-of-season Elo rankings & strongest non-champion.  
8. **`8_Model_Radar.py`** – Radar chart of normalized model performance.  

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/dominik-sv/NBA_teams_elo.git
cd NBA_teams_elo
pip install -r requirements.txt

---

## Run the dashboard
In the terminal, write:
streamlit run dashboard.py

Then open the printed URL (usually something like "localhost")