# NBA Teams Elo

An end-to-end project analyzing NBA teams using **Elo rating systems**.  
It includes data scraping, Elo calculation, multiple Elo model variations, evaluation of predictive accuracy, and a fully interactive **Streamlit dashboard**.

---

## Features

### Elo Rating Models
- **basic** → Classic Elo system  
- **margin** → Elo with margin of victory adjustment  
- **home_adv** → Elo with home-court advantage  
- **updK_end** → Elo with rising K-factor toward the playoffs  
- **updK_start** → Elo with falling K-factor toward the playoffs  
- **transfer_elo** → Elo transferred from past season with regression to mean  

### Evaluation & Research
- Compare Elo models against win% and net rating baselines  
- Compute **MAE**, **RMSE**, and **binary error** across playoff series  
- Predict **NBA champions** from Elo ratings  
- Analyze the relationship between Elo ratings and win percentage  

### Streamlit Dashboard (pages/)
- **1_Elo_Progression** → Elo progression for any team and season  
- **2_Elo_vs_Win** → Scatterplot of Elo vs. win percentage  
- **3_Model_Leaderboard** → Table + bar chart of model errors  
- **4_Playoff_Predictions** → Series-by-series correctness + champion pick  
- **5_Series_Simulator** → Best-of-3/5/7 series win probability (Elo-based, analytical)  
- **6_Champion_Leaderboard** → Historical champion correctness by model  
- **7_Season_End_Rankings** → Season-end Elo rankings & strongest non-champion  
- **8_Model_Radar** → Radar chart of normalized, inverted model performance  
- **9_PlayIn_Toggle** → Non-destructive tool to mark Play-In dates and save an adjusted CSV

---

## ⚙️ Installation

```bash
git clone https://github.com/dominik-sv/NBA_teams_elo.git
cd NBA_teams_elo
pip install -r requirements.txt
