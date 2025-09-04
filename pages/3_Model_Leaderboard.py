import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_data_dir():
    for name in ("Data", "data"):
        path = os.path.join(BASE_DIR, "..", name)
        if os.path.exists(path):
            return path
    return os.path.join(BASE_DIR, "..", "Data")

DATA = get_data_dir()
MODEL_STATS = os.path.join(DATA, "model_stats", "model_stats.json")

st.title("Model Leaderboard")

if not os.path.exists(MODEL_STATS):
    st.warning("Model stats not found. Run `python evaluate_models.py` to create Data/model_stats/model_stats.json.")
    st.stop()

with open(MODEL_STATS) as f:
    stats = json.load(f)

df = pd.DataFrame(stats).T
# Keep defensively: some keys may be missing
for col in ["mae", "rmse", "bin_error"]:
    if col not in df.columns:
        df[col] = float("nan")

df = df[["mae", "rmse", "bin_error"]].copy()
df["Score"] = df[["mae", "rmse", "bin_error"]].sum(axis=1, min_count=1)
df = df.sort_values("Score").reset_index().rename(columns={"index": "Model"})

model_descriptions = {
    "elo_basic": "Classic Elo, no margin or home bonus",
    "elo_margin": "Elo + margin of victory multiplier",
    "elo_home_adv": "Elo + home court advantage",
    "elo_updK_end": "Elo with rising K toward season end",
    "elo_updK_start": "Elo with falling K toward season end",
    "elo_transfer_elo": "Elo transferred from last season with decay",
    "win_rate": "Baseline: regular season win %",
    "net_rating": "Baseline: average net points per game"
}
df["Description"] = df["Model"].map(model_descriptions)

st.markdown("Each model is evaluated on:")
st.markdown("- **MAE**, **RMSE**, **Binary Error**, and combined **Score** (= sum of the three).")

st.dataframe(
    df[["Model", "Description", "mae", "rmse", "bin_error", "Score"]]
    .style.format({col: "{:.3f}" for col in ["mae", "rmse", "bin_error", "Score"]})
)

melt_df = df.melt(id_vars=["Model"], value_vars=["mae", "rmse", "bin_error"], var_name="Metric", value_name="Value")
fig = px.bar(melt_df, x="Model", y="Value", color="Metric", barmode="group", title="Model Error Breakdown")
st.plotly_chart(fig, use_container_width=True)
