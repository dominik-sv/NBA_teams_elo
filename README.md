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

* [Data/](./Data)
  * [elo_history/](./Data/elo_history)
    * [elo_constants.json](./Data/elo_history/elo_constants.json)
    * [elo_df_basic.csv](./Data/elo_history/elo_df_basic.csv)
    * [elo_df_home_adv.csv](./Data/elo_history/elo_df_home_adv.csv)
    * [elo_df_margin.csv](./Data/elo_history/elo_df_margin.csv)
    * [elo_df_transfer_elo.csv](./Data/elo_history/elo_df_transfer_elo.csv)
    * [elo_df_updK_end.csv](./Data/elo_history/elo_df_updK_end.csv)
    * [elo_df_updK_start.csv](./Data/elo_history/elo_df_updK_start.csv)
  * [model_stats/](./Data/model_stats)
    * [model_stats.json](./Data/model_stats/model_stats.json)
  * [playoff_results/](./Data/playoff_results)
    * [results.csv](./Data/playoff_results/results.csv)
  * [team_stats/](./Data/team_stats)
    * [team_stats.json](./Data/team_stats/team_stats.json)
  * [match_data.csv](./Data/match_data.csv)
* [pages/](./pages)
  * [1_Elo_Progression.py](./pages/1_Elo_Progression.py)
  * [2_Elo_vs_Win.py](./pages/2_Elo_vs_Win.py)
  * [3_Model_Leaderboard.py](./pages/3_Model_Leaderboard.py)
  * [4_Playoff_Predictions.py](./pages/4_Playoff_Predictions.py)
  * [5_Series_Simulator.py](./pages/5_Series_Simulator.py)
  * [6_Champion_Leaderboard.py](./pages/6_Champion_Leaderboard.py)
  * [7_Season_End_Rankings.py](./pages/7_Season_End_Rankings.py)
  * [8_Model_Radar.py](./pages/8_Model_Radar.py)
* [venv/](./venv)
  * [Include/](./venv/Include)
  * [Lib/](./venv/Lib)
    * [site-packages/](./venv/Lib/site-packages)
      * [pip/](./venv/Lib/site-packages/pip)
        * [_internal/](./venv/Lib/site-packages/pip/_internal)
        * [_vendor/](./venv/Lib/site-packages/pip/_vendor)
        * [__pycache__/](./venv/Lib/site-packages/pip/__pycache__)
        * [py.typed](./venv/Lib/site-packages/pip/py.typed)
        * [__init__.py](./venv/Lib/site-packages/pip/__init__.py)
        * [__main__.py](./venv/Lib/site-packages/pip/__main__.py)
        * [__pip-runner__.py](./venv/Lib/site-packages/pip/__pip-runner__.py)
      * [pip-24.0.dist-info/](./venv/Lib/site-packages/pip-24.0.dist-info)
        * [AUTHORS.txt](./venv/Lib/site-packages/pip-24.0.dist-info/AUTHORS.txt)
        * [entry_points.txt](./venv/Lib/site-packages/pip-24.0.dist-info/entry_points.txt)
        * [INSTALLER](./venv/Lib/site-packages/pip-24.0.dist-info/INSTALLER)
        * [LICENSE.txt](./venv/Lib/site-packages/pip-24.0.dist-info/LICENSE.txt)
        * [METADATA](./venv/Lib/site-packages/pip-24.0.dist-info/METADATA)
        * [RECORD](./venv/Lib/site-packages/pip-24.0.dist-info/RECORD)
        * [REQUESTED](./venv/Lib/site-packages/pip-24.0.dist-info/REQUESTED)
        * [top_level.txt](./venv/Lib/site-packages/pip-24.0.dist-info/top_level.txt)
        * [WHEEL](./venv/Lib/site-packages/pip-24.0.dist-info/WHEEL)
  * [Scripts/](./venv/Scripts)
    * [activate](./venv/Scripts/activate)
    * [activate.bat](./venv/Scripts/activate.bat)
    * [Activate.ps1](./venv/Scripts/Activate.ps1)
    * [deactivate.bat](./venv/Scripts/deactivate.bat)
    * [pip.exe](./venv/Scripts/pip.exe)
    * [pip3.12.exe](./venv/Scripts/pip3.12.exe)
    * [pip3.exe](./venv/Scripts/pip3.exe)
    * [python.exe](./venv/Scripts/python.exe)
    * [pythonw.exe](./venv/Scripts/pythonw.exe)
  * [pyvenv.cfg](./venv/pyvenv.cfg)
* [.gitignore](./.gitignore)
* [calculate_elo.py](./calculate_elo.py)
* [combine_scraped_data.ipynb](./combine_scraped_data.ipynb)
* [dashboard.py](./dashboard.py)
* [evaluate_models.py](./evaluate_models.py)
* [plot_figures.py](./plot_figures.py)
* [README.md](./README.md)
* [requirements.txt](./requirements.txt)
* [scrape_data.ipynb](./scrape_data.ipynb)

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