import pandas as pd
import os

# Import
data_directory = "data"
elo_directory = "elo_history"
comb_directory = os.path.join(data_directory, elo_directory)
os.makedirs(comb_directory, exist_ok=True)

MODELS_LIST = ["basic", "margin", "home_adv", "updK_end", "updK_start"]

elo_df_basic = pd.read_csv(os.path.join(comb_directory, f"elo_df_basic.csv"))
elo_df_margin = pd.read_csv(os.path.join(comb_directory, f"elo_df_margin.csv"))
elo_df_home_adv = pd.read_csv(os.path.join(comb_directory, f"elo_df_home_adv.csv"))
elo_df_updK_end = pd.read_csv(os.path.join(comb_directory, f"elo_df_updK_end.csv"))
elo_df_updK_start = pd.read_csv(os.path.join(comb_directory, f"elo_df_updK_start.csv"))
